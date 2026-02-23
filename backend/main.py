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

