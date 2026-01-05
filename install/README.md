

1.  ## Create role (LabRole) 
    Check if LabRole role exists
    If not, do the following:
    Open IAM Console - IAM → Roles → LabRole
    Add inline policy - Click Add permissions → Create inline policy
    Open LabRole.json
    replace ACCOUNT_ID to your account id.
    Policy JSON (copy-paste as it is)
    4.Save policy - name it InsuranceSystemDynamoAccess

2. ## Run the installation batch process
    Open CloudShell terminal and upload install.zip and extract files and run the installation process by this commands:
    unzip install.zip -d .
    sudo yum install dos2unix -y
    dos2unix install.sh
    chmod +x install.sh
    ./install.sh

3. ## Associate application in the Managed Login menu:
    Go to Amazon Cognito → User pools → InsuranceSystemUserPool → App clients → App client: InsuranceSystemSPAClient
    On the left menu panel under Branding, click "Managed login New"
    In Style box click "Create style"
    Choose an app client "InsuranceSystemSPAClient" and click "Create".

4. ## Enter the application
    Go to Amazon S3 → Buckets → insurance-claim-damage-pages
    Click index.html and click open
    These are the users for testing
    sahar81@gmail.com/38388112Sm$ - for agent
    edenony@gmail.com/38388112Sm$ - for admin
    ## WebSite https://insurance-claim-damage-pages-v05.s3.us-east-1.amazonaws.com/index.html
    ## Swagger https://insurance-claim-damage-pages-v05.s3.us-east-1.amazonaws.com/swagger/index.html
## -------------------------------------------------------------------------------------------------------

## NOT IN USE !!!


3. Create an API Gateway (import)
    in file InsuranceSystemAPI-openapi.json replace the lambda account id from 263015886377 to the account id number.
    API Gateway → Create an API
    Choose REST API
    Select Import
    Upload InsuranceSystemAPI-openapi.json
    Choose Ignore warnings and API endpoint type = Regional (default)
    Click create

4. Fix api authorizer:
    Go to API Gateway → APIs → InsuranceSystemAPI → Authorizers
    Choose InsuranceSystemCognitoAuthorizer and click Edit
    Change the cognito user pool to "InsuranceSystemUserPool" and click Save changes

5. Allow API Gateway to invoke ALL Lambdas
    Set the new API_ID of the API Gateway you created (as shown in the left top of the resources page)
    Run the following command in the CloudShell terminal:
    ----------------------------------------------
    REGION="us-east-1"
    ACCOUNT_ID="263015886377" #MUST BE REPLACED !!!    
    API_ID="06qgyhpfhb" #MUST BE REPLACED !!!    
    echo "Set lambdas functions permission"
    for FUNC in addClaim addPolicy deletePolicy getPolicy getPolicies updateClaimStatus updatePolicy getAdminDashboard getAdminDashboardDrilldown getAdminStatistics getTokenData addDamageAreas importInsuranceData resendTokenNotification
    do
    aws lambda add-permission \
        --function-name $FUNC \
        --statement-id apigw-$FUNC \
        --action lambda:InvokeFunction \
        --principal apigateway.amazonaws.com \
        --source-arn arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*/*
    done
    ----------------------------------------------

6. Create prod stage:
    Go to API Gateway → APIs → Resources - InsuranceSystemAPIthe
    Go to the root resource ('/')
    Refresh the browser and click the Deploy API button
    Choose new stage
    Name the stage "prod" and click Deploy

7. Associate application in the Managed Login menu:
    Go to Amazon Cognito → User pools → InsuranceSystemUserPool → App clients → App client: InsuranceSystemSPAClient
    On the left menu panel under Branding, click "Managed login New"
    In Style box click "Create style"
    Choose an app client "InsuranceSystemSPAClient" and click "Create".


8. update the config.js file in website\
    Go to Amazon S3 → Buckets → insurance-claim-damage-pages
    Click the config.js file and download the file
    Edit the file:
    Go to Amazon Cognito → User pools → InsuranceSystemUserPool → App clients → App client: InsuranceSystemSPAClient
    In Quick setup guide choose JavaScript and replace the following fields:
    ----------------------------------------------
    const config = {
    cognitoDomain: 'replace with the new cognitoDomain', 
    clientId: 'replace with the new clientId', 
    redirectUri: 'replace with the new logoutUri', 
    scope: 'email openid phone',
    responseType: 'code',
    baseAPI: "Go to API Gateway → APIs → InsuranceSystemAPI → Stages and replace with the Invoke URL of prod",
    };
    ----------------------------------------------
    upload config.js again to s3 bucket (replace the existing one with the updated one)

9. Enter the application
    Go to Amazon S3 → Buckets → insurance-claim-damage-pages
    Click index.html and click open
    These are the users for testing
    sahar81@gmail.com/38388112Sm$ - for agent
    edenony@gmail.com/38388112Sm$ - for admin
    ## WebSite https://insurance-claim-damage-pages-v02.s3.us-east-1.amazonaws.com/index.html
    ## Swagger https://insurance-claim-damage-pages-v02.s3.us-east-1.amazonaws.com/swagger/index.html
