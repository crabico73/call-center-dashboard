from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import requests
from enum import Enum
from app.services.high_tier_analytics import HighTierAnalyticsService

class NotificationType(Enum):
    LIVE_PERSON_REQUEST = "live_person_request"
    CONTRACT_SIGNED = "contract_signed"
    HIGH_TIER_CONTRACT_SIGNED = "high_tier_contract_signed"
    AMENDMENT_SIGNED = "amendment_signed"

@dataclass
class NotificationConfig:
    email_address: str
    phone_number: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from_number: str
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    notification_preferences: Dict[str, List[str]]  # type -> ["email", "sms"]
    high_tier_thresholds: Dict[str, float]  # subscription_tier -> monthly_value

class NotificationService:
    def __init__(self, config: NotificationConfig, analytics_service: Optional[HighTierAnalyticsService] = None):
        self.config = config
        self.analytics_service = analytics_service
        self._validate_config()
        
    def _validate_config(self):
        """Validate configuration and credentials"""
        required_fields = [
            'email_address', 'phone_number', 'smtp_server', 
            'smtp_port', 'smtp_username', 'smtp_password'
        ]
        
        for field in required_fields:
            if not getattr(self.config, field):
                raise ValueError(f"Missing required configuration: {field}")

    def notify_live_person_request(self,
                                 prospect_info: Dict[str, Any],
                                 confidence_score: float,
                                 conversation_summary: str) -> bool:
        """
        Send notification for live person request with high conversion confidence
        
        Args:
            prospect_info: Dictionary containing prospect details
            confidence_score: AI's confidence score for conversion (0-1)
            conversation_summary: Summary of the conversation so far
        """
        if confidence_score < 0.7:  # Only notify for high-confidence prospects
            return False

        # Prepare notification content
        subject = f"Hot Lead Request: {prospect_info.get('company_name')} - {confidence_score*100:.0f}% Confidence"
        
        email_body = f"""
        Hot Lead Requesting Live Contact
        
        Company: {prospect_info.get('company_name')}
        Contact: {prospect_info.get('contact_name')}
        Industry: {prospect_info.get('industry')}
        Confidence Score: {confidence_score*100:.0f}%
        
        Estimated Deal Value: ${prospect_info.get('estimated_value', 0):,.2f}
        
        Conversation Summary:
        {conversation_summary}
        
        Contact Information:
        Email: {prospect_info.get('email')}
        Phone: {prospect_info.get('phone')}
        
        Best Time to Contact: {prospect_info.get('preferred_contact_time', 'Not specified')}
        """

        sms_body = (
            f"Hot Lead: {prospect_info.get('company_name')} "
            f"({confidence_score*100:.0f}% confidence) "
            f"requesting live contact. "
            f"Est. value: ${prospect_info.get('estimated_value', 0):,.0f}"
        )

        return self._send_notifications(
            NotificationType.LIVE_PERSON_REQUEST,
            subject,
            email_body,
            sms_body
        )

    def notify_contract_signed(self,
                             contract_details: Dict[str, Any],
                             customer_info: Dict[str, Any]) -> bool:
        """
        Send notification when a service contract is signed
        
        Args:
            contract_details: Dictionary containing contract information
            customer_info: Dictionary containing customer details
        """
        # Check if this is a high-tier contract
        subscription_tier = contract_details.get('subscription_tier')
        monthly_value = contract_details.get('value', {}).get('monthly', 0)
        is_high_tier = (
            subscription_tier in ['Enterprise', 'Ultimate'] or
            monthly_value >= self.config.high_tier_thresholds.get(subscription_tier, float('inf'))
        )
        
        if is_high_tier:
            # Track high-tier contract in analytics
            if self.analytics_service:
                self.analytics_service.track_contract_signed(contract_details, customer_info)
            return self._notify_high_tier_contract_signed(contract_details, customer_info)
        
        subject = f"Contract Signed: {customer_info.get('company_name')}"
        
        contract_value = contract_details.get('value', {})
        term_months = contract_details.get('terms', {}).get('initial_term_months', 0)
        
        email_body = f"""
        New Contract Signed!
        
        Customer Information:
        Company: {customer_info.get('company_name')}
        Industry: {customer_info.get('industry')}
        
        Contract Details:
        Type: {contract_details.get('subscription_tier')}
        Term: {term_months} months
        Monthly Value: ${contract_value.get('monthly', 0):,.2f}
        Total Contract Value: ${contract_value.get('total', 0):,.2f}
        
        Start Date: {contract_details.get('terms', {}).get('start_date')}
        
        Primary Contact:
        Name: {customer_info.get('contact_name')}
        Email: {customer_info.get('email')}
        Phone: {customer_info.get('phone')}
        """

        sms_body = (
            f"Contract Signed: {customer_info.get('company_name')} - "
            f"${contract_value.get('total', 0):,.0f} "
            f"({term_months} months)"
        )

        return self._send_notifications(
            NotificationType.CONTRACT_SIGNED,
            subject,
            email_body,
            sms_body
        )

    def _notify_high_tier_contract_signed(self,
                                        contract_details: Dict[str, Any],
                                        customer_info: Dict[str, Any]) -> bool:
        """Special notification for high-tier contract signings"""
        subject = f"🌟 HIGH-TIER CONTRACT SIGNED: {customer_info.get('company_name')} 🌟"
        
        contract_value = contract_details.get('value', {})
        term_months = contract_details.get('terms', {}).get('initial_term_months', 0)
        
        # Get analytics metrics if available
        analytics_metrics = None
        if self.analytics_service:
            analytics_metrics = self.analytics_service.get_current_metrics()
        
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1a237e, #0d47a1); color: white; padding: 20px; border-radius: 10px;">
                <h1 style="text-align: center; color: gold;">🎉 High-Tier Contract Signed! 🎉</h1>
                
                <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h2 style="color: #ffd700;">Customer Information</h2>
                    <p><strong>Company:</strong> {customer_info.get('company_name')}</p>
                    <p><strong>Industry:</strong> {customer_info.get('industry')}</p>
                </div>
                
                <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h2 style="color: #ffd700;">Contract Details</h2>
                    <p><strong>Type:</strong> {contract_details.get('subscription_tier')}</p>
                    <p><strong>Term:</strong> {term_months} months</p>
                    <p><strong>Monthly Value:</strong> <span style="color: #ffd700; font-size: 1.2em;">${contract_value.get('monthly', 0):,.2f}</span></p>
                    <p><strong>Total Contract Value:</strong> <span style="color: #ffd700; font-size: 1.4em;">${contract_value.get('total', 0):,.2f}</span></p>
                    <p><strong>Start Date:</strong> {contract_details.get('terms', {}).get('start_date')}</p>
                </div>
                
                <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h2 style="color: #ffd700;">Primary Contact</h2>
                    <p><strong>Name:</strong> {customer_info.get('contact_name')}</p>
                    <p><strong>Email:</strong> {customer_info.get('email')}</p>
                    <p><strong>Phone:</strong> {customer_info.get('phone')}</p>
                </div>
                
                {self._generate_analytics_section(analytics_metrics) if analytics_metrics else ''}
            </div>
        </body>
        </html>
        """

        sms_body = (
            f"🌟 HIGH-TIER CONTRACT SIGNED! 🌟\n"
            f"{customer_info.get('company_name')} - "
            f"${contract_value.get('total', 0):,.0f} "
            f"({term_months} months)\n"
            f"Tier: {contract_details.get('subscription_tier')}"
        )

        return self._send_notifications(
            NotificationType.HIGH_TIER_CONTRACT_SIGNED,
            subject,
            email_body,
            sms_body,
            is_html=True
        )

    def _generate_analytics_section(self, metrics: Any) -> str:
        """Generate analytics section for high-tier contract email"""
        return f"""
        <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h2 style="color: #ffd700;">High-Tier Contract Analytics</h2>
            <p><strong>Total High-Tier Contracts:</strong> {metrics.contract_count}</p>
            <p><strong>Total Contract Value:</strong> <span style="color: #ffd700;">${metrics.total_contract_value:,.2f}</span></p>
            <p><strong>YTD Growth:</strong> <span style="color: #ffd700;">{metrics.year_to_date_growth:+.1f}%</span></p>
            <p><strong>Average Contract Term:</strong> {metrics.average_contract_term:.1f} months</p>
            <p><a href="/dashboard" style="color: #ffd700; text-decoration: none;">View Full Analytics Dashboard →</a></p>
        </div>
        """

    def _send_notifications(self,
                          notification_type: NotificationType,
                          subject: str,
                          email_body: str,
                          sms_body: str,
                          is_html: bool = False) -> bool:
        """Send notifications based on preferences"""
        success = True
        preferences = self.config.notification_preferences.get(
            notification_type.value,
            ["email", "sms"]  # Default to both if not specified
        )
        
        if "email" in preferences:
            success &= self._send_email(subject, email_body, is_html)
            
        if "sms" in preferences:
            success &= self._send_sms(sms_body)
            
        return success

    def _send_email(self, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.smtp_username
            msg['To'] = self.config.email_address
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_username, self.config.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    def _send_sms(self, body: str) -> bool:
        """Send SMS notification using Twilio"""
        try:
            if not all([self.config.twilio_account_sid,
                       self.config.twilio_auth_token,
                       self.config.twilio_from_number]):
                print("Twilio configuration missing")
                return False
                
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.config.twilio_account_sid}/Messages.json"
            
            payload = {
                "To": self.config.phone_number,
                "From": self.config.twilio_from_number,
                "Body": body
            }
            
            response = requests.post(
                url,
                data=payload,
                auth=(self.config.twilio_account_sid, self.config.twilio_auth_token)
            )
            
            return response.status_code == 201
            
        except Exception as e:
            print(f"Failed to send SMS: {str(e)}")
            return False 