from sqlalchemy.orm import Session
from backend import models, schemas
import pandas as pd
import math

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance in km between two GPS coordinates."""
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

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

def dispatch_tanker(db: Session, village_id: int, radius_km: float = 500.0):
    """Find the nearest available tanker within radius_km using the Haversine formula."""
    # Get the requesting village's GPS coordinates
    village = db.query(models.Village).filter(models.Village.id == village_id).first()
    if not village:
        return {"success": False, "message": "Village not found!"}

    # Fetch all available tankers and calculate distances
    available_tankers = db.query(models.Tanker).filter(models.Tanker.is_available == True).all()
    
    nearest_tanker = None
    nearest_distance = float('inf')

    for tanker in available_tankers:
        if tanker.current_latitude is None or tanker.current_longitude is None:
            continue
        dist = haversine_km(
            village.latitude, village.longitude,
            tanker.current_latitude, tanker.current_longitude
        )
        if dist < nearest_distance and dist <= radius_km:
            nearest_distance = dist
            nearest_tanker = tanker

    if nearest_tanker:
        nearest_tanker.is_available = False
        db.commit()
        db.refresh(nearest_tanker)
        return {
            "success": True,
            "tanker_license": nearest_tanker.license_plate,
            "distance_km": round(nearest_distance, 1),
            "message": f"Nearest tanker {nearest_tanker.license_plate} dispatched from {nearest_distance:.0f} km away!"
        }
    return {"success": False, "message": f"No tankers available within {radius_km:.0f} km of {village.name}! Consider requesting inter-district support."}
