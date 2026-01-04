import json
import boto3
from collections import defaultdict
from auth import require_admin
from response import ok, error


dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

# ---------------- HANDLER ----------------

def handler(event, context):
    if not require_admin(event):
        return error(403, "Admin access required")

    resp = table.scan()
    items = resp.get("Items", [])

    claims = [i for i in items if i.get("entityType") == "POLICY_CLAIM"]
    policies = {
        i["policyNumber"]: i
        for i in items
        if i.get("entityType") == "POLICY"
    }

    stats = {
        "claimsByStatus": claims_by_status(claims),
        "claimsByApprovedAction": claims_by_action(claims),
        "claimsOverTime": claims_over_time(claims),
        "approvedValueByMonth": approved_value_by_month(claims),
        "policiesOverTime": policies_over_time(policies.values()),
        "claimsByVehicleYear": claims_by_vehicle_year(claims, policies),
    }

    return ok(200, stats)


# ---------------- HELPERS ----------------

def bucket(value, ranges):
    for label, low, high in ranges:
        if low <= value < high:
            return label
    return ranges[-1][0]


def chart(chart_type, labels, data, drill_key, title):
    return {
        "title": title,
        "type": chart_type,
        "data": {
            "labels": labels,
            "datasets": [{"label": "Count", "data": data}]
        },
        "drilldown": {
            "enabled": True,
            "endpoint": "/admin/statistics/drilldown",
            "key": drill_key
        }
    }


# ---------------- GRAPHS ----------------

def claims_by_status(claims):
    c = defaultdict(int)
    for i in claims:
        c[i["status"]] += 1
    return chart("pie", list(c.keys()), list(c.values()), "claimsByStatus", "Claims by Status")


def claims_by_action(claims):
    c = defaultdict(int)
    for i in claims:
        c[i["approvedAction"]] += 1
    return chart("bar", list(c.keys()), list(c.values()), "claimsByApprovedAction", "Claims by Approval Method")


def claims_over_time(claims):
    c = defaultdict(int)
    for i in claims:
        c[i["createdAt"][:10]] += 1
    labels = sorted(c.keys())
    return chart("line", labels, [c[d] for d in labels], "claimsByDate", "Claims Over Time")


def approved_value_by_month(claims):
    s = defaultdict(int)
    for i in claims:
        s[i["createdAt"][:7]] += int(i.get("approvedValue", 0))
    labels = sorted(s.keys())
    return chart("bar", labels, [s[m] for m in labels], "approvedValueByMonth", "Approved Claim Value by Month")


def policies_over_time(policies):
    c = defaultdict(int)
    for p in policies:
        c[p["createdAt"][:10]] += 1
    labels = sorted(c.keys())
    return chart("line", labels, [c[d] for d in labels], "policiesByDate", "Policies Created Over Time")


def claims_by_vehicle_year(claims, policies):
    c = defaultdict(int)
    for cl in claims:
        p = policies.get(cl["policyNumber"])
        if p:
            c[str(p["vehicle"]["year"])] += 1
    return chart("bar", list(c.keys()), list(c.values()), "claimsByVehicleYear", "Claims by Vehicle Year")