VERSION="v01"
REGION="us-east-1"
ACCOUNT_ID="263015886377" #MUST BE REPLACED !!!
USER_POOL_NAME="InsuranceSystemUserPool-$VERSION"
APP_CLIENT_NAME="InsuranceSystemSPAClient-$VERSION"
BUCKET_NAME="insurance-claim-damage-pages-$VERSION"
DOMAIN_PREFIX="insurance-claim-damage-$VERSION"
CALLBACK_URLS="https://insurance-claim-damage-pages-$VERSION.s3.us-east-1.amazonaws.com/index.html"
LOGOUT_URLS="https://insurance-claim-damage-pages-$VERSION.s3.us-east-1.amazonaws.com/index.html"
SWAGGER_URL="https://insurance-claim-damage-pages-$VERSION.s3.us-east-1.amazonaws.com/swagger/index.html"
ADMIN_EMAIL="insurance.system.manager@gmail.com"
AGENT_EMAIL="insurance.system.agent@gmail.com"
PASSWORD="1463Aa99$"
API_NAME="InsuranceSystemAPI"
COGNITO_USER_POOL_NAME="InsuranceSystemUserPool"
AUTHORIZER_NAME="InsuranceSystemCognitoAuthorizer"               
OPENAPI_FILE="api-getaway.json"
LAMBDA_FUNCTIONS=(
  addClaim addPolicy deletePolicy getPolicy getPolicies
  updateClaimStatus updatePolicy
  getAdminDashboard getAdminDashboardDrilldown
  getAdminStatistics getTokenData
  addDamageAreas importInsuranceData resendTokenNotification
)


echo "Create Cognito User Pool (Email sign-in, required attributes)"
USER_POOL_ID=$(aws cognito-idp create-user-pool \
  --region $REGION \
  --pool-name "$USER_POOL_NAME" \
  --username-attributes "email" \
  --auto-verified-attributes "email" \
  --deletion-protection "ACTIVE" \
  --user-pool-tier "ESSENTIALS" \
  --schema '{"Name":"email","Required":true}' '{"Name":"nickname","Required":true}' \
  --username-configuration '{"CaseSensitive":false}' \
  --admin-create-user-config '{"AllowAdminCreateUserOnly":false}' \
  --query "UserPool.Id" \
  --output text)

echo "User Pool ID: $USER_POOL_ID"

echo "Create App Client (SPA / public client)"
APP_CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --client-name "$APP_CLIENT_NAME" \
  --user-pool-id $USER_POOL_ID \
  --no-generate-secret \
  --explicit-auth-flows \
      'ALLOW_REFRESH_TOKEN_AUTH' \
      'ALLOW_USER_SRP_AUTH' \
      'ALLOW_USER_AUTH' \
  --auth-session-validity 15  \
  --refresh-token-validity 60  \
  --access-token-validity 60  \
  --id-token-validity 60  \
  --token-validity-units '{"RefreshToken":"days","AccessToken":"minutes","IdToken":"minutes"}'  \
  --prevent-user-existence-errors ENABLED \
  --allowed-o-auth-flows code \
  --allowed-o-auth-scopes 'openid' 'phone' 'email' \
  --allowed-o-auth-flows-user-pool-client \
  --supported-identity-providers 'COGNITO' \
  --callback-urls "$CALLBACK_URLS" \
  --logout-urls "$LOGOUT_URLS" \
  --query "UserPoolClient.ClientId" \
  --output text)

echo "App Client ID: $APP_CLIENT_ID"

echo "Create Cognito User Pool Domain"
aws cognito-idp create-user-pool-domain \
    --domain $DOMAIN_PREFIX \
    --user-pool-id $USER_POOL_ID \
    --region $REGION \
    --managed-login-version 2

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
    --zip-file fileb://auth-layer.zip \
    --compatible-runtimes python3.14

aws lambda publish-layer-version \
    --layer-name response-layer \
    --zip-file fileb://response-layer.zip \
    --compatible-runtimes python3.14

echo "Add lambdas functions"
for FUNC in "${LAMBDA_FUNCTIONS[@]}"; do
  echo "Creating $FUNC ..."
  aws lambda create-function \
    --function-name $FUNC \
    --runtime python3.14 \
    --role arn:aws:iam::"$ACCOUNT_ID":role/LabRole \
    --handler $FUNC.handler \
    --zip-file fileb://$FUNC.zip
done

echo "Set lambdas functions layers"
for FUNC in "${LAMBDA_FUNCTIONS[@]}"; do
  echo "Adding layers to $FUNC ..."
  aws lambda update-function-configuration \
    --function-name $FUNC \
    --layers arn:aws:lambda:us-east-1:"$ACCOUNT_ID":layer:auth-layer:1 arn:aws:lambda:us-east-1:"$ACCOUNT_ID":layer:response-layer:1
done

echo "Set addClaim lambda environment variables"

FUNCTION_NAME="addClaim"
DAMAGES_PAGE_PATH="pages/damages.html"

echo "Updating environment variables for Lambda: $FUNCTION_NAME"

aws lambda update-function-configuration \
  --function-name "$FUNCTION_NAME" \
  --environment "Variables={
    S3_BUCKET_NAME=$BUCKET_NAME,
    S3_OBJECT_PATH=$DAMAGES_PAGE_PATH
  }" \
  --output text > /dev/null

echo "Environment variables updated successfully"


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
  ]' \
  --output text > /dev/null

echo "Create Dynamo DB database is in process..."
aws dynamodb wait table-exists --table-name InsuranceSystem

aws dynamodb update-time-to-live \
  --table-name InsuranceSystem \
  --time-to-live-specification "Enabled=true,AttributeName=expiresAt"


echo "Import records to database..."
aws lambda invoke \
  --function-name importInsuranceData \
  --cli-binary-format raw-in-base64-out \
  --payload fileb://policy.json \
  response.json

echo "Create S3 bucket"
aws s3api create-bucket \
  --bucket $BUCKET_NAME \
  --region us-east-1

echo "Extract website.zip and Upload into S3"
unzip website.zip -d website
aws s3 sync website/ s3://$BUCKET_NAME/

aws s3 website s3://$BUCKET_NAME/ --index-document index.html --error-document index.html
aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration '{
        "BlockPublicAcls": false,
        "IgnorePublicAcls": false,
        "BlockPublicPolicy": false,
        "RestrictPublicBuckets": false
    }'
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicRead",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::'"$BUCKET_NAME"'/*"
  }]
}'

echo "Import API getaway file"
echo "Replacing Lambda Account and user poll ID in OpenAPI file..."
sed -i "s/ACCOUNT_ID/$ACCOUNT_ID/g" "$OPENAPI_FILE"
sed -i "s/USER_POOL_ID/$USER_POOL_ID/g" "$OPENAPI_FILE"

API_ID=$(aws apigateway import-rest-api \
  --region $REGION \
  --body fileb://$OPENAPI_FILE \
  --no-cli-pager \
  --no-fail-on-warnings \
  --query id \
  --output text)

echo "Created API Gateway with ID: $API_ID"

echo "Granting API Gateway invoke permissions..."
for FUNC in "${LAMBDA_FUNCTIONS[@]}"; do
  aws lambda add-permission \
    --function-name $FUNC \
    --statement-id apigw-$API_ID-$FUNC \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*/*
done

echo "Deploying prod stage..."
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod

CLIENT_ID=$(aws cognito-idp list-user-pool-clients \
  --user-pool-id $USER_POOL_ID \
  --query "UserPoolClients[0].ClientId" \
  --output text)

COGNITO_DOMAIN_FULL="https://${DOMAIN_PREFIX}.auth.us-east-1.amazoncognito.com"
INVOKE_URL="https://$API_ID.execute-api.$REGION.amazonaws.com/prod"

echo "Create config.js file"
cp config.js config.js.bak   # backup first

sed -i \
  -e "s|COGNITO_DOMAIN_FULL_PLACEHOLDER|$COGNITO_DOMAIN_FULL|g" \
  -e "s|CLIENT_ID_PLACEHOLDER|$CLIENT_ID|g" \
  -e "s|REDIRECT_URI_PLACEHOLDER|$CALLBACK_URLS|g" \
  -e "s|INVOKE_URL_PLACEHOLDER|$INVOKE_URL|g" \
  config.js

echo "Update configuration file to S3 bucket"
aws s3 cp config.js s3://$BUCKET_NAME/

echo "=========================================="
echo "Insurance System setup completed successfully."
echo "## WebSite URL: $CALLBACK_URLS"
echo "## Swagger URL: $SWAGGER_URL"
echo "## IMPORTANT: To set the default Managed login style, go to:"
echo "## AWS Console → Cognito → User Pools → $USER_POOL_NAME → App client: $APP_CLIENT_NAME → Managed login → Style → Create style."
echo "=========================================="