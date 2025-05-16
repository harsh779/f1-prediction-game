from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from models import Base, User, Race, Prediction, RaceResult
from database import engine

def init_db():
    print("Initializing database...")
    
    # Remove existing database file if it exists
    if os.path.exists("f1_predictions.db"):
        print("Removing existing database...")
        os.remove("f1_predictions.db")
    
    # Create all tables
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Database setup completed successfully!")

if __name__ == "__main__":
    init_db() 