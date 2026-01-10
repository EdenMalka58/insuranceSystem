---
tocdepth: 0
---

# `updatePolicy` Lambda

## Overview
Updates an existing insurance policy by modifying insured details, vehicle information, coverage values, or validity period.  
Only the provided fields are updated; omitted fields remain unchanged.

## Permissions
Admin only (Cognito group: `admin`)

## API Mapping
- **Path:** `/policies/{policyNumber}`
- **Method:** `PUT`

---
## Python Run Example

```python
import json
from updatePolicy import handler

event = {
    "body": json.dumps({
    "insuredValue": 1.0,
    "deductibleValue": 1.0,
    "insured": {
        "name": "string",
        "email": "string",
        "phone": "string"
    },
    "vehicle": {
        "make": "string",
        "model": "string",
        "year": 1,
        "licensePlate": "string"
    },
    "validity": {
        "startDate": "string",
        "endDate": "string"
    }
})
}

response = handler(event, None)
print(response)
```

---
## Request Object `UpdatePolicyRequest`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `insuredValue` | `number` | No | Updated insured monetary value of the policy |
| `deductibleValue` | `number` | No | Updated deductible amount applied to claims under the policy |
| `insured` | `object` | No | Updated insured person details such as name, email, and phone |
| `vehicle` | `object` | No | Updated vehicle information associated with the policy |
| `validity` | `object` | No | Updated policy validity period including start and end dates |

---
## Response Object `UpdatePolicyResponse`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `message` | `string` | No | Confirmation message indicating the policy was updated successfully |