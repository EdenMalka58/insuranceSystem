---
tocdepth: 0
---

# `getAdminStatistics` Lambda

## Overview
Returns aggregated statistical insights for administrative analysis, including claim distributions, trends, and correlations across policies and claims.

## Permissions
User must belong to the **`admin`** Cognito group.

## API Mapping
- **Path:** `/statistics`
- **Method:** `GET`

---
## Python Run Example

```python
import json
from getAdminStatistics import handler

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
## Response Object `GetAdminStatisticsResponse`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `claimsByStatus` | `object` | No | Aggregation of claims grouped by their current status |
| `claimsByApprovedAction` | `object` | No | Distribution of claims by approval action type (automatic or manual) |
| `claimsOverTime` | `object` | No | Time-based aggregation of claim counts or values |
| `approvedValueByMonth` | `object` | No | Monthly aggregation of approved claim values |
| `policiesOverTime` | `object` | No | Time-based aggregation of policy creation or activity |
| `claimsByVehicleYear` | `object` | No | Distribution of claims grouped by vehicle manufacturing year |
| `claimsByVehicleValue` | `object` | No | Distribution of claims grouped by insured vehicle value |
| `approvalRateByDeductible` | `object` | No | Analysis of claim approval rates relative to deductible values |
| `avgClaimCostByVehicleValue` | `object` | No | Average claim cost grouped by vehicle insured value ranges |
| `deductibleVsOutcome` | `object` | No | Correlation between deductible values and claim outcomes |
