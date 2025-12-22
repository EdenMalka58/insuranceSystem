import json
import boto3
from boto3.dynamodb.conditions import Attr
from datetime import datetime
from decimal import Decimal

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def handler(event, context):

    params = event.get("queryStringParameters") or {}
    drill_type = params.get("type")
    value = params.get("value")
    year = int(params.get("year", datetime.utcnow().year))

    # ---------- POLICIES DRILLDOWN ----------
    if drill_type == "policies":
        policies = table.scan(
            FilterExpression=Attr("entityType").eq("POLICY")
        )["Items"]

        # Optional year filter
        policies = [
            p for p in policies
            if p.get("createdAt", "").startswith(str(year))
        ]

        return ok(policies)

    # ---------- CLAIMS ----------
    claims = table.scan(
        FilterExpression=Attr("entityType").eq("POLICY_CLAIM")
    )["Items"]

    # Year filter
    claims = [
        c for c in claims
        if c.get("createdAt", "").startswith(str(year))
    ]

    # ---------- Drilldown Logic ----------
    if drill_type == "claimsByStatus":
        claims = [c for c in claims if c["status"] == value]

    elif drill_type == "damagesReported":
        claims = [c for c in claims if len(c.get("damageAreas", [])) > 0]

    elif drill_type == "autoApproved":
        claims = [
            c for c in claims
            if c["status"] == "approved" and c["approvedAction"] == "automatically"
        ]

    elif drill_type == "manualApproved":
        claims = [
            c for c in claims
            if c["status"] == "approved" and c["approvedAction"] == "manually"
        ]

    elif drill_type == "waitingClaims":
        claims = [c for c in claims if c["approvedAction"] == "waiting"]

    elif drill_type == "approvedClaimsByMonth":
        claims = [
            c for c in claims
            if c["status"] == "approved" and c["createdAt"][5:7] == value
        ]

    elif drill_type == "rejectedClaimsByMonth":
        claims = [
            c for c in claims
            if c["status"] == "rejected" and c["createdAt"][5:7] == value
        ]

    else:
        return error(400, "Invalid drilldown type")

    return ok(claims)

def ok(body):
    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body, default=decimal_default)
    }

def error(code, msg):
    return {
        "statusCode": code,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"error": msg})
    }
#{
#    "queryStringParameters": {
#    "type": "claimsByStatus",
#    "value": "approved"
#  }
#}