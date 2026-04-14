import json
import os
import uuid
from datetime import datetime, timezone

import boto3

# get the DynamoDB table from the Lambda environment
def get_table():
    table_name = os.environ.get("TABLE_NAME")
    if not table_name:
        raise RuntimeError("TABLE_NAME environment variable is not set")
    return boto3.resource("dynamodb").Table(table_name)

def handler(event, context):
    # reject requests with no body at all
    body = event.get("body")
    if not body:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing request body"})
        }

    # reject invalid JSON instead of crashing
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON"})
        }

    # make sure the required fields are actually there
    required_fields = {"source", "severity", "message"}
    if not required_fields.issubset(payload):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required fields"})
        }

    # severity levels i'm accepting - anything else gets rejected
    valid_severities = {"low", "medium", "high", "critical"}
    if payload["severity"] not in valid_severities:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid severity"})
        }

    # build the event record with a unique id and UTC timestamp
    item = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": payload["source"],
        "severity": payload["severity"],
        "message": payload["message"],
    }

    # write the event into DynamoDB
    table = get_table()
    table.put_item(Item=item)

    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Event stored", "event_id": item["event_id"]})
    }
