---
tocdepth: 0
---

# `deletePolicy` Lambda

## Overview
Deletes an existing insurance policy record permanently from the system.

## Permissions
User must belong to the **`agent`** Cognito group.

## API Mapping
- **Path:** `/policies/{policyNumber}`
- **Method:** `DELETE`

---
## Python Run Example

```python
import json
from deletePolicy import handler

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
## Response Object `DeletePolicyResponse`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `message` | `string` | No | Confirmation message indicating that the policy was successfully deleted |
