import json
import os
import sys
from unittest.mock import Mock

# let the test import ingest.py from the lambda folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lambda"))

import ingest

def test_valid_event(monkeypatch):
    # fake DynamoDB table so the test does not hit real AWS
    mock_table = Mock()

    # set the env var and replace get_table() with our fake table
    monkeypatch.setenv("TABLE_NAME", "test-table")
    monkeypatch.setattr(ingest, "get_table", lambda: mock_table)

    # basic happy path - valid event should return 201
    event = {
        "body": json.dumps({
            "source": "auth-service",
            "severity": "high",
            "message": "failed login attempt"
        })
    }

    response = ingest.handler(event, None)

    assert response["statusCode"] == 201
    mock_table.put_item.assert_called_once()


def test_missing_body(monkeypatch):
    # body is missing entirely, so it should reject with 400
    monkeypatch.setenv("TABLE_NAME", "test-table")

    response = ingest.handler({}, None)

    assert response["statusCode"] == 400


def test_invalid_severity(monkeypatch):
    # invalid severity should be rejected with 400
    monkeypatch.setenv("TABLE_NAME", "test-table")

    event = {
        "body": json.dumps({
            "source": "auth-service",
            "severity": "urgent",
            "message": "failed login attempt"
        })
    }

    response = ingest.handler(event, None)

    assert response["statusCode"] == 400
