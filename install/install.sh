REGION=us-east-1
ACCOUNT_ID=263015886377 #MUST BE REPLACED !!!
USER_POOL_NAME="InsuranceSystemUserPool"
APP_CLIENT_NAME="InsuranceSystemSPAClient"
AUTHORIZER_NAME="InsuranceSystemCognitoAuthorizer"
BUCKET_NAME=insurance-claim-damage-pages-v3 #MUST BE REPLACED or add version !!!
CALLBACK_URLS="https://insurance-claim-damage-pages-v3.s3.us-east-1.amazonaws.com/index.html"
LOGOUT_URLS="https://insurance-claim-damage-pages-v3.s3.us-east-1.amazonaws.com/index.html"
ADMIN_EMAIL="edenony@gmail.com"
AGENT_EMAIL="sahar81@gmail.com"
PASSWORD="38388112Sm$"
DOMAIN_PREFIX=insurance-claim-damage

echo "Create Cognito User Pool (Email sign-in, required attributes)"
USER_POOL_ID=$(aws cognito-idp create-user-pool \
  --region $REGION \
  --pool-name "$USER_POOL_NAME" \
  --username-attributes email \
  --auto-verified-attributes email \
  --schema \
      Name=email,AttributeDataType=String,Required=true \
      Name=nickname,AttributeDataType=String,Required=true \
  --policies '{
    "PasswordPolicy": {
      "MinimumLength": 8,
      "RequireUppercase": true,
      "RequireLowercase": true,
      "RequireNumbers": true,
      "RequireSymbols": true
    }
  }' \
  --query "UserPool.Id" \
  --output text)

echo "User Pool ID: $USER_POOL_ID"

echo "Create App Client (SPA / public client)"
APP_CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --region $REGION \
  --user-pool-id $USER_POOL_ID \
  --client-name "$APP_CLIENT_NAME" \
    --explicit-auth-flows \
      ALLOW_USER_PASSWORD_AUTH \
      ALLOW_REFRESH_TOKEN_AUTH \
      ALLOW_USER_SRP_AUTH \
  --supported-identity-providers COGNITO \
  --callback-urls "$CALLBACK_URLS" \
  --logout-urls "$LOGOUT_URLS" \
  --allowed-o-auth-flows code \
  --allowed-o-auth-scopes email openid profile \
  --allowed-o-auth-flows-user-pool-client \
  --prevent-user-existence-errors ENABLED \
  --query "UserPoolClient.ClientId" \
  --output text)

echo "App Client ID: $APP_CLIENT_ID"

echo "Create Cognito User Pool Domain"
aws cognito-idp create-user-pool-domain \
    --domain $DOMAIN_PREFIX \
    --user-pool-id $USER_POOL_ID \
    --region $REGION

echo "Create User Pool Groups"
aws cognito-idp create-group \
  --region $REGION \
  --user-pool-id $USER_POOL_ID \
  --group-name admin

aws cognito-idp create-group \
  --region $REGION \
  --user-pool-id $USER_POOL_ID \
  --group-name agent

echo "Create Users (with email + nickname)"
aws cognito-idp admin-create-user \
  --region $REGION \
  --user-pool-id $USER_POOL_ID \
  --username $ADMIN_EMAIL \
  --user-attributes \
      Name=email,Value=$ADMIN_EMAIL \
      Name=email_verified,Value=true \
      Name=nickname,Value=eden \
  --message-action SUPPRESS

aws cognito-idp admin-create-user \
  --region $REGION \
  --user-pool-id $USER_POOL_ID \
  --username $AGENT_EMAIL \
  --user-attributes \
      Name=email,Value=$AGENT_EMAIL \
      Name=email_verified,Value=true \
      Name=nickname,Value=sahar \
  --message-action SUPPRESS

echo "Set Permanent Passwords"
aws cognito-idp admin-set-user-password \
  --region $REGION \
  --user-pool-id $USER_POOL_ID \
  --username $ADMIN_EMAIL \
  --password "$PASSWORD" \
  --permanent

aws cognito-idp admin-set-user-password \
  --region $REGION \
  --user-pool-id $USER_POOL_ID \
  --username $AGENT_EMAIL \
  --password "$PASSWORD" \
  --permanent

echo "Assign Users to Groups"
aws cognito-idp admin-add-user-to-group \
  --region $REGION \
  --user-pool-id $USER_POOL_ID \
  --username $ADMIN_EMAIL \
  --group-name admin

aws cognito-idp admin-add-user-to-group \
  --region $REGION \
  --user-pool-id $USER_POOL_ID \
  --username $AGENT_EMAIL \
  --group-name agent


echo "Add lambdas layers"
aws lambda publish-layer-version \
    --layer-name auth-layer \
    --zip-file fileb:///home/cloudshell-user/auth-layer.zip \
    --compatible-runtimes python3.14

aws lambda publish-layer-version \
    --layer-name response-layer \
    --zip-file fileb:///home/cloudshell-user/response-layer.zip \
    --compatible-runtimes python3.14

echo "Add lambdas functions"
for FUNC in addClaim addPolicy deletePolicy getPolicy getPolicies updateClaimStatus updatePolicy getAdminDashboard getAdminDashboardDrilldown getAdminStatistics getTokenData addDamageAreas importInsuranceData
do
  echo "Creating $FUNC ..."
  aws lambda create-function \
    --function-name $FUNC \
    --runtime python3.14 \
    --role arn:aws:iam::"$ACCOUNT_ID":role/LabRole \
    --handler $FUNC.handler \
    --zip-file fileb:///home/cloudshell-user/$FUNC.zip
done

echo "Set lambdas functions layers"
for FUNC in addClaim addPolicy deletePolicy getPolicy getPolicies updateClaimStatus updatePolicy getAdminDashboard getAdminDashboardDrilldown getAdminStatistics getTokenData addDamageAreas importInsuranceData
do
  echo "Adding layers to $FUNC ..."
  aws lambda update-function-configuration \
    --function-name $FUNC \
    --layers arn:aws:lambda:us-east-1:"$ACCOUNT_ID":layer:auth-layer:1 arn:aws:lambda:us-east-1:"$ACCOUNT_ID":layer:response-layer:1
done

echo "Create Dynamo DB database"
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

echo "Create Dynamo DB database is in process..."
sleep 10

aws dynamodb update-time-to-live \
  --table-name InsuranceSystem \
  --time-to-live-specification "Enabled=true,AttributeName=expiresAt"

sleep 5

echo "Import records to database..."
aws lambda invoke \
  --function-name importInsuranceData \
  --cli-binary-format raw-in-base64-out \
  --payload fileb:///home/cloudshell-user/policy.json \
  response.json

echo "Create S3 bucket"
aws s3api create-bucket \
  --bucket $BUCKET_NAME \
  --region us-east-1

echo "Extract website.zip and Upload into S3"
unzip website.zip -d website
aws s3 sync website/ s3://$BUCKET_NAME/

echo "Insurance System setup completed."

  