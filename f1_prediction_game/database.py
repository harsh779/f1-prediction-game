from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use SQLite for both local and Streamlit Cloud
DATABASE_URL = "sqlite:///f1_predictions.db"

# Create engine with proper SQLite configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

# Initialize database
def init_db():
    Base.metadata.create_all(bind=engine)

# Call init_db when the module is imported
init_db()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close() 