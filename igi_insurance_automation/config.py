"""
Configuration settings for IGI Insurance Automation System
"""

import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database configuration
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'igi_insurance.db')}"

# Gmail API configuration
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')

# CSV configuration
DUES_CSV_PATH = os.path.join(BASE_DIR, 'data', 'dues.csv')

# Automation settings
DUE_PAYMENT_DAYS_THRESHOLD = 30  # Days to send reminder before due date
AUTOMATION_CHECK_INTERVAL = 3600  # Check every hour (in seconds)

# Company information
COMPANY_NAME = "IGI Insurance Limited"
COMPANY_ADDRESS = "IGI House, 61-63 Jinnah Avenue, Islamabad, Pakistan"
COMPANY_PHONE = "+92-51-111-444-111"
COMPANY_EMAIL = "info@igi.com.pk"
COMPANY_WEBSITE = "www.igi.com.pk"

# RPA configuration
RPA_TIMEOUT = 30  # seconds
RPA_HEADLESS = True  # Run browser in headless mode

# PDF generation settings
PDF_OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
