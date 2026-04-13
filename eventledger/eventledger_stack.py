from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigw,
    aws_cloudwatch as cloudwatch,
    RemovalPolicy,
    Duration,
)
from constructs import Construct


class EventledgerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # storing events in dynamo - partition by event_id, sort by timestamp
        # so i can query all events for a given id in time order later
        table = dynamodb.Table(
            self, "EventsTable",
            partition_key=dynamodb.Attribute(
                name="event_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # fine for dev, would change this in prod
        )

        # lambda that actually handles the incoming events
        # code lives in the /lambda folder, handler is ingest.py -> handler()
        handler = lambda_.Function(
            self, "IngestHandler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("lambda"),
            handler="ingest.handler",
            environment={
                "TABLE_NAME": table.table_name,  # passing table name in as env var
            },
            timeout=Duration.seconds(10),
        )

        # without this the lambda can't touch the table at all
        table.grant_read_write_data(handler)

        # api gateway sitting in front of the lambda
        # only exposing one endpoint for now - POST /events
        api = apigw.RestApi(
            self, "EventledgerApi",
            rest_api_name="eventledger",
            description="Security event ingestion API",
        )

        events = api.root.add_resource("events")
        events.add_method("POST", apigw.LambdaIntegration(handler))

        # dashboard to see what the lambda is actually doing
        # invocations, errors, duration - the basics
        dashboard = cloudwatch.Dashboard(
            self, "EventledgerDashboard",
            dashboard_name="eventledger",
        )

        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Lambda Invocations",
                left=[handler.metric_invocations()],
            ),
            cloudwatch.GraphWidget(
                title="Lambda Errors",
                left=[handler.metric_errors()],
            ),
            cloudwatch.GraphWidget(
                title="Lambda Duration P95",
                left=[handler.metric_duration()],
            ),
        )
        