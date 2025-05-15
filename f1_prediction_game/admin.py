import streamlit as st
import pandas as pd
from datetime import datetime
import json
from database import SessionLocal, engine
import models
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def is_admin():
    return st.session_state.user and st.session_state.user.username == "admin"

def add_race(name: str, date: datetime, practice1_start: datetime, is_sprint: bool):
    db = get_db()
    race = models.Race(
        name=name,
        date=date,
        practice1_start=practice1_start,
        is_sprint=is_sprint
    )
    db.add(race)
    db.commit()
    return race

def add_race_result(
    race_id: int,
    drivers: dict,
    constructor_positions: dict,
    wildcards: dict
):
    db = get_db()
    result = models.RaceResult(
        race_id=race_id,
        p1_driver=drivers['p1'],
        p2_driver=drivers['p2'],
        p3_driver=drivers['p3'],
        p10_driver=drivers['p10'],
        p11_driver=drivers['p11'],
        p19_driver=drivers['p19'],
        p20_driver=drivers['p20'],
        constructor_positions=json.dumps(constructor_positions),
        biggest_loser=wildcards.get('biggest_loser'),
        sprint_biggest_loser=wildcards.get('sprint_biggest_loser'),
        sprint_biggest_gainer=wildcards.get('sprint_biggest_gainer')
    )
    db.add(result)
    
    # Update user points
    race = db.query(models.Race).filter(models.Race.id == race_id).first()
    predictions = db.query(models.Prediction).filter(models.Prediction.race_id == race_id).all()
    
    for prediction in predictions:
        points = calculate_points(prediction, result)
        prediction.points = points
        prediction.user.total_points += points
    
    db.commit()
    return result

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
    st.title("F1 Prediction Game Admin")
    
    if not is_admin():
        st.error("Access denied. Admin privileges required.")
        return
    
    menu = st.sidebar.selectbox(
        "Admin Menu",
        ["Add Race", "Enter Results", "View All Predictions"]
    )
    
    if menu == "Add Race":
        st.header("Add New Race")
        
        name = st.text_input("Race Name")
        date = st.date_input("Race Date")
        time = st.time_input("Race Time")
        p1_date = st.date_input("Practice 1 Date")
        p1_time = st.time_input("Practice 1 Time")
        is_sprint = st.checkbox("Sprint Race Weekend")
        
        if st.button("Add Race"):
            race_datetime = datetime.combine(date, time)
            p1_datetime = datetime.combine(p1_date, p1_time)
            
            race = add_race(name, race_datetime, p1_datetime, is_sprint)
            st.success(f"Race {name} added successfully!")
    
    elif menu == "Enter Results":
        st.header("Enter Race Results")
        
        db = get_db()
        races = db.query(models.Race).filter(
            models.Race.date < datetime.now()
        ).order_by(models.Race.date.desc()).all()
        
        if not races:
            st.warning("No past races found")
            return
        
        race = st.selectbox("Select Race", races, format_func=lambda x: x.name)
        
        # Driver results
        st.subheader("Driver Results")
        drivers = {
            'p1': st.text_input("1st Place Driver"),
            'p2': st.text_input("2nd Place Driver"),
            'p3': st.text_input("3rd Place Driver"),
            'p10': st.text_input("10th Place Driver"),
            'p11': st.text_input("11th Place Driver"),
            'p19': st.text_input("19th Place Driver"),
            'p20': st.text_input("20th Place Driver")
        }
        
        # Constructor results
        st.subheader("Constructor Results")
        constructor_positions = {}
        for i in range(1, 11):
            constructor = st.text_input(f"{i}th Place Constructor")
            if constructor:
                constructor_positions[constructor] = i
        
        # Wildcard results
        st.subheader("Wildcard Results")
        wildcards = {
            'biggest_loser': st.text_input("Biggest Position Loser"),
            'sprint_biggest_loser': st.text_input("Sprint Race Biggest Loser") if race.is_sprint else None,
            'sprint_biggest_gainer': st.text_input("Sprint Race Biggest Gainer") if race.is_sprint else None
        }
        
        if st.button("Submit Results"):
            if all(drivers.values()) and constructor_positions:
                result = add_race_result(
                    race.id,
                    drivers,
                    constructor_positions,
                    wildcards
                )
                st.success("Results submitted and points calculated!")
            else:
                st.error("Please fill in all required fields")
    
    elif menu == "View All Predictions":
        st.header("All Predictions")
        
        db = get_db()
        predictions = db.query(models.Prediction).all()
        
        if not predictions:
            st.info("No predictions found")
            return
        
        for pred in predictions:
            st.subheader(f"Race: {pred.race.name}")
            st.write(f"User: {pred.user.username}")
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