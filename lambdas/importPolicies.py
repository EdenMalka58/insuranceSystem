import json
import boto3
from datetime import datetime
from decimal import Decimal

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")


def to_decimal(obj):
    if isinstance(obj, list):
        return [to_decimal(i) for i in obj]
    if isinstance(obj, dict):
        return {k: to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, float):
        return Decimal(str(obj))
    return obj


def handler(event, context):
    try:
        body = json.loads(event.get("body", "[]"))

        if not isinstance(body, list):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Body must be a JSON array"})
            }

        policies_created = 0
        claims_created = 0

        for policy in body:
            policy_number = policy["policyNumber"]
            insured = policy["insured"]

            # -------------------------
            # POLICY ITEM
            # -------------------------
            policy_item = {
                "PK": f"POLICY#{policy_number}",
                "SK": "METADATA",
                "entityType": "POLICY",
                "policyNumber": policy_number,
                "insured": insured,
                "vehicle": policy["vehicle"],
                "validity": policy["validity"],
                "insuredValue": policy["insuredValue"],
                "deductibleValue": policy["deductibleValue"],
                "createdAt": policy.get("createdAt", datetime.utcnow().isoformat()),

                # GSI1 – User policies
                "GSI1PK": insured["idNumber"],
                "GSI1SK": f"POLICY#{policy_number}"
            }

            table.put_item(Item=to_decimal(policy_item))
            policies_created += 1

            # -------------------------
            # CLAIM ITEMS (if exist)
            # -------------------------
            for claim in policy.get("claims", []):
                claim_number = claim["claimNumber"]

                claim_item = {
                    "PK": f"POLICY#{policy_number}",
                    "SK": f"CLAIM#{claim_number}",
                    "entityType": "POLICY_CLAIM",
                    "claimNumber": claim_number,
                    "policyNumber": policy_number,
                    "claimDate": claim["claimDate"],
                    "description": claim.get("description", ""),
                    "status": claim["status"],
                    "approvedAction": claim["approvedAction"],
                    "assessmentValue": claim["assessmentValue"],
                    "approvedValue": claim["approvedValue"],
                    "damageAreas": claim.get("damageAreas", []),
                    "createdAt": claim.get("createdAt", datetime.utcnow().isoformat()),
                    "updatedAt": claim.get("updatedAt", datetime.utcnow().isoformat()),

                    # GSI2 – Policy claims
                    "GSI2PK": policy_number,
                    "GSI2SK": f"CLAIM#{claim_number}"
                }

                table.put_item(Item=to_decimal(claim_item))
                claims_created += 1

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Import completed successfully",
                "policiesCreated": policies_created,
                "claimsCreated": claims_created
            }),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }

    # request
    # {"body": "[{\"policyNumber\":\"POL-2025-001\",\"insured\":{\"email\":\"sahar81@gmail.com\",\"idNumber\":\"38388112\",\"name\":\"SaharMalka\",\"phone\":\"054-4552280\"},\"vehicle\":{\"model\":\"Mazda3\",\"plateNumber\":\"888-23-444\",\"year\":2024},\"validity\":{\"end\":\"2025-12-31\",\"start\":\"2025-01-01\"},\"insuredValue\":120000,\"deductibleValue\":2500,\"createdAt\":\"2025-12-20T05:09:31.941126\",\"claims\":[{\"claimNumber\":\"CLM-1001\",\"claimDate\":\"2025-12-21\",\"description\":\"\",\"status\":\"approved\",\"approvedAction\":\"manually\",\"assessmentValue\":40200,\"approvedValue\":40200,\"damageAreas\":[{\"area\":\"frontRight\",\"severity\":\"extensive\",\"estimatedCost\":4800},{\"area\":\"front\",\"severity\":\"extensive\",\"estimatedCost\":5200},{\"area\":\"frontLeft\",\"severity\":\"extensive\",\"estimatedCost\":4800},{\"area\":\"leftFrontSide\",\"severity\":\"extensive\",\"estimatedCost\":6200},{\"area\":\"leftSide\",\"severity\":\"extensive\",\"estimatedCost\":6500},{\"area\":\"rightFrontSide\",\"severity\":\"extensive\",\"estimatedCost\":6200},{\"area\":\"rightSide\",\"severity\":\"extensive\",\"estimatedCost\":6500}],\"createdAt\":\"2025-12-21T16:58:48.396139\",\"updatedAt\":\"2025-12-21T17:00:31.178853\"}]},{\"policyNumber\":\"POL-2025-002\",\"insured\":{\"email\":\"david.cohen@gmail.com\",\"idNumber\":\"123456789\",\"name\":\"DavidCohen\",\"phone\":\"054-1111111\"},\"vehicle\":{\"model\":\"ToyotaCorolla\",\"plateNumber\":\"12-345-67\",\"year\":2023},\"validity\":{\"start\":\"2025-01-01\",\"end\":\"2025-12-31\"},\"insuredValue\":110000,\"deductibleValue\":3000,\"createdAt\":\"2025-01-05T10:12:00.000Z\",\"claims\":[{\"claimNumber\":\"CLM-1002\",\"claimDate\":\"2025-01-18\",\"description\":\"Frontcollision\",\"status\":\"approved\",\"approvedAction\":\"automatically\",\"assessmentValue\":18500,\"approvedValue\":18500,\"damageAreas\":[{\"area\":\"front\",\"severity\":\"medium\",\"estimatedCost\":7500},{\"area\":\"frontLeft\",\"severity\":\"light\",\"estimatedCost\":4200}],\"createdAt\":\"2025-01-18T09:30:00.000Z\",\"updatedAt\":\"2025-01-18T10:00:00.000Z\"}]},{\"policyNumber\":\"POL-2025-004\",\"insured\":{\"email\":\"yael.levi@gmail.com\",\"idNumber\":\"234567891\",\"name\":\"YaelLevi\",\"phone\":\"054-2222222\"},\"vehicle\":{\"model\":\"Mazda3\",\"plateNumber\":\"23-456-78\",\"year\":2024},\"validity\":{\"start\":\"2025-02-01\",\"end\":\"2026-01-31\"},\"insuredValue\":98000,\"deductibleValue\":2500,\"createdAt\":\"2025-02-03T11:00:00.000Z\",\"claims\":[{\"claimNumber\":\"CLM-1003\",\"claimDate\":\"2025-02-22\",\"description\":\"Reardamage\",\"status\":\"rejected\",\"approvedAction\":\"manually\",\"assessmentValue\":12000,\"approvedValue\":0,\"damageAreas\":[{\"area\":\"rear\",\"severity\":\"medium\",\"estimatedCost\":12000}],\"createdAt\":\"2025-02-22T15:10:00.000Z\",\"updatedAt\":\"2025-02-23T09:00:00.000Z\"}]},{\"policyNumber\":\"POL-2025-005\",\"insured\":{\"email\":\"user1@gmail.com\",\"idNumber\":\"11111111\",\"name\":\"UserOne\",\"phone\":\"050-1111111\"},\"vehicle\":{\"model\":\"Mazda3\",\"plateNumber\":\"11-111-11\",\"year\":2024},\"validity\":{\"start\":\"2025-01-01\",\"end\":\"2025-12-31\"},\"insuredValue\":120000,\"deductibleValue\":2500,\"createdAt\":\"2025-01-05T08:00:00Z\",\"claims\":[{\"claimNumber\":\"CLM-1004\",\"claimDate\":\"2025-01-20\",\"description\":\"Frontdamage\",\"status\":\"approved\",\"approvedAction\":\"automatically\",\"assessmentValue\":10000,\"approvedValue\":10000,\"damageAreas\":[{\"area\":\"front\",\"severity\":\"extensive\",\"estimatedCost\":5200},{\"area\":\"frontLeft\",\"severity\":\"extensive\",\"estimatedCost\":4800}],\"createdAt\":\"2025-01-20T10:00:00Z\",\"updatedAt\":\"2025-01-20T10:10:00Z\"}]},{\"policyNumber\":\"POL-2025-006\",\"insured\":{\"email\":\"user2@gmail.com\",\"idNumber\":\"22222222\",\"name\":\"UserTwo\",\"phone\":\"050-2222222\"},\"vehicle\":{\"model\":\"ToyotaCorolla\",\"plateNumber\":\"22-222-22\",\"year\":2023},\"validity\":{\"start\":\"2025-02-01\",\"end\":\"2026-01-31\"},\"insuredValue\":95000,\"deductibleValue\":3000,\"createdAt\":\"2025-02-02T08:00:00Z\",\"claims\":[]},{\"policyNumber\":\"POL-2025-007\",\"insured\":{\"email\":\"user3@gmail.com\",\"idNumber\":\"33333333\",\"name\":\"UserThree\",\"phone\":\"050-3333333\"},\"vehicle\":{\"model\":\"HyundaiTucson\",\"plateNumber\":\"33-333-33\",\"year\":2022},\"validity\":{\"start\":\"2025-03-01\",\"end\":\"2026-02-28\"},\"insuredValue\":140000,\"deductibleValue\":3500,\"createdAt\":\"2025-03-01T09:00:00Z\",\"claims\":[{\"claimNumber\":\"CLM-1005\",\"claimDate\":\"2025-03-18\",\"description\":\"Multipledamages\",\"status\":\"approved\",\"approvedAction\":\"manually\",\"assessmentValue\":55600,\"approvedValue\":55600,\"damageAreas\":[{\"area\":\"front\",\"severity\":\"extensive\",\"estimatedCost\":5200},{\"area\":\"rear\",\"severity\":\"extensive\",\"estimatedCost\":6000},{\"area\":\"leftSide\",\"severity\":\"extensive\",\"estimatedCost\":6500},{\"area\":\"rightSide\",\"severity\":\"extensive\",\"estimatedCost\":6500},{\"area\":\"leftFrontSide\",\"severity\":\"extensive\",\"estimatedCost\":6200},{\"area\":\"rightFrontSide\",\"severity\":\"extensive\",\"estimatedCost\":6200},{\"area\":\"rearLeft\",\"severity\":\"extensive\",\"estimatedCost\":5600},{\"area\":\"rearRight\",\"severity\":\"extensive\",\"estimatedCost\":5600}],\"createdAt\":\"2025-03-18T14:00:00Z\",\"updatedAt\":\"2025-03-18T15:00:00Z\"}]},{\"policyNumber\":\"POL-2025-008\",\"insured\":{\"email\":\"user4@gmail.com\",\"idNumber\":\"44444444\",\"name\":\"UserFour\",\"phone\":\"050-4444444\"},\"vehicle\":{\"model\":\"KiaSportage\",\"plateNumber\":\"44-444-44\",\"year\":2021},\"validity\":{\"start\":\"2025-04-01\",\"end\":\"2026-03-31\"},\"insuredValue\":110000,\"deductibleValue\":4000,\"createdAt\":\"2025-04-01T08:00:00Z\",\"claims\":[{\"claimNumber\":\"CLM-1006\",\"claimDate\":\"2025-04-10\",\"description\":\"Severeaccident\",\"status\":\"rejected\",\"approvedAction\":\"manually\",\"assessmentValue\":67600,\"approvedValue\":0,\"damageAreas\":[{\"area\":\"front\",\"severity\":\"extensive\",\"estimatedCost\":5200},{\"area\":\"rear\",\"severity\":\"extensive\",\"estimatedCost\":6000},{\"area\":\"leftSide\",\"severity\":\"extensive\",\"estimatedCost\":6500},{\"area\":\"rightSide\",\"severity\":\"extensive\",\"estimatedCost\":6500},{\"area\":\"leftFrontSide\",\"severity\":\"extensive\",\"estimatedCost\":6200},{\"area\":\"rightFrontSide\",\"severity\":\"extensive\",\"estimatedCost\":6200},{\"area\":\"leftRearSide\",\"severity\":\"extensive\",\"estimatedCost\":6200},{\"area\":\"rightRearSide\",\"severity\":\"extensive\",\"estimatedCost\":6200},{\"area\":\"rearLeft\",\"severity\":\"extensive\",\"estimatedCost\":5600},{\"area\":\"rearRight\",\"severity\":\"extensive\",\"estimatedCost\":5600}],\"createdAt\":\"2025-04-10T12:00:00Z\",\"updatedAt\":\"2025-04-10T13:00:00Z\"}]},{\"policyNumber\":\"POL-2025-009\",\"insured\":{\"email\":\"user5@gmail.com\",\"idNumber\":\"55555555\",\"name\":\"UserFive\",\"phone\":\"050-5555555\"},\"vehicle\":{\"model\":\"SkodaOctavia\",\"plateNumber\":\"55-555-55\",\"year\":2024},\"validity\":{\"start\":\"2025-05-01\",\"end\":\"2026-04-30\"},\"insuredValue\":98000,\"deductibleValue\":2000,\"createdAt\":\"2025-05-01T08:00:00Z\",\"claims\":[]}]" }
    
