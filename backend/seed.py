from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import random

def seed_db():
    db = SessionLocal()
    
    # Check if we already have data
    if db.query(models.Village).first():
        print("Database already seeded.")
        db.close()
        return

    villages_data = [
        {"name": "Rampur", "district": "Pune", "population": 4500, "latitude": 18.5204, "longitude": 73.8567},
        {"name": "Shivapur", "district": "Pune", "population": 2100, "latitude": 18.3323, "longitude": 73.8687},
        {"name": "Khalapur", "district": "Raigad", "population": 6200, "latitude": 18.8267, "longitude": 73.2844},
        {"name": "Karjat", "district": "Raigad", "population": 3800, "latitude": 18.9102, "longitude": 73.3283},
        {"name": "Lonavala (Rural)", "district": "Pune", "population": 1500, "latitude": 18.7516, "longitude": 73.4039},
    ]

    for v_data in villages_data:
        village = models.Village(**v_data)
        db.add(village)
        db.commit()
        db.refresh(village)
        
        # Add a water data reading for each
        # Let's make Rampur and Karjat highly stressed
        if v_data["name"] in ["Rampur", "Karjat"]:
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
