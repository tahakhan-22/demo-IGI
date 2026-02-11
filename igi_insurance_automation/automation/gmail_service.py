"""
Gmail API integration with OAuth 2.0
Handles email sending and reading
"""

import os
import base64
import pickle
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ..config import GMAIL_SCOPES, CREDENTIALS_FILE, TOKEN_FILE


class GmailService:
    """Gmail service for sending and reading emails"""
    
    def __init__(self):
        self.service = None
        self.authenticated = False
    
    def authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0"""
        creds = None
        
        # Check if credentials file exists
        if not os.path.exists(CREDENTIALS_FILE):
            return False, "credentials.json not found. Please download it from Google Cloud Console."
        
        # Load token if exists
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, GMAIL_SCOPES)
        
        # If credentials are not valid, refresh or get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    return False, f"Failed to refresh token: {str(e)}"
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, GMAIL_SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    return False, f"Failed to authenticate: {str(e)}"
            
            # Save credentials for next run
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.authenticated = True
            return True, "Successfully authenticated with Gmail"
        except Exception as e:
            return False, f"Failed to build service: {str(e)}"
    
    def send_email(self, to, subject, body):
        """Send email via Gmail API"""
        if not self.authenticated or not self.service:
            return False, "Not authenticated. Please authenticate first."
        
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return True, f"Email sent successfully. Message ID: {send_message['id']}"
        except HttpError as error:
            return False, f"Failed to send email: {str(error)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def read_unread_emails(self, max_results=10):
        """Fetch latest unread emails"""
        if not self.authenticated or not self.service:
            return False, "Not authenticated. Please authenticate first.", []
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            email_list = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Extract headers
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                
                # Extract body
                body = ''
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            if 'data' in part['body']:
                                body = base64.urlsafe_b64decode(part['body']['data']).decode()
                                break
                else:
                    if 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                        body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode()
                
                email_list.append({
                    'id': message['id'],
                    'subject': subject,
                    'from': from_email,
                    'body': body
                })
            
            return True, f"Found {len(email_list)} unread emails", email_list
        except HttpError as error:
            return False, f"Failed to read emails: {str(error)}", []
        except Exception as e:
            return False, f"Error: {str(e)}", []
    
    def mark_as_read(self, message_id):
        """Mark email as read"""
        if not self.authenticated or not self.service:
            return False, "Not authenticated. Please authenticate first."
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True, "Email marked as read"
        except HttpError as error:
            return False, f"Failed to mark as read: {str(error)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
