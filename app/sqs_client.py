import json
from typing import Any

import boto3

from app.config import settings


def _get_client():
    """Create an SQS client. Uses endpoint_url for LocalStack."""
    kwargs = {
        "region_name": settings.AWS_REGION,
        "aws_access_key_id": settings.AWS_ACCESS_KEY_ID or None,
        "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY or None,
    }
    if settings.SQS_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.SQS_ENDPOINT_URL
    return boto3.client("sqs", **kwargs)


def enqueue_location_update(payload: dict[str, Any]) -> None:
    """Publish a location update message to SQS."""
    if not settings.SQS_QUEUE_URL:
        # No queue configured — silently skip
        return
    try:
        client = _get_client()
        client.send_message(
            QueueUrl=settings.SQS_QUEUE_URL,
            MessageBody=json.dumps(payload, default=str),
        )
    except Exception:
        # Queue is best-effort for now — don't fail the HTTP request
        pass