import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DeviceType(str, enum.Enum):
    energy_meter = "energy_meter"
    solar_meter = "solar_meter"
    water_meter = "water_meter"
    environmental_sensor = "environmental_sensor"


class DeviceStatus(str, enum.Enum):
    online = "online"
    offline = "offline"
    warning = "warning"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True, nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(Enum(DeviceType, name="device_type"), nullable=False)
    location: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[DeviceStatus] = mapped_column(
        Enum(DeviceStatus, name="device_status"), default=DeviceStatus.online
    )
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    department = relationship("Department", back_populates="devices")
