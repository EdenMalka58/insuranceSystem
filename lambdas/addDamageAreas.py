import json
import boto3
from datetime import datetime, timezone
from time import time
from decimal import Decimal
from response import ok, error

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

ALLOWED_AREAS = {
    "front","frontLeft","frontRight",
    "rear","rearRight","rearLeft",
    "rightSide","rightFrontSide","rightRearSide",
    "leftSide","leftFrontSide","leftRearSide"
}

ALLOWED_SEVERITIES = {"slight", "medium", "extensive"}

PRICE_TABLE = {
    "front":            {"slight": 700,  "medium": 2200, "extensive": 5200},
    "frontLeft":        {"slight": 600,  "medium": 2000, "extensive": 4800},
    "frontRight":       {"slight": 600,  "medium": 2000, "extensive": 4800},
    "rear":             {"slight": 800,  "medium": 2500, "extensive": 6000},
    "rearLeft":         {"slight": 700,  "medium": 2300, "extensive": 5600},
    "rearRight":        {"slight": 700,  "medium": 2300, "extensive": 5600},
    "rightSide":        {"slight": 900,  "medium": 2800, "extensive": 6500},
    "rightFrontSide":   {"slight": 850,  "medium": 2600, "extensive": 6200},
    "rightRearSide":    {"slight": 850,  "medium": 2600, "extensive": 6200},
    "leftSide":         {"slight": 900,  "medium": 2800, "extensive": 6500},
    "leftFrontSide":    {"slight": 850,  "medium": 2600, "extensive": 6200},
    "leftRearSide":     {"slight": 850,  "medium": 2600, "extensive": 6200}
}

MAX_APPROVED_VALUE = 15000

def handler(event, context):
    try:

        # 1. Check the token's existence and validity.
        # 2. Validate damageAreas with ALLOWED_AREAS and ALLOWED_SEVERITIES
        # 3. For each damageArea calculate the estimatedCost field using PRICE_TABLE
        # 4. Update the damageAreas in claim record by claimNumber and policyNumber from the token record
        # 5. Calculate the claim total cost and update the assessmentValue field (from all damageAreas)
        # 6. Calculate the claim status by if smaller then deductibleValue (in policy) or smaller then MAX_APPROVED_VALUE "APPROVED" else "REJECTED"
        # 7. If the status is "APPROVED" update the approvedValue field from assessmentValue
        # 8. Update the claim record
        # 9. Update the token as used

        # Get token
        path_params = event.get("pathParameters") or {}
        token = path_params.get("tokenId")
        if not token:
            return error(400, "token is required")

        # Read token
        token_resp = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": f"TOKEN#{token}"}
        )
        if not token_resp.get("Items"):
            return error(404, "Invalid token")

        token_item = token_resp["Items"][0]

        # Validate token
        # Check expiration
        expires_at = int(token_item["expiresAt"])
        now = int(time())

        if expires_at < now:
            return error(403, "Token expired")

        if token_item.get("used") is True:
            return error(403, "Token already used")

        policy_number = token_item["policyNumber"]
        claim_number = token_item["claimNumber"]

        # Parse body
        body = json.loads(event.get("body", "{}"))
        damage_areas = body.get("damageAreas")
        if not isinstance(damage_areas, list) or not damage_areas:
            return error(400, "damageAreas must be a non-empty list")

        enriched_areas = []
        total_cost = 0

        # Validate + calculate cost
        for item in damage_areas:
            area = item.get("area")
            severity = item.get("severity")

            if area not in ALLOWED_AREAS:
                return error(400, f"Invalid area: {area}")
            if severity not in ALLOWED_SEVERITIES:
                return error(400, f"Invalid severity: {severity}")

            cost = PRICE_TABLE[area][severity]
            total_cost += cost

            enriched_areas.append({
                "area": area,
                "severity": severity,
                "estimatedCost": cost
            })

        assessment_value = total_cost

        # Read policy (for deductible)
        policy_resp = table.get_item(
            Key={
                "PK": f"POLICY#{policy_number}",
                "SK": "METADATA"
            }
        )
        if "Item" not in policy_resp:
            return error(404, "Policy not found")

        deductible = int(policy_resp["Item"]["deductibleValue"])

        # Calculate claim status
        if assessment_value <= deductible or assessment_value <= MAX_APPROVED_VALUE:
            status = "approved"
            approved_value = assessment_value
            approved_action = "automatically"
        else:
            status = "rejected"
            approved_value = 0
            approved_action = "waiting"

        # Update claim
        table.update_item(
            Key={
                "PK": f"POLICY#{policy_number}",
                "SK": f"CLAIM#{claim_number}"
            },
            UpdateExpression="""
                SET damageAreas = :areas,
                    assessmentValue = :assessment,
                    approvedValue = :approved,
                    approvedAction = :approvedAction,
                    #s = :status,
                    updatedAt = :updated
            """,
            ExpressionAttributeNames={
                "#s": "status"
            },
            ExpressionAttributeValues={
                ":areas": enriched_areas,
                ":assessment": assessment_value,
                ":approved": approved_value,
                ":status": status,
                ":approvedAction": approved_action,
                ":updated": datetime.utcnow().isoformat()
            },
            ConditionExpression="attribute_exists(PK)"
        )

        # Mark token as used (atomic, one-time)
        table.update_item(
            Key={
                "PK": token_item["PK"],   # TOKEN#{token}
                "SK": token_item["SK"]    # CLAIM#{claimNumber}
            },
            UpdateExpression="SET used = :true",
            ConditionExpression="used = :false",
            ExpressionAttributeValues={
                ":true": True,
                ":false": False
            }
        )

        return ok({
            "claimNumber": claim_number,
            "assessmentValue": assessment_value,
            "approvedValue": approved_value,
            "status": status,
            "damageAreas": enriched_areas
        })

    except Exception as e:
        return error(500, str(e))


#{
#  "pathParameters": {
#    "tokenId": "1d8e5a80-00b7-4ef5-9585-b68deff9170f"
#  },
#  "body": "{\n    \"damageAreas\": [\n      { \"area\": \"front\", \"severity\": \"medium\" },\n      { \"area\": \"leftSide\", \"severity\": \"slight\" },\n      { \"area\": \"rear\", \"severity\": \"extensive\" }\n    ]\n  }"
#}
