import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def safe_dict(value):
    return value if isinstance(value, dict) else {}


def handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        search_query = params.get("query")  # can be policyNumber or insured idNumber

        if not search_query:
            # Fallback scan for all policies only
            response = table.scan(
                FilterExpression=Attr("entityType").eq("POLICY")
            )
            items = response.get("Items", [])

        else:
            items = []

            # Try search by policyNumber
            policy_response = table.get_item(
                Key={
                    "PK": f"POLICY#{search_query}",
                    "SK": "METADATA"
                }
            )
            if "Item" in policy_response:
                items.append(policy_response["Item"])
            else:
                # Try search by insured idNumber using GSI1_UserPolicies
                gsi_response = table.query(
                    IndexName="GSI1_UserPolicies",
                    KeyConditionExpression=Key("GSI1PK").eq(search_query)
                )
                items.extend(gsi_response.get("Items", []))

        policies = []
        for item in items:
            insured = safe_dict(item.get("insured"))
            vehicle = safe_dict(item.get("vehicle"))
            validity = safe_dict(item.get("validity"))

            policies.append({
                "policyNumber": item.get("policyNumber"),
                "insured": insured,
                "vehicle": vehicle,
                "validity": validity,
                "insuredValue": item.get("insuredValue"),
                "deductibleValue": item.get("deductibleValue"),
                "createdAt": item.get("createdAt")
            })
            
            policies.sort(
                key=lambda x: x.get("createdAt", ""),
                reverse=True
            )                

        return {
            "statusCode": 200,
            "body": json.dumps(policies, default=decimal_default, ensure_ascii=False),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}, ensure_ascii=False),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }
