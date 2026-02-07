from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ===== USER SCHEMAS =====
class UserBase(BaseModel):
    strava_id: int
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    strava_access_token: Optional[str] = None
    strava_refresh_token: Optional[str] = None
    strava_token_expires_at: Optional[datetime] = None
    strava_scope: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_picture: Optional[str] = None
    strava_access_token: Optional[str] = None
    strava_refresh_token: Optional[str] = None
    strava_token_expires_at: Optional[datetime] = None
    strava_scope: Optional[str] = None


class UserResponse(UserBase):
    id: int
    profile_picture: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime]

    class Config:
        from_attributes = True


# ===== ACTIVITY SCHEMAS =====
class ActivityBase(BaseModel):
    name: str
    activity_type: str
    distance: float
    duration: int
    elevation_gain: Optional[float] = None
    average_speed: Optional[float] = None
    max_speed: Optional[float] = None
    start_date: datetime


class ActivityCreate(ActivityBase):
    user_id: int
    strava_id: int
    description: Optional[str] = None
    average_heart_rate: Optional[float] = None
    max_heart_rate: Optional[float] = None
    average_cadence: Optional[float] = None
    start_date_local: datetime
    timezone: Optional[str] = None
    weather: Optional[str] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    gear_id: Optional[int] = None
    raw_data: Optional[dict] = None


class ActivityResponse(ActivityBase):
    id: int
    user_id: int
    strava_id: int
    description: Optional[str]
    elevation_gain: Optional[float]
    average_heart_rate: Optional[float]
    max_heart_rate: Optional[float]
    average_cadence: Optional[float]
    start_date_local: datetime
    timezone: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== GEAR SCHEMAS =====
class GearBase(BaseModel):
    name: str
    gear_type: str
    brand: Optional[str] = None
    model: Optional[str] = None


class GearCreate(GearBase):
    user_id: int
    strava_id: Optional[str] = None
    description: Optional[str] = None
    is_primary: bool = False
    retired: bool = False
    distance: float = 0
    initial_purchase_date: Optional[datetime] = None


class GearUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None
    is_primary: Optional[bool] = None
    retired: Optional[bool] = None
    distance: Optional[float] = None


class GearResponse(GearBase):
    id: int
    user_id: int
    strava_id: Optional[str]
    description: Optional[str]
    is_primary: bool
    retired: bool
    distance: float
    initial_purchase_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== SYNC LOG SCHEMAS =====
class SyncLogCreate(BaseModel):
    user_id: int
    sync_type: str
    status: str
    message: Optional[str] = None
    activities_synced: int = 0
    activities_skipped: int = 0
    activities_failed: int = 0
    error_details: Optional[dict] = None


class SyncLogResponse(SyncLogCreate):
    id: int
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True




