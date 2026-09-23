from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Driver


class DriverRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, phone: str | None) -> Driver:
        driver = Driver(name=name, phone=phone)
        self.db.add(driver)
        self.db.commit()
        self.db.refresh(driver)
        return driver

    def get_by_id(self, driver_id: UUID) -> Driver | None:
        return self.db.query(Driver).filter(Driver.id == driver_id).first()

    def list_all(self) -> list[Driver]:
        return self.db.query(Driver).order_by(Driver.created_at.desc()).all()