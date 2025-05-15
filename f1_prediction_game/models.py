from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    total_points = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    predictions = relationship("Prediction", back_populates="user")

class Race(Base):
    __tablename__ = "races"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    date = Column(DateTime)
    practice1_start = Column(DateTime)
    is_sprint = Column(Boolean, default=False)
    predictions = relationship("Prediction", back_populates="race")
    results = relationship("RaceResult", back_populates="race")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    race_id = Column(Integer, ForeignKey("races.id"))
    predictions = Column(JSON)
    points = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="predictions")
    race = relationship("Race", back_populates="predictions")

class RaceResult(Base):
    __tablename__ = "race_results"
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.id"))
    
    # Final positions
    p1_driver = Column(String)
    p2_driver = Column(String)
    p3_driver = Column(String)
    p10_driver = Column(String)
    p11_driver = Column(String)
    p19_driver = Column(String)
    p20_driver = Column(String)
    
    # Constructor final positions
    constructor_positions = Column(String)  # JSON string of constructor rankings
    
    # Special results
    biggest_loser = Column(String)
    sprint_biggest_loser = Column(String)
    sprint_biggest_gainer = Column(String)
    
    race = relationship("Race", back_populates="results") 