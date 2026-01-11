---
tocdepth: 0
---

# `getPolicy` Lambda

## Overview
Retrieves detailed information for a specific insurance policy, including associated claims and claim statistics.

## Permissions
User must belong to the **`agent`** Cognito group.

## API Mapping
- **Path:** `/policies/{policyNumber}`
- **Method:** `GET`

---
## Python Run Example

```python
import json
from getPolicy import handler

event = {
    "body": json.dumps({})
}

response = handler(event, None)
print(response)
```

---
## Request Object `None`
_No request body._

---
## Response Object `GetPolicyResponse`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `policy` | `object` | No | Policy details including insured, vehicle, validity period, and coverage values |
| `claimsCount` | `integer` | No | Total number of claims associated with the policy |
| `claims` | array of [`claim`](getpolicyresponse_claims)  | No | List of claim records linked to the policy |
