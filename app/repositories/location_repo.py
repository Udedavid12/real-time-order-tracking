from datetime import datetime
from uuid import UUID

from geoalchemy2.elements import WKTElement
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import LocationUpdate


class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        driver_id: UUID,
        latitude: float,
        longitude: float,
        recorded_at: datetime,
    ) -> LocationUpdate:
        point_wkt = f"POINT({longitude} {latitude})"
        location = LocationUpdate(
            driver_id=driver_id,
            coordinates=WKTElement(point_wkt, srid=4326),
            recorded_at=recorded_at,
        )
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location

    def get_latest_for_driver(self, driver_id: UUID) -> LocationUpdate | None:
        return (
            self.db.query(LocationUpdate)
            .filter(LocationUpdate.driver_id == driver_id)
            .order_by(LocationUpdate.recorded_at.desc())
            .first()
        )

    def get_history(
        self, driver_id: UUID, limit: int = 100
    ) -> list[LocationUpdate]:
        return (
            self.db.query(LocationUpdate)
            .filter(LocationUpdate.driver_id == driver_id)
            .order_by(LocationUpdate.recorded_at.desc())
            .limit(limit)
            .all()
        )

    def find_nearby(
        self, latitude: float, longitude: float, radius_km: float
    ) -> list[LocationUpdate]:
        """Return the most recent location for each driver within radius_km."""
        point_wkt = f"POINT({longitude} {latitude})"
        radius_m = radius_km * 1000

        # Subquery: latest recorded_at per driver
        latest_subq = (
            self.db.query(
                LocationUpdate.driver_id,
                func.max(LocationUpdate.recorded_at).label("max_recorded"),
            )
            .group_by(LocationUpdate.driver_id)
            .subquery()
        )

        return (
            self.db.query(LocationUpdate)
            .join(
                latest_subq,
                (LocationUpdate.driver_id == latest_subq.c.driver_id)
                & (LocationUpdate.recorded_at == latest_subq.c.max_recorded),
            )
            .filter(
                func.ST_DWithin(
                    LocationUpdate.coordinates,
                    WKTElement(point_wkt, srid=4326),
                    radius_m,
                )
            )
            .all()
        )