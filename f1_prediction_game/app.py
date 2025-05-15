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
    
    for constructor, pred_pos in constructor_predictions.items():
        if constructor in constructor_results:
            actual_pos = constructor_results[constructor]
            points += 2 if pred_pos == actual_pos else -abs(pred_pos - actual_pos)
    
    # Wildcard points
    if prediction.biggest_loser == result.biggest_loser:
        points += 5
    if prediction.sprint_biggest_loser == result.sprint_biggest_loser:
        points += 5
    if prediction.sprint_biggest_gainer == result.sprint_biggest_gainer:
        points += 5
    
    return points

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
    
    # Display race details in a cleaner format
    st.markdown(f"""
        ### {selected_race['name']}
        **Circuit:** {selected_race['circuit']}  
        **Country:** {selected_race['country']}  
        **Date:** {selected_race['date']}
    """)
    st.markdown("---")
    
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
        p4 = st.selectbox("4th Place", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
        p5 = st.selectbox("5th Place", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
        p6 = st.selectbox("6th Place", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
    
    # Constructor predictions
    st.markdown("### Constructor Predictions")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Top 3")
        c1 = st.selectbox("1st Place", options=constructors, format_func=lambda x: x['name'])
        c2 = st.selectbox("2nd Place", options=constructors, format_func=lambda x: x['name'])
        c3 = st.selectbox("3rd Place", options=constructors, format_func=lambda x: x['name'])
    
    with col2:
        st.markdown("#### Other Positions")
        c4 = st.selectbox("4th Place", options=constructors, format_func=lambda x: x['name'])
        c5 = st.selectbox("5th Place", options=constructors, format_func=lambda x: x['name'])
        c6 = st.selectbox("6th Place", options=constructors, format_func=lambda x: x['name'])
    
    # Wildcard predictions
    st.markdown("### Wildcard Predictions")
    col1, col2 = st.columns(2)
    
    with col1:
        fastest_lap = st.selectbox("Fastest Lap", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
    
    with col2:
        dnf = st.selectbox("First DNF", options=drivers, format_func=lambda x: f"{x['name']} (#{x['number']})")
    
    # Submit prediction
    if st.button("Submit Prediction"):
        prediction = {
            'race_id': selected_race['id'],
            'driver_predictions': {
                'p1': p1['id'],
                'p2': p2['id'],
                'p3': p3['id'],
                'p4': p4['id'],
                'p5': p5['id'],
                'p6': p6['id']
            },
            'constructor_predictions': {
                'c1': c1['id'],
                'c2': c2['id'],
                'c3': c3['id'],
                'c4': c4['id'],
                'c5': c5['id'],
                'c6': c6['id']
            },
            'wildcard_predictions': {
                'fastest_lap': fastest_lap['id'],
                'dnf': dnf['id']
            }
        }
        
        with Session(engine) as db:
            new_prediction = models.Prediction(
                user_id=st.session_state.user.id,
                race_id=selected_race['id'],
                predictions=json.dumps(prediction)
            )
            db.add(new_prediction)
            db.commit()
            st.success("Prediction submitted successfully!")

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