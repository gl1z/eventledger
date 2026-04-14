# eventledger

Serverless security event ingestion API built on AWS. Accepts structured security events via HTTP, validates them, and stores them in DynamoDB with a timestamp and unique ID.

Built with AWS Lambda, API Gateway, and DynamoDB. Deployed as infrastructure as code using AWS CDK (Python).

## Architecture

POST /events → API Gateway → Lambda (ingest.py) → DynamoDB

CloudWatch dashboard tracks invocations, errors, and duration.

## Event schema

```json
{
  "source": "auth-service",
  "severity": "high",
  "message": "multiple failed login attempts detected"
}
```

Accepted severity levels: `low`, `medium`, `high`, `critical`

## Deploy

```bash
pip install -r requirements.txt
cdk bootstrap
cdk deploy
```

## Stack

- **API Gateway** — REST API, single POST endpoint
- **Lambda** — Python 3.12, validates and writes events
- **DynamoDB** — on-demand, partition key `event_id`, sort key `timestamp`
- **CloudWatch** — dashboard with invocation count, error rate, duration
