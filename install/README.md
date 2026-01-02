## Create role (LabRole)

Check if LabRole role exists
If not, do the following:
1. Open IAM Console - IAM → Roles → LabRole
2. Add inline policy - Click Add permissions → Create inline policy
3. Policy JSON (copy-paste as it is)
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

Create Cognito
-----------------
Go to Cognito → User pools
Click Create user pool
Select: "Single-page application (SPA)"
Name your application: "InsuranceSystemUserPool"
Options for sign-in identifiers: Email
Required attributes for sign-up: Email, Nickname
Click Create user directory
Rename the User pool as "InsuranceSystemUserPool"
Go to Amazon Cognito → User pools → InsuranceSystemUserPool → App clients → App client: InsuranceSystemSPAClient
Go to Login pages and in Managed login pages configuration click Edit
Add the following and change the version (increment by one):
Allowed callback URLs
https://insurance-claim-damage-pages-v2.s3.us-east-1.amazonaws.com/index.html
Allowed sign-out URLs
https://insurance-claim-damage-pages-v2.s3.us-east-1.amazonaws.com/index.html

Go to groups
Create these groups: admin, agent
Add 2 users with password : 
email: edenony@gmail.com, password: 38388112Sm$ 
email: sahar81@gmail.com, password: 38388112Sm$
set groups to users: edenony@gmail.com as admin, sahar81@gmail.com as agent

Open CloudShell terminal
upload install.zip
unzip install.zip -d .
sudo yum install dos2unix -y
dos2unix install.sh
chmod +x install.sh
./install.sh


in file InsuranceSystemAPI-openapi.json replace the lambda account id from 263015886377 to the account id number.

1. API Gateway → Create an API
2. Choose REST API
3. Select Import
4. Upload InsuranceSystemAPI-openapi.json
5. Choose Ignore warnings and API endpoint type = Regional (default)
6. Create
7. fix api authorizer:
    Go to API Gateway → APIs → InsuranceSystemAPI → Authorizers
    Choose InsuranceSystemCognitoAuthorizer and press Edit
    Change the cognito user pool to "InsuranceSystemUserPool" and press Save changes

8. Allow API Gateway to invoke ALL Lambdas
    Set the new API_ID of the API Gateway you created (as shown in the left top of the resources page)
    Run the following command in the CloudShell terminal:
    ----------------------------------------------
    API_ID=c7y3mgkb35
    echo "Set lambdas functions permission"
    for FUNC in addClaim addPolicy deletePolicy getPolicy getPolicies updateClaimStatus updatePolicy getAdminDashboard getAdminDashboardDrilldown getAdminStatistics getTokenData addDamageAreas importInsuranceData
    do
    aws lambda add-permission \
        --function-name $FUNC \
        --statement-id apigw-$FUNC \
        --action lambda:InvokeFunction \
        --principal apigateway.amazonaws.com \
        --source-arn arn:aws:execute-api:us-east-1:263015886377:$API_ID/*/*/*
    done
    ----------------------------------------------

9. Create prod stage:
    Go to API Gateway → APIs → Resources - InsuranceSystemAPIthe
    Go to the root resource ('/')
    Refresh the browser and click the Deploy API button
    Choose new stage
    Name the stage "prod" and press Deploy

<!-- 10. change cognito domain to "Managed login - Recommended":
    Go to Amazon Cognito → User pools → InsuranceSystemUserPool → App clients → App client: InsuranceSystemSPAClient
    On the left menu panel under Branding, click Domain
    In Cognito domain press Edit (in the right top of the page)
    Choose Managed login - Recommended and click Save changes -->
10. Associate application in the Managed Login menu:
    Go to Amazon Cognito → User pools → InsuranceSystemUserPool → App clients → App client: InsuranceSystemSPAClient
    On the left menu panel under Branding, click "Managed login New"
    In Style box click "Create style"
    Choose an app client "InsuranceSystemSPAClient" and click "Create".


11. update the config.js file in website\
    Go to Amazon S3 → Buckets → insurance-claim-damage-pages
    Click the config.js file and download the file
    Edit the file:
    Go to Amazon Cognito → User pools → InsuranceSystemUserPool → App clients → App client: InsuranceSystemSPAClient
    In Quick setup guide choose JavaScript and replace the following fields:
    
    const config = {
    cognitoDomain: 'replace with the new cognitoDomain', 
    clientId: 'replace with the new clientId', 
    redirectUri: 'replace with the new logoutUri', 
    scope: 'email openid phone',
    responseType: 'code',
    baseAPI: "Go to API Gateway → APIs → InsuranceSystemAPI → Stages and replace with the Invoke URL of prod",
    };

    upload config.js again to s3 bucket (replace the existing one with the updated one)