import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from ingest import handler

def test_valid_event():
    # basic happy path - proper event should come back 201
    event = {
        "body": json.dumps({
            "source": "test-service",
            "event_type": "auth.failure",
            "severity": "high",
            "message": "failed login attempt"
        })
    }
    response = handler(event, None)
    assert response["statusCode"] == 201

def test_missing_body():
    # if there's no body at all it should reject it, not crash
    response = handler({}, None)
    assert response["statusCode"] == 400
    