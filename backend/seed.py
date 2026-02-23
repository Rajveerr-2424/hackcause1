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
        {"name": "Jaipur", "district": "Rajasthan", "population": 3046000, "latitude": 26.9124, "longitude": 75.7873},
        {"name": "Anantapur", "district": "Andhra Pradesh", "population": 45000, "latitude": 14.6819, "longitude": 77.6006},
        {"name": "Guntur", "district": "Andhra Pradesh", "population": 743000, "latitude": 16.3067, "longitude": 80.4365},
        {"name": "Madurai", "district": "Tamil Nadu", "population": 98000, "latitude": 9.9252, "longitude": 78.1198},
        {"name": "Coimbatore", "district": "Tamil Nadu", "population": 1601000, "latitude": 11.0168, "longitude": 76.9558},
        {"name": "Gaya", "district": "Bihar", "population": 55000, "latitude": 24.7964, "longitude": 84.9914},
        {"name": "Patna", "district": "Bihar", "population": 2046000, "latitude": 25.5941, "longitude": 85.1376},
        {"name": "Latur", "district": "Maharashtra", "population": 72000, "latitude": 18.4088, "longitude": 76.5604},
        {"name": "Pune", "district": "Maharashtra", "population": 3124000, "latitude": 18.5204, "longitude": 73.8567},
        {"name": "Nagpur", "district": "Maharashtra", "population": 2405000, "latitude": 21.1458, "longitude": 79.0882},
        {"name": "Solapur", "district": "Maharashtra", "population": 951000, "latitude": 17.6599, "longitude": 75.9064},
        {"name": "Bhopal", "district": "Madhya Pradesh", "population": 115000, "latitude": 23.2599, "longitude": 77.4126},
        {"name": "Indore", "district": "Madhya Pradesh", "population": 1960000, "latitude": 22.7196, "longitude": 75.8577},
        {"name": "Kutch", "district": "Gujarat", "population": 34000, "latitude": 23.7337, "longitude": 69.8597},
        {"name": "Ahmedabad", "district": "Gujarat", "population": 5570000, "latitude": 23.0225, "longitude": 72.5714},
        {"name": "Surat", "district": "Gujarat", "population": 4466000, "latitude": 21.1702, "longitude": 72.8311},
        {"name": "Lucknow", "district": "Uttar Pradesh", "population": 2817000, "latitude": 26.8467, "longitude": 80.9462},
        {"name": "Kanpur", "district": "Uttar Pradesh", "population": 2765000, "latitude": 26.4499, "longitude": 80.3319},
        {"name": "Hubli", "district": "Karnataka", "population": 943000, "latitude": 15.3647, "longitude": 75.1240},
        {"name": "Raipur", "district": "Chhattisgarh", "population": 1122000, "latitude": 21.2514, "longitude": 81.6296},
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
