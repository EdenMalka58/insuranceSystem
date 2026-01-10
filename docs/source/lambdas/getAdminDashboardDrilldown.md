---
tocdepth: 0
---

# `getAdminDashboardDrilldown` Lambda

## Overview
Returns detailed drilldown data for administrative dashboard widgets, based on the selected drilldown type and parameters.

## Permissions
User must belong to the **`admin`** Cognito group.

## API Mapping
- **Path:** `/dashboard/drilldown`
- **Method:** `GET`

---
## Python Run Example

```python
import json
from getAdminDashboardDrilldown import handler

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
## Response Object `GetAdminDashboardDrilldownResponse`
_Response is array or complex structure._
