from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Village(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    district = Column(String, index=True)
    population = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    
    water_data = relationship("WaterData", back_populates="village")

class WaterData(Base):
    __tablename__ = "water_data"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"))
    record_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Metrics
    rainfall_deviation_mm = Column(Float)  # Negative means deficit
    groundwater_level_m = Column(Float)    # Depth to water table
    
    # Computed
    stress_index = Column(Float) # 0.0 to 10.0 (Higher is worse)
    predicted_stress_index = Column(Float, nullable=True) # 30-day forecast based on trend
    
    village = relationship("Village", back_populates="water_data")

class Tanker(Base):
    __tablename__ = "tankers"

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, unique=True, index=True)
    capacity_liters = Column(Integer)
    is_available = Column(Boolean, default=True)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
