import json
import boto3
from datetime import datetime, timezone
from time import time
from decimal import Decimal


dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def handler(event, context):
    try:
        # 1. Check if the token exists
        # 2. Check if the token has expired
        # 3. Check if the token is not used
        # 4. Read the claim record and check if the status is open 
        # 5. Read the policy and return this data: {insured, vehicle}

        # Get token
        path_params = event.get("pathParameters") or {}
        token = path_params.get("tokenId")

        if not token:
            return error(400, "token is required")

        # Read token record
        token_resp = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={
                ":pk": f"TOKEN#{token}"
            }
        )

        if not token_resp.get("Items"):
            return error(404, "Invalid token")

        token_item = token_resp["Items"][0]

        # Check expiration
        expires_at = int(token_item["expiresAt"])
        now = int(time())

        if expires_at < now:
            return error(403, "Token expired")

        # Check used
        if token_item.get("used") is True:
            return error(403, "Token already used")

        policy_number = token_item.get("policyNumber")
        claim_number = token_item.get("claimNumber")

        if not policy_number or not claim_number:
            return error(400, "Invalid token data")

        # Read claim (CORRECT PK/SK)
        claim_resp = table.get_item(
            Key={
                "PK": f"POLICY#{policy_number}",
                "SK": f"CLAIM#{claim_number}"
            }
        )

        claim_item = claim_resp.get("Item")
        if not claim_item:
            return error(404, f"Claim #{claim_number} not found")

        if claim_item.get("status") != "opened":
            return error(403, "Claim is not open")

        # Read policy
        policy_resp = table.get_item(
            Key={
                "PK": f"POLICY#{policy_number}",
                "SK": "METADATA"
            }
        )

        policy_item = policy_resp.get("Item")
        if not policy_item:
            return error(404, f"Policy #{policy_number} not found")

        # Success
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "policyNumber": policy_number,
                "claimNumber": claim_number,
                "insured": policy_item.get("insured"),
                "vehicle": policy_item.get("vehicle")
            }, default=decimal_default, ensure_ascii=False)
        }

    except Exception as e:
        return error(500, str(e))


def error(status, message):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"error": message})
    }
