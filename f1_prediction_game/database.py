from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Check if running on Streamlit Cloud
if os.getenv('STREAMLIT_SERVER_RUNNING'):
    # Use PostgreSQL for Streamlit Cloud
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/f1_prediction')
else:
    # Use SQLite for local development
    DATABASE_URL = "sqlite:///f1_predictions.db"

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close() 