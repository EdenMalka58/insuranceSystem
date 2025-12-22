import json
import boto3

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

def handler(event, context):

    params = event.get("queryStringParameters") or {}
    dtype = params.get("type")
    value = params.get("value")

    if not dtype or not value:
        return response(400, {"error": "type and value required"})

    items = table.scan()["Items"]
    claims = [i for i in items if i.get("entityType") == "POLICY_CLAIM"]
    policies = {i["policyNumber"]: i for i in items if i.get("entityType") == "POLICY"}

    result = []

    for c in claims:
        p = policies.get(c["policyNumber"])

        if dtype == "claimsByStatus" and c["status"] == value:
            result.append(c)

        elif dtype == "claimsByApprovedAction" and c["approvedAction"] == value:
            result.append(c)

        elif dtype == "claimsByDate" and c["createdAt"].startswith(value):
            result.append(c)

        elif dtype == "approvedValueByMonth" and c["createdAt"].startswith(value):
            result.append(c)

        elif dtype == "claimsByVehicleYear" and p and str(p["vehicle"]["year"]) == value:
            result.append(c)

        elif dtype == "claimsByVehicleValue" and p:
            if value in str(p["insuredValue"]):
                result.append(c)

        elif dtype == "approvalRateByDeductible" and p:
            if value in str(p["deductibleValue"]):
                result.append(c)

        elif dtype == "avgClaimCostByVehicleValue" and p:
            if value in str(p["insuredValue"]):
                result.append(c)

        elif dtype == "deductibleVsOutcome" and p:
            if value in str(p["deductibleValue"]):
                result.append(c)

    return response(200, result)


def response(code, body):
    return {
        "statusCode": code,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body, default=str)
    }

#{
#    "queryStringParameters": {
#    "type": "claimsByStatus",
#    "value": "approved"
#  }
#}