import json
import boto3
from datetime import datetime

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("InsuranceSystem")

def handler(event, context):
    try:
        path_params = event.get("pathParameters") or {}
        policy_number = path_params.get("policyNumber")

        if not policy_number:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "policyNumber is required"}),
                "headers": {"Access-Control-Allow-Origin": "*"}
            }

        body = json.loads(event.get("body", "{}"))
        if not body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Request body is empty"}),
                "headers": {"Access-Control-Allow-Origin": "*"}
            }

        update_expressions = []
        expression_values = {}
        expression_names = {}

        def add_update(path, value):
            key = path.replace(".", "_")
            update_expressions.append(f"{path} = :{key}")
            expression_values[f":{key}"] = value

        # Flat fields
        if "insuredValue" in body:
            add_update("insuredValue", body["insuredValue"])

        if "deductibleValue" in body:
            add_update("deductibleValue", body["deductibleValue"])

        # Nested fields
        for section in ["insured", "vehicle", "validity"]:
            if section in body:
                for field, value in body[section].items():
                    attr = f"{section}.{field}"
                    name_key = f"#{section}_{field}"
                    expression_names[name_key] = field
                    update_expressions.append(
                        f"{section}.#{section}_{field} = :{section}_{field}"
                    )
                    expression_values[f":{section}_{field}"] = value

        # updatedAt
        update_expressions.append("updatedAt = :updatedAt")
        expression_values[":updatedAt"] = datetime.utcnow().isoformat()

        if not update_expressions:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No valid fields to update"}),
                "headers": {"Access-Control-Allow-Origin": "*"}
            }

        update_expression = "SET " + ", ".join(update_expressions)

        table.update_item(
            Key={
                "PK": f"POLICY#{policy_number}",
                "SK": "METADATA"
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names if expression_names else None,
            ConditionExpression="attribute_exists(PK)"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Policy updated successfully"}),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }
