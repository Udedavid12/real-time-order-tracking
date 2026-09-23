from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DriverCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    phone: str | None = Field(None, max_length=20)


class DriverResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    phone: str | None
    created_at: datetime