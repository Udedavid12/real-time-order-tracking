from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import LocationUpdate
from app.repositories.driver_repo import DriverRepository
from app.repositories.location_repo import LocationRepository


class DriverNotFoundError(Exception):
    pass


class LocationService:
    def __init__(self, db: Session):
        self.db = db
        self.location_repo = LocationRepository(db)
        self.driver_repo = DriverRepository(db)

    def record_location(
        self,
        driver_id: UUID,
        latitude: float,
        longitude: float,
        recorded_at: datetime,
    ) -> LocationUpdate:
        driver = self.driver_repo.get_by_id(driver_id)
        if driver is None:
            raise DriverNotFoundError(f"Driver {driver_id} not found")

        return self.location_repo.create(
            driver_id=driver_id,
            latitude=latitude,
            longitude=longitude,
            recorded_at=recorded_at,
        )

    def get_latest(self, driver_id: UUID) -> LocationUpdate | None:
        return self.location_repo.get_latest_for_driver(driver_id)

    def get_history(self, driver_id: UUID, limit: int = 100) -> list[LocationUpdate]:
        return self.location_repo.get_history(driver_id, limit=limit)

    def find_nearby(
        self, latitude: float, longitude: float, radius_km: float
    ) -> list[LocationUpdate]:
        return self.location_repo.find_nearby(latitude, longitude, radius_km)