import streamlit as st
import pandas as pd
from datetime import datetime
import json
from database import SessionLocal, engine
import models
from sqlalchemy.orm import Session
import bcrypt
from typing import List
from f1_data import F1Data

# Initialize database
models.Base.metadata.create_all(bind=engine)

# Initialize F1 data fetcher
f1_data = F1Data()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'show_success' not in st.session_state:
    st.session_state.show_success = False
if 'registration_success' not in st.session_state:
    st.session_state.registration_success = False

# Cache F1 data
@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def get_cached_f1_data():
    st.write("Debug: Fetching F1 data")
    races = f1_data.get_upcoming_races()
    drivers = f1_data.get_drivers()
    constructors = f1_data.get_constructors()
    st.write(f"Debug: Fetched {len(races)} races, {len(drivers)} drivers, {len(constructors)} constructors")
    return {
        'races': races,
        'drivers': drivers,
        'constructors': constructors
    }

# Clear cache on app start
get_cached_f1_data.clear()

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        st.error(f"Password verification error: {str(e)}")
        return False

def login_user(email: str, password: str) -> bool:
    try:
        db = get_db()
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user:
            st.error("User not found")
            return False
            
        if verify_password(password, user.password):
            st.session_state.user = user
            return True
        else:
            st.error("Invalid password")
            return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False
    finally:
        db.close()

def register_user(email: str, password: str, name: str) -> bool:
    try:
        db = get_db()
        # Check if user already exists
        existing_user = db.query(models.User).filter(models.User.email == email).first()
        if existing_user:
            st.error("Email already registered")
            return False
        
        # Create new user
        hashed_password = hash_password(password)
        new_user = models.User(email=email, password=hashed_password, name=name)
        db.add(new_user)
        db.commit()
        return True
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False
    finally:
        db.close()

def create_prediction(
    user_id: int,
    race_id: int,
    drivers: dict,
    constructors: dict,
    wildcards: dict
) -> models.Prediction:
    db = get_db()
    prediction = models.Prediction(
        user_id=user_id,
        race_id=race_id,
        p1_driver=drivers['p1'],
        p2_driver=drivers['p2'],
        p3_driver=drivers['p3'],
        p10_driver=drivers['p10'],
        p11_driver=drivers['p11'],
        p19_driver=drivers['p19'],
        p20_driver=drivers['p20'],
        p1_constructor=constructors['p1'],
        p2_constructor=constructors['p2'],
        p5_constructor=constructors['p5'],
        p6_constructor=constructors['p6'],
        p10_constructor=constructors['p10'],
        biggest_loser=wildcards.get('biggest_loser'),
        sprint_biggest_loser=wildcards.get('sprint_biggest_loser'),
        sprint_biggest_gainer=wildcards.get('sprint_biggest_gainer')
    )
    db.add(prediction)
    db.commit()
    return prediction

def calculate_points(prediction: models.Prediction, result: models.RaceResult) -> float:
    points = 0.0
    
    # Driver positions
    driver_positions = {
        prediction.p1_driver: 1,
        prediction.p2_driver: 2,
        prediction.p3_driver: 3,
        prediction.p10_driver: 10,
        prediction.p11_driver: 11,
        prediction.p19_driver: 19,
        prediction.p20_driver: 20
    }
    
    actual_positions = {
        result.p1_driver: 1,
        result.p2_driver: 2,
        result.p3_driver: 3,
        result.p10_driver: 10,
        result.p11_driver: 11,
        result.p19_driver: 19,
        result.p20_driver: 20
    }
    
    # Calculate driver position points
    for driver, pred_pos in driver_positions.items():
        if driver in actual_positions:
            actual_pos = actual_positions[driver]
            # New rule: +2 for exact match, -abs(difference) for mismatch
            points += 2 if pred_pos == actual_pos else -abs(pred_pos - actual_pos)
    
    # Constructor points
    constructor_results = json.loads(result.constructor_positions)
    constructor_predictions = {
        prediction.p1_constructor: 1,
        prediction.p2_constructor: 2,
        prediction.p5_constructor: 5,
        prediction.p6_constructor: 6,
        prediction.p10_constructor: 10
    }
    
    # Calculate constructor points based on sum of driver positions
    for constructor, pred_pos in constructor_predictions.items():
        if constructor in constructor_results:
            actual_pos = constructor_results[constructor]
            # Same scoring rule as drivers: +2 for exact match, -abs(difference) for mismatch
            points += 2 if pred_pos == actual_pos else -abs(pred_pos - actual_pos)
    
    # Wildcard points
    if prediction.biggest_loser == result.biggest_loser:
        points += 5
    if prediction.sprint_biggest_loser == result.sprint_biggest_loser:
        points += 5
    if prediction.sprint_biggest_gainer == result.sprint_biggest_gainer:
        points += 5
    
    # Winner prediction points
    if prediction.race_winner == result.p1_driver:
        points += 50
    if prediction.constructor_winner == result.p1_constructor:
        points += 25
    
    return points

def handle_missing_prediction(predictions: List[models.Prediction], results: List[models.RaceResult]) -> float:
    """Handle cases where a user didn't submit predictions."""
    if not predictions:
        # Find the lowest score among other players
        lowest_score = min([calculate_points(p, r) for p, r in zip(predictions, results)])
        return lowest_score - 5
    return 0.0

def validate_prediction(prediction: models.Prediction, race: models.Race) -> bool:
    """Validate if the prediction is valid based on the rules."""
    # Check if all required predictions are present
    required_fields = [
        'p1_driver', 'p2_driver', 'p3_driver', 'p10_driver', 'p11_driver',
        'p19_driver', 'p20_driver', 'p1_constructor', 'p2_constructor',
        'p5_constructor', 'p6_constructor', 'p10_constructor',
        'biggest_loser', 'sprint_biggest_loser', 'sprint_biggest_gainer',
        'race_winner', 'constructor_winner'
    ]
    
    for field in required_fields:
        if not getattr(prediction, field, None):
            return False
    
    return True

# Page config
st.set_page_config(
    page_title="F1 Prediction Game",
    page_icon="🏎️",
    layout="wide"
)

# Navigation
def show_navigation():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <h1>🏎️ F1 Prediction Game</h1>
            </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.user:
        with col3:
            if st.button("Logout"):
                st.session_state.user = None
                st.session_state.page = 'home'
                st.rerun()

# Home page
def show_home():
    st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
            <h2>Welcome to the F1 Prediction Game!</h2>
            <p>Predict race results and compete with friends!</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_button"):
            if not email or not password:
                st.error("Please enter both email and password")
                return
            if login_user(email, password):
                st.session_state.show_success = True
                st.rerun()
    
    with col2:
        st.markdown("### Register")
        # Registration form
        with st.form("register_form", clear_on_submit=True):
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            name = st.text_input("Name", key="register_name")
            submit = st.form_submit_button("Register")
            
            if submit:
                if not email or not password or not name:
                    st.error("Please fill in all registration fields")
                else:
                    try:
                        if register_user(email, password, name):
                            st.success("Registration successful! Please log in.")
                            st.session_state.registration_success = True
                            st.rerun()
                        else:
                            st.error("Registration failed. Please try again.")
                    except Exception as e:
                        st.error(f"Registration error: {str(e)}")

# Predictions page
def show_predictions():
    st.markdown(f"### Welcome, {st.session_state.user.name}!")
    
    # Get F1 data
    f1_data = get_cached_f1_data()
    races = f1_data['races']
    drivers = f1_data['drivers']
    constructors = f1_data['constructors']
    
    # Race selection
    st.markdown("### Select Race")
    if not races:
        st.error("No races available")
        return
        
    # Create race options
    race_options = [f"{race['name']} ({race['date']})" for race in races]
    selected_race_name = st.selectbox("Choose a race", options=race_options)
    
    # Get selected race details
    selected_race = next(race for race in races if f"{race['name']} ({race['date']})" == selected_race_name)
    
    # Display race details
    st.markdown(f"""
        ### {selected_race['name']}
        **Circuit:** {selected_race['circuit']}  
        **Country:** {selected_race['country']}  
        **Date:** {selected_race['date']}
    """)
    st.markdown("---")
    
    # Create prediction form
    with st.form("prediction_form"):
        # Driver predictions
        st.markdown("### Driver Predictions")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Top 3")
            p1 = st.selectbox("1st Place", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
            p2 = st.selectbox("2nd Place", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
            p3 = st.selectbox("3rd Place", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
        
        with col2:
            st.markdown("#### Other Positions")
            p10 = st.selectbox("10th Place", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
            p11 = st.selectbox("11th Place", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
            p19 = st.selectbox("19th Place", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
            p20 = st.selectbox("20th Place", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
        
        # Constructor predictions
        st.markdown("### Constructor Predictions")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Top 2")
            c1 = st.selectbox("1st Place Constructor", options=constructors, format_func=lambda x: x['name'])
            c2 = st.selectbox("2nd Place Constructor", options=constructors, format_func=lambda x: x['name'])
        
        with col2:
            st.markdown("#### Other Positions")
            c5 = st.selectbox("5th Place Constructor", options=constructors, format_func=lambda x: x['name'])
            c6 = st.selectbox("6th Place Constructor", options=constructors, format_func=lambda x: x['name'])
            c10 = st.selectbox("10th Place Constructor", options=constructors, format_func=lambda x: x['name'])
        
        # Wildcard predictions
        st.markdown("### Wildcard Predictions")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Race")
            biggest_loser = st.selectbox("Biggest Loser", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
        
        with col2:
            st.markdown("#### Sprint (if applicable)")
            sprint_biggest_loser = st.selectbox("Sprint Biggest Loser", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
            sprint_biggest_gainer = st.selectbox("Sprint Biggest Gainer", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
        
        # Winner predictions
        st.markdown("### Winner Predictions")
        col1, col2 = st.columns(2)
        
        with col1:
            race_winner = st.selectbox("Race Winner", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
        
        with col2:
            constructor_winner = st.selectbox("Constructor Winner", options=constructors, format_func=lambda x: x['name'])
        
        # Submit button
        submit = st.form_submit_button("Submit Prediction")
        
        if submit:
            # Validate predictions
            if not all([p1, p2, p3, p10, p11, p19, p20, c1, c2, c5, c6, c10, 
                       biggest_loser, sprint_biggest_loser, sprint_biggest_gainer,
                       race_winner, constructor_winner]):
                st.error("Please fill in all prediction fields")
                return
            
            try:
                # Create prediction
                prediction = models.Prediction(
                    user_id=st.session_state.user.id,
                    race_id=selected_race['id'],
                    p1_driver=p1['id'],
                    p2_driver=p2['id'],
                    p3_driver=p3['id'],
                    p10_driver=p10['id'],
                    p11_driver=p11['id'],
                    p19_driver=p19['id'],
                    p20_driver=p20['id'],
                    p1_constructor=c1['id'],
                    p2_constructor=c2['id'],
                    p5_constructor=c5['id'],
                    p6_constructor=c6['id'],
                    p10_constructor=c10['id'],
                    biggest_loser=biggest_loser['id'],
                    sprint_biggest_loser=sprint_biggest_loser['id'],
                    sprint_biggest_gainer=sprint_biggest_gainer['id'],
                    race_winner=race_winner['id'],
                    constructor_winner=constructor_winner['id']
                )
                
                # Save prediction
                db = get_db()
                db.add(prediction)
                db.commit()
                st.success("Prediction submitted successfully!")
                
            except Exception as e:
                st.error(f"Error submitting prediction: {str(e)}")

# Leaderboard page
def show_leaderboard():
    st.markdown("### Leaderboard")
    
    with Session(engine) as db:
        users = db.query(models.User).all()
        leaderboard_data = []
        
        for user in users:
            predictions = db.query(models.Prediction).filter(models.Prediction.user_id == user.id).all()
            total_points = sum(pred.points for pred in predictions)
            leaderboard_data.append({
                'Name': user.name,
                'Points': total_points,
                'Predictions': len(predictions)
            })
        
        if leaderboard_data:
            df = pd.DataFrame(leaderboard_data)
            df = df.sort_values('Points', ascending=False)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No predictions have been made yet.")

# Main app
def main():
    show_navigation()
    
    # Show success messages if needed
    if st.session_state.show_success:
        st.success("Login successful!")
        st.session_state.show_success = False
    
    if st.session_state.registration_success:
        st.success("Registration successful! Please login.")
        st.session_state.registration_success = False
    
    if st.session_state.user:
        tab1, tab2 = st.tabs(["Make Prediction", "Leaderboard"])
        with tab1:
            show_predictions()
        with tab2:
            show_leaderboard()
    else:
        show_home()

if __name__ == "__main__":
    main() 