---
tocdepth: 0
---

# `getAdminDashboard` Lambda

## Overview
Returns aggregated administrative dashboard statistics for the selected year,
including policy counters, claim trends, and activity summaries.

## Permissions
User must belong to the **`admin`** Cognito group.

## API Mapping
- **Path:** `/dashboard`
- **Method:** `GET`
- **Authorization:** Admin only (Cognito group: `admin`)

## Query String Parameters

| Name | Type | Required | Description |
|-----|------|----------|-------------|
| `year` | integer | No | Year for which dashboard statistics are calculated. Defaults to the current year if not provided. |

---
## Python Run Example

```python
from getAdminDashboard import handler

event = {
    "queryStringParameters": {
        "year": "2024"
    },
    "requestContext": {
        "authorizer": {
            "claims": {
                "cognito:groups": ["admin"]
            }
        }
    }
}

response = handler(event, None)
print(response)
```

---
## Request Object `None`
_No request body._

---
## Response Object `GetAdminDashboardResponse`

| Field | Type | Required | Description |
|------|------|----------|-------------|
| `year` | `integer` | Yes | The year for which the dashboard statistics are calculated. Derived from the `year` query parameter or defaults to the current UTC year. |
| `counters` | `array` | Yes | High-level summary counters for policies and claims, including totals, amounts, and drilldown metadata for dashboard navigation. |
| `claimsOverview` | `object` | Yes | Monthly aggregation of approved and rejected claim values for the selected year, structured for chart visualization. |
| `activity` | `array` | Yes | Sidebar activity indicators summarizing claim processing actions such as reported damages, approvals, and waiting claims. |
