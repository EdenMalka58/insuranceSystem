---
tocdepth: 0
---

# `resendTokenNotification` Lambda

## Overview
Resends a damage reporting access token notification for an existing claim.

## Permissions
User must belong to the **`agent`** Cognito group.

## API Mapping
- **Path:** `/claims/{claimNumber}/resend`
- **Method:** `POST`

---
## Python Run Example

```python
import json
from resendTokenNotification import handler

event = {
    "body": json.dumps({
    "policyNumber": "string",
    "claimNumber": "string"
})
}

response = handler(event, None)
print(response)
```

---
## Request Object `ResendTokenNotificationRequest`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `policyNumber` | `string` | Yes | Identifier of the policy associated with the claim |
| `claimNumber` | `string` | Yes | Identifier of the claim for which the notification is resent |

---
## Response Object `ResendTokenNotificationResponse`
| Field | Type | Required | Description |
|------|------|----------|-------------|
| `message` | `string` | No | Informational message indicating the result of the resend operation |
| `claimNumber` | `string` | No | Identifier of the claim for which the notification was resent |
| `policyNumber` | `string` | No | Policy number associated with the claim |
| `emailSent` | `boolean` | No | Indicates whether the notification email was successfully sent |

