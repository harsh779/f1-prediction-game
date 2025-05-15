import os
from database import engine
from models import Base

def init_db():
    # Remove existing database file if it exists
    if os.path.exists("f1_predictions.db"):
        os.remove("f1_predictions.db")
        print("Removed existing database file")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db() 