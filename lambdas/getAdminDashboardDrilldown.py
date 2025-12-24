import json
import boto3
from boto3.dynamodb.conditions import Attr
from datetime import datetime
from decimal import Decimal
from auth import require_admin
from response import ok, error


dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

def handler(event, context):
    if not require_admin(event):
        return error(403, "Admin access required")

    params = event.get("queryStringParameters") or {}
    drill_type = params.get("type")
    value = params.get("value")
    year = int(params.get("year", datetime.utcnow().year))

    # ---------- POLICIES DRILLDOWN ----------
    if drill_type == "policies":
        policies = table.scan(
            FilterExpression=Attr("entityType").eq("POLICY")
        )["Items"]

        return ok(policies)

    # ---------- CLAIMS ----------
    claims = table.scan(
        FilterExpression=Attr("entityType").eq("POLICY_CLAIM")
    )["Items"]

    
    if drill_type == "approvedClaimsByMonth" or drill_type == "rejectedClaimsByMonth":
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

#{
#    "queryStringParameters": {
#    "type": "claimsByStatus",
#    "value": "approved"
#  }
#}