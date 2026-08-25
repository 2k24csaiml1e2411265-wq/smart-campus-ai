from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: str
    department_code: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=4)


class UserOut(BaseModel):
    id: int
    email: str
    role: str
    department_id: int | None
    full_name: str

    class Config:
        from_attributes = True


class DepartmentOut(BaseModel):
    id: int
    name: str
    code: str
    building: str
    floor_area: float
    student_count: int
    staff_count: int
    active: bool

    class Config:
        from_attributes = True


class DepartmentUpdate(BaseModel):
    building: str | None = None
    floor_area: float | None = None
    student_count: int | None = None
    staff_count: int | None = None
    active: bool | None = None


class DeviceOut(BaseModel):
    id: int
    device_id: str
    department_id: int
    department_code: str | None = None
    device_type: str
    location: str
    status: str
    last_seen: datetime | None
    last_value: float | None
    health: str | None = None

    class Config:
        from_attributes = True


class EnergyReadingIn(BaseModel):
    device_id: str
    department: str
    timestamp: datetime | None = None
    energy_kwh: float
    voltage: float
    current: float
    power_factor: float
    temperature: float
    occupancy: int
    is_simulated: bool = True
    is_anomaly_injected: bool = False


class SolarReadingIn(BaseModel):
    device_id: str
    department: str
    timestamp: datetime | None = None
    solar_kwh: float
    voltage: float
    current: float
    irradiance: float
    is_simulated: bool = True


class WaterReadingIn(BaseModel):
    device_id: str
    department: str
    timestamp: datetime | None = None
    water_litres: float
    flow_rate: float
    pressure: float
    is_simulated: bool = True
    is_anomaly_injected: bool = False


class EnvironmentReadingIn(BaseModel):
    device_id: str
    department: str
    timestamp: datetime | None = None
    temperature: float
    humidity: float
    occupancy: int
    is_simulated: bool = True


class DeviceHeartbeatIn(BaseModel):
    device_id: str
    department: str
    status: str = "online"
    last_value: float | None = None


class AnomalyOut(BaseModel):
    id: int
    department_id: int
    department_code: str | None = None
    timestamp: datetime
    metric: str
    actual_value: float
    expected_value: float
    anomaly_score: float
    severity: str
    reason: str
    recommendation: str
    status: str
    deviation_pct: float | None = None

    class Config:
        from_attributes = True


class AnomalyStatusUpdate(BaseModel):
    status: str


class ForecastOut(BaseModel):
    department_code: str
    timestamp: datetime
    forecast_for: datetime
    predicted_kwh: float
    lower_bound: float
    upper_bound: float
    model_name: str
    horizon_hours: int
    confidence: float


class HealthOut(BaseModel):
    api: str
    database: str
    mqtt: str
    ml: str
    simulator: str
    last_data_timestamp: datetime | None
    campus: str
    data_mode: str
    details: dict[str, Any] = {}
