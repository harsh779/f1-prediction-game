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

# Cache F1 data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_f1_data():
    return {
        'races': f1_data.get_upcoming_races(),
        'drivers': f1_data.get_drivers(),
        'constructors': f1_data.get_constructors(),
        'driver_constructor_map': f1_data.get_driver_constructor_mapping()
    }

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def login_user(username: str, password: str) -> bool:
    db = get_db()
    user = db.query(models.User).filter(models.User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        st.session_state.user = user
        return True
    return False

def register_user(username: str, email: str, password: str) -> bool:
    db = get_db()
    if db.query(models.User).filter(models.User.username == username).first():
        return False
    
    hashed_password = hash_password(password)
    user = models.User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    return True

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

def main():
    st.title("F1 Prediction Game")
    
    # Sidebar for navigation
    menu = st.sidebar.selectbox(
        "Menu",
        ["Login", "Register", "Make Prediction", "Leaderboard", "My Predictions"]
    )
    
    if menu == "Login":
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(username, password):
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
    
    elif menu == "Register":
        st.header("Register")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            if register_user(username, email, password):
                st.success("Registration successful! Please login.")
            else:
                st.error("Username already exists")
    
    elif menu == "Make Prediction":
        if not st.session_state.user:
            st.warning("Please login first")
            return
        
        st.header("Make Prediction")
        
        # Get F1 data
        f1_data_cache = get_cached_f1_data()
        races = f1_data_cache['races']
        drivers = f1_data_cache['drivers']
        constructors = f1_data_cache['constructors']
        
        if not races:
            st.warning("No upcoming races available")
            return
        
        # Race selection
        race_options = {f"{race['name']} ({race['date']})": race for race in races}
        selected_race = st.selectbox("Select Race", options=list(race_options.keys()))
        race = race_options[selected_race]
        
        # Driver predictions
        st.subheader("Driver Predictions")
        driver_options = {f"{driver['name']} (#{driver['number']})": driver['id'] for driver in drivers}
        
        drivers = {
            'p1': st.selectbox("1st Place Driver", options=list(driver_options.keys())),
            'p2': st.selectbox("2nd Place Driver", options=list(driver_options.keys())),
            'p3': st.selectbox("3rd Place Driver", options=list(driver_options.keys())),
            'p10': st.selectbox("10th Place Driver", options=list(driver_options.keys())),
            'p11': st.selectbox("11th Place Driver", options=list(driver_options.keys())),
            'p19': st.selectbox("19th Place Driver", options=list(driver_options.keys())),
            'p20': st.selectbox("20th Place Driver", options=list(driver_options.keys()))
        }
        
        # Constructor predictions
        st.subheader("Constructor Predictions")
        constructor_options = {constructor['name']: constructor['id'] for constructor in constructors}
        
        constructors = {
            'p1': st.selectbox("1st Place Constructor", options=list(constructor_options.keys())),
            'p2': st.selectbox("2nd Place Constructor", options=list(constructor_options.keys())),
            'p5': st.selectbox("5th Place Constructor", options=list(constructor_options.keys())),
            'p6': st.selectbox("6th Place Constructor", options=list(constructor_options.keys())),
            'p10': st.selectbox("10th Place Constructor", options=list(constructor_options.keys()))
        }
        
        # Wildcard predictions
        st.subheader("Wildcard Predictions")
        wildcards = {
            'biggest_loser': st.selectbox("Biggest Position Loser", options=list(driver_options.keys())),
            'sprint_biggest_loser': st.selectbox("Sprint Race Biggest Loser", options=list(driver_options.keys())),
            'sprint_biggest_gainer': st.selectbox("Sprint Race Biggest Gainer", options=list(driver_options.keys()))
        }
        
        if st.button("Submit Prediction"):
            # Convert selections to IDs
            drivers = {k: driver_options[v] for k, v in drivers.items()}
            constructors = {k: constructor_options[v] for k, v in constructors.items()}
            wildcards = {k: driver_options[v] for k, v in wildcards.items()}
            
            prediction = create_prediction(
                st.session_state.user.id,
                int(race['id']),
                drivers,
                constructors,
                wildcards
            )
            st.success("Prediction submitted successfully!")
    
    elif menu == "Leaderboard":
        st.header("Leaderboard")
        db = get_db()
        users = db.query(models.User).order_by(models.User.total_points.desc()).all()
        
        leaderboard_data = []
        for user in users:
            leaderboard_data.append({
                "Username": user.username,
                "Total Points": user.total_points
            })
        
        st.table(pd.DataFrame(leaderboard_data))
    
    elif menu == "My Predictions":
        if not st.session_state.user:
            st.warning("Please login first")
            return
        
        st.header("My Predictions")
        db = get_db()
        predictions = db.query(models.Prediction).filter(
            models.Prediction.user_id == st.session_state.user.id
        ).all()
        
        if predictions:
            for prediction in predictions:
                st.subheader(f"Race {prediction.race_id}")
                st.write(f"P1 Driver: {prediction.p1_driver}")
                st.write(f"P2 Driver: {prediction.p2_driver}")
                st.write(f"P3 Driver: {prediction.p3_driver}")
                st.write("---")
        else:
            st.info("No predictions made yet")

if __name__ == "__main__":
    main() 