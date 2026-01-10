---
tocdepth: 0
---

# `addClaim` Lambda

## Overview
Creates a new insurance claim associated with an existing policy.  
The claim can include damage details and optional assessment and approval values.

## Permissions
User must belong to the **`agent`** Cognito group.

## API Mapping
- **Path:** `/claims`
- **Method:** `POST`

---
## Python Run Example

```python
import json
from addClaim import handler

event = {
    "body": json.dumps({
    "policyNumber": "string",
    "claimNumber": "string",
    "claimDate": "string",
    "description": "string",
    "assessmentValue": 1.0,
    "approvedValue": 1.0,
    "damageAreas": [
        "string"
    ]
})
}

response = handler(event, None)
print(response)
```

---
## Request Object `AddClaimRequest`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `policyNumber` | `string` | Yes | Reference to policy number in the insurance company |
| `claimNumber` | `string` | Yes | Reference to claim number in the policy in the insurance company |
| `claimDate` | `string` | Yes | Date when the claim was created or reported |
| `description` | `string` | Yes | Description of the damage or incident being claimed |
| `assessmentValue` | `number` | No | Estimated monetary value of the assessed damage |
| `approvedValue` | `number` | No | Approved payout value for the claim, if applicable |
| `damageAreas` | `array` | No | List of damaged areas or components related to the claim |

---
## Response Object `AddClaimResponse`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `message` | `string` | No | Informational message indicating the result of the operation |
| `claimNumber` | `string` | No | Identifier of the created claim |
| `policyNumber` | `string` | No | Policy number associated with the claim |
| `emailSent` | `boolean` | No | Indicates whether a notification email was sent |
