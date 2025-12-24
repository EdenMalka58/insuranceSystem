import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
from decimal import Decimal
from auth import require_agent
from response import ok, error


dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

def handler(event, context):
    if not require_agent(event):
        return error(403, "Agent access required")

    try:
        body = json.loads(event.get("body", "{}"))

        policy_number = body.get("policyNumber")
        claim_number = body.get("claimNumber")
        isApproved = body.get("isApproved")

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
        if isApproved is True:
            status = "approved"
            assessment_value = claim.get("assessmentValue", 0)
        else:
            status = "rejected"
            assessment_value = 0
        

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
                ":status": status,
                ":approvedValue": assessment_value,
                ":approvedAction": "manually",
                ":updatedAt": datetime.utcnow().isoformat()
            },
            ConditionExpression="attribute_exists(PK)"
        )

        return ok({
            "message": "Claim approved manually",
            "policyNumber": policy_number,
            "claimNumber": claim_number,
            "approvedValue": assessment_value,
            "approvedAction": "manually"
        })

    except ClientError as e:
        return error(500, "Internal sever error")
    except Exception as e:
        return error(500, "Internal sever error")
