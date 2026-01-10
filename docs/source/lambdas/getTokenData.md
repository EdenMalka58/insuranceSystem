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
## Response Object `GetAdminStatisticsResponse`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `claimsByStatus` | `object` | No | Aggregation of claims grouped by their current status |
| `claimsByApprovedAction` | `object` | No | Distribution of claims based on approval action type |
| `claimsOverTime` | `object` | No | Time-based aggregation of claim activity |
| `approvedValueByMonth` | `object` | No | Monthly aggregation of approved claim values |
| `policiesOverTime` | `object` | No | Time-based aggregation of policy activity |
| `claimsByVehicleYear` | `object` | No | Distribution of claims grouped by vehicle manufacturing year |
| `claimsByVehicleValue` | `object` | No | Distribution of claims grouped by insured vehicle value |
| `approvalRateByDeductible` | `object` | No | Analysis of approval rates relative to deductible values |
| `avgClaimCostByVehicleValue` | `object` | No | Average claim cost grouped by vehicle value ranges |
| `deductibleVsOutcome` | `object` | No | Correlation between deductible values and claim outcomes |
