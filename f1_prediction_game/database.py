from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use SQLite for local development and PostgreSQL for Streamlit Cloud
if os.environ.get('STREAMLIT_SERVER_RUNNING'):
    # Streamlit Cloud environment
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///./f1_predictions.db')
else:
    # Local development
    DATABASE_URL = "sqlite:///./f1_predictions.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 