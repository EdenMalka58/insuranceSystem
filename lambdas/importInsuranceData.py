import json
import boto3
from datetime import datetime
from decimal import Decimal

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")


# -----------------------------
# Helpers
# -----------------------------

def to_decimal(obj):
    """Convert floats to Decimal (required by DynamoDB)"""
    if isinstance(obj, list):
        return [to_decimal(i) for i in obj]
    if isinstance(obj, dict):
        return {k: to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, float):
        return Decimal(str(obj))
    return obj


# -----------------------------
# Handler
# -----------------------------

def handler(event, context):
    try:
        # SUPPORT BOTH:
        # - API Gateway: { "body": "json-string" }
        # - CLI invoke: [ {...}, {...} ]

        if isinstance(event, list):
            body = event
        elif isinstance(event, dict) and "body" in event:
            body = json.loads(event["body"])
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid input format"})
            }

        if not isinstance(body, list):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Payload must be a JSON array"})
            }

        policies_created = 0
        claims_created = 0

        for policy in event:
            policy_number = policy["policyNumber"]
            insured = policy["insured"]

            # =========================
            # POLICY ITEM
            # =========================
            policy_item = {
                "PK": f"POLICY#{policy_number}",
                "SK": "METADATA",
                "entityType": "POLICY",
                "policyNumber": policy_number,
                "insured": insured,
                "vehicle": policy["vehicle"],
                "validity": policy["validity"],
                "insuredValue": policy["insuredValue"],
                "deductibleValue": policy["deductibleValue"],
                "createdAt": policy.get(
                    "createdAt", datetime.utcnow().isoformat()
                ),

                # GSI1 – User Policies
                "GSI1PK": insured["idNumber"],
                "GSI1SK": f"POLICY#{policy_number}"
            }

            table.put_item(Item=to_decimal(policy_item))
            policies_created += 1

            # =========================
            # CLAIM ITEMS (optional)
            # =========================
            for claim in policy.get("claims", []):
                claim_number = claim["claimNumber"]

                claim_item = {
                    "PK": f"POLICY#{policy_number}",
                    "SK": f"CLAIM#{claim_number}",
                    "entityType": "POLICY_CLAIM",
                    "claimNumber": claim_number,
                    "policyNumber": policy_number,
                    "claimDate": claim["claimDate"],
                    "description": claim.get("description", ""),
                    "status": claim["status"],
                    "approvedAction": claim["approvedAction"],
                    "assessmentValue": claim["assessmentValue"],
                    "approvedValue": claim["approvedValue"],
                    "damageAreas": claim.get("damageAreas", []),
                    "createdAt": claim.get(
                        "createdAt", datetime.utcnow().isoformat()
                    ),
                    "updatedAt": claim.get(
                        "updatedAt", datetime.utcnow().isoformat()
                    ),

                    # GSI2 – Policy Claims
                    "GSI2PK": policy_number,
                    "GSI2SK": f"CLAIM#{claim_number}"
                }

                table.put_item(Item=to_decimal(claim_item))
                claims_created += 1

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Import completed successfully",
                "policiesCreated": policies_created,
                "claimsCreated": claims_created
            }),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            }),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }