import aws_cdk as core
import aws_cdk.assertions as assertions
from eventledger.eventledger_stack import EventledgerStack

def test_stack_has_lambda():
    app = core.App()
    stack = EventledgerStack(app, "eventledger")
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "ingest.handler",
        "Runtime": "python3.12",
    })

def test_stack_has_dynamodb_table():
    app = core.App()
    stack = EventledgerStack(app, "eventledger")
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "BillingMode": "PAY_PER_REQUEST",
    })

def test_stack_has_dashboard():
    app = core.App()
    stack = EventledgerStack(app, "eventledger")
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties("AWS::CloudWatch::Dashboard", {
        "DashboardName": "eventledger",
    })
    