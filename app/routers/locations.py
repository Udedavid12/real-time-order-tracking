from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.location import LocationCreate, LocationResponse
from app.services.location_service import DriverNotFoundError, LocationService
from app.websocket_manager import manager

router = APIRouter(prefix="/api/v1/locations", tags=["locations"])


def _to_response(loc) -> LocationResponse:
    """Convert a LocationUpdate ORM object (with PostGIS coordinates) to API shape."""
    from geoalchemy2.shape import to_shape

    point = to_shape(loc.coordinates)
    return LocationResponse(
        id=loc.id,
        driver_id=loc.driver_id,
        latitude=point.y,
        longitude=point.x,
        recorded_at=loc.recorded_at,
        created_at=loc.created_at,
    )


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def record_location(payload: LocationCreate, db: Session = Depends(get_db)):
    service = LocationService(db)
    try:
        loc = service.record_location(
            driver_id=payload.driver_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            recorded_at=payload.recorded_at,
        )
    except DriverNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    response = _to_response(loc)

    await manager.broadcast(
        payload.driver_id,
        {
            "event": "location_update",
            "data": response.model_dump(mode="json"),
        },
    )

    return response


@router.get("/nearby", response_model=list[LocationResponse])
def find_nearby(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(5.0, gt=0, le=100),
    db: Session = Depends(get_db),
):
    service = LocationService(db)
    results = service.find_nearby(latitude, longitude, radius_km)
    return [_to_response(loc) for loc in results]


@router.get("/{driver_id}/latest", response_model=LocationResponse)
def get_latest(driver_id: UUID, db: Session = Depends(get_db)):
    service = LocationService(db)
    data = service.get_latest_cached(driver_id)
    if data is None:
        raise HTTPException(status_code=404, detail="No location found for driver")
    return LocationResponse(**data)


@router.get("/{driver_id}/history", response_model=list[LocationResponse])
def get_history(
    driver_id: UUID,
    limit: int = Query(100, gt=0, le=1000),
    db: Session = Depends(get_db),
):
    service = LocationService(db)
    results = service.get_history(driver_id, limit=limit)
    return [_to_response(loc) for loc in results]