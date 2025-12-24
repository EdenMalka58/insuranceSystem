import json
from decimal import Decimal

def require_admin(event):
    if not event or "requestContext" not in event or "authorizer" not in event["requestContext"]:
      return False  # Invalid event structure

    claims = event["requestContext"]["authorizer"]["claims"]
    groups = claims.get("cognito:groups", [])
    return "admin" in groups

def require_agent(event):
    # Check if the event is not None and contains the necessary keys
    if not event or "requestContext" not in event or "authorizer" not in event["requestContext"]:
        return False  # Invalid event structure
    
    claims = event["requestContext"]["authorizer"]["claims"]
    groups = claims.get("cognito:groups", [])

    # Check if either "agent" or "admin" is in the groups
    return any(group in groups for group in ["agent", "admin"])