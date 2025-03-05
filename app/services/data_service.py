from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
import random

class DataService:
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize the data service with database connection"""
        if connection_string is None:
            # Store database in AppData/Local
            app_data_dir = os.path.join(os.environ['LOCALAPPDATA'], 'CallCenterDashboard')
            os.makedirs(app_data_dir, exist_ok=True)
            db_path = os.path.join(app_data_dir, 'call_center.db')
            connection_string = f'sqlite:///{db_path}'
        
        try:
            self.engine = create_engine(connection_string)
            # Test the connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"Successfully connected to database at: {connection_string.replace('sqlite:///', '')}")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def verify_database(self) -> bool:
        """Verify database exists and has the correct schema"""
        try:
            with self.engine.connect() as conn:
                # Check if calls table exists
                result = conn.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='calls'"
                ))
                return bool(result.scalar())
        except Exception:
            return False

    def get_daily_calls(self, days: int = 30) -> pd.DataFrame:
        """Get daily call statistics for the specified number of days"""
        query = text("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total_calls,
                AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_rate,
                AVG(duration) as avg_duration
            FROM calls
            WHERE timestamp >= :start_date
            GROUP BY DATE(timestamp)
            ORDER BY date
        """)
        
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"start_date": start_date})
                df = pd.DataFrame(result.fetchall(), columns=['date', 'total_calls', 'success_rate', 'avg_duration'])
                return df
        except Exception as e:
            print(f"Error fetching daily calls: {e}")
            # Return sample data if database is not available
            return self._generate_sample_data(days)

    def get_current_day_stats(self) -> Dict:
        """Get statistics for the current day"""
        query = text("""
            SELECT 
                COUNT(*) as total_calls,
                AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_rate,
                AVG(duration) as avg_duration
            FROM calls
            WHERE DATE(timestamp) = DATE('now')
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query)
                row = result.fetchone()
                return {
                    'total_calls': row[0] if row[0] else 0,
                    'success_rate': row[1] if row[1] else 0,
                    'avg_duration': row[2] if row[2] else 0
                }
        except Exception as e:
            print(f"Error fetching current day stats: {e}")
            # Return sample data if database is not available
            sample = self._generate_sample_data(1)
            return {
                'total_calls': sample['calls'].iloc[-1],
                'success_rate': sample['success_rate'].iloc[-1],
                'avg_duration': sample['avg_duration'].iloc[-1]
            }

    def get_hourly_distribution(self) -> pd.DataFrame:
        """Get call distribution by hour"""
        query = text("""
            SELECT 
                STRFTIME('%H', timestamp) as hour,
                COUNT(*) as call_count,
                AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_rate
            FROM calls
            WHERE timestamp >= DATE('now', '-7 days')
            GROUP BY STRFTIME('%H', timestamp)
            ORDER BY hour
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query)
                return pd.DataFrame(result.fetchall(), columns=['hour', 'call_count', 'success_rate'])
        except Exception as e:
            print(f"Error fetching hourly distribution: {e}")
            # Return sample hourly data
            hours = range(24)
            return pd.DataFrame({
                'hour': hours,
                'call_count': [100 + h * 10 + (12 - abs(12 - h)) * 20 for h in hours],
                'success_rate': [0.7 + (12 - abs(12 - h)) * 0.01 for h in hours]
            })

    def _generate_sample_data(self, days: int) -> pd.DataFrame:
        """Generate sample data for testing"""
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=days-1),
            end=datetime.now(),
            freq='D'
        )
        return pd.DataFrame({
            'date': dates,
            'calls': [100 + i * 5 + i ** 2 for i in range(len(dates))],
            'success_rate': [0.75 + 0.01 * i for i in range(len(dates))],
            'avg_duration': [180 + i * 2 for i in range(len(dates))]
        })

    def create_test_database(self):
        """Create and populate test database with sample data"""
        # Create tables
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                duration INTEGER,
                status TEXT,
                phone_number TEXT,
                agent_id INTEGER
            )
        """)
        
        try:
            # Create table
            with self.engine.begin() as conn:
                conn.execute(create_table_query)
                
                # Check if we already have data
                result = conn.execute(text("SELECT COUNT(*) FROM calls"))
                count = result.scalar()
                
                if count == 0:
                    print("Populating database with sample data...")
                    # Generate sample data
                    now = datetime.now()
                    sample_data = []
                    
                    for i in range(1000):  # Generate 1000 sample calls
                        timestamp = now - timedelta(
                            days=random.randint(0, 30),
                            hours=random.randint(0, 23),
                            minutes=random.randint(0, 59)
                        )
                        duration = random.randint(60, 600)  # 1-10 minutes
                        status = random.choice(['completed', 'failed', 'no-answer'])
                        phone_number = f"+1{random.randint(2000000000, 9999999999)}"
                        agent_id = random.randint(1, 10)
                        
                        sample_data.append({
                            'timestamp': timestamp,
                            'duration': duration,
                            'status': status,
                            'phone_number': phone_number,
                            'agent_id': agent_id
                        })
                    
                    # Insert sample data
                    insert_query = text("""
                        INSERT INTO calls (timestamp, duration, status, phone_number, agent_id)
                        VALUES (:timestamp, :duration, :status, :phone_number, :agent_id)
                    """)
                    
                    for data in sample_data:
                        conn.execute(insert_query, data)
                    
                    print("Test database populated with sample data")
                else:
                    print(f"Database already contains {count} records")
                
        except Exception as e:
            print(f"Error creating/populating test database: {e}")
            raise 