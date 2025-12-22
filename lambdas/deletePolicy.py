import json
import boto3

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

def handler(event, context):
    try:
        path_params = event.get("pathParameters") or {}
        policy_number = path_params.get("policyNumber")

        if not policy_number:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "policyNumber is required"}),
                "headers": {"Access-Control-Allow-Origin": "*"}
            }

        table.delete_item(
            Key={
                "PK": f"POLICY#{policy_number}",
                "SK": "METADATA"
            },
            ConditionExpression="attribute_exists(PK)"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Policy deleted successfully"}),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }
