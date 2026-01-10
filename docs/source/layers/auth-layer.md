# Authentication & Authorization Layer

## Overview

The **Authentication & Authorization Layer** provides shared helper functions
used by AWS Lambda handlers to enforce **role-based access control (RBAC)**
based on **Amazon Cognito User Pool claims**.

This layer is designed to work with **API Gateway Lambda proxy integration**
where Cognito authorizer claims are injected into the Lambda event.

---

## Module Contents

```python
    if not require_admin(event):
        return error(403, "Admin access required")
    if not require_agent(event):
        return error(403, "Agent access required")
