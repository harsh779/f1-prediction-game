import streamlit as st
import pandas as pd
from datetime import datetime
import json
from database import SessionLocal, engine
import models
from sqlalchemy.orm import Session
import bcrypt
from typing import List

# Initialize database
models.Base.metadata.create_all(bind=engine)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None

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
        
        # Get available races
        db = get_db()
        races = db.query(models.Race).filter(models.Race.practice1_start > datetime.now()).all()
        
        if not races:
            st.warning("No upcoming races available")
            return
        
        race = st.selectbox("Select Race", races, format_func=lambda x: x.name)
        
        # Driver predictions
        st.subheader("Driver Predictions")
        drivers = {
            'p1': st.text_input("1st Place Driver"),
            'p2': st.text_input("2nd Place Driver"),
            'p3': st.text_input("3rd Place Driver"),
            'p10': st.text_input("10th Place Driver"),
            'p11': st.text_input("11th Place Driver"),
            'p19': st.text_input("19th Place Driver"),
            'p20': st.text_input("20th Place Driver")
        }
        
        # Constructor predictions
        st.subheader("Constructor Predictions")
        constructors = {
            'p1': st.text_input("1st Place Constructor"),
            'p2': st.text_input("2nd Place Constructor"),
            'p5': st.text_input("5th Place Constructor"),
            'p6': st.text_input("6th Place Constructor"),
            'p10': st.text_input("10th Place Constructor")
        }
        
        # Wildcard predictions
        st.subheader("Wildcard Predictions")
        wildcards = {
            'biggest_loser': st.text_input("Biggest Position Loser"),
            'sprint_biggest_loser': st.text_input("Sprint Race Biggest Loser"),
            'sprint_biggest_gainer': st.text_input("Sprint Race Biggest Gainer")
        }
        
        if st.button("Submit Prediction"):
            if all(drivers.values()) and all(constructors.values()):
                prediction = create_prediction(
                    st.session_state.user.id,
                    race.id,
                    drivers,
                    constructors,
                    wildcards
                )
                st.success("Prediction submitted successfully!")
            else:
                st.error("Please fill in all required fields")
    
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
        
        if not predictions:
            st.info("No predictions made yet")
            return
        
        for pred in predictions:
            st.subheader(f"Race: {pred.race.name}")
            st.write(f"Points: {pred.points}")
            st.write("Driver Predictions:")
            st.write(f"P1: {pred.p1_driver}")
            st.write(f"P2: {pred.p2_driver}")
            st.write(f"P3: {pred.p3_driver}")
            st.write(f"P10: {pred.p10_driver}")
            st.write(f"P11: {pred.p11_driver}")
            st.write(f"P19: {pred.p19_driver}")
            st.write(f"P20: {pred.p20_driver}")
            st.write("Constructor Predictions:")
            st.write(f"P1: {pred.p1_constructor}")
            st.write(f"P2: {pred.p2_constructor}")
            st.write(f"P5: {pred.p5_constructor}")
            st.write(f"P6: {pred.p6_constructor}")
            st.write(f"P10: {pred.p10_constructor}")
            st.write("Wildcard Predictions:")
            st.write(f"Biggest Loser: {pred.biggest_loser}")
            if pred.race.is_sprint:
                st.write(f"Sprint Biggest Loser: {pred.sprint_biggest_loser}")
                st.write(f"Sprint Biggest Gainer: {pred.sprint_biggest_gainer}")
            st.markdown("---")

if __name__ == "__main__":
    main() 