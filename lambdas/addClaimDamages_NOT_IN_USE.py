import json
import boto3
import time
import uuid


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('InsuranceSystem')

# ---------------- AUTH ----------------

def is_admin(event):
    claims = event.get("requestContext", {}) \
                  .get("authorizer", {}) \
                  .get("claims", {})
    return claims.get("custom:role") == "admin"


def handler(event, context):
    # Extract token
    token = event["headers"].get("Authorization", "").replace("ClaimToken ", "")
    # if not is_admin(event):
    #    return response(403, {"error": "Admin access required"})


    if not token:
        return {"statusCode": 401, "body": "Missing token"}

    # Find token record
    res = table.get_item(
        Key={
            "PK": f"TOKEN#{token}",
            "SK": "METADATA"
        }
    )

    item = res.get("Item")

    # Verify token
    if (
        not item or
        item["used"] or
        item["expiresAt"] < int(time.time())
    ):
        return {"statusCode": 403, "body": "Invalid or expired token"}

    claim_id = item["claimId"]

    # Read damages from the request body
    body = json.loads(event["body"])
    damages = body.get("damages", [])

    if not damages:
        return {"statusCode": 400, "body": "No damages provided"}

    # Add damages to claim
    for damage in damages:
        table.put_item(Item={
            "PK": f"CLAIM#{claim_id}",
            "SK": f"DAMAGE#{uuid.uuid4()}",
            "area": damage["area"],
            "severity": damage["severity"],
            "createdAt": int(time.time())
        })

    # Set token as used
    table.update_item(
        Key={
            "PK": f"TOKEN#{token}",
            "SK": "METADATA"
        },
        UpdateExpression="SET used = :u",
        ExpressionAttributeValues={":u": True}
    )

    sf = boto3.client('stepfunctions')

    sf.start_execution(
        stateMachineArn="arn:aws:states:us-east-1:044017822232:stateMachine:ProcessClaim",
        input=json.dumps({
            "claimId": claim_id
        })
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "claimId": claim_id,
            "damagesAdded": len(damages)
        })
    }
