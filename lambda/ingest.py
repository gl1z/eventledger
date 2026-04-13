import json
import os
import uuid
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

# severity levels i'm accepting - anything else gets rejected
VALID_SEVERITIES = {"low", "medium", "high", "critical"}


def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return _response(400, {"error": "invalid json"})

    # make sure the required fields are actually there
    source = body.get("source")
    severity = body.get("severity")
    message = body.get("message")

    if not source or not severity or not message:
        return _response(400, {"error": "source, severity and message are required"})

    if severity not in VALID_SEVERITIES:
        return _response(400, {"error": f"severity must be one of {VALID_SEVERITIES}"})

    event_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    # write the event to dynamo
    table.put_item(Item={
        "event_id": event_id,
        "timestamp": timestamp,
        "source": source,
        "severity": severity,
        "message": message,
    })

    return _response(201, {
        "event_id": event_id,
        "timestamp": timestamp,
        "status": "recorded",
    })


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
