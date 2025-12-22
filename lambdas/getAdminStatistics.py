import json
import boto3
from collections import defaultdict

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

# ---------------- HANDLER ----------------

def handler(event, context):

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
        "claimsByVehicleValue": claims_by_vehicle_value(claims, policies),
        "approvalRateByDeductible": approval_rate_by_deductible(claims, policies),
        "avgClaimCostByVehicleValue": avg_claim_cost_by_vehicle_value(claims, policies),
        "deductibleVsOutcome": deductible_vs_outcome(claims, policies)
    }

    return response(200, stats)


# ---------------- HELPERS ----------------

def bucket(value, ranges):
    for label, low, high in ranges:
        if low <= value < high:
            return label
    return ranges[-1][0]


def chart(chart_type, labels, data, drill_key):
    return {
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
    return chart("pie", list(c.keys()), list(c.values()), "claimsByStatus")


def claims_by_action(claims):
    c = defaultdict(int)
    for i in claims:
        c[i["approvedAction"]] += 1
    return chart("bar", list(c.keys()), list(c.values()), "claimsByApprovedAction")


def claims_over_time(claims):
    c = defaultdict(int)
    for i in claims:
        c[i["createdAt"][:10]] += 1
    labels = sorted(c.keys())
    return chart("line", labels, [c[d] for d in labels], "claimsByDate")


def approved_value_by_month(claims):
    s = defaultdict(int)
    for i in claims:
        s[i["createdAt"][:7]] += int(i.get("approvedValue", 0))
    labels = sorted(s.keys())
    return chart("bar", labels, [s[m] for m in labels], "approvedValueByMonth")


def policies_over_time(policies):
    c = defaultdict(int)
    for p in policies:
        c[p["createdAt"][:10]] += 1
    labels = sorted(c.keys())
    return chart("line", labels, [c[d] for d in labels], "policiesByDate")


def claims_by_vehicle_year(claims, policies):
    c = defaultdict(int)
    for cl in claims:
        p = policies.get(cl["policyNumber"])
        if p:
            c[str(p["vehicle"]["year"])] += 1
    return chart("bar", list(c.keys()), list(c.values()), "claimsByVehicleYear")


def claims_by_vehicle_value(claims, policies):
    ranges = [("0-50K",0,50000),("50K-100K",50000,100000),
              ("100K-200K",100000,200000),("200K+",200000,10**9)]
    c = defaultdict(int)
    for cl in claims:
        p = policies.get(cl["policyNumber"])
        if p:
            c[bucket(p["insuredValue"], ranges)] += 1
    return chart("bar", list(c.keys()), list(c.values()), "claimsByVehicleValue")


def approval_rate_by_deductible(claims, policies):
    ranges = [("0-1K",0,1000),("1K-3K",1000,3000),
              ("3K-5K",3000,5000),("5K+",5000,10**9)]
    total, approved = defaultdict(int), defaultdict(int)

    for cl in claims:
        p = policies.get(cl["policyNumber"])
        if p:
            b = bucket(p["deductibleValue"], ranges)
            total[b] += 1
            if cl["status"] == "approved":
                approved[b] += 1

    labels = list(total.keys())
    rates = [round((approved[l]/total[l])*100,1) if total[l] else 0 for l in labels]

    return {
        "type": "bar",
        "data": {"labels": labels,
                 "datasets": [{"label": "Approval %", "data": rates}]},
        "drilldown": {"enabled": True, "key": "approvalRateByDeductible"}
    }


def avg_claim_cost_by_vehicle_value(claims, policies):
    ranges = [("0-50K",0,50000),("50K-100K",50000,100000),
              ("100K-200K",100000,200000),("200K+",200000,10**9)]
    sums, cnt = defaultdict(int), defaultdict(int)

    for cl in claims:
        p = policies.get(cl["policyNumber"])
        if p:
            b = bucket(p["insuredValue"], ranges)
            sums[b] += int(cl.get("assessmentValue", 0))
            cnt[b] += 1

    labels = list(sums.keys())
    avg = [round(sums[l]/cnt[l],2) if cnt[l] else 0 for l in labels]

    return {
        "type": "line",
        "data": {"labels": labels,
                 "datasets": [{"label": "Avg Claim Cost", "data": avg}]},
        "drilldown": {"enabled": True, "key": "avgClaimCostByVehicleValue"}
    }


def deductible_vs_outcome(claims, policies):
    ranges = [("0-1K",0,1000),("1K-3K",1000,3000),
              ("3K-5K",3000,5000),("5K+",5000,10**9)]
    app, rej = defaultdict(int), defaultdict(int)

    for cl in claims:
        p = policies.get(cl["policyNumber"])
        if p:
            b = bucket(p["deductibleValue"], ranges)
            if cl["status"] == "approved":
                app[b] += 1
            elif cl["status"] == "rejected":
                rej[b] += 1

    labels = list(app.keys())
    return {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [
                {"label": "Approved", "data": [app[l] for l in labels]},
                {"label": "Rejected", "data": [rej[l] for l in labels]}
            ]
        },
        "options": {"stacked": True},
        "drilldown": {"enabled": True, "key": "deductibleVsOutcome"}
    }


def response(code, body):
    return {
        "statusCode": code,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body, default=str)
    }
