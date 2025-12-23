import json
from decimal import Decimal

def require_admin_or_agent(event):
    groups = event["requestContext"]["authorizer"]["claims"].get("cognito:groups", [])
    return bool(set(groups) & {"admin", "agent"})

def require_admin(event):
    claims = event["requestContext"]["authorizer"]["claims"]
    groups = claims.get("cognito:groups", [])
    return "admin" in groups
