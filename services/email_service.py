# email_service.py
import os
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any


# -----------------------------
# Environment Variables
# -----------------------------
SES_REGION = os.getenv("SES_REGION")
SES_SENDER = os.getenv("SES_SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

if not SES_SENDER:
    raise ValueError("Missing required environment variable: SES_SENDER_EMAIL")

if not RECIPIENT_EMAIL:
    raise ValueError("Missing required environment variable: RECIPIENT_EMAIL")


# -----------------------------
# SES Client
# -----------------------------
ses_client = boto3.client("ses", region_name=SES_REGION)


# -----------------------------
# Email Sending Function
# -----------------------------
def send_email(subject: str, body: str) -> Dict[str, Any]:
    """
    Sends an email using AWS SES.

    Rules:
    - Always sends FROM the verified SES_SENDER_EMAIL.
    - Always sends TO RECIPIENT_EMAIL (your personal email).
    - Same behavior in local and production environments.

    Returns:
        { "status": "success", "message_id": "..." }
        or
        { "status": "error", "error": "message" }
    """

    email_request = {
        "Source": SES_SENDER,
        "Destination": {"ToAddresses": [RECIPIENT_EMAIL]},
        "Message": {
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}},
        },
    }

    try:
        response = ses_client.send_email(**email_request)
        return {
            "status": "success",
            "message_id": response.get("MessageId")
        }

    except ClientError as e:
        error_message = e.response["Error"]["Message"]
        return {
            "status": "error",
            "error": error_message
        }