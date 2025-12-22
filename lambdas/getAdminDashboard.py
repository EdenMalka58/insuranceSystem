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
    year = params.get("year")

    try:
        selected_year = int(year) if year else datetime.utcnow().year
    except ValueError:
        return error(400, "Invalid year")

    # ---------- Fetch Data ----------
    policies = table.scan(
        FilterExpression=Attr("entityType").eq("POLICY")
    )["Items"]

    claims = table.scan(
        FilterExpression=Attr("entityType").eq("POLICY_CLAIM")
    )["Items"]

    # ---------- Top Counters ----------
    total_policies = len(policies)
    total_policy_value = sum(int(p.get("insuredValue", 0)) for p in policies)

    opened_claims = [c for c in claims if c["status"] == "opened"]
    approved_claims = [c for c in claims if c["status"] == "approved"]
    rejected_claims = [c for c in claims if c["status"] == "rejected"]

    # ---------- Monthly Aggregation ----------
    months = [f"{i:02d}" for i in range(1, 13)]
    approved_monthly = {m: 0 for m in months}
    rejected_monthly = {m: 0 for m in months}

    for c in approved_claims:
        if c["createdAt"].startswith(str(selected_year)):
            m = c["createdAt"][5:7]
            approved_monthly[m] += int(c.get("approvedValue", 0))

    for c in rejected_claims:
        if c["createdAt"].startswith(str(selected_year)):
            m = c["createdAt"][5:7]
            rejected_monthly[m] += int(c.get("assessmentValue", 0))

    # ---------- Activity Sidebar ----------
    damages_reported = sum(1 for c in claims if len(c.get("damageAreas", [])) > 0)
    auto_approved = sum(1 for c in claims if c["status"] == "approved" and c["approvedAction"] == "automatically")
    manual_approved = sum(1 for c in claims if c["status"] == "approved" and c["approvedAction"] == "manually")
    waiting_claims = sum(1 for c in claims if c["approvedAction"] == "waiting")

    # ---------- Response ----------
    response = {
        "year": selected_year,

        "counters": [
            {
                "id": "totalPolicies",
                "title": "Total Policies",
                "count": total_policies,
                "amount": total_policy_value,
                "color": "primary",
                "drilldown": {"type": "policies"}
            },
            {
                "id": "claimsOpened",
                "title": "Claims Opened",
                "count": len(opened_claims),
                "amount": 0,
                "color": "info",
                "drilldown": {"type": "claimsByStatus", "value": "opened"}
            },
            {
                "id": "claimsApproved",
                "title": "Claims Approved",
                "count": len(approved_claims),
                "amount": sum(int(c.get("approvedValue", 0)) for c in approved_claims),
                "color": "success",
                "drilldown": {"type": "claimsByStatus", "value": "approved"}
            },
            {
                "id": "claimsRejected",
                "title": "Claims Rejected",
                "count": len(rejected_claims),
                "amount": sum(int(c.get("assessmentValue", 0)) for c in rejected_claims),
                "color": "warning",
                "drilldown": {"type": "claimsByStatus", "value": "rejected"}
            }
        ],

        "claimsOverview": {
            "type": "line",
            "labels": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
            "datasets": [
                {
                    "label": "Approved Claims",
                    "data": [approved_monthly[m] for m in months],
                    "borderColor": "rgb(13,110,253)",
                    "backgroundColor": "rgba(13,110,253,0.1)",
                    "drilldownType": "approvedClaimsByMonth",
                    "fill": True
                },
                {
                    "label": "Rejected Claims",
                    "data": [rejected_monthly[m] for m in months],
                    "borderColor": "rgb(220,53,69)",
                    "backgroundColor": "rgba(220,53,69,0.1)",
                    "drilldownType": "rejectedClaimsByMonth",
                    "fill": True
                }
            ]
        },

        "activity": [
            {"label": "Damages reported", "count": damages_reported, "color": "primary", "type": "damagesReported"},
            {"label": "Automatically approved", "count": auto_approved, "color": "success", "type": "autoApproved"},
            {"label": "Manually approved", "count": manual_approved, "color": "info", "type": "manualApproved"},
            {"label": "Claims waiting", "count": waiting_claims, "color": "warning", "type": "waitingClaims"}
        ]
    }

    return ok(response)

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
