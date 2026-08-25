from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SustainabilityScore(Base):
    __tablename__ = "sustainability_scores"
    __table_args__ = (Index("ix_score_dept_ts", "department_id", "timestamp"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    energy_score: Mapped[float] = mapped_column(Float, nullable=False)
    solar_score: Mapped[float] = mapped_column(Float, nullable=False)
    water_score: Mapped[float] = mapped_column(Float, nullable=False)
    carbon_score: Mapped[float] = mapped_column(Float, nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    consistency_score: Mapped[float] = mapped_column(Float, nullable=False)
    energy_efficiency: Mapped[float] = mapped_column(Float, default=0)
    energy_reduction: Mapped[float] = mapped_column(Float, default=0)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    kwh_per_student: Mapped[float] = mapped_column(Float, default=0)
    kwh_per_sqm: Mapped[float] = mapped_column(Float, default=0)
