from pydantic import BaseModel
from typing import List, Optional
import datetime

# --- Village Schemas ---
class VillageBase(BaseModel):
    name: str
    district: str
    population: int
    latitude: float
    longitude: float

class VillageCreate(VillageBase):
    pass

class VillageResponse(VillageBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Water Data Schemas ---
class WaterDataBase(BaseModel):
    rainfall_deviation_mm: float
    groundwater_level_m: float

class WaterDataCreate(WaterDataBase):
    village_id: int

class WaterDataResponse(WaterDataBase):
    id: int
    village_id: int
    record_date: datetime.datetime
    stress_index: float

    class Config:
        from_attributes = True

# --- Tanker Schemas ---
class TankerBase(BaseModel):
    license_plate: str
    capacity_liters: int

class TankerCreate(TankerBase):
    pass

class TankerResponse(TankerBase):
    id: int
    is_available: bool
    current_latitude: Optional[float]
    current_longitude: Optional[float]

    class Config:
        from_attributes = True
