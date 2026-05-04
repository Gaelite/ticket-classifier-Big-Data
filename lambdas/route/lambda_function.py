"""
Lambda 3: Route
Guarda el ticket en el folder de S3 correspondiente según su severidad:
  - s3://bucket/urgent/
  - s3://bucket/normal/
  - s3://bucket/low/
"""

import json
import logging
import os
import boto3
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")

VALID_SEVERITIES = {"urgent", "normal", "low"}


def lambda_handler(event: dict, context) -> dict:
    """
    Recibe el evento clasificado y lo persiste en S3 bajo el folder
    correspondiente a su severidad.
    """
    logger.info(f"Route Lambda received event: {json.dumps(event)}")

    bucket_name = os.environ.get("BUCKET_NAME")
    if not bucket_name:
        raise EnvironmentError("BUCKET_NAME environment variable is not set")

    ticket_id = event.get("ticket_id", "unknown")
    severity = event.get("severity", "").lower()

    if severity not in VALID_SEVERITIES:
        raise ValueError(f"[{ticket_id}] Invalid severity value: '{severity}'")

    # Nombre del objeto en S3: severity/ticket_id_timestamp.json
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    s3_key = f"{severity}/{ticket_id}_{timestamp}.json"

    # Agregar metadatos de routing al evento
    enriched_event = {
        **event,
        "routed_to": f"s3://{bucket_name}/{s3_key}",
        "routed_at": timestamp,
        "status": "processed",
    }

    # Persistir en S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=json.dumps(enriched_event, indent=2),
        ContentType="application/json",
    )

    logger.info(f"[{ticket_id}] Ticket routed to s3://{bucket_name}/{s3_key}")

    return enriched_event