from sqlalchemy.orm import Session
import models, schemas
import pandas as pd

def calculate_stress_index(rainfall_deviation: float, groundwater_level: float) -> float:
    # Basic Heuristic calculation for stress
    # Higher index (max 10) = Higher stress (more dangerous drought)
    
    # Rainfall deviation: negative means less rain. More negative -> higher stress.
    rain_stress = max(0, -rainfall_deviation * 0.05) 
    
    # Groundwater level: deeper water (larger number) -> higher stress
    groundwater_stress = max(0, groundwater_level * 0.1)
    
    total_stress = rain_stress + groundwater_stress
    return min(10.0, round(total_stress, 2))

def create_village(db: Session, village: schemas.VillageCreate):
    db_village = models.Village(**village.model_dump())
    db.add(db_village)
    db.commit()
    db.refresh(db_village)
    return db_village

def get_villages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Village).offset(skip).limit(limit).all()

def add_water_data(db: Session, data: schemas.WaterDataCreate):
    stress = calculate_stress_index(data.rainfall_deviation_mm, data.groundwater_level_m)
    db_data = models.WaterData(
        village_id=data.village_id,
        rainfall_deviation_mm=data.rainfall_deviation_mm,
        groundwater_level_m=data.groundwater_level_m,
        stress_index=stress
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def get_stressed_villages(db: Session, threshold: float = 7.0):
    # Returns the latest water data where stress > threshold, joined with village data
    
    return db.query(models.Village, models.WaterData).join(models.WaterData).filter(
        models.WaterData.stress_index >= threshold
    ).order_by(models.WaterData.stress_index.desc()).all()
