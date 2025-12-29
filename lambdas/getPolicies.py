import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
from auth import require_agent
from response import ok, error

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

DEFAULT_PAGE_SIZE = 5
MAX_PAGE_SIZE = 50


# ---------- HELPERS ----------

def safe_dict(v):
    return v if isinstance(v, dict) else {}


# ---------- HANDLER ----------

def handler(event, context):
    if not require_agent(event):
        return error(403, "Agent access required")

    try:
        params = event.get("queryStringParameters") or {}

        search_query = params.get("query")

        page = max(int(params.get("page", 1)), 1)
        page_size = min(
            max(int(params.get("pageSize", DEFAULT_PAGE_SIZE)), 1),
            MAX_PAGE_SIZE
        )

        items = []

        # ---------- NO SEARCH SCAN ALL POLICIES ----------
        if not search_query:
            scan_kwargs = {
                "FilterExpression": (
                    Attr("PK").begins_with("POLICY#") &
                    Attr("SK").eq("METADATA")
                )
            }

            while True:
                response = table.scan(**scan_kwargs)
                items.extend(response.get("Items", []))

                if "LastEvaluatedKey" not in response:
                    break

                scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

        # ---------- SEARCH ----------
        else:
            policy_response = table.get_item(
                Key={
                    "PK": f"POLICY#{search_query}",
                    "SK": "METADATA"
                }
            )

            if "Item" in policy_response:
                items = [policy_response["Item"]]
            else:
                query_kwargs = {
                    "IndexName": "GSI1_UserPolicies",
                    "KeyConditionExpression": Key("GSI1PK").eq(search_query)
                }

                while True:
                    response = table.query(**query_kwargs)
                    items.extend(response.get("Items", []))

                    if "LastEvaluatedKey" not in response:
                        break

                    query_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

        # ---------- SORT ----------
        items.sort(
            key=lambda x: x.get("createdAt", ""),
            reverse=True
        )

        # ---------- PAGINATION ----------
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size

        paged_items = items[start:end]
        has_next = end < total

        # ---------- SHAPE ----------
        policies = [{
            "policyNumber": i.get("policyNumber"),
            "insured": safe_dict(i.get("insured")),
            "vehicle": safe_dict(i.get("vehicle")),
            "validity": safe_dict(i.get("validity")),
            "insuredValue": i.get("insuredValue"),
            "deductibleValue": i.get("deductibleValue"),
            "createdAt": i.get("createdAt")
        } for i in paged_items]

        return ok({
            "items": policies,
            "page": page,
            "pageSize": page_size,
            "total": total,
            "hasNext": has_next
        })

    except Exception as e:
        return error(500, "Internal server error")
