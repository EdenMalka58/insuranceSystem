Create API Gateway
-----------------
in file InsuranceSystemAPI-openapi.json replace the lambda arn from 263015886377 to the new arn.

1. API Gateway → Create API
2. Choose REST API
3. Select Import
4. Upload InsuranceSystemAPI-openapi.json
5. Choose Ignore warnings
6. Create

echo "Create API Gateway (HTTP API – not REST)"
API_ID=$(aws apigatewayv2 create-api \
  --name InsuranceSystemAPI \
  --protocol-type HTTP \
  --cors-configuration '{
    "AllowOrigins":["*"],
    "AllowMethods":["GET","POST","PUT","DELETE","OPTIONS"],
    "AllowHeaders":["*"],
    "AllowCredentials": false
  }' \
  --query ApiId \
  --output text)

echo "API ID: $API_ID"

echo "Create Lambda integration"
INTEGRATION_ID=$(aws apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type AWS_PROXY \
  --integration-uri arn:aws:lambda:us-east-1:$ACCOUNT_ID:function:getPolicies \
  --payload-format-version 2.0 \
  --query IntegrationId \
  --output text)

echo "Create routes"
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "GET /policies" \
  --target integrations/$INTEGRATION_ID


echo "Create stage (auto-deploy)"
aws apigatewayv2 create-stage \
  --api-id $API_ID \
  --stage-name prod \
  --auto-deploy

echo "Add Lambda permission"
aws lambda add-permission \
  --function-name getPolicies \
  --statement-id apigw-policies \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn arn:aws:execute-api:us-east-1:$ACCOUNT_ID:$API_ID/*/*/policies

echo "Cognito Authorizer"
aws apigatewayv2 create-authorizer \
  --api-id $API_ID \
  --name CognitoAuth \
  --authorizer-type JWT \
  --identity-source '$request.header.Authorization' \
  --jwt-configuration '{
    "Issuer":"https://cognito-idp.us-east-1.amazonaws.com/'"$USER_POOL_ID"'",
    "Audience":["'"$APP_CLIENT_ID"'"]
  }'
