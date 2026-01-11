---
tocdepth: 0
---

# `getTokenData` Lambda

## Overview
Retrieves claim and damage-related data associated with a specific access token, typically used for damage reporting workflows.

## Permissions
Public access via token (no authenticated user required).

## API Mapping
- **Path:** `/damages/{tokenId}`
- **Method:** `GET`

---
## Query String Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tokenId` | `string` | No | Unique token identifier used to retrieve associated claim and damage data |

---
## Python Run Example

```python
import json
from getTokenData import handler

event = {
    "body": json.dumps({
    "tokenId": "string"
})
}

response = handler(event, None)
print(response)
```

---
## Request Object `GetTokenDataRequest`
_No request body._

---
## Response Object `GetTokenDataResponse`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `policyNumber` | `string` | No | Identifier of the policy associated with the claim |
| `claimNumber` | `string` | No | Identifier of the claim for which the notification is resent |
| `insured` | object of [`insured`](updatepolicyrequest_insured) | No | Insured party personal and contact details |
| `vehicle` | object [`vehicle`](updatepolicyrequest_vehicle) | No | Vehicle details covered by the policy |