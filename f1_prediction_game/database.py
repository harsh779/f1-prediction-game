from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use PostgreSQL for Streamlit Cloud and SQLite for local development
if os.getenv("STREAMLIT_SERVER_RUNNING"):
    DATABASE_URL = "postgresql://postgres:[YOUR-PASSWORD]@db.nujseuauucrsrhemoota.supabase.co:5432/postgres"
else:
    DATABASE_URL = "sqlite:///f1_predictions.db"

# Create engine with proper PostgreSQL configuration
engine = create_engine(
    DATABASE_URL
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

# Initialize database
def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close() 