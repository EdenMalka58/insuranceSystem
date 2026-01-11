---
tocdepth: 0
---

# `addPolicy` Lambda

## Overview
Creates a new insurance policy record, including insured details, vehicle information, policy validity, and coverage values.

## Permissions
User must belong to the **`agent`** Cognito group.

## API Mapping
- **Path:** `/policies`
- **Method:** `POST`

---
## Python Run Example

```python
import json
from addPolicy import handler

event = {
    "body": json.dumps({
    "policyNumber": "string",
    "insured": {
        "name": "string",
        "email": "string",
        "phone": "string",
        "idNumber": "string"
    },
    "vehicle": {
        "model": "string",
        "year": 1,
        "plateNumber": "string"
    },
    "validity": {
        "start": "string",
        "end": "string"
    },
    "insuredValue": 1.0,
    "deductibleValue": 1.0
})
}

response = handler(event, None)
print(response)
```

---
## Request Object `AddPolicyRequest`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `policyNumber` | `string` | Yes | Unique identifier of the insurance policy |
| `insured` | object [`insured`](addpolicyrequest_insured) | No | Insured party personal and contact details |
| `vehicle` | object [`vehicle`](addpolicyrequest_vehicle) | No | Vehicle details covered by the policy |
| `validity` | object [validity](addpolicyrequest_validity) | Yes | Policy coverage period including start and end dates |
| `insuredValue` | `number` | Yes | Total insured value covered by the policy |
| `deductibleValue` | `number` | Yes | Deductible amount applied to claims under the policy |

---
## Response Object `AddPolicyResponse`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `message` | `string` | No | Informational message indicating the result of the policy creation |
| `policyNumber` | `string` | No | Identifier of the newly created policy |
