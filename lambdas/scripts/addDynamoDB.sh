aws dynamodb create-table \
  --table-name InsuranceSystem \
  --billing-mode PAY_PER_REQUEST \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
    AttributeName=GSI1PK,AttributeType=S \
    AttributeName=GSI1SK,AttributeType=S \
    AttributeName=GSI2PK,AttributeType=S \
    AttributeName=GSI2SK,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --global-secondary-indexes '[
    {
      "IndexName": "GSI1_UserPolicies",
      "KeySchema": [
        { "AttributeName": "GSI1PK", "KeyType": "HASH" },
        { "AttributeName": "GSI1SK", "KeyType": "RANGE" }
      ],
      "Projection": { "ProjectionType": "ALL" }
    },
    {
      "IndexName": "GSI2_PolicyClaims",
      "KeySchema": [
        { "AttributeName": "GSI2PK", "KeyType": "HASH" },
        { "AttributeName": "GSI2SK", "KeyType": "RANGE" }
      ],
      "Projection": { "ProjectionType": "ALL" }
    }
  ]'

aws dynamodb update-time-to-live \
  --table-name InsuranceSystem \
  --time-to-live-specification "Enabled=true,AttributeName=expiresAt"


# export from my dynamo db table 
aws dynamodb scan \
  --table-name InsuranceSystem \
  --output json > table_backup.json

# Convert to BatchWrite format
jq '{InsuranceSystem: [.Items[] | {PutRequest: {Item: .}}]}' table_backup.json > batch.json

# download batch.json file via console client (action button)

