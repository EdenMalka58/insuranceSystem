---
tocdepth: 0
---

# `getPolicies` Lambda

## Overview
Retrieves a paginated list of insurance policies stored in the system.

## Permissions
User must belong to the **`agent`** Cognito group.

## API Mapping
- **Path:** `/policies`
- **Method:** `GET`

---
## Python Run Example

```python
import json
from getPolicies import handler

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
## Response Object `GetPoliciesResponse`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `items` | `array` | No | List of insurance policy records returned in the response |
| `page` | `integer` | No | Current page number of the paginated result |
| `pageSize` | `integer` | No | Number of policy records returned per page |
| `total` | `integer` | No | Total number of policy records available |
| `hasNext` | `boolean` | No | Indicates whether there are more pages of results available |
