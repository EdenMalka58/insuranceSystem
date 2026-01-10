---
tocdepth: 0
---

# `updateClaimStatus` Lambda

## Overview
Updates the approval status of an existing insurance claim.  
Based on the approval decision, the claim is marked as approved or rejected and related approval metadata is updated accordingly.

## Permissions
User must belong to the **`agent`** Cognito group.

## API Mapping
- **Path:** `/claims/{claimNumber}`
- **Method:** `PUT`

---
## Python Run Example

```python
import json
from updateClaimStatus import handler

event = {
    "body": json.dumps({
    "policyNumber": "string",
    "claimNumber": "string",
    "isApproved": false
})
}

response = handler(event, None)
print(response)
```

---
## Request Object `UpdateClaimStatusRequest`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `policyNumber` | `string` | Yes | Identifier of the policy associated with the claim |
| `claimNumber` | `string` | Yes | Identifier of the claim whose status is being updated |
| `isApproved` | `boolean` | Yes | Indicates whether the claim is approved (`true`) or rejected (`false`) |

---
## Response Object `UpdateClaimStatusResponse`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `message` | `string` | No | Informational message describing the result of the status update |
| `policyNumber` | `string` | No | Policy number associated with the updated claim |
| `claimNumber` | `string` | No | Identifier of the updated claim |
| `approvedValue` | `number` | No | Final approved monetary value for the claim, if approved |
| `approvedAction` | `string` | No | Outcome of the approval decision (for example: `approved`, `rejected`, or `pending`) |
