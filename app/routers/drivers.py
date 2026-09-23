from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.driver_repo import DriverRepository
from app.schemas.driver import DriverCreate, DriverResponse

router = APIRouter(prefix="/api/v1/drivers", tags=["drivers"])


@router.post("", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreate, db: Session = Depends(get_db)):
    repo = DriverRepository(db)
    return repo.create(name=payload.name, phone=payload.phone)


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(driver_id: str, db: Session = Depends(get_db)):
    repo = DriverRepository(db)
    driver = repo.get_by_id(driver_id)
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.get("", response_model=list[DriverResponse])
def list_drivers(db: Session = Depends(get_db)):
    repo = DriverRepository(db)
    return repo.list_all()