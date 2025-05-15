from database import engine
from models import Base
import os

def init_db():
    # Remove existing database file if it exists
    if os.path.exists("f1_predictions.db"):
        os.remove("f1_predictions.db")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db() 