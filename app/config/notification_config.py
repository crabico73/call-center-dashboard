from typing import Dict, List
import os
from app.services.notification_service import NotificationConfig, NotificationType

def load_notification_config() -> NotificationConfig:
    """Load notification configuration from environment variables"""
    
    # Default notification preferences
    default_preferences = {
        NotificationType.LIVE_PERSON_REQUEST.value: ["email", "sms"],
        NotificationType.CONTRACT_SIGNED.value: ["email", "sms"],
        NotificationType.HIGH_TIER_CONTRACT_SIGNED.value: ["email", "sms"],  # Always notify both for high-tier
        NotificationType.AMENDMENT_SIGNED.value: ["email"]
    }
    
    # High-tier contract thresholds (monthly value in USD)
    high_tier_thresholds = {
        "Starter": 5000,      # Unusual high value for Starter
        "Professional": 7500,  # Unusual high value for Professional
        "Enterprise": 0,      # Always notify for Enterprise
        "Ultimate": 0         # Always notify for Ultimate
    }
    
    return NotificationConfig(
        email_address=os.getenv('NOTIFICATION_EMAIL'),
        phone_number=os.getenv('NOTIFICATION_PHONE'),
        twilio_account_sid=os.getenv('TWILIO_ACCOUNT_SID'),
        twilio_auth_token=os.getenv('TWILIO_AUTH_TOKEN'),
        twilio_from_number=os.getenv('TWILIO_FROM_NUMBER'),
        smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        smtp_username=os.getenv('SMTP_USERNAME'),
        smtp_password=os.getenv('SMTP_PASSWORD'),
        notification_preferences=default_preferences,
        high_tier_thresholds=high_tier_thresholds
    ) 