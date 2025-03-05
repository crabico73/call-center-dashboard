import os
import sqlite3
from datetime import datetime
import json
from pathlib import Path

class PaymentService:
    def __init__(self):
        """Initialize the payment service"""
        self.db_path = self._get_db_path()
        self._init_db()
    
    def _get_db_path(self):
        """Get the path to the payment database"""
        base_path = Path(__file__).parent.parent.parent
        data_dir = base_path / 'data'
        data_dir.mkdir(exist_ok=True)
        return str(data_dir / 'payment_info.db')
    
    def _init_db(self):
        """Initialize the payment database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create payment_info table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payment_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_name TEXT NOT NULL,
                    dba_name TEXT,
                    tax_id TEXT NOT NULL,
                    years_business INTEGER,
                    bank_name TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    routing_number TEXT NOT NULL,
                    account_number TEXT NOT NULL,
                    signer_name TEXT NOT NULL,
                    signer_title TEXT NOT NULL,
                    signer_email TEXT NOT NULL,
                    signer_phone TEXT NOT NULL,
                    agreement_accepted BOOLEAN NOT NULL,
                    submission_date TIMESTAMP NOT NULL,
                    reference_number TEXT NOT NULL UNIQUE
                )
            ''')
            conn.commit()
    
    def save_payment_info(self, payment_data):
        """
        Save payment information to the database
        Args:
            payment_data (dict): Dictionary containing payment information
        Returns:
            str: Reference number for the saved payment information
        """
        reference_number = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO payment_info (
                    business_name, dba_name, tax_id, years_business,
                    bank_name, account_type, routing_number, account_number,
                    signer_name, signer_title, signer_email, signer_phone,
                    agreement_accepted, submission_date, reference_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                payment_data['business_name'],
                payment_data.get('dba_name', ''),
                payment_data['tax_id'],
                payment_data.get('years_business', 0),
                payment_data['bank_name'],
                payment_data['account_type'],
                payment_data['routing_number'],
                payment_data['account_number'],
                payment_data['signer_name'],
                payment_data['signer_title'],
                payment_data['signer_email'],
                payment_data['signer_phone'],
                payment_data['agreement_accepted'],
                datetime.now().isoformat(),
                reference_number
            ))
            conn.commit()
        
        return reference_number
    
    def get_payment_info(self, reference_number):
        """
        Retrieve payment information by reference number
        Args:
            reference_number (str): Reference number of the payment information
        Returns:
            dict: Payment information or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM payment_info WHERE reference_number = ?
            ''', (reference_number,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    def export_payment_info_csv(self, start_date=None, end_date=None):
        """
        Export payment information to CSV format
        Args:
            start_date (str, optional): Start date for filtering (YYYY-MM-DD)
            end_date (str, optional): End date for filtering (YYYY-MM-DD)
        Returns:
            str: CSV content
        """
        query = 'SELECT * FROM payment_info'
        params = []
        
        if start_date or end_date:
            query += ' WHERE '
            if start_date:
                query += 'submission_date >= ?'
                params.append(f"{start_date} 00:00:00")
            if end_date:
                if start_date:
                    query += ' AND '
                query += 'submission_date <= ?'
                params.append(f"{end_date} 23:59:59")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if not rows:
                return "No payment information found for the specified period"
            
            # Create CSV content
            headers = list(dict(rows[0]).keys())
            csv_content = ",".join(headers) + "\n"
            
            for row in rows:
                row_dict = dict(row)
                csv_content += ",".join(str(row_dict[header]) for header in headers) + "\n"
            
            return csv_content 