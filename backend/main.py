from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import models, schemas, crud
from database import engine, get_db

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Integrated Drought Warning & Smart Tanker Management System API",
    description="API for managing drought warnings and optimizing water tanker allocations.",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173", # Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Drought Warning API is running."}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/villages/", response_model=schemas.VillageResponse)
def create_village(village: schemas.VillageCreate, db: Session = Depends(get_db)):
    return crud.create_village(db=db, village=village)

@app.get("/villages/", response_model=list[schemas.VillageResponse])
def read_villages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    villages = crud.get_villages(db, skip=skip, limit=limit)
    return villages

@app.post("/water-data/", response_model=schemas.WaterDataResponse)
def create_water_data(data: schemas.WaterDataCreate, db: Session = Depends(get_db)):
    # Verify village exists
    db_village = db.query(models.Village).filter(models.Village.id == data.village_id).first()
    if not db_village:
        raise HTTPException(status_code=404, detail="Village not found")
    return crud.add_water_data(db=db, data=data)

@app.get("/crisis-dashboard/")
def get_crisis_dashboard(threshold: float = 6.0, db: Session = Depends(get_db)):
    """Returns a list of highly stressed villages prioritizing tanker allocation."""
    results = crud.get_stressed_villages(db, threshold=threshold)
    
    dashboard_data = []
    for village, w_data in results:
        # Triage Algorithm: Priority = Stress Index * Population scale factor
        triage_score = min(100.0, round(w_data.stress_index * (1 + (village.population / 100000)), 2))
        
        dashboard_data.append({
            "village_id": village.id,
            "village_name": village.name,
            "district": village.district,
            "population": village.population,
            "location": {"lat": village.latitude, "lng": village.longitude},
            "stress_index": w_data.stress_index,
            "predicted_stress_index": w_data.predicted_stress_index,
            "priority_score": triage_score,
            "last_recorded": w_data.record_date
        })
        
    # Sort strictly by triage priority score rather than basic stress
    dashboard_data.sort(key=lambda x: x["priority_score"], reverse=True)
    return dashboard_data

@app.get("/tankers/available")
def get_available_tankers(db: Session = Depends(get_db)):
    """Returns the count of currently available water tankers."""
    count = db.query(models.Tanker).filter(models.Tanker.is_available == True).count()
    return {"available": count}

@app.get("/tankers/fleet")
def get_tanker_fleet(db: Session = Depends(get_db)):
    """Returns all tankers with their availability and state info (derived from license plate)."""
    state_map = {
        "MH": "Maharashtra", "MP": "Madhya Pradesh", "RJ": "Rajasthan",
        "GJ": "Gujarat", "KA": "Karnataka", "UP": "Uttar Pradesh",
        "DL": "Delhi", "TN": "Tamil Nadu", "AP": "Andhra Pradesh",
        "TS": "Telangana", "KL": "Kerala", "WB": "West Bengal",
        "RJ": "Rajasthan", "HR": "Haryana", "PB": "Punjab",
    }
    tankers = db.query(models.Tanker).all()
    fleet = []
    for t in tankers:
        prefix = t.license_plate.split("-")[0]
        state = state_map.get(prefix, prefix)
        fleet.append({
            "license_plate": t.license_plate,
            "state": state,
            "capacity_liters": t.capacity_liters,
            "is_available": t.is_available,
            "lat": t.current_latitude,
            "lng": t.current_longitude,
        })
    return fleet

@app.post("/dispatch-tanker/{village_id}")
def dispatch_tanker_to_village(village_id: int, db: Session = Depends(get_db)):
    """Simulates dispatching an available tanker to a critical village."""
    result = crud.dispatch_tanker(db, village_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/city-rainfall/{village_id}")
def get_city_rainfall(village_id: int, db: Session = Depends(get_db)):
    """Fetches real weekly rainfall data from Open-Meteo for a specific village."""
    import requests
    from datetime import date, timedelta

    village = db.query(models.Village).filter(models.Village.id == village_id).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    end_date = date.today()
    start_date = end_date - timedelta(days=83)  # 12 weeks

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": village.latitude,
        "longitude": village.longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": "precipitation_sum",
        "timezone": "Asia/Kolkata"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        daily_rain = data.get("daily", {}).get("precipitation_sum", [])
    except Exception:
        raise HTTPException(status_code=502, detail="Could not fetch rainfall data")

    # Aggregate into weekly buckets
    weeks = []
    for i in range(0, min(84, len(daily_rain)), 7):
        chunk = daily_rain[i:i+7]
        total = round(sum(v for v in chunk if v is not None), 1)
        weeks.append({"week": f"W{i//7 + 1}", "actual": total, "forecast": None})

    # 4-week forward forecast (linear decay from last known value)
    last_val = weeks[-1]["actual"] if weeks else 0
    for j in range(1, 5):
        weeks.append({"week": f"F{j}", "actual": None, "forecast": round(max(0, last_val * max(0.05, 1 - j * 0.25)), 1)})

    return {"village": village.name, "data": weeks}
