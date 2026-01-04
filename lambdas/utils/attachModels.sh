set -e
API_ID=azy4fomrz8

ENDPOINTS=(
  "/policies|GET||GetPoliciesResponse"
  "/policies|POST|AddPolicyRequest|AddPolicyResponse"
  "/policies/{policyNumber}|GET||GetPolicyResponse"
  "/policies/{policyNumber}|PUT|UpdatePolicyRequest|UpdatePolicyResponse"
  "/policies/{policyNumber}|DELETE||DeletePolicyResponse"
  "/claims|POST|AddClaimRequest|AddClaimResponse"
  "/claims/{claimNumber}|PUT|UpdateClaimRequest|UpdateClaimResponse"
  "/claims/{claimNumber}/resend|POST|ResendTokenNotificationRequest|ResendTokenNotificationResponse"
  "/damages/{tokenId}|GET|GetTokenDataRequest|GetTokenDataResponse"
  "/damages/{tokenId}|POST|AddClaimDamagesRequest|AddClaimDamagesResponse"
  "/dashboard|GET||GetAdminDashboardResponse"
  "/dashboard/drilldown|GET||GetAdminDashboardResponse"
  "/statistics|GET||GetAdminStatisticsResponse"
)


for item in "${ENDPOINTS[@]}"; do
  IFS="|" read -r RESOURCE_PATH HTTP_METHOD REQUEST_MODEL RESPONSE_MODEL <<< "$item"

  echo "Processing $HTTP_METHOD $RESOURCE_PATH"

  # Get resource ID
  RESOURCE_ID=$(aws apigateway get-resources \
    --rest-api-id $"$API_ID" \
    --query "items[?path=='$RESOURCE_PATH'].id" \
    --output text)

  if [ -z "$RESOURCE_ID" ]; then
    echo "Resource not found for path $RESOURCE_PATH"
    continue
  fi
  
  # Attach request model if defined
  if [ -n "$REQUEST_MODEL" ]; then
    echo "Setting request model: $REQUEST_MODEL"
    aws apigateway update-method \
      --rest-api-id $"$API_ID" \
      --resource-id $RESOURCE_ID \
      --http-method $HTTP_METHOD \
      --patch-operations op=add,path=/requestModels/application~1json,value=$REQUEST_MODEL
  fi

  # Attach method responses
  echo "Setting success response model: $RESPONSE_MODEL"
  aws apigateway put-method-response \
    --rest-api-id $"$API_ID" \
    --resource-id $RESOURCE_ID \
    --http-method $HTTP_METHOD \
    --status-code 200 \
    --response-models application/json=$RESPONSE_MODEL

  for code in 400 403 500; do
    echo "Setting error response model for $code"
    aws apigateway put-method-response \
      --rest-api-id $"$API_ID" \
      --resource-id $RESOURCE_ID \
      --http-method $HTTP_METHOD \
      --status-code $code \
      --response-models application/json=$ERROR_MODEL
  done

done

echo "Done attaching models to API Gateway methods"






for item in "${ENDPOINTS[@]}"; do
  IFS="|" read -r RESOURCE_PATH HTTP_METHOD REQUEST_MODEL RESPONSE_MODEL <<< "$item"

  echo "Processing $HTTP_METHOD $RESOURCE_PATH"

  # Get resource ID
  RESOURCE_ID=$(aws apigateway get-resources \
    --rest-api-id $"$API_ID" \
    --query "items[?path=='$RESOURCE_PATH'].id" \
    --output text)

  if [ -z "$RESOURCE_ID" ]; then
    echo "Resource not found for path $RESOURCE_PATH"
    continue
  fi

  for code in 400 403 500; do
    echo "Setting error response model for $code"
    aws apigateway put-method-response \
      --rest-api-id $"$API_ID" \
      --resource-id $RESOURCE_ID \
      --http-method $HTTP_METHOD \
      --status-code $code \
      --response-models application/json=Error
  done

done
