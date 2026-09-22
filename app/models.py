import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    locations = relationship("LocationUpdate", back_populates="driver", cascade="all, delete-orphan")


class LocationUpdate(Base):
    __tablename__ = "location_updates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False)
    coordinates = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    driver = relationship("Driver", back_populates="locations")

    __table_args__ = (
        Index("idx_location_driver_recorded", "driver_id", recorded_at.desc()),
        Index("idx_location_coordinates", "coordinates", postgresql_using="gist"),
    )