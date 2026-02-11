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
    
    # Fetch latest email
    if st.button("📥 Fetch Latest Email for Processing", key="fetch_email_btn"):
        with st.spinner("Fetching latest unread email..."):
            success, message, emails = gmail.read_unread_emails(max_results=1)
            
            if success and emails:
                email = emails[0]
                st.session_state.email_to_process = email
                st.success("Email fetched successfully!")
            else:
                st.error("No unread emails found")
    
    # Process email if available
    if 'email_to_process' in st.session_state:
        email = st.session_state.email_to_process
        
        st.subheader("📧 Email Content")
        st.text_area("Email Body", email['body'], height=200, key="email_body_display")
        
        # Parse email
        if st.button("🔍 Parse Email Data", key="parse_email_btn"):
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
                # ========================================
                # 1. CLIENT INFORMATION SECTION
                # ========================================
                st.write("**Client Information**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    client_code = st.text_input("Client Code", 
                        value=parsed['client'].get('client_code', ''), key="form_client_code")
                    client_name = st.text_input("Client Name", 
                        value=parsed['client'].get('client_name', ''), key="form_client_name")
                    client_type = st.selectbox("Client Type", 
                        ['Individual', 'Corporate'],
                        index=0 if parsed['client'].get('client_type', 'Individual') == 'Individual' else 1,
                        key="form_client_type")
                
                with col2:
                    cnic_no = st.text_input("CNIC No", 
                        value=parsed['client'].get('cnic_no', ''), key="form_cnic_no")
                    old_nic_no = st.text_input("Old NIC No", 
                        value=parsed['client'].get('old_nic_no', ''), key="form_old_nic_no")
                    ntn_no = st.text_input("NTN No", 
                        value=parsed['client'].get('ntn_no', ''), key="form_ntn_no")
                
                with col3:
                    passport_no = st.text_input("Passport No", 
                        value=parsed['client'].get('passport_no', ''), key="form_passport_no")
                
                # ========================================
                # 2. CLIENT ADDRESS SECTION (with expander)
                # ========================================
                with st.expander("📍 Client Address", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        address_type = st.selectbox("Address Type", 
                            ['House', 'Office', 'Factory', 'Other'],
                            index=['House', 'Office', 'Factory', 'Other'].index(
                                parsed['client'].get('address_type', 'House')
                            ) if parsed['client'].get('address_type', 'House') in ['House', 'Office', 'Factory', 'Other'] else 0,
                            key="form_address_type")
                        address_line = st.text_area("Address Line", 
                            value=parsed['client'].get('address_line', ''), height=100, key="form_address_line")
                        country = st.text_input("Country", 
                            value=parsed['client'].get('country', 'Pakistan'), key="form_country")
                        city = st.text_input("City", 
                            value=parsed['client'].get('city', ''), key="form_city")
                    
                    with col2:
                        phone_1 = st.text_input("Phone 1", 
                            value=parsed['client'].get('phone_1', ''), key="form_phone_1")
                        phone_2 = st.text_input("Phone 2", 
                            value=parsed['client'].get('phone_2', ''), key="form_phone_2")
                        fax = st.text_input("Fax", 
                            value=parsed['client'].get('fax', ''), key="form_fax")
                        email = st.text_input("Email", 
                            value=parsed['client'].get('email', ''), key="form_email")
                        is_primary = st.checkbox("Is Primary Address", value=True, key="form_is_primary")
                
                # ========================================
                # 3. VEHICLE DETAILS (OD) SECTION
                # ========================================
                st.write("**Vehicle Details (OD)**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    vehicle_sum_insured = st.number_input("Sum Insured (PKR)", 
                        value=float(parsed['policy'].get('sum_insured', 1000000)), 
                        min_value=0.0, step=10000.0, key="form_vehicle_sum_insured")
                    vehicle_policy_type = st.text_input("Policy Type", 
                        value=parsed['policy'].get('policy_type', 'New'), key="form_vehicle_policy_type")
                    applied_for_registration = st.selectbox("Applied for Registration", 
                        ['Yes', 'No'],
                        index=0 if parsed['vehicle'].get('applied_for_registration', 'No') == 'Yes' else 1,
                        key="form_applied_for_registration")
                    registration_no = st.text_input("Registration No", 
                        value=parsed['vehicle'].get('registration_no', ''), key="form_registration_no")
                    engine_no = st.text_input("Engine No", 
                        value=parsed['vehicle'].get('engine_no', ''), key="form_engine_no")
                
                with col2:
                    chassis_no = st.text_input("Chassis No", 
                        value=parsed['vehicle'].get('chassis_no', ''), key="form_chassis_no")
                    make_model = st.text_input("Make/Model", 
                        value=parsed['vehicle'].get('make_model', ''), key="form_make_model")
                    passenger_capacity = st.number_input("Passenger Capacity", 
                        value=parsed['vehicle'].get('passenger_capacity', 5), 
                        min_value=1, max_value=100, key="form_passenger_capacity")
                    body_type = st.text_input("Body Type", 
                        value=parsed['vehicle'].get('body_type', ''), key="form_body_type")
                    power_cc = st.number_input("Power (CC)", 
                        value=parsed['vehicle'].get('power_cc', 1000), 
                        min_value=0, max_value=10000, key="form_power_cc")
                
                with col3:
                    color = st.text_input("Color", 
                        value=parsed['vehicle'].get('color', ''), key="form_color")
                    year_of_manufacturing = st.number_input("Year of Manufacturing", 
                        value=parsed['vehicle'].get('year_of_manufacturing', 2024), 
                        min_value=1990, max_value=2030, key="form_year_of_manufacturing")
                    vehicle_age = datetime.now().year - year_of_manufacturing
                    st.text_input("Vehicle Age (Auto-calculated)", 
                        value=f"{vehicle_age} years", disabled=True, key="form_vehicle_age_display")
                    keeper_name = st.text_input("Keeper Name", 
                        value=parsed['vehicle'].get('keeper_name', ''), key="form_keeper_name")
                    keeper_address = st.text_area("Keeper Address", 
                        value=parsed['vehicle'].get('keeper_address', ''), height=70, key="form_keeper_address")
                
                # Additional vehicle fields
                col1, col2 = st.columns(2)
                with col1:
                    accessories = st.text_area("Accessories", 
                        value=parsed['vehicle'].get('accessories', ''), height=60, key="form_accessories")
                    accessories_sum_insured = st.number_input("Accessories Sum Insured (PKR)", 
                        value=float(parsed['vehicle'].get('accessories_sum_insured', 0)), 
                        min_value=0.0, step=1000.0, key="form_accessories_sum_insured")
                    license_no = st.text_input("License No", 
                        value=parsed['vehicle'].get('license_no', ''), key="form_license_no")
                
                with col2:
                    purchase_order_loan_no = st.text_input("Purchase Order/Loan No", 
                        value=parsed['vehicle'].get('purchase_order_loan_no', ''), key="form_purchase_order_loan_no")
                    other_information = st.text_area("Other Information", 
                        value=parsed['vehicle'].get('other_information', ''), height=60, key="form_other_information")
                    vehicle_mobile_phone = st.text_input("Mobile Phone", 
                        value=parsed['vehicle'].get('mobile_phone', ''), key="form_vehicle_mobile_phone")
                    vehicle_email = st.text_input("Vehicle Email", 
                        value=parsed['vehicle'].get('email', ''), key="form_vehicle_email")
                
                # ========================================
                # 4. POLICY INFORMATION SECTION
                # ========================================
                st.write("**Policy Information**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    base_document_no = st.text_input("Base Document No", 
                        value=parsed['policy'].get('base_document_no', ''), key="form_base_document_no")
                    document_no = st.text_input("Document No", 
                        value=parsed['policy'].get('document_no', ''), key="form_document_no")
                    business_class = st.text_input("Business Class", 
                        value=parsed['policy'].get('business_class', 'Motor'), key="form_business_class")
                    issue_date = st.date_input("Issue Date", 
                        value=datetime.now().date(), key="form_issue_date")
                
                with col2:
                    comm_date = st.date_input("Commencement Date", 
                        value=datetime.now().date(), key="form_comm_date")
                    expiry_date = st.date_input("Expiry Date", 
                        value=(datetime.now() + timedelta(days=365)).date(), key="form_expiry_date")
                    policy_type = st.selectbox("Policy Type", 
                        ['New', 'Renewal', 'Endorsement'],
                        index=['New', 'Renewal', 'Endorsement'].index(
                            parsed['policy'].get('policy_type', 'New')
                        ) if parsed['policy'].get('policy_type', 'New') in ['New', 'Renewal', 'Endorsement'] else 0,
                        key="form_policy_type")
                    region = st.text_input("Region", 
                        value=parsed['policy'].get('region', ''), key="form_region")
                
                with col3:
                    installment_mode = st.selectbox("Installment Mode", 
                        ['Single', 'Monthly', 'Quarterly', 'Half-Yearly', 'Yearly'],
                        index=['Single', 'Monthly', 'Quarterly', 'Half-Yearly', 'Yearly'].index(
                            parsed['policy'].get('installment_mode', 'Single')
                        ) if parsed['policy'].get('installment_mode', 'Single') in ['Single', 'Monthly', 'Quarterly', 'Half-Yearly', 'Yearly'] else 0,
                        key="form_installment_mode")
                    geographical_limit = st.text_input("Geographical Limit", 
                        value=parsed['policy'].get('geographical_limit', 'Pakistan'), key="form_geographical_limit")
                    currency = st.text_input("Currency", 
                        value=parsed['policy'].get('currency', 'PKR'), key="form_currency")
                    bodily_injury_lol = st.number_input("Bodily Injury LOL (PKR)", 
                        value=float(parsed['policy'].get('bodily_injury_lol', 0)), 
                        min_value=0.0, step=10000.0, key="form_bodily_injury_lol")
                
                # Additional policy fields
                col1, col2, col3 = st.columns(3)
                with col1:
                    property_damage_lol = st.number_input("Property Damage LOL (PKR)", 
                        value=float(parsed['policy'].get('property_damage_lol', 0)), 
                        min_value=0.0, step=10000.0, key="form_property_damage_lol")
                    sum_insured = st.number_input("Sum Insured (PKR)", 
                        value=float(parsed['policy'].get('sum_insured', 1000000)), 
                        min_value=0.0, step=10000.0, key="form_sum_insured")
                
                with col2:
                    gross_premium = st.number_input("Gross Premium (PKR)", 
                        value=float(parsed['policy'].get('gross_premium', 0)), 
                        min_value=0.0, step=100.0, key="form_gross_premium")
                    charges = st.number_input("Charges (PKR)", 
                        value=float(parsed['policy'].get('charges', 0)), 
                        min_value=0.0, step=100.0, key="form_charges")
                
                with col3:
                    premium_payable = st.number_input("Premium Payable (PKR)", 
                        value=float(parsed['policy'].get('premium_payable', 0)), 
                        min_value=0.0, step=100.0, key="form_premium_payable")
                
                # Calculate premium if values not provided
                if gross_premium == 0:
                    calculator = PremiumCalculator()
                    premium = calculator.calculate_motor_premium(
                        sum_insured=sum_insured,
                        vehicle_age=vehicle_age,
                        policy_type='comprehensive'
                    )
                    
                    st.write("**Premium Calculation (Auto)**")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Gross Premium", f"PKR {premium['gross_premium']:,.2f}")
                        st.metric("Net Premium", f"PKR {premium['net_premium']:,.2f}")
                    
                    with col2:
                        st.metric("Total Charges", f"PKR {premium['total_charges']:,.2f}")
                        st.metric("Total Discount", f"PKR {premium['total_discount']:,.2f}")
                    
                    with col3:
                        st.metric("Premium Payable", f"PKR {premium['premium_payable']:,.2f}")
                    
                    # Update values with calculated premium
                    gross_premium = premium['gross_premium']
                    charges = premium['total_charges']
                    premium_payable = premium['premium_payable']
                
                # Submit button
                submitted = st.form_submit_button("✅ Complete Policy")
                
                if submitted:
                    with st.spinner("Processing policy..."):
                        policy_service = PolicyService()
                        
                        # Create client
                        client_data = {
                            'client_code': client_code,
                            'client_name': client_name,
                            'client_type': client_type,
                            'cnic_no': cnic_no,
                            'old_nic_no': old_nic_no,
                            'ntn_no': ntn_no,
                            'passport_no': passport_no
                        }
                        
                        success, message, client = policy_service.create_client(client_data)
                        
                        if success:
                            # Create client address
                            address_data = {
                                'address_type': address_type,
                                'address_line': address_line,
                                'country': country,
                                'city': city,
                                'phone_1': phone_1,
                                'phone_2': phone_2,
                                'fax': fax,
                                'email': email,
                                'is_primary': is_primary
                            }
                            policy_service.create_client_address(address_data, client.client_id)
                            
                            # Create policy
                            policy_data = {
                                'base_document_no': base_document_no,
                                'document_no': document_no,
                                'business_class': business_class,
                                'issue_date': issue_date,
                                'comm_date': comm_date,
                                'expiry_date': expiry_date,
                                'policy_type': policy_type,
                                'region': region,
                                'installment_mode': installment_mode,
                                'geographical_limit': geographical_limit,
                                'currency': currency,
                                'sum_insured': sum_insured,
                                'gross_premium': gross_premium,
                                'charges': charges,
                                'premium_payable': premium_payable,
                                'bodily_injury_lol': bodily_injury_lol,
                                'property_damage_lol': property_damage_lol
                            }
                            
                            success, message, policy = policy_service.create_policy(
                                policy_data, client.client_id
                            )
                            
                            if success:
                                # Create policy schedule first
                                schedule_data = {
                                    'sum_insured': vehicle_sum_insured
                                }
                                success, message, schedule = policy_service.create_policy_schedule(
                                    schedule_data, policy.policy_id
                                )
                                
                                if success:
                                    # Create vehicle with schedule_id
                                    vehicle_data = {
                                        'sum_insured': vehicle_sum_insured,
                                        'policy_type': vehicle_policy_type,
                                        'applied_for_registration': applied_for_registration,
                                        'registration_no': registration_no,
                                        'engine_no': engine_no,
                                        'chassis_no': chassis_no,
                                        'make_model': make_model,
                                        'passenger_capacity': passenger_capacity,
                                        'body_type': body_type,
                                        'power_cc': power_cc,
                                        'color': color,
                                        'year_of_manufacturing': year_of_manufacturing,
                                        'keeper_name': keeper_name,
                                        'keeper_address': keeper_address,
                                        'accessories': accessories,
                                        'accessories_sum_insured': accessories_sum_insured,
                                        'license_no': license_no,
                                        'purchase_order_loan_no': purchase_order_loan_no,
                                        'other_information': other_information,
                                        'mobile_phone': vehicle_mobile_phone,
                                        'email': vehicle_email
                                    }
                                    
                                    success, message, vehicle = policy_service.create_vehicle(
                                        vehicle_data, schedule.schedule_id
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
                                        st.info(f"Policy Document No: {policy.document_no}")
                                        
                                        # Store for cover letter generation
                                        st.session_state.created_policy_id = policy.policy_id
                                        
                                        # Mark email as read
                                        gmail.mark_as_read(email['id'])
                                    else:
                                        st.error(f"Error creating vehicle: {message}")
                                else:
                                    st.error(f"Error creating schedule: {message}")
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
