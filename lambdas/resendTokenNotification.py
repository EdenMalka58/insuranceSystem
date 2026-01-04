import json
import boto3
import time
import os
from datetime import datetime
from uuid import uuid4
from botocore.exceptions import ClientError
from auth import require_agent
from response import ok, error


dynamo = boto3.resource("dynamodb")
sns = boto3.client('sns', region_name='us-east-1')
table = dynamo.Table("InsuranceSystem")

def get_or_create_email_topic(email):
    topic_name = f"claim-email-{email.replace('@','-').replace('.','-')}"

    # 1. Find or create topic
    topic_arn = None
    paginator = sns.get_paginator("list_topics")
    for page in paginator.paginate():
        for topic in page["Topics"]:
            if topic["TopicArn"].endswith(f":{topic_name}"):
                topic_arn = topic["TopicArn"]
                break
        if topic_arn:
            break

    if not topic_arn:
        response = sns.create_topic(Name=topic_name)
        topic_arn = response["TopicArn"]

    # 2. Check existing subscriptions (CRITICAL)
    subs = sns.list_subscriptions_by_topic(
        TopicArn=topic_arn
    )["Subscriptions"]

    for sub in subs:
        if sub.get("Endpoint") == email:
            return topic_arn  # already subscribed

    # 3. Subscribe ONLY if not exists
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol="email",
        Endpoint=email
    )

    return topic_arn

def send_claim_notification(claim_number, policy_number, landing_url, insured_name, insured_email, plate, vehicle):
    """Send claim notification via SNS"""

    topic_arn = get_or_create_email_topic(insured_email)

    subject = f"Claim {claim_number} - Report Damage Areas"
    
    message = f"""
Claim Created Successfully

Dear {insured_name},

Your insurance claim has been created with the following details:

Claim Number: {claim_number}
Policy Number: {policy_number}
Plate: {plate}
Vehicle: {vehicle}

Please visit this link to report the damage areas:
{landing_url}

Note: This link will expire in 5 hours.

If you have any questions, please contact our support team.

Best regards,
Insurance Team
    """
    
    try:
        response = sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message,
            MessageAttributes={
                'claimNumber': {
                    'DataType': 'String',
                    'StringValue': claim_number
                },
                'policyNumber': {
                    'DataType': 'String',
                    'StringValue': policy_number
                }
            }
        )
        return True, response['MessageId'], topic_arn
    except ClientError as e:
        return False, str(e), None


def handler(event, context):
    if not require_agent(event):
        return error(403, "Agent access required")

    try:
        body = json.loads(event.get("body", "{}"))

        required_fields = [
            "policyNumber",
            "claimNumber"
        ]

        missing = [f for f in required_fields if f not in body]
        if missing:
            return error(400, f"Missing fields: {missing}")
        
        claim_number = body.get("claimNumber")
        policy_number = body.get("policyNumber")        

        # Verify policy exists
        policy_key = {
            "PK": f"POLICY#{policy_number}",
            "SK": "METADATA"
        }
        
        try:
            policy_response = table.get_item(Key=policy_key)
            if "Item" not in policy_response:
                return error(404, "Policy not found")
        except Exception as e:
            return error(500, f"Error verifying policy: {str(e)}")
                
        claim_key = {
            "PK": f"POLICY#{policy_number}",
            "SK": f"CLAIM#{claim_number}"
        }

        claim_resp = table.get_item(Key=claim_key)
        if "Item" not in claim_resp:
            return error(404, "Claim not found")        

        # Create token record to store information for driver's addDamages process  
        token = str(uuid4())
        now = int(time.time())
        expires_at = now + 3600 * 5  # five hours
        # Link to landing page
        landing_url = (
            "https://insurance-claim-damage-pages.s3.us-east-1.amazonaws.com/pages/damages.html"
            f"?token={token}"
        )
        # Create token
        table.put_item(Item={
            "PK": f"TOKEN#{token}",
            "SK": f"CLAIM#{claim_number}",
            "entityType": "CLAIM_ACCESS_TOKEN",
            # policyNumber and claimNumber are mandatory in token record for quick data lookup
            "policyNumber": policy_number,
            "claimNumber": claim_number,
            "expiresAt": expires_at, # TTL was configured under this field
            "used": False
        })
        policy = policy_response.get("Item", {})
        insured = policy.get("insured", {})
        insured_email = insured.get("email")
        insured_name = insured.get("name")
        vehicle = policy.get("vehicle", {})
        vehicle_model = vehicle.get("model")
        vehicle_year = vehicle.get("year")
        vehicle_plate = vehicle.get("plateNumber")        
         # Send email

        # Send notification via SNS
        if insured_email:
            notification_sent, notification_result, topic_arn = send_claim_notification(
                claim_number=claim_number,
                policy_number=policy_number,
                landing_url=landing_url,
                insured_name=insured_name,
                insured_email=insured_email,
                plate=vehicle_plate,
                vehicle=f"{vehicle_model} {vehicle_year}"                
            )
        
        if not notification_sent:
            print(f"Failed to send email: {notification_result}")

        return ok({
            "message": "Notification sent successfully",
            "claimNumber": claim_number,
            "policyNumber": policy_number,
            "emailSent": notification_sent,
        })

    except Exception as e:
        return error(500, 'Internal sever error')   
    
    # request
    # {"body": "{\"policyNumber\":\"POL987654\",\"claimNumber\":\"888777667\"}"}