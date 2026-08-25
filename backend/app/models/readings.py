from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EnergyReading(Base):
    __tablename__ = "energy_readings"
    __table_args__ = (
        Index("ix_energy_dept_ts", "department_id", "timestamp"),
        Index("ix_energy_device_ts", "device_id", "timestamp"),
        Index("ix_energy_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True, nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    energy_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    voltage: Mapped[float] = mapped_column(Float, nullable=False)
    current: Mapped[float] = mapped_column(Float, nullable=False)
    power_factor: Mapped[float] = mapped_column(Float, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    occupancy: Mapped[int] = mapped_column(Integer, nullable=False)
    is_simulated: Mapped[bool] = mapped_column(default=True)
    is_anomaly_injected: Mapped[bool] = mapped_column(default=False)


class SolarReading(Base):
    __tablename__ = "solar_readings"
    __table_args__ = (
        Index("ix_solar_dept_ts", "department_id", "timestamp"),
        Index("ix_solar_device_id", "device_id"),
        Index("ix_solar_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True, nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    solar_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    voltage: Mapped[float] = mapped_column(Float, nullable=False)
    current: Mapped[float] = mapped_column(Float, nullable=False)
    irradiance: Mapped[float] = mapped_column(Float, nullable=False)
    is_simulated: Mapped[bool] = mapped_column(default=True)


class WaterReading(Base):
    __tablename__ = "water_readings"
    __table_args__ = (
        Index("ix_water_dept_ts", "department_id", "timestamp"),
        Index("ix_water_device_id", "device_id"),
        Index("ix_water_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True, nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    water_litres: Mapped[float] = mapped_column(Float, nullable=False)
    flow_rate: Mapped[float] = mapped_column(Float, nullable=False)
    pressure: Mapped[float] = mapped_column(Float, nullable=False)
    is_simulated: Mapped[bool] = mapped_column(default=True)
    is_anomaly_injected: Mapped[bool] = mapped_column(default=False)


class EnvironmentReading(Base):
    __tablename__ = "environment_readings"
    __table_args__ = (
        Index("ix_env_dept_ts", "department_id", "timestamp"),
        Index("ix_env_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True, nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    occupancy: Mapped[int] = mapped_column(Integer, nullable=False)
    is_simulated: Mapped[bool] = mapped_column(default=True)
