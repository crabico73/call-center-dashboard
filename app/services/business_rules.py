"""
Business rules service for managing call center operations
"""

from datetime import datetime, time, timedelta
import pytz
from typing import Dict, Optional

class BusinessRulesService:
    def __init__(self):
        self.business_hours = {
            'start': time(9, 0),  # 9:00 AM
            'end': time(17, 0)    # 5:00 PM
        }
        
        # Common business timezones
        self.supported_timezones = {
            'US/Eastern': 'Eastern Time',
            'US/Central': 'Central Time',
            'US/Mountain': 'Mountain Time',
            'US/Pacific': 'Pacific Time',
            'Europe/London': 'UK Time',
            'Europe/Paris': 'Central European Time',
            'Asia/Tokyo': 'Japan Time',
            'Australia/Sydney': 'Sydney Time'
        }
    
    def is_business_hours(self, timezone_str: str) -> Dict:
        """
        Check if current time is within business hours for given timezone
        Returns dict with status and next available time
        """
        try:
            tz = pytz.timezone(timezone_str)
            current_time = datetime.now(tz)
            current_time_only = current_time.time()
            
            is_business = (
                self.business_hours['start'] <= current_time_only <= self.business_hours['end'] and
                current_time.weekday() < 5  # Monday = 0, Friday = 4
            )
            
            next_time = None
            if not is_business:
                if current_time.weekday() >= 5:  # Weekend
                    # Next Monday
                    days_ahead = 7 - current_time.weekday()
                    next_time = current_time.replace(
                        hour=self.business_hours['start'].hour,
                        minute=self.business_hours['start'].minute,
                        second=0
                    ) + timedelta(days=days_ahead)
                elif current_time_only < self.business_hours['start']:
                    # Later today
                    next_time = current_time.replace(
                        hour=self.business_hours['start'].hour,
                        minute=self.business_hours['start'].minute,
                        second=0
                    )
                else:
                    # Next business day
                    next_time = current_time.replace(
                        hour=self.business_hours['start'].hour,
                        minute=self.business_hours['start'].minute,
                        second=0
                    ) + timedelta(days=1)
                    if next_time.weekday() >= 5:  # If next day is weekend
                        next_time = next_time + timedelta(days=(7-next_time.weekday()))
            
            return {
                'is_business_hours': is_business,
                'current_time': current_time.strftime('%I:%M %p'),
                'current_day': current_time.strftime('%A'),
                'next_available': next_time.strftime('%I:%M %p %A') if next_time else None,
                'timezone_name': self.supported_timezones.get(timezone_str, timezone_str)
            }
            
        except Exception as e:
            print(f"Error checking business hours: {e}")
            return {
                'is_business_hours': False,
                'error': f"Invalid timezone: {timezone_str}"
            }
    
    def get_available_timezones(self) -> Dict[str, str]:
        """Get list of supported timezones"""
        return self.supported_timezones
    
    def can_make_call(self, target_timezone: str) -> Dict:
        """
        Determine if a call can be made to the target timezone
        Returns dict with call status and reason
        """
        status = self.is_business_hours(target_timezone)
        
        if not status.get('is_business_hours', False):
            return {
                'can_call': False,
                'reason': f"Outside business hours in {status.get('timezone_name', target_timezone)}. "
                         f"Next available: {status.get('next_available')}",
                'status': status
            }
        
        return {
            'can_call': True,
            'reason': f"Business hours in {status.get('timezone_name', target_timezone)}: "
                     f"{status.get('current_time')} {status.get('current_day')}",
            'status': status
        } 