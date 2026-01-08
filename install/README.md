

1.  ## Create role (LabRole) 
    Check if LabRole role exists
    If not, do the following:
    Open IAM Console - IAM → Roles → LabRole
    Add inline policy - Click Add permissions → Create inline policy
    Open LabRole.json
    IMPORTANT! replace ACCOUNT_ID to your account id.
    Policy JSON (copy-paste as it is)
    4.Save policy - name it InsuranceSystemDynamoAccess

2. ## Run the installation batch process
    Open CloudShell terminal and upload install.zip and extract files and run the installation process using these commands:
    unzip install.zip -d .
    IMPORTANT! replace the ACCOUNT_ID in install.sh to your account id
    sudo yum install dos2unix -y
    dos2unix install.sh
    chmod +x install.sh
    ./install.sh

3. ## Associate application in the Managed Login menu:
    Go to Amazon Cognito → User pools → InsuranceSystemUserPool → App clients → App client: InsuranceSystemSPAClient
    On the left menu panel under Branding, click "Managed login New"
    In the Style box click "Create style"
    Choose an app client named "InsuranceSystemSPAClient" and click "Create".

4. ## Enter the application
    Go to Amazon S3 → Buckets → insurance-claim-damage-pages
    Click index.html and click open
    These are the users for testing
    sahar81@gmail.com/38388112Sm$ - for agent
    edenony@gmail.com/38388112Sm$ - for admin
    ## WebSite https://insurance-claim-damage-pages-v05.s3.us-east-1.amazonaws.com/index.html
    ## Swagger https://insurance-claim-damage-pages-v05.s3.us-east-1.amazonaws.com/swagger/index.html
## -------------------------------------------------------------------------------------------------------