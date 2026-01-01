import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
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
                
        # Get full policy metadata
        policy_response = table.get_item(
            Key={
                "PK": f"POLICY#{policy_number}",
                "SK": "METADATA"
            }
        )

        if "Item" not in policy_response:
            return error(404, "Policy not found")

        policy_item = policy_response["Item"]

        # Get all claims using GSI
        response = table.query(
            IndexName="GSI2_PolicyClaims",
            KeyConditionExpression=Key("GSI2PK").eq(policy_number)
        )


        claims = []
        for item in response.get("Items", []):
            claims.append({
                "claimNumber": item.get("claimNumber"),
                "claimDate": item.get("claimDate"),
                "description": item.get("description"),
                "status": item.get("status"),
                "approvedAction": item.get("approvedAction"),
                "assessmentValue": item.get("assessmentValue"),
                "approvedValue": item.get("approvedValue"),
                "damageAreas": item.get("damageAreas", []),
                "createdAt": item.get("createdAt"),
                "updatedAt": item.get("updatedAt")
            })

        # Return full policy + claims
        return ok({
            "policy": policy_item,
            "claimsCount": len(claims),
            "claims": claims
        })

    except Exception as e:
        return error(500, 'Internal sever error')
# request
# {
#     "queryStringParameters": {
#     "policyNumber": "POL987654"
#   }
# }