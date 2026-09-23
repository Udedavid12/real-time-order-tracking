import asyncio
from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    """
    Tracks active WebSocket connections grouped by driver_id.
    A single driver may have many subscribers (multiple app clients watching).
    """

    def __init__(self):
        # driver_id (str) -> list of WebSocket connections
        self._connections: dict[str, list[WebSocket]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def connect(self, driver_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[str(driver_id)].append(websocket)

    async def disconnect(self, driver_id: UUID, websocket: WebSocket) -> None:
        async with self._lock:
            key = str(driver_id)
            if key in self._connections:
                try:
                    self._connections[key].remove(websocket)
                except ValueError:
                    pass
                if not self._connections[key]:
                    del self._connections[key]

    async def broadcast(self, driver_id: UUID, message: dict) -> None:
        """Send a message to every subscriber of a given driver."""
        async with self._lock:
            subscribers = list(self._connections.get(str(driver_id), []))

        # Send outside the lock — slow clients shouldn't block others
        dead: list[WebSocket] = []
        for ws in subscribers:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)

        # Clean up connections that errored
        if dead:
            async with self._lock:
                key = str(driver_id)
                for ws in dead:
                    if key in self._connections and ws in self._connections[key]:
                        self._connections[key].remove(ws)
                    if key in self._connections and not self._connections[key]:
                        del self._connections[key]

    def subscriber_count(self, driver_id: UUID) -> int:
        return len(self._connections.get(str(driver_id), []))


# Singleton — shared across the whole app
manager = ConnectionManager()