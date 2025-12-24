import json
import boto3
from auth import require_agent
from response import ok, error


dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

def handler(event, context):
    if not require_agent(event):
        return error(403, "Agent access required")

    try:
        path_params = event.get("pathParameters") or {}
        policy_number = path_params.get("policyNumber")

        if not policy_number:
            return error(400, "policyNumber is required")
                

        table.delete_item(
            Key={
                "PK": f"POLICY#{policy_number}",
                "SK": "METADATA"
            },
            ConditionExpression="attribute_exists(PK)"
        )

        return ok({"message": "Policy deleted successfully"})

    except Exception as e:
        return error(500, "Internal sever error")
