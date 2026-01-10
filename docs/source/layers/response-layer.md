# Response Layer

## Overview

The **Response Layer** provides shared helper functions for building
API Gateway–compatible HTTP responses from AWS Lambda functions.

This layer standardizes:
- HTTP status codes
- CORS headers
- JSON serialization
- Error and success payload formats

It is designed for **Lambda proxy integration**.

---

## Module Contents

```python
error(status, message)
ok(body)
response(code, body)
decimal_default(obj)
