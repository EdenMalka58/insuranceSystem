#!/bin/bash

set -e

# =========================
# CONFIG
# =========================
ROLE_NAME="LabRole"
INLINE_POLICY_NAME="InsuranceSystemDynamoAccess"
TRUST_POLICY_FILE="trust-policy-lambda.json"
INLINE_POLICY_FILE="LabRole.json"

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "Using AWS Account ID: $ACCOUNT_ID"

# =========================
# 1. Create trust policy for Lambda
# =========================
cat > $TRUST_POLICY_FILE <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# =========================
# 2. Create IAM Role
# =========================
aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document file://$TRUST_POLICY_FILE

echo "Role $ROLE_NAME created"

# =========================
# 3. Attach AWSLambdaBasicExecutionRole
# =========================
aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

echo "Attached AWSLambdaBasicExecutionRole"

# =========================
# 4. Replace ACCOUNT_ID in LabRole.json
# =========================
sed "s/ACCOUNT_ID/$ACCOUNT_ID/g" $INLINE_POLICY_FILE > /tmp/${INLINE_POLICY_FILE}.tmp

# =========================
# 5. Create inline policy
# =========================
aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name $INLINE_POLICY_NAME \
  --policy-document file:///tmp/${INLINE_POLICY_FILE}.tmp

echo "Inline policy $INLINE_POLICY_NAME attached"

# =========================
# 6. Cleanup
# =========================
rm -f $TRUST_POLICY_FILE /tmp/${INLINE_POLICY_FILE}.tmp

echo "LabRole setup completed successfully"
