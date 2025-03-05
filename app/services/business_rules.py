"""
Business rules service for managing call center operations
"""

from datetime import datetime, time, timedelta, date
import pytz
from typing import Dict, Optional
import sqlite3
from pathlib import Path

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

class BusinessRules:
    def __init__(self):
        """Initialize business rules service"""
        self.db_path = self._get_db_path()
        self.daily_contract_goal = 3  # Default daily goal
        self._init_db()
    
    def _get_db_path(self):
        """Get the path to the business rules database"""
        base_path = Path(__file__).parent.parent.parent
        data_dir = base_path / 'data'
        data_dir.mkdir(exist_ok=True)
        return str(data_dir / 'business_rules.db')
    
    def _init_db(self):
        """Initialize the database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create contracts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_contracts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_date DATE NOT NULL,
                    business_name TEXT NOT NULL,
                    contract_time TIMESTAMP NOT NULL
                )
            ''')
            
            # Create settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Insert default daily goal if not exists
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', ('daily_contract_goal', str(self.daily_contract_goal), datetime.now().isoformat()))
            
            conn.commit()
    
    def set_daily_goal(self, goal: int) -> bool:
        """Set the daily contract goal
        Args:
            goal (int): Number of contracts per day
        Returns:
            bool: True if successful
        """
        if goal < 1:
            return False
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE settings 
                    SET value = ?, updated_at = ?
                    WHERE key = ?
                ''', (str(goal), datetime.now().isoformat(), 'daily_contract_goal'))
                conn.commit()
                self.daily_contract_goal = goal
                return True
        except Exception as e:
            print(f"Error setting daily goal: {e}")
            return False
    
    def get_daily_goal(self) -> int:
        """Get the current daily contract goal
        Returns:
            int: Current daily goal
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM settings WHERE key = ?', ('daily_contract_goal',))
                result = cursor.fetchone()
                return int(result[0]) if result else self.daily_contract_goal
        except Exception as e:
            print(f"Error getting daily goal: {e}")
            return self.daily_contract_goal
    
    def add_contract(self, business_name: str) -> bool:
        """Record a new contract
        Args:
            business_name (str): Name of the business that signed
        Returns:
            bool: True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now()
                cursor.execute('''
                    INSERT INTO daily_contracts (contract_date, business_name, contract_time)
                    VALUES (?, ?, ?)
                ''', (now.date().isoformat(), business_name, now.isoformat()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding contract: {e}")
            return False
    
    def get_todays_contracts(self) -> list:
        """Get list of today's contracts
        Returns:
            list: List of contracts for today
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                today = date.today().isoformat()
                cursor.execute('''
                    SELECT business_name, contract_time 
                    FROM daily_contracts 
                    WHERE contract_date = ?
                    ORDER BY contract_time DESC
                ''', (today,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting today's contracts: {e}")
            return []
    
    def can_accept_more_contracts(self) -> bool:
        """Check if we can accept more contracts today
        Returns:
            bool: True if we haven't reached the daily goal
        """
        try:
            today_count = len(self.get_todays_contracts())
            daily_goal = self.get_daily_goal()
            return today_count < daily_goal
        except Exception as e:
            print(f"Error checking contract limit: {e}")
            return False
    
    def get_daily_stats(self) -> dict:
        """Get statistics for today
        Returns:
            dict: Statistics including goal, current count, and remaining
        """
        try:
            daily_goal = self.get_daily_goal()
            today_contracts = self.get_todays_contracts()
            return {
                'goal': daily_goal,
                'current': len(today_contracts),
                'remaining': max(0, daily_goal - len(today_contracts)),
                'contracts': today_contracts
            }
        except Exception as e:
            print(f"Error getting daily stats: {e}")
            return {
                'goal': self.daily_contract_goal,
                'current': 0,
                'remaining': self.daily_contract_goal,
                'contracts': []
            } 