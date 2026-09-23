from fastapi import FastAPI

from app.database import Base, engine
from app.routers import drivers, locations

app = FastAPI(
    title="Real-Time Order Tracking API",
    description="Backend service for tracking drivers in real time.",
    version="0.1.0",
)

app.include_router(drivers.router)
app.include_router(locations.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}