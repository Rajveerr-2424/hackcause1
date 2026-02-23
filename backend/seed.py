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
        # Original Pilot Villages
        {"name": "Pune", "district": "Maharashtra", "population": 3124000, "latitude": 18.5204, "longitude": 73.8567},
        {"name": "Karjat", "district": "Raigad", "population": 3800, "latitude": 18.9102, "longitude": 73.3283},
        {"name": "Khalapur", "district": "Raigad", "population": 6200, "latitude": 18.8267, "longitude": 73.2844},
        {"name": "Lonavala (Rural)", "district": "Pune", "population": 1500, "latitude": 18.7516, "longitude": 73.4039},
        {"name": "Rampur", "district": "Pune", "population": 4500, "latitude": 18.5204, "longitude": 73.8567},
        {"name": "Shivapur", "district": "Pune", "population": 2100, "latitude": 18.3323, "longitude": 73.8687},
        
        # North India
        {"name": "Delhi", "district": "Delhi", "population": 16787000, "latitude": 28.7041, "longitude": 77.1025},
        {"name": "Chandigarh", "district": "Chandigarh", "population": 1055000, "latitude": 30.7333, "longitude": 76.7794},
        {"name": "Srinagar", "district": "Jammu & Kashmir", "population": 1183000, "latitude": 34.0837, "longitude": 74.7973},
        {"name": "Amritsar", "district": "Punjab", "population": 1132000, "latitude": 31.6340, "longitude": 74.8723},
        {"name": "Shimla", "district": "Himachal Pradesh", "population": 169000, "latitude": 31.1048, "longitude": 77.1734},
        {"name": "Dehradun", "district": "Uttarakhand", "population": 578000, "latitude": 30.3165, "longitude": 78.0322},

        # West & Central
        {"name": "Mumbai", "district": "Maharashtra", "population": 12442000, "latitude": 19.0760, "longitude": 72.8777},
        {"name": "Surat", "district": "Gujarat", "population": 4466000, "latitude": 21.1702, "longitude": 72.8311},
        {"name": "Ahmedabad", "district": "Gujarat", "population": 5570000, "latitude": 23.0225, "longitude": 72.5714},
        {"name": "Rajkot", "district": "Gujarat", "population": 1390000, "latitude": 22.3039, "longitude": 70.8022},
        {"name": "Bhopal", "district": "Madhya Pradesh", "population": 1798000, "latitude": 23.2599, "longitude": 77.4126},
        {"name": "Indore", "district": "Madhya Pradesh", "population": 1960000, "latitude": 22.7196, "longitude": 75.8577},
        {"name": "Gwalior", "district": "Madhya Pradesh", "population": 1054000, "latitude": 26.2183, "longitude": 78.1828},
        {"name": "Jaipur", "district": "Rajasthan", "population": 3046000, "latitude": 26.9124, "longitude": 75.7873},
        {"name": "Jodhpur", "district": "Rajasthan", "population": 1033000, "latitude": 26.2389, "longitude": 73.0243},
        {"name": "Udaipur", "district": "Rajasthan", "population": 451000, "latitude": 24.5854, "longitude": 73.7125},

        # East & North-East
        {"name": "Kolkata", "district": "West Bengal", "population": 4496000, "latitude": 22.5726, "longitude": 88.3639},
        {"name": "Darjeeling", "district": "West Bengal", "population": 118000, "latitude": 27.0360, "longitude": 88.2627},
        {"name": "Patna", "district": "Bihar", "population": 2046000, "latitude": 25.5941, "longitude": 85.1376},
        {"name": "Gaya", "district": "Bihar", "population": 474000, "latitude": 24.7964, "longitude": 84.9914},
        {"name": "Bhubaneswar", "district": "Odisha", "population": 841000, "latitude": 20.2961, "longitude": 85.8245},
        {"name": "Guwahati", "district": "Assam", "population": 962000, "latitude": 26.1445, "longitude": 91.7362},
        {"name": "Shillong", "district": "Meghalaya", "population": 143000, "latitude": 25.5788, "longitude": 91.8933},

        # South
        {"name": "Bengaluru", "district": "Karnataka", "population": 8443000, "latitude": 12.9716, "longitude": 77.5946},
        {"name": "Mysuru", "district": "Karnataka", "population": 920000, "latitude": 12.2958, "longitude": 76.6394},
        {"name": "Chennai", "district": "Tamil Nadu", "population": 7088000, "latitude": 13.0827, "longitude": 80.2707},
        {"name": "Madurai", "district": "Tamil Nadu", "population": 1017000, "latitude": 9.9252, "longitude": 78.1198},
        {"name": "Coimbatore", "district": "Tamil Nadu", "population": 1601000, "latitude": 11.0168, "longitude": 76.9558},
        {"name": "Hyderabad", "district": "Telangana", "population": 6993000, "latitude": 17.3850, "longitude": 78.4867},
        {"name": "Visakhapatnam", "district": "Andhra Pradesh", "population": 2035000, "latitude": 17.6868, "longitude": 83.2185},
        {"name": "Kochi", "district": "Kerala", "population": 602000, "latitude": 9.9312, "longitude": 76.2673},
        {"name": "Thiruvananthapuram", "district": "Kerala", "population": 743000, "latitude": 8.5241, "longitude": 76.9366},
    ]

    for v_data in villages_data:
        village = models.Village(**v_data)
        db.add(village)
        db.commit()
        db.refresh(village)
        
        # Add a water data reading for each
        # Fetch REAL historical rainfall data from Open-Meteo (past 3 months)
        import requests
        from datetime import datetime, timedelta
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        try:
            url = f"https://archive-api.open-meteo.com/v1/archive?latitude={v_data['latitude']}&longitude={v_data['longitude']}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=auto"
            response = requests.get(url)
            weather_data = response.json()
            
            # Calculate total rainfall in last 90 days vs an assumed healthy average of ~150mm for this period
            total_rain = sum([rain for rain in weather_data['daily']['precipitation_sum'] if rain is not None])
            
            # If rain is incredibly low (e.g. < 20mm in 3 months), it's a severe deficit
            rain_dev = total_rain - 150.0 
            
            # Groundwater is harder to get free live APIs for, so we derive it inversely from the real rain deficit
            # If there is a massive rain deficit, the groundwater is likely depleting rapidly.
            gw_level = 15.0 + max(0, (-rain_dev * 0.2))

        except Exception as e:
            print(f"API Error fetching data for {v_data['name']}: {e}")
            rain_dev = 0.0
            gw_level = 15.0
            
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
    # Add a geographically spread tanker fleet across India
    tankers = [
        # Maharashtra (Near Pune/Mumbai)
        {"license_plate": "MH-12-AB-1234", "capacity_liters": 10000, "is_available": True, "current_latitude": 18.5204, "current_longitude": 73.8567},
        {"license_plate": "MH-12-XY-9876", "capacity_liters": 15000, "is_available": True, "current_latitude": 19.0760, "current_longitude": 72.8777},
        {"license_plate": "MH-14-GH-5555", "capacity_liters": 8000,  "is_available": True, "current_latitude": 18.9102, "current_longitude": 73.3283},
        # Madhya Pradesh (Near Bhopal/Indore)
        {"license_plate": "MP-09-AA-0001", "capacity_liters": 10000, "is_available": True, "current_latitude": 23.2599, "current_longitude": 77.4126},
        {"license_plate": "MP-09-BB-0002", "capacity_liters": 12000, "is_available": True, "current_latitude": 22.7196, "current_longitude": 75.8577},
        # Rajasthan (Near Jaipur)
        {"license_plate": "RJ-14-CC-1111", "capacity_liters": 10000, "is_available": True, "current_latitude": 26.9124, "current_longitude": 75.7873},
        {"license_plate": "RJ-14-DD-2222", "capacity_liters": 15000, "is_available": True, "current_latitude": 26.2389, "current_longitude": 73.0243},
        # Gujarat (Near Ahmedabad)
        {"license_plate": "GJ-01-EE-3333", "capacity_liters": 10000, "is_available": True, "current_latitude": 23.0225, "current_longitude": 72.5714},
        # Karnataka (Near Bengaluru)
        {"license_plate": "KA-01-FF-4444", "capacity_liters": 10000, "is_available": True, "current_latitude": 12.9716, "current_longitude": 77.5946},
        # Uttar Pradesh (Near Lucknow)
        {"license_plate": "UP-32-GG-5555", "capacity_liters": 12000, "is_available": True, "current_latitude": 26.8467, "current_longitude": 80.9462},
        # Delhi
        {"license_plate": "DL-01-HH-6666", "capacity_liters": 8000,  "is_available": True, "current_latitude": 28.7041, "current_longitude": 77.1025},
        # Tamil Nadu (Near Chennai)
        {"license_plate": "TN-01-II-7777", "capacity_liters": 10000, "is_available": True, "current_latitude": 13.0827, "current_longitude": 80.2707},
    ]
    for t_data in tankers:
        tanker = models.Tanker(**t_data)
        db.add(tanker)
        db.commit()

    print("Database seeded with sample villages, water data, and tankers.")
    db.close()

if __name__ == "__main__":
    seed_db()
