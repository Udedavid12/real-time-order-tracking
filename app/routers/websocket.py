from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket_manager import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/tracking/{driver_id}")
async def track_driver(websocket: WebSocket, driver_id: UUID):
    """
    Client connects here to receive real-time location updates for a driver.
    """
    await manager.connect(driver_id, websocket)

    try:
        # Send a quick confirmation
        await websocket.send_json(
            {
                "event": "connected",
                "driver_id": str(driver_id),
                "message": "Subscribed to driver location updates.",
            }
        )

        # Keep the connection open. Any message from the client is treated as a ping.
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        await manager.disconnect(driver_id, websocket)
    except Exception:
        await manager.disconnect(driver_id, websocket)