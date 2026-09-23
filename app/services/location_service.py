from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.cache import cache_delete, cache_get, cache_set, driver_latest_key
from app.models import LocationUpdate
from app.repositories.driver_repo import DriverRepository
from app.repositories.location_repo import LocationRepository


class DriverNotFoundError(Exception):
    pass


def _serialize_location(loc: LocationUpdate) -> dict:
    """Convert a LocationUpdate ORM row to a dict (with lat/lon, not PostGIS)."""
    from geoalchemy2.shape import to_shape

    point = to_shape(loc.coordinates)
    return {
        "id": str(loc.id),
        "driver_id": str(loc.driver_id),
        "latitude": point.y,
        "longitude": point.x,
        "recorded_at": loc.recorded_at.isoformat(),
        "created_at": loc.created_at.isoformat(),
    }


class LocationService:
    CACHE_TTL_SECONDS = 60

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

        location = self.location_repo.create(
            driver_id=driver_id,
            latitude=latitude,
            longitude=longitude,
            recorded_at=recorded_at,
        )

        # Cache update happens in the worker — see app/worker.py

        return location

    def get_latest_cached(self, driver_id: UUID) -> dict | None:
        """
        Read-through cache:
        1. Try Redis first
        2. On miss, query Postgres
        3. Store result in Redis for next time
        """
        key = driver_latest_key(str(driver_id))

        cached = cache_get(key)
        if cached is not None:
            return cached

        loc = self.location_repo.get_latest_for_driver(driver_id)
        if loc is None:
            return None

        serialized = _serialize_location(loc)
        cache_set(key, serialized, ttl_seconds=self.CACHE_TTL_SECONDS)
        return serialized

    def get_latest(self, driver_id: UUID) -> LocationUpdate | None:
        return self.location_repo.get_latest_for_driver(driver_id)

    def get_history(self, driver_id: UUID, limit: int = 100) -> list[LocationUpdate]:
        return self.location_repo.get_history(driver_id, limit=limit)

    def find_nearby(
        self, latitude: float, longitude: float, radius_km: float
    ) -> list[LocationUpdate]:
        return self.location_repo.find_nearby(latitude, longitude, radius_km)