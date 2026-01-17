import json
import boto3
from datetime import datetime
from auth import require_agent
from response import ok, error
from botocore.exceptions import ClientError

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

def handler(event, context):
    if not require_agent(event):
        return error(403, "Agent access required")

    try:
        body = json.loads(event.get("body", "{}"))

        required_fields = [
            "policyNumber",
            "insured",
            "vehicle",
            "validity",
            "insuredValue",
            "deductibleValue"
        ]

        missing = [f for f in required_fields if f not in body]
        if missing:
            return error(400, f"Missing fields: {missing}")

        policy_number = body.get("policyNumber")
        
        item = {
            "PK": f"POLICY#{policy_number}",
            "SK": "METADATA",
            "entityType": "POLICY",
            "policyNumber": policy_number,
            "insured": {
                "name": body["insured"].get("name"),
                "email": body["insured"].get("email"),
                "phone": body["insured"].get("phone"),
                "idNumber": body["insured"].get("idNumber")
            },
            "vehicle": {
                "model": body["vehicle"].get("model"),
                "year": body["vehicle"].get("year"),
                "plateNumber": body["vehicle"].get("plateNumber")
            },
            "validity": {
                "start": body["validity"].get("start"),
                "end": body["validity"].get("end")
            },
            "insuredValue": body["insuredValue"],
            "deductibleValue": body["deductibleValue"],
            "createdAt": datetime.utcnow().isoformat(),

             # GSI1_UserPolicies attributes
            "GSI1PK": body["insured"]["idNumber"],  # Partition Key for user
            "GSI1SK": f"POLICY#{policy_number}"  # Sort Key for user's policies
        }

        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(PK)"
        )
        
        return ok({
            "message": "Policy created successfully", "policyNumber": policy_number
        })

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code == "ConditionalCheckFailedException":
            return error(409, "Policy already exists")

        # Any other DynamoDB error
        return error(500, "DynamoDB error")        
    except Exception as e:
        return error(500, "Internal sever error")
# request
#{
#  "body": "{\"policyNumber\":\"POL987654\",\"insured\":{\"name\":\"Eden Malka\",\"email\":\"saharmalka1975@gmail.com\",\"phone\":\"0501234567\",\"idNumber\":\"12345678\"},\"vehicle\":{\"model\":\"Toyota Corolla\",\"year\":2021,\"plateNumber\":\"12-345-67\"},\"validity\":{\"start\":\"2025-01-01\",\"end\":\"2026-01-01\"},\"insuredValue\":80000,\"deductibleValue\":1500}"
#}