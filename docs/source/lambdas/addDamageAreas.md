---
tocdepth: 0
---

# `addDamageAreas` Lambda

## Overview
Adds one or more damage areas to an existing insurance claim and updates the claim assessment values accordingly.

## Permissions
Public access via token (no authenticated user required).

## API Mapping
- **Path:** `/damages/{tokenId}`
- **Method:** `POST`

---
## Python Run Example

```python
import json
from addDamageAreas import handler

event = {
    "body": json.dumps({
    "damageAreas": [
        {
            "area": "string",
            "severity": "string"
        }
    ]
})
}

response = handler(event, None)
print(response)
```

---
## Request Object `AddClaimDamagesRequest`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `damageAreas` | `array` | Yes | List of damage areas to be added to the claim, including area identifiers and severity levels |

---
## Response Object `AddClaimDamagesResponse`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `claimNumber` | `string` | No | Identifier of the claim associated with the reported damages |
| `assessmentValue` | `number` | No | Updated assessed value of the claim after adding damage areas |
| `approvedValue` | `number` | No | Updated approved value of the claim, if already determined |
| `status` | `string` | No | Current status of the claim after processing damage areas |
| `damageAreas` | `array` | No | List of all damage areas currently associated with the claim |