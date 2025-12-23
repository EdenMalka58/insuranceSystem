import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
import base64

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

PAGE_SIZE = 5


# ---------- HELPERS ----------

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def safe_dict(v):
    return v if isinstance(v, dict) else {}


def encode_token(key):
    if not key:
        return None
    return base64.b64encode(json.dumps(key).encode()).decode()


def decode_token(token):
    if not token:
        return None

    padding = '=' * (-len(token) % 4)
    token += padding

    return json.loads(
        base64.urlsafe_b64decode(token.encode()).decode()
    )

# ---------- HANDLER ----------

def handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        search_query = params.get("query")
        next_page_token = decode_token(params.get("nextPage"))

        items = []
        last_key = next_page_token

        # NO SEARCH → SCAN POLICIES ONLY (FIXED)
        if not search_query:
            while len(items) < PAGE_SIZE:
                scan_kwargs = {
                    "FilterExpression": (
                        Attr("PK").begins_with("POLICY#") &
                        Attr("SK").eq("METADATA")
                    ),
                    "Limit": PAGE_SIZE
                }

                if last_key:
                    scan_kwargs["ExclusiveStartKey"] = last_key

                response = table.scan(**scan_kwargs)
                items.extend(response.get("Items", []))
                last_key = response.get("LastEvaluatedKey")

                if not last_key:
                    break

        # SEARCH BY policyNumber OR insured idNumber
        else:
            policy_response = table.get_item(
                Key={
                    "PK": f"POLICY#{search_query}",
                    "SK": "METADATA"
                }
            )

            if "Item" in policy_response:
                items = [policy_response["Item"]]
                last_key = None
            else:
                query_kwargs = {
                    "IndexName": "GSI1_UserPolicies",
                    "KeyConditionExpression": Key("GSI1PK").eq(search_query),
                    "Limit": PAGE_SIZE
                }

                if next_page_token:
                    query_kwargs["ExclusiveStartKey"] = next_page_token

                response = table.query(**query_kwargs)
                items = response.get("Items", [])
                last_key = response.get("LastEvaluatedKey")

        # ---------- SHAPE ----------
        policies = [{
            "policyNumber": i.get("policyNumber"),
            "insured": safe_dict(i.get("insured")),
            "vehicle": safe_dict(i.get("vehicle")),
            "validity": safe_dict(i.get("validity")),
            "insuredValue": i.get("insuredValue"),
            "deductibleValue": i.get("deductibleValue"),
            "createdAt": i.get("createdAt")
        } for i in items[:PAGE_SIZE]]

        policies.sort(key=lambda x: x.get("createdAt", ""), reverse=True)

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "items": policies,
                "nextPage": encode_token(last_key)
            }, default=decimal_default)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
#{
#  "queryStringParameters": {
#    "query": "38388112"
#  }
#}
