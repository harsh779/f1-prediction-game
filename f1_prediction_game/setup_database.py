from database import Base, engine
from models import User, Prediction
from sqlalchemy import text
import time

def init_db():
    try:
        # Drop all tables
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped successfully")
        
        # Create all tables
        print("Creating new tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
        return True
    except Exception as e:
        print(f"Error during database setup: {str(e)}")
        print("\nPlease make sure:")
        print("1. No other process is actively using the database")
        print("2. You have write permissions in the current directory")
        print("3. The database file is not locked by another process")
        return False

if __name__ == "__main__":
    print("Initializing database...")
    if init_db():
        print("Database setup completed successfully!")
    else:
        print("Database setup failed. Please follow the instructions above and try again.") 