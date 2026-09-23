import asyncio
import json
import logging

from app.cache import cache_set, driver_latest_key
from app.config import settings
from app.sqs_client import _get_client
from app.websocket_manager import manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 60


async def process_message(body: dict) -> None:
    """Handle one SQS message: update cache, broadcast via WebSocket."""
    event = body.get("event")
    if event != "location_update":
        logger.warning("Unknown event type: %s", event)
        return

    data = body.get("data", {})
    driver_id = data.get("driver_id")
    if not driver_id:
        logger.warning("No driver_id in message")
        return

    # Update Redis
    cache_set(driver_latest_key(driver_id), data, ttl_seconds=CACHE_TTL_SECONDS)

    # Broadcast over WebSocket
    await manager.broadcast(
        driver_id,
        {"event": "location_update", "data": data},
    )

    logger.info("Processed location update for driver %s", driver_id)


async def consume_loop():
    """Long-running loop that polls SQS and processes messages."""
    if not settings.SQS_QUEUE_URL:
        logger.error("SQS_QUEUE_URL is not set — worker cannot start")
        return

    client = _get_client()
    logger.info("Worker started. Polling %s", settings.SQS_QUEUE_URL)

    while True:
        try:
            response = client.receive_message(
                QueueUrl=settings.SQS_QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=5,   # long polling
            )
            messages = response.get("Messages", [])
            for msg in messages:
                try:
                    body = json.loads(msg["Body"])
                    await process_message(body)
                except Exception:
                    logger.exception("Failed to process message")
                finally:
                    client.delete_message(
                        QueueUrl=settings.SQS_QUEUE_URL,
                        ReceiptHandle=msg["ReceiptHandle"],
                    )
        except Exception:
            logger.exception("Error polling SQS")
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(consume_loop())