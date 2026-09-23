import asyncio
import json

import websockets


DRIVER_ID = "e406621a-809a-463d-9c41-ff46225e3cad"
WS_URL = f"ws://127.0.0.1:8000/ws/tracking/{DRIVER_ID}"


async def listen():
    async with websockets.connect(WS_URL) as ws:
        print(f"Connected to {WS_URL}")
        async for message in ws:
            print("Received:", json.dumps(json.loads(message), indent=2))


if __name__ == "__main__":
    asyncio.run(listen())