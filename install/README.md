## Create role (LabRole)

1. Open IAM Console - IAM → Roles → LabRole
2. Add inline policy - Click Add permissions → Create inline policy
3. Policy JSON (copy-paste exactly)
   {
   "Version": "2012-10-17",
   "Statement": [
   {
   "Sid": "DynamoDBAccess",
   "Effect": "Allow",
   "Action": [
   "dynamodb:PutItem",
   "dynamodb:GetItem",
   "dynamodb:UpdateItem",
   "dynamodb:DeleteItem",
   "dynamodb:BatchWriteItem",
   "dynamodb:Query",
   "dynamodb:Scan"
   ],
   "Resource": [
   "arn:aws:dynamodb:us-east-1:263015886377:table/InsuranceSystem",
   "arn:aws:dynamodb:us-east-1:263015886377:table/InsuranceSystem/index/*"
   ]
   },
   {
   "Sid": "SNSAccess",
   "Effect": "Allow",
   "Action": [
   "sns:ListTopics",
   "sns:CreateTopic",
   "sns:ListSubscriptionsByTopic",
   "sns:Subscribe",
   "sns:Publish",
   "sns:DeleteTopic"
   ],
   "Resource": "\*"
   }
   ]
   }
   4.Save policy - name it InsuranceSystemDynamoAccess

upload install.zip
unzip install.zip -d .
chmod +x install.sh
./install.sh

## Create API Gateway

in file InsuranceSystemAPI-openapi.json replace the lambda arn from 263015886377 to the new arn number.

1. API Gateway → Create API
2. Choose REST API
3. Select Import
4. Upload InsuranceSystemAPI-openapi.json
5. Choose Ignore warnings
6. Create
7. Enable CORS
8. create prod stage

9. change cognito domain to Managed login - Recommended
10. fix api authorizer
11. update the config.js file in website\
     api getaway invoke url: baseAPI
    cognitoDomain: cognitoDomain
    cognito clientId : clientId
    upload config.js to s3 bucket
12. Enable Static Website Hosting
    In the S3 console:
    Go to your bucket.
    Properties → Static website hosting.
    Enable it, set index.html as the index document.
13. Block public access (bucket settings)
    edit
    unchecked Block all public access
14. Make the files public
    go to bucket policy
    Click Edit
    replace Resource to bucket ARN (copy ARN button)
    {
    "Version": "2012-10-17",
    "Statement": [
    {
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    }
    ]
    }
15. Allow API Gateway to invoke ALL Lambdas
    API_ID=4r73rvjc7k
    for FUNC in addClaim addPolicy deletePolicy getPolicy getPolicies updateClaimStatus updatePolicy getAdminDashboard getAdminDashboardDrilldown getAdminStatistics getTokenData addDamageAreas importInsuranceData
    do
    echo "Granting API Gateway permission to $FUNC"

aws lambda add-permission \
 --function-name $FUNC \
    --statement-id api-gw-$FUNC \
 --action lambda:InvokeFunction \
 --principal apigateway.amazonaws.com \
 --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/_/_/\*" \
 --region $REGION || echo "Permission already exists"
done
