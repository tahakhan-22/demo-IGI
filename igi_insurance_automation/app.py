"""
IGI Insurance Automation System - Main Streamlit Dashboard
Complete automation control panel with all modules
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db, get_session
from database.models import AutomationLog, Policy, Client, Vehicle
from automation.gmail_service import GmailService
from automation.email_parser import EmailParser
from automation.csv_scanner import CSVScanner
from automation.rpa_engine import RPAEngine
from services.policy_service import PolicyService
from services.premium_calculator import PremiumCalculator
from services.cover_letter_generator import CoverLetterGenerator
from config import COMPANY_NAME

# Page configuration
st.set_page_config(
    page_title="IGI Insurance Automation System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Initialize services
@st.cache_resource
def get_gmail_service():
    return GmailService()

@st.cache_resource
def get_rpa_engine():
    return RPAEngine()


def check_system_status():
    """Check status of all system components"""
    status = {
        'gmail': False,
        'rpa': False,
        'database': False
    }
    
    # Check Gmail
    gmail = get_gmail_service()
    if gmail.authenticated:
        status['gmail'] = True
    
    # Check Database
    try:
        from sqlalchemy import text
        session = get_session()
        session.execute(text("SELECT 1"))
        session.close()
        status['database'] = True
    except:
        pass
    
    # RPA is always available
    status['rpa'] = True
    
    return status


def display_system_status():
    """Display system status indicators"""
    st.subheader("🔧 System Status")
    
    status = check_system_status()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if status['gmail']:
            st.success("✅ Gmail Connected")
        else:
            st.error("❌ Gmail Disconnected")
    
    with col2:
        if status['rpa']:
            st.success("✅ RPA Engine Ready")
        else:
            st.error("❌ RPA Engine Offline")
    
    with col3:
        if status['database']:
            st.success("✅ Database Connected")
        else:
            st.error("❌ Database Error")


def display_automation_logs():
    """Display recent automation logs"""
    st.subheader("📋 Recent Automation Logs")
    
    try:
        session = get_session()
        logs = session.query(AutomationLog).order_by(
            AutomationLog.executed_at.desc()
        ).limit(10).all()
        session.close()
        
        if logs:
            log_data = []
            for log in logs:
                log_data.append({
                    'Time': log.executed_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'Type': log.automation_type,
                    'Status': log.status,
                    'Message': log.message
                })
            
            df = pd.DataFrame(log_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No automation logs yet")
    except Exception as e:
        st.error(f"Error loading logs: {str(e)}")


def email_automation_module():
    """Email Automation Module"""
    st.header("📧 Email Automation")
    
    gmail = get_gmail_service()
    
    # Authentication section
    if not gmail.authenticated:
        st.warning("Gmail not authenticated. Please authenticate to use email features.")
        
        if st.button("🔑 Authenticate Gmail"):
            with st.spinner("Authenticating with Gmail..."):
                success, message = gmail.authenticate()
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
                    if "credentials.json" in message:
                        st.info("""
                        **Setup Instructions:**
                        1. Go to Google Cloud Console
                        2. Create a new project or select existing
                        3. Enable Gmail API
                        4. Create OAuth 2.0 credentials
                        5. Download credentials.json
                        6. Place it in the project root directory
                        """)
    else:
        st.success("✅ Gmail authenticated successfully")
        
        # Read unread emails
        if st.button("📥 Read Unread Emails"):
            with st.spinner("Fetching unread emails..."):
                success, message, emails = gmail.read_unread_emails()
                if success:
                    st.success(message)
                    
                    if emails:
                        for email in emails:
                            with st.expander(f"📨 {email['subject']} - From: {email['from']}"):
                                st.text_area("Email Body", email['body'], height=200)
                                
                                if st.button(f"Mark as Read", key=f"read_{email['id']}"):
                                    success, msg = gmail.mark_as_read(email['id'])
                                    if success:
                                        st.success(msg)
                                    else:
                                        st.error(msg)
                    else:
                        st.info("No unread emails found")
                else:
                    st.error(message)


def payment_reminder_module():
    """Payment Reminder Automation Module"""
    st.header("💰 Payment Reminder Automation")
    
    gmail = get_gmail_service()
    
    if not gmail.authenticated:
        st.warning("Gmail authentication required to send reminders")
        return
    
    st.info(f"Scans CSV file for payments due within 30 days and sends automated reminders")
    
    # Display CSV data
    try:
        df = pd.read_csv('igi_insurance_automation/data/dues.csv')
        st.subheader("📊 Current Due Payments")
        st.dataframe(df, use_container_width=True)
        
        # Highlight upcoming dues
        today = datetime.now().date()
        threshold = today + timedelta(days=30)
        
        df['due_date'] = pd.to_datetime(df['due_date'])
        upcoming = df[(df['due_date'].dt.date >= today) & (df['due_date'].dt.date <= threshold)]
        
        st.subheader(f"⚠️ Due Within 30 Days ({len(upcoming)} clients)")
        if len(upcoming) > 0:
            st.dataframe(upcoming, use_container_width=True)
    except Exception as e:
        st.error(f"Error reading CSV: {str(e)}")
    
    # Trigger automation
    if st.button("🚀 Send Payment Reminders"):
        with st.spinner("Scanning CSV and sending reminders..."):
            scanner = CSVScanner(gmail)
            results = scanner.scan_and_send_reminders()
            
            st.success(f"Scan Complete!")
            st.write(f"Total Scanned: {results['total_scanned']}")
            st.write(f"Reminders Sent: {results['reminders_sent']}")
            st.write(f"Errors: {results['errors']}")
            
            if results['details']:
                st.subheader("Details")
                for detail in results['details']:
                    if detail.get('status') == 'Sent':
                        st.success(f"✅ {detail['client']} - {detail['message']}")
                    else:
                        st.error(f"❌ {detail.get('client', 'Unknown')} - {detail['message']}")


def policy_processing_module():
    """Email-to-Form Policy Processing Module"""
    st.header("📄 Policy Processing (Email → Form → RPA)")
    
    gmail = get_gmail_service()
    
    if not gmail.authenticated:
        st.warning("Gmail authentication required")
        return
    
    # Initialize session state for email navigation
    if 'fetched_emails' not in st.session_state:
        st.session_state.fetched_emails = []
    if 'current_email_index' not in st.session_state:
        st.session_state.current_email_index = 0
    
    # Fetch emails
    if st.button("📥 Fetch Emails for Processing", key="fetch_emails_btn"):
        with st.spinner("Fetching unread emails..."):
            success, message, emails = gmail.read_unread_emails(max_results=20)
            
            if success and emails:
                st.session_state.fetched_emails = emails
                st.session_state.current_email_index = 0
                st.session_state.email_to_process = emails[0]
                # Clear any parsed data from previous session
                if 'parsed_data' in st.session_state:
                    del st.session_state.parsed_data
                st.success(f"Fetched {len(emails)} unread email(s)!")
            else:
                st.error("No unread emails found")
                st.session_state.fetched_emails = []
    
    # Display email navigation and process email if available
    if st.session_state.fetched_emails:
        total_emails = len(st.session_state.fetched_emails)
        current_idx = st.session_state.current_email_index
        
        # Check if we're past the end (all emails processed)
        if current_idx >= total_emails:
            st.info("✅ No more emails to process. Click 'Fetch Emails' to refresh.")
            return
        
        # Navigation UI (above email body)
        st.subheader("📧 Email Navigation")
        
        # Email counter and subject/sender preview
        email = st.session_state.fetched_emails[current_idx]
        st.write(f"**Email {current_idx + 1} of {total_emails}**")
        st.write(f"**Subject:** {email['subject']}")
        st.write(f"**From:** {email['from']}")
        
        # Navigation buttons in columns
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("⬅️ Previous Email", disabled=(current_idx == 0), key=f"prev_email_btn_{current_idx}"):
                st.session_state.current_email_index -= 1
                st.session_state.email_to_process = st.session_state.fetched_emails[st.session_state.current_email_index]
                # Clear parsed data when switching emails
                if 'parsed_data' in st.session_state:
                    del st.session_state.parsed_data
                st.rerun()
        
        with col2:
            if st.button("➡️ Next Email", disabled=(current_idx >= total_emails - 1), key=f"next_email_btn_{current_idx}"):
                st.session_state.current_email_index += 1
                st.session_state.email_to_process = st.session_state.fetched_emails[st.session_state.current_email_index]
                # Clear parsed data when switching emails
                if 'parsed_data' in st.session_state:
                    del st.session_state.parsed_data
                st.rerun()
        
        with col3:
            if st.button("⏭️ Skip & Mark as Read", key=f"skip_email_btn_{current_idx}"):
                # Mark current email as read
                gmail.mark_as_read(email['id'])
                # Move to next email
                st.session_state.current_email_index += 1
                # Clear parsed data
                if 'parsed_data' in st.session_state:
                    del st.session_state.parsed_data
                # Update email_to_process if there are more emails
                if st.session_state.current_email_index < total_emails:
                    st.session_state.email_to_process = st.session_state.fetched_emails[st.session_state.current_email_index]
                st.success("Email marked as read and skipped!")
                st.rerun()
        
        with col4:
            st.write("")  # Empty column for spacing
        
        st.markdown("---")
        
        # Update email_to_process to current email
        st.session_state.email_to_process = email
    
    # Process email if available
    if 'email_to_process' in st.session_state and st.session_state.fetched_emails:
        email = st.session_state.email_to_process
        
        st.subheader("📧 Email Content")
        st.text_area("Email Body", email['body'], height=200, key="email_body")
        
        # Parse email
        if st.button("🔍 Parse Email Data"):
            with st.spinner("Parsing email data..."):
                parser = EmailParser()
                parsed_data = parser.parse_email(email['body'])
                st.session_state.parsed_data = parsed_data
                st.success("Email parsed successfully!")
        
        # Display parsed data and form
        if 'parsed_data' in st.session_state:
            parsed = st.session_state.parsed_data
            
            st.subheader("📝 Auto-Filled Policy Form")
            
            with st.form("policy_form"):
                st.write("**Client Information**")
                col1, col2 = st.columns(2)
                
                with col1:
                    client_name = st.text_input("Client Name", 
                        value=parsed['client'].get('name', ''))
                    client_cnic = st.text_input("CNIC", 
                        value=parsed['client'].get('cnic', ''))
                    client_phone = st.text_input("Phone", 
                        value=parsed['client'].get('phone', ''))
                
                with col2:
                    client_email = st.text_input("Email", 
                        value=parsed['client'].get('email', ''))
                    client_city = st.text_input("City", 
                        value=parsed['client'].get('city', ''))
                    client_address = st.text_area("Address", 
                        value=parsed['client'].get('address', ''), height=100)
                
                st.write("**Vehicle Information**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    vehicle_make = st.text_input("Make", 
                        value=parsed['vehicle'].get('make', ''))
                    vehicle_model = st.text_input("Model", 
                        value=parsed['vehicle'].get('model', ''))
                    vehicle_year = st.number_input("Year", 
                        value=parsed['vehicle'].get('year', 2024), min_value=1990, max_value=2030)
                
                with col2:
                    engine_number = st.text_input("Engine Number", 
                        value=parsed['vehicle'].get('engine_number', ''))
                    chassis_number = st.text_input("Chassis Number", 
                        value=parsed['vehicle'].get('chassis_number', ''))
                    registration_number = st.text_input("Registration Number", 
                        value=parsed['vehicle'].get('registration_number', ''))
                
                with col3:
                    vehicle_color = st.text_input("Color", 
                        value=parsed['vehicle'].get('color', ''))
                    fuel_type = st.selectbox("Fuel Type", 
                        ['Petrol', 'Diesel', 'Electric', 'Hybrid'],
                        index=0 if not parsed['vehicle'].get('fuel_type') else 
                        ['Petrol', 'Diesel', 'Electric', 'Hybrid'].index(parsed['vehicle'].get('fuel_type', 'Petrol')))
                
                st.write("**Policy Information**")
                col1, col2 = st.columns(2)
                
                with col1:
                    sum_insured = st.number_input("Sum Insured (PKR)", 
                        value=float(parsed['policy'].get('sum_insured', 1000000)), 
                        min_value=0.0, step=10000.0)
                    commencement_date = st.date_input("Commencement Date", 
                        value=datetime.now().date())
                
                with col2:
                    coverage_months = st.number_input("Coverage Period (months)", 
                        value=parsed['policy'].get('coverage_months', 12), 
                        min_value=1, max_value=60)
                    expiry_date = commencement_date + timedelta(days=coverage_months * 30)
                    st.date_input("Expiry Date (Auto-calculated)", value=expiry_date, disabled=True)
                
                # Calculate premium
                calculator = PremiumCalculator()
                vehicle_age = datetime.now().year - vehicle_year
                premium = calculator.calculate_motor_premium(
                    sum_insured=sum_insured,
                    vehicle_age=vehicle_age,
                    policy_type='comprehensive'
                )
                
                st.write("**Premium Calculation**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Gross Premium", f"PKR {premium['gross_premium']:,.2f}")
                    st.metric("Net Premium", f"PKR {premium['net_premium']:,.2f}")
                
                with col2:
                    st.metric("Total Charges", f"PKR {premium['total_charges']:,.2f}")
                    st.metric("Total Discount", f"PKR {premium['total_discount']:,.2f}")
                
                with col3:
                    st.metric("Premium Payable", f"PKR {premium['premium_payable']:,.2f}", 
                             delta=None, delta_color="normal")
                
                # Submit button
                submitted = st.form_submit_button("✅ Complete Policy")
                
                if submitted:
                    with st.spinner("Processing policy..."):
                        # Create policy
                        policy_service = PolicyService()
                        
                        # Create client
                        client_data = {
                            'name': client_name,
                            'cnic': client_cnic,
                            'phone': client_phone,
                            'email': client_email,
                            'address': client_address,
                            'city': client_city,
                            'client_type': 'Individual'
                        }
                        
                        success, message, client = policy_service.create_client(client_data)
                        
                        if success:
                            # Create policy
                            policy_data = {
                                'commencement_date': commencement_date,
                                'expiry_date': expiry_date,
                                'sum_insured': sum_insured,
                                'gross_premium': premium['gross_premium'],
                                'net_premium': premium['net_premium'],
                                'premium_payable': premium['premium_payable']
                            }
                            
                            success, message, policy = policy_service.create_policy(
                                policy_data, client.id
                            )
                            
                            if success:
                                # Create vehicle
                                vehicle_data = {
                                    'make': vehicle_make,
                                    'model': vehicle_model,
                                    'year_of_manufacturing': vehicle_year,
                                    'engine_number': engine_number,
                                    'chassis_number': chassis_number,
                                    'registration_number': registration_number,
                                    'color': vehicle_color,
                                    'fuel_type': fuel_type,
                                    'sum_insured': sum_insured
                                }
                                
                                success, message, vehicle = policy_service.create_vehicle(
                                    vehicle_data, policy.id
                                )
                                
                                if success:
                                    # Execute RPA
                                    rpa = get_rpa_engine()
                                    rpa.fill_streamlit_form({
                                        'client': client_data,
                                        'vehicle': vehicle_data,
                                        'policy': policy_data
                                    })
                                    
                                    st.success("✅ Policy created successfully!")
                                    st.info(f"Policy Number: {policy.policy_number}")
                                    
                                    # Store for cover letter generation
                                    st.session_state.created_policy_id = policy.id
                                    
                                    # Mark email as read
                                    gmail.mark_as_read(email['id'])
                                else:
                                    st.error(f"Error creating vehicle: {message}")
                            else:
                                st.error(f"Error creating policy: {message}")
                        else:
                            st.error(f"Error creating client: {message}")
                        
                        policy_service.close()


def cover_letter_module():
    """Cover Letter Generation Module"""
    st.header("🧾 Cover Letter Generator")
    
    # Get policies
    try:
        session = get_session()
        policies = session.query(Policy).order_by(Policy.created_at.desc()).limit(20).all()
        session.close()
        
        if policies:
            policy_options = {f"{p.policy_number} - {p.client.name}": p.id for p in policies}
            
            selected = st.selectbox("Select Policy", list(policy_options.keys()))
            
            if st.button("📄 Generate Cover Letter"):
                policy_id = policy_options[selected]
                
                with st.spinner("Generating cover letter..."):
                    session = get_session()
                    policy = session.query(Policy).filter_by(id=policy_id).first()
                    
                    if policy:
                        # Prepare data
                        policy_data = {
                            'client': {
                                'name': policy.client.name,
                                'cnic': policy.client.cnic,
                                'address': policy.client.address,
                                'phone': policy.client.phone,
                                'email': policy.client.email
                            },
                            'policy': {
                                'policy_number': policy.policy_number,
                                'coverage_type': 'Comprehensive',
                                'commencement_date': str(policy.commencement_date),
                                'expiry_date': str(policy.expiry_date),
                                'sum_insured': policy.sum_insured
                            },
                            'premium': {
                                'basic_premium': policy.gross_premium,
                                'gross_premium': policy.gross_premium,
                                'total_discount': 0,
                                'net_premium': policy.net_premium,
                                'stamp_duty': 40,
                                'fid_fee': 100,
                                'provincial_tax': policy.net_premium * 0.01,
                                'total_charges': 140 + policy.net_premium * 0.01,
                                'premium_payable': policy.premium_payable
                            },
                            'clauses': [],
                            'warranties': []
                        }
                        
                        # Add vehicle if exists
                        if policy.vehicles:
                            vehicle = policy.vehicles[0]
                            policy_data['vehicle'] = {
                                'make': vehicle.make,
                                'model': vehicle.model,
                                'year_of_manufacturing': vehicle.year_of_manufacturing,
                                'engine_number': vehicle.engine_number,
                                'chassis_number': vehicle.chassis_number,
                                'registration_number': vehicle.registration_number,
                                'color': vehicle.color,
                                'fuel_type': vehicle.fuel_type
                            }
                        
                        # Generate letter
                        generator = CoverLetterGenerator()
                        letter = generator.generate_cover_letter(policy_data)
                        
                        st.subheader("📄 Cover Letter")
                        st.text_area("", letter, height=600)
                        
                        # Generate PDF
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📥 Download as PDF"):
                                success, message, file_path = generator.generate_pdf(policy_data)
                                if success:
                                    st.success(message)
                                    st.info(f"PDF saved to: {file_path}")
                                else:
                                    st.error(message)
                    
                    session.close()
        else:
            st.info("No policies found. Create a policy first.")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")


def database_viewer_module():
    """Policy Database Viewer Module"""
    st.header("📊 Policy Database Viewer")
    
    try:
        session = get_session()
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["Policies", "Clients", "Vehicles"])
        
        with tab1:
            st.subheader("All Policies")
            policies = session.query(Policy).all()
            
            if policies:
                policy_data = []
                for p in policies:
                    policy_data.append({
                        'Policy Number': p.policy_number,
                        'Client': p.client.name,
                        'Status': p.status,
                        'Commencement': str(p.commencement_date),
                        'Expiry': str(p.expiry_date),
                        'Sum Insured': f"PKR {p.sum_insured:,.2f}",
                        'Premium Payable': f"PKR {p.premium_payable:,.2f}"
                    })
                
                df = pd.DataFrame(policy_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No policies found")
        
        with tab2:
            st.subheader("All Clients")
            clients = session.query(Client).all()
            
            if clients:
                client_data = []
                for c in clients:
                    client_data.append({
                        'Name': c.name,
                        'CNIC': c.cnic,
                        'Phone': c.phone,
                        'Email': c.email,
                        'City': c.city,
                        'Policies': len(c.policies)
                    })
                
                df = pd.DataFrame(client_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No clients found")
        
        with tab3:
            st.subheader("All Vehicles")
            vehicles = session.query(Vehicle).all()
            
            if vehicles:
                vehicle_data = []
                for v in vehicles:
                    vehicle_data.append({
                        'Make/Model': f"{v.make} {v.model}",
                        'Year': v.year_of_manufacturing,
                        'Engine No': v.engine_number,
                        'Chassis No': v.chassis_number,
                        'Registration': v.registration_number,
                        'Policy': v.policy.policy_number
                    })
                
                df = pd.DataFrame(vehicle_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No vehicles found")
        
        session.close()
    
    except Exception as e:
        st.error(f"Error: {str(e)}")


def main():
    """Main application"""
    
    # Title
    st.title(f"🏢 {COMPANY_NAME}")
    st.subheader("Insurance Automation System - Control Panel")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio(
        "Select Module",
        [
            "🏠 Dashboard",
            "📧 Email Automation",
            "💰 Payment Reminders",
            "📄 Policy Processing",
            "🧾 Cover Letter Generator",
            "📊 Database Viewer"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Quick Guide:**
    - Dashboard: System status & logs
    - Email Automation: Read emails
    - Payment Reminders: Auto-send due alerts
    - Policy Processing: Email → Form → Save
    - Cover Letter: Generate policy documents
    - Database: View all records
    """)
    
    # Route to appropriate module
    if page == "🏠 Dashboard":
        st.header("🏠 Dashboard")
        display_system_status()
        st.markdown("---")
        display_automation_logs()
    
    elif page == "📧 Email Automation":
        email_automation_module()
    
    elif page == "💰 Payment Reminders":
        payment_reminder_module()
    
    elif page == "📄 Policy Processing":
        policy_processing_module()
    
    elif page == "🧾 Cover Letter Generator":
        cover_letter_module()
    
    elif page == "📊 Database Viewer":
        database_viewer_module()


if __name__ == "__main__":
    main()
