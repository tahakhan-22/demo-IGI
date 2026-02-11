"""
CSV scanner for automated payment reminders
Scans CSV file for due payments and sends email reminders
"""

import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Handle imports for both module and direct execution
try:
    from ..config import DUES_CSV_PATH, DUE_PAYMENT_DAYS_THRESHOLD
    from ..database.db import get_session
    from ..database.models import AutomationLog
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import DUES_CSV_PATH, DUE_PAYMENT_DAYS_THRESHOLD
    from database.db import get_session
    from database.models import AutomationLog


class CSVScanner:
    """Scanner for processing due payment reminders"""
    
    def __init__(self, gmail_service):
        self.gmail_service = gmail_service
        self.dues_file = DUES_CSV_PATH
        self.threshold_days = DUE_PAYMENT_DAYS_THRESHOLD
    
    def scan_and_send_reminders(self):
        """Scan CSV and send payment reminders"""
        results = {
            'total_scanned': 0,
            'reminders_sent': 0,
            'errors': 0,
            'details': []
        }
        
        try:
            # Read CSV file
            df = pd.read_csv(self.dues_file)
            results['total_scanned'] = len(df)
            
            # Get current date
            today = datetime.now().date()
            threshold_date = today + timedelta(days=self.threshold_days)
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Parse due date
                    due_date = pd.to_datetime(row['due_date']).date()
                    
                    # Check if due date is within threshold
                    if today <= due_date <= threshold_date:
                        # Send reminder email
                        success, message = self._send_reminder(
                            row['client_name'],
                            row['email'],
                            row['due_date'],
                            row['amount_due']
                        )
                        
                        if success:
                            results['reminders_sent'] += 1
                            results['details'].append({
                                'client': row['client_name'],
                                'email': row['email'],
                                'status': 'Sent',
                                'message': message
                            })
                            
                            # Log to database
                            self._log_automation(
                                'CSV Scanner - Reminder Sent',
                                'Success',
                                f"Reminder sent to {row['client_name']} ({row['email']})",
                                f"Due Date: {row['due_date']}, Amount: PKR {row['amount_due']}"
                            )
                        else:
                            results['errors'] += 1
                            results['details'].append({
                                'client': row['client_name'],
                                'email': row['email'],
                                'status': 'Failed',
                                'message': message
                            })
                            
                            # Log error
                            self._log_automation(
                                'CSV Scanner - Reminder Failed',
                                'Failed',
                                f"Failed to send reminder to {row['client_name']}",
                                message
                            )
                
                except Exception as e:
                    results['errors'] += 1
                    results['details'].append({
                        'client': row.get('client_name', 'Unknown'),
                        'email': row.get('email', 'Unknown'),
                        'status': 'Error',
                        'message': str(e)
                    })
        
        except FileNotFoundError:
            results['details'].append({
                'status': 'Error',
                'message': f'CSV file not found: {self.dues_file}'
            })
            self._log_automation(
                'CSV Scanner - File Not Found',
                'Failed',
                f'CSV file not found: {self.dues_file}',
                ''
            )
        except Exception as e:
            results['details'].append({
                'status': 'Error',
                'message': f'Error reading CSV: {str(e)}'
            })
            self._log_automation(
                'CSV Scanner - Error',
                'Failed',
                'Error reading CSV file',
                str(e)
            )
        
        return results
    
    def _send_reminder(self, client_name, email, due_date, amount_due):
        """Send payment reminder email"""
        subject = "Policy Payment Reminder"
        
        body = f"""Dear {client_name},

Your policy payment of PKR {amount_due} is due on {due_date}.
Please ensure payment to avoid lapse.

Regards,
IGI Insurance"""
        
        return self.gmail_service.send_email(email, subject, body)
    
    def _log_automation(self, automation_type, status, message, details):
        """Log automation activity to database"""
        try:
            session = get_session()
            log = AutomationLog(
                automation_type=automation_type,
                status=status,
                message=message,
                details=details
            )
            session.add(log)
            session.commit()
            session.close()
        except Exception as e:
            print(f"Failed to log automation: {str(e)}")
