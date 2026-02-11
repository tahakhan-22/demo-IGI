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
from database.models import (
    AutomationLog, Policy, Client, ClientAddress, ClientBank,
    PolicySchedule, VehicleDetail, DiscountType, PolicyDiscount,
    DepreciationExcess, DeductibleInsurance, ClauseMaster, PolicyClause,
    Warranty, Agent, PolicyAgent, DocumentDescription
)
from automation.gmail_service import GmailService
from automation.email_parser import EmailParser
from automation.csv_scanner import CSVScanner
from automation.rpa_engine import RPAEngine
from services.policy_service import PolicyService
from services.premium_calculator import PremiumCalculator
from services.cover_letter_generator import CoverLetterGenerator
from config import COMPANY_NAME

# Constants
ADDRESS_TYPES = ['House', 'Office', 'Factory', 'Other']
POLICY_TYPES = ['New', 'Renewal', 'Endorsement']
INSTALLMENT_MODES = ['Single', 'Monthly', 'Quarterly', 'Half-Yearly', 'Yearly']
CLIENT_TYPES = ['Individual', 'Corporate']

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
                        CLIENT_TYPES,
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
                            ADDRESS_TYPES,
                            index=ADDRESS_TYPES.index(
                                parsed['client'].get('address_type', 'House')
                            ) if parsed['client'].get('address_type', 'House') in ADDRESS_TYPES else 0,
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
                        POLICY_TYPES,
                        index=POLICY_TYPES.index(
                            parsed['policy'].get('policy_type', 'New')
                        ) if parsed['policy'].get('policy_type', 'New') in POLICY_TYPES else 0,
                        key="form_policy_type")
                    region = st.text_input("Region", 
                        value=parsed['policy'].get('region', ''), key="form_region")
                
                with col3:
                    installment_mode = st.selectbox("Installment Mode", 
                        INSTALLMENT_MODES,
                        index=INSTALLMENT_MODES.index(
                            parsed['policy'].get('installment_mode', 'Single')
                        ) if parsed['policy'].get('installment_mode', 'Single') in INSTALLMENT_MODES else 0,
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
            policy_options = {f"{p.document_no} - {p.client.client_name}": p.policy_id for p in policies}
            
            selected = st.selectbox("Select Policy", list(policy_options.keys()), key="cover_letter_policy_select")
            
            if st.button("📄 Generate Cover Letter", key="generate_cover_letter_btn"):
                policy_id = policy_options[selected]
                
                with st.spinner("Generating cover letter..."):
                    session = get_session()
                    policy = session.query(Policy).filter_by(policy_id=policy_id).first()
                    
                    if policy:
                        # Prepare data
                        # Get primary address if exists
                        primary_address = None
                        if policy.client.addresses:
                            primary_address = next((a for a in policy.client.addresses if a.is_primary), policy.client.addresses[0])
                        
                        policy_data = {
                            'client': {
                                'name': policy.client.client_name,
                                'client_code': policy.client.client_code or 'N/A',
                                'cnic': policy.client.cnic_no or 'N/A',
                                'ntn': policy.client.ntn_no or 'N/A',
                                'address': primary_address.address_line if primary_address else 'N/A',
                                'city': primary_address.city if primary_address else 'N/A',
                                'phone': primary_address.phone_1 if primary_address else 'N/A',
                                'email': primary_address.email if primary_address else 'N/A'
                            },
                            'policy': {
                                'policy_number': policy.document_no,
                                'base_document_no': policy.base_document_no or 'N/A',
                                'business_class': policy.business_class or 'Motor',
                                'policy_type': policy.policy_type or 'New',
                                'coverage_type': 'Comprehensive',
                                'commencement_date': str(policy.comm_date),
                                'expiry_date': str(policy.expiry_date),
                                'issue_date': str(policy.issue_date),
                                'region': policy.region or 'N/A',
                                'geographical_limit': policy.geographical_limit or 'Pakistan',
                                'currency': policy.currency or 'PKR',
                                'sum_insured': policy.sum_insured,
                                'bodily_injury_lol': policy.bodily_injury_lol or 0,
                                'property_damage_lol': policy.property_damage_lol or 0
                            },
                            'premium': {
                                'basic_premium': policy.gross_premium,
                                'gross_premium': policy.gross_premium,
                                'total_discount': 0,  # Calculate from discounts
                                'net_premium': policy.gross_premium,  # After discounts
                                'total_charges': policy.charges or 0,
                                'premium_payable': policy.premium_payable
                            },
                            'clauses': [],
                            'warranties': []
                        }
                        
                        # Calculate total discounts
                        if policy.discounts:
                            total_discount = sum(d.amount for d in policy.discounts)
                            policy_data['premium']['total_discount'] = total_discount
                            policy_data['premium']['net_premium'] = policy.gross_premium - total_discount
                        
                        # Add vehicle if exists (from schedules)
                        if policy.schedules:
                            for schedule in policy.schedules:
                                if schedule.vehicle:
                                    vehicle = schedule.vehicle
                                    policy_data['vehicle'] = {
                                        'make_model': vehicle.make_model,
                                        'year_of_manufacturing': vehicle.year_of_manufacturing,
                                        'vehicle_age': vehicle.vehicle_age or 0,
                                        'engine_number': vehicle.engine_no,
                                        'chassis_number': vehicle.chassis_no,
                                        'registration_number': vehicle.registration_no or 'N/A',
                                        'color': vehicle.color or 'N/A',
                                        'passenger_capacity': vehicle.passenger_capacity or 'N/A',
                                        'body_type': vehicle.body_type or 'N/A',
                                        'power_cc': vehicle.power_cc or 'N/A',
                                        'keeper_name': vehicle.keeper_name or 'N/A',
                                        'accessories': vehicle.accessories or 'N/A'
                                    }
                                    break
                        
                        # Add clauses
                        if policy.policy_clauses:
                            for pc in policy.policy_clauses:
                                if pc.is_checked and pc.clause:
                                    policy_data['clauses'].append({
                                        'clause_code': pc.clause.clause_code,
                                        'clause_text': pc.clause.clause_name,
                                        'is_applicable': True,
                                        'limit': pc.clause_limit
                                    })
                        
                        # Add warranties
                        if policy.warranties:
                            for w in policy.warranties:
                                if w.is_applicable:
                                    policy_data['warranties'].append({
                                        'warranty_code': w.warranty_type or 'N/A',
                                        'warranty_text': w.description,
                                        'is_applicable': True,
                                        'tracker_details': w.tracker_details
                                    })
                        
                        # Generate letter
                        generator = CoverLetterGenerator()
                        letter = generator.generate_cover_letter(policy_data)
                        
                        st.subheader("📄 Cover Letter")
                        st.text_area("", letter, height=600, key="cover_letter_text")
                        
                        # Generate PDF
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📥 Download as PDF", key="download_pdf_btn"):
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
        tabs = st.tabs([
            "Policies", "Clients", "Addresses", "Vehicles", 
            "Schedules", "Discounts", "Clauses", "Warranties", 
            "Agents", "Documents"
        ])
        
        # Tab 0: Policies
        with tabs[0]:
            st.subheader("All Policies")
            policies = session.query(Policy).all()
            
            if policies:
                policy_data = []
                for p in policies:
                    policy_data.append({
                        'Document No': p.document_no,
                        'Client': p.client.client_name,
                        'Policy Type': p.policy_type or 'N/A',
                        'Commencement': str(p.comm_date),
                        'Expiry': str(p.expiry_date),
                        'Sum Insured': f"{p.currency} {p.sum_insured:,.2f}",
                        'Premium Payable': f"{p.currency} {p.premium_payable:,.2f}"
                    })
                
                df = pd.DataFrame(policy_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No policies found")
        
        # Tab 1: Clients
        with tabs[1]:
            st.subheader("All Clients")
            clients = session.query(Client).all()
            
            if clients:
                client_data = []
                for c in clients:
                    client_data.append({
                        'Client Code': c.client_code or 'N/A',
                        'Name': c.client_name,
                        'Type': c.client_type or 'N/A',
                        'CNIC': c.cnic_no or 'N/A',
                        'NTN': c.ntn_no or 'N/A',
                        'Policies': len(c.policies)
                    })
                
                df = pd.DataFrame(client_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No clients found")
        
        # Tab 2: Addresses
        with tabs[2]:
            st.subheader("Client Addresses")
            addresses = session.query(ClientAddress).all()
            
            if addresses:
                address_data = []
                for a in addresses:
                    address_data.append({
                        'Client': a.client.client_name,
                        'Type': a.address_type or 'N/A',
                        'Address': a.address_line,
                        'City': a.city,
                        'Country': a.country,
                        'Phone 1': a.phone_1 or 'N/A',
                        'Primary': '✓' if a.is_primary else '✗'
                    })
                
                df = pd.DataFrame(address_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No addresses found")
        
        # Tab 3: Vehicles
        with tabs[3]:
            st.subheader("All Vehicles")
            vehicles = session.query(VehicleDetail).all()
            
            if vehicles:
                vehicle_data = []
                for v in vehicles:
                    vehicle_data.append({
                        'Make/Model': v.make_model,
                        'Year': v.year_of_manufacturing,
                        'Age': v.vehicle_age or 'N/A',
                        'Engine No': v.engine_no,
                        'Chassis No': v.chassis_no,
                        'Registration': v.registration_no or 'N/A',
                        'Color': v.color or 'N/A',
                        'Sum Insured': f"PKR {v.sum_insured:,.2f}"
                    })
                
                df = pd.DataFrame(vehicle_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No vehicles found")
        
        # Tab 4: Schedules
        with tabs[4]:
            st.subheader("Policy Schedules")
            schedules = session.query(PolicySchedule).all()
            
            if schedules:
                schedule_data = []
                for s in schedules:
                    schedule_data.append({
                        'Policy': s.policy.document_no,
                        'Item No': s.item_no or 'N/A',
                        'Sum Insured': f"PKR {s.sum_insured:,.2f}",
                        'Basic Premium': f"PKR {s.basic_premium:,.2f}",
                        'Gross Premium': f"PKR {s.gross_premium:,.2f}",
                        'Risk/Peril Type': s.risk_peril_type or 'N/A'
                    })
                
                df = pd.DataFrame(schedule_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No schedules found")
        
        # Tab 5: Discounts
        with tabs[5]:
            st.subheader("Policy Discounts")
            discounts = session.query(PolicyDiscount).all()
            
            if discounts:
                discount_data = []
                for d in discounts:
                    discount_data.append({
                        'Policy': d.policy.document_no,
                        'Discount Type': d.discount_type.discount_name if d.discount_type else 'N/A',
                        'Rate %': d.rate_percent or 'N/A',
                        'Amount': f"PKR {d.amount:,.2f}"
                    })
                
                df = pd.DataFrame(discount_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No discounts found")
        
        # Tab 6: Clauses
        with tabs[6]:
            st.subheader("Policy Clauses")
            clauses = session.query(PolicyClause).all()
            
            if clauses:
                clause_data = []
                for c in clauses:
                    clause_data.append({
                        'Policy': c.policy.document_no,
                        'Clause Code': c.clause.clause_code if c.clause else 'N/A',
                        'Clause Name': c.clause.clause_name if c.clause else 'N/A',
                        'Limit': f"PKR {c.clause_limit:,.2f}" if c.clause_limit else 'N/A',
                        'Checked': '✓' if c.is_checked else '✗'
                    })
                
                df = pd.DataFrame(clause_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No clauses found")
        
        # Tab 7: Warranties
        with tabs[7]:
            st.subheader("Warranties")
            warranties = session.query(Warranty).all()
            
            if warranties:
                warranty_data = []
                for w in warranties:
                    warranty_data.append({
                        'Policy': w.policy.document_no,
                        'Type': w.warranty_type or 'N/A',
                        'Description': w.description[:50] + '...' if len(w.description) > 50 else w.description,
                        'Tracker Details': w.tracker_details[:30] + '...' if w.tracker_details and len(w.tracker_details) > 30 else w.tracker_details or 'N/A',
                        'Applicable': '✓' if w.is_applicable else '✗'
                    })
                
                df = pd.DataFrame(warranty_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No warranties found")
        
        # Tab 8: Agents
        with tabs[8]:
            st.subheader("Policy Agents & Commission")
            policy_agents = session.query(PolicyAgent).all()
            
            if policy_agents:
                agent_data = []
                for pa in policy_agents:
                    agent_data.append({
                        'Policy': pa.policy.document_no,
                        'Agent Code': pa.agent.agent_code if pa.agent else 'N/A',
                        'Agent Name': pa.agent.agent_name if pa.agent else 'N/A',
                        'Apportionment %': pa.apportionment_rate_percent,
                        'Commission': f"PKR {pa.commission_amount:,.2f}",
                        'Premium Share %': pa.premium_share_percent
                    })
                
                df = pd.DataFrame(agent_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No agent commissions found")
        
        # Tab 9: Documents
        with tabs[9]:
            st.subheader("Document Descriptions")
            documents = session.query(DocumentDescription).all()
            
            if documents:
                document_data = []
                for doc in documents:
                    document_data.append({
                        'Policy': doc.policy.document_no,
                        'Document Type': doc.document_type,
                        'Description': doc.description[:50] + '...' if len(doc.description) > 50 else doc.description,
                        'File Path': doc.file_path or 'N/A',
                        'Uploaded': str(doc.uploaded_at) if doc.uploaded_at else 'N/A'
                    })
                
                df = pd.DataFrame(document_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No documents found")
        
        session.close()
    
    except Exception as e:
        st.error(f"Error loading database viewer: {str(e)}")
        # Log full traceback for debugging
        import logging
        logging.exception("Database viewer error:")


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
