import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
from decimal import Decimal

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))

        policy_number = body.get("policyNumber")
        claim_number = body.get("claimNumber")

        if not policy_number or not claim_number:
            return error(400, "policyNumber and claimNumber are required")

        # Read claim to get assessmentValue
        claim_resp = table.get_item(
            Key={
                "PK": f"POLICY#{policy_number}",
                "SK": f"CLAIM#{claim_number}"
            }
        )

        if "Item" not in claim_resp:
            return error(404, "Claim not found")

        claim = claim_resp["Item"]
        assessment_value = claim.get("assessmentValue", 0)

        # Update claim manually
        table.update_item(
            Key={
                "PK": f"POLICY#{policy_number}",
                "SK": f"CLAIM#{claim_number}"
            },
            UpdateExpression="""
                SET #s = :status,
                    approvedValue = :approvedValue,
                    approvedAction = :approvedAction,
                    updatedAt = :updatedAt
            """,
            ExpressionAttributeNames={
                "#s": "status"
            },
            ExpressionAttributeValues={
                ":status": "approved",
                ":approvedValue": assessment_value,
                ":approvedAction": "manually",
                ":updatedAt": datetime.utcnow().isoformat()
            },
            ConditionExpression="attribute_exists(PK)"
        )

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "message": "Claim approved manually",
                "policyNumber": policy_number,
                "claimNumber": claim_number,
                "approvedValue": assessment_value,
                "approvedAction": "manually"
            }, default=decimal_default, ensure_ascii=False)
        }

    except ClientError as e:
        return error(500, str(e))
    except Exception as e:
        return error(500, str(e))


def error(status, message):
    return {
        "statusCode": status,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"error": message})
    }
