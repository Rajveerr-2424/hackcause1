from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import random

def seed_db():
    db = SessionLocal()
    
    # Check if we already have data, if so, clear it for a fresh seed
    if db.query(models.Village).first():
        print("Clearing old local database records...")
        db.query(models.WaterData).delete()
        db.query(models.Tanker).delete()
        db.query(models.Village).delete()
        db.commit()

    villages_data = [
        {"name": "Jaisalmer", "district": "Rajasthan", "population": 65000, "latitude": 26.9157, "longitude": 70.9083},
        {"name": "Bikaner", "district": "Rajasthan", "population": 82000, "latitude": 28.0229, "longitude": 73.3119},
        {"name": "Anantapur", "district": "Andhra Pradesh", "population": 45000, "latitude": 14.6819, "longitude": 77.6006},
        {"name": "Madurai", "district": "Tamil Nadu", "population": 98000, "latitude": 9.9252, "longitude": 78.1198},
        {"name": "Gaya", "district": "Bihar", "population": 55000, "latitude": 24.7964, "longitude": 84.9914},
        {"name": "Latur", "district": "Maharashtra", "population": 72000, "latitude": 18.4088, "longitude": 76.5604},
        {"name": "Bhopal", "district": "Madhya Pradesh", "population": 115000, "latitude": 23.2599, "longitude": 77.4126},
        {"name": "Kutch", "district": "Gujarat", "population": 34000, "latitude": 23.7337, "longitude": 69.8597}
    ]

    for v_data in villages_data:
        village = models.Village(**v_data)
        db.add(village)
        db.commit()
        db.refresh(village)
        
        # Add a water data reading for each
        # Let's make Jaisalmer, Latur, and Anantapur highly stressed
        if v_data["name"] in ["Jaisalmer", "Latur", "Anantapur"]:
            rain_dev = -80.0 # Heavy deficit
            gw_level = 55.0  # Deep
        else:
            rain_dev = random.uniform(-10.0, 10.0)
            gw_level = random.uniform(10.0, 20.0)
            
        rain_stress = max(0, -rain_dev * 0.05) 
        gw_stress = max(0, gw_level * 0.1)
        total_stress = min(10.0, round(rain_stress + gw_stress, 2))
        
        water_data = models.WaterData(
            village_id=village.id,
            rainfall_deviation_mm=rain_dev,
            groundwater_level_m=gw_level,
            stress_index=total_stress
        )
        db.add(water_data)
        db.commit()

    # Add some tankers
    tankers = [
        {"license_plate": "MH-12-AB-1234", "capacity_liters": 10000, "is_available": True, "current_latitude": 18.5204, "current_longitude": 73.8567},
        {"license_plate": "MH-12-XY-9876", "capacity_liters": 15000, "is_available": True, "current_latitude": 18.6000, "current_longitude": 73.7000},
        {"license_plate": "MH-14-GH-5555", "capacity_liters": 8000, "is_available": False, "current_latitude": 18.9102, "current_longitude": 73.3283},
    ]
    for t_data in tankers:
        tanker = models.Tanker(**t_data)
        db.add(tanker)
        db.commit()

    print("Database seeded with sample villages, water data, and tankers.")
    db.close()

if __name__ == "__main__":
    seed_db()
