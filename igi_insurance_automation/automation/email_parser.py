"""
Email parser for extracting structured data from emails
Uses regex and NLP for data extraction
"""

import re
from datetime import datetime


class EmailParser:
    """Parser for extracting structured insurance data from emails"""
    
    def __init__(self):
        self.extracted_data = {}
    
    def parse_email(self, email_body):
        """Parse email body and extract structured data"""
        self.extracted_data = {
            'client': self._extract_client_info(email_body),
            'vehicle': self._extract_vehicle_info(email_body),
            'policy': self._extract_policy_info(email_body),
            'notes': self._extract_notes(email_body)
        }
        return self.extracted_data
    
    def _extract_client_info(self, text):
        """Extract client information"""
        client = {}
        
        # Client Code extraction
        client_code_pattern = r'Client\s+Code\s*[:\-]\s*([A-Za-z0-9\-]+)'
        client_code_match = re.search(client_code_pattern, text, re.IGNORECASE)
        if client_code_match:
            client['client_code'] = client_code_match.group(1).strip()
        
        # Name extraction (look for "Name:" or "Client Name:")
        name_pattern = r'(?:Client\s+)?Name\s*[:\-]\s*([A-Za-z\s\.]+)'
        name_match = re.search(name_pattern, text, re.IGNORECASE)
        if name_match:
            client['client_name'] = name_match.group(1).strip()
        
        # Client Type extraction
        client_type_pattern = r'Client\s+Type\s*[:\-]\s*(Individual|Corporate)'
        client_type_match = re.search(client_type_pattern, text, re.IGNORECASE)
        if client_type_match:
            client['client_type'] = client_type_match.group(1).strip()
        
        # CNIC extraction (format: 12345-1234567-1 or 1234512345671)
        cnic_pattern = r'CNIC\s*(?:No\.?|Number)?\s*[:\-]\s*(\d{5}[\-]?\d{7}[\-]?\d{1})'
        cnic_match = re.search(cnic_pattern, text, re.IGNORECASE)
        if cnic_match:
            client['cnic_no'] = cnic_match.group(1).strip()
        
        # Old NIC extraction
        old_nic_pattern = r'Old\s+(?:NIC|N\.I\.C\.)\s*(?:No\.?|Number)?\s*[:\-]\s*([A-Za-z0-9\-]+)'
        old_nic_match = re.search(old_nic_pattern, text, re.IGNORECASE)
        if old_nic_match:
            client['old_nic_no'] = old_nic_match.group(1).strip()
        
        # NTN extraction
        ntn_pattern = r'NTN\s*(?:No\.?|Number)?\s*[:\-]\s*([A-Za-z0-9\-]+)'
        ntn_match = re.search(ntn_pattern, text, re.IGNORECASE)
        if ntn_match:
            client['ntn_no'] = ntn_match.group(1).strip()
        
        # Passport extraction
        passport_pattern = r'Passport\s*(?:No\.?|Number)?\s*[:\-]\s*([A-Za-z0-9\-]+)'
        passport_match = re.search(passport_pattern, text, re.IGNORECASE)
        if passport_match:
            client['passport_no'] = passport_match.group(1).strip()
        
        # Phone extraction (primary)
        phone_pattern = r'(?:Phone|Mobile|Contact)\s*(?:1)?\s*[:\-]\s*([\+\d\-\(\)\s]{10,20})'
        phone_match = re.search(phone_pattern, text, re.IGNORECASE)
        if phone_match:
            client['phone_1'] = phone_match.group(1).strip()
        
        # Phone 2 extraction
        phone2_pattern = r'(?:Phone|Mobile|Contact)\s*2\s*[:\-]\s*([\+\d\-\(\)\s]{10,20})'
        phone2_match = re.search(phone2_pattern, text, re.IGNORECASE)
        if phone2_match:
            client['phone_2'] = phone2_match.group(1).strip()
        
        # Fax extraction
        fax_pattern = r'Fax\s*[:\-]\s*([\+\d\-\(\)\s]{10,20})'
        fax_match = re.search(fax_pattern, text, re.IGNORECASE)
        if fax_match:
            client['fax'] = fax_match.group(1).strip()
        
        # Email extraction
        email_pattern = r'Email\s*[:\-]\s*([\w\.\-]+@[\w\.\-]+\.\w+)'
        email_match = re.search(email_pattern, text, re.IGNORECASE)
        if email_match:
            client['email'] = email_match.group(1).strip()
        
        # Address Type extraction
        address_type_pattern = r'Address\s+Type\s*[:\-]\s*(House|Office|Factory|Other)'
        address_type_match = re.search(address_type_pattern, text, re.IGNORECASE)
        if address_type_match:
            client['address_type'] = address_type_match.group(1).strip()
        
        # Address extraction
        address_pattern = r'Address(?:\s+Line)?\s*[:\-]\s*([A-Za-z0-9\s\,\.]+(?:\n[A-Za-z0-9\s\,\.]+)?)'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            client['address_line'] = address_match.group(1).strip()
        
        # Country extraction
        country_pattern = r'Country\s*[:\-]\s*([A-Za-z\s]+)'
        country_match = re.search(country_pattern, text, re.IGNORECASE)
        if country_match:
            client['country'] = country_match.group(1).strip()
        else:
            client['country'] = 'Pakistan'  # Default
        
        # City extraction
        city_pattern = r'City\s*[:\-]\s*([A-Za-z\s]+)'
        city_match = re.search(city_pattern, text, re.IGNORECASE)
        if city_match:
            client['city'] = city_match.group(1).strip()
        
        return client
    
    def _extract_vehicle_info(self, text):
        """Extract vehicle information"""
        vehicle = {}
        
        # Make/Model (combined)
        make_model_pattern = r'Make(?:\s+/\s*Model|\s+&\s+Model)?\s*[:\-]\s*([A-Za-z0-9\s\-/]+)'
        make_model_match = re.search(make_model_pattern, text, re.IGNORECASE)
        if make_model_match:
            vehicle['make_model'] = make_model_match.group(1).strip()
        
        # Vehicle Make (separate)
        make_pattern = r'(?:Vehicle\s+)?Make\s*[:\-]\s*([A-Za-z\s]+)'
        make_match = re.search(make_pattern, text, re.IGNORECASE)
        if make_match:
            vehicle['make'] = make_match.group(1).strip()
        
        # Vehicle Model (separate)
        model_pattern = r'Model\s*[:\-]\s*([A-Za-z0-9\s\-]+)'
        model_match = re.search(model_pattern, text, re.IGNORECASE)
        if model_match:
            vehicle['model'] = model_match.group(1).strip()
        
        # Year of Manufacturing
        year_pattern = r'(?:Year|Manufacturing\s+Year|Year\s+of\s+Manufacturing)\s*[:\-]\s*(\d{4})'
        year_match = re.search(year_pattern, text, re.IGNORECASE)
        if year_match:
            vehicle['year_of_manufacturing'] = int(year_match.group(1))
        
        # Engine Number
        engine_pattern = r'Engine\s*(?:Number|#|No\.?)\s*[:\-]\s*([A-Za-z0-9\-]+)'
        engine_match = re.search(engine_pattern, text, re.IGNORECASE)
        if engine_match:
            vehicle['engine_no'] = engine_match.group(1).strip()
        
        # Chassis Number
        chassis_pattern = r'Chassis\s*(?:Number|#|No\.?)\s*[:\-]\s*([A-Za-z0-9\-]+)'
        chassis_match = re.search(chassis_pattern, text, re.IGNORECASE)
        if chassis_match:
            vehicle['chassis_no'] = chassis_match.group(1).strip()
        
        # Registration Number
        reg_pattern = r'Registration\s*(?:Number|#|No\.?)\s*[:\-]\s*([A-Za-z0-9\-\s]+)'
        reg_match = re.search(reg_pattern, text, re.IGNORECASE)
        if reg_match:
            vehicle['registration_no'] = reg_match.group(1).strip()
        
        # Applied for Registration
        applied_reg_pattern = r'Applied\s+for\s+Registration\s*[:\-]\s*(Yes|No)'
        applied_reg_match = re.search(applied_reg_pattern, text, re.IGNORECASE)
        if applied_reg_match:
            vehicle['applied_for_registration'] = applied_reg_match.group(1).strip()
        
        # Passenger Capacity
        passenger_pattern = r'(?:Passenger\s+)?Capacity\s*[:\-]\s*(\d+)'
        passenger_match = re.search(passenger_pattern, text, re.IGNORECASE)
        if passenger_match:
            vehicle['passenger_capacity'] = int(passenger_match.group(1))
        
        # Body Type
        body_type_pattern = r'Body\s+Type\s*[:\-]\s*([A-Za-z\s]+)'
        body_type_match = re.search(body_type_pattern, text, re.IGNORECASE)
        if body_type_match:
            vehicle['body_type'] = body_type_match.group(1).strip()
        
        # Power (CC)
        power_cc_pattern = r'(?:Power|Engine\s+Capacity|CC)\s*[:\-]\s*(\d+)\s*(?:cc|CC)?'
        power_cc_match = re.search(power_cc_pattern, text, re.IGNORECASE)
        if power_cc_match:
            vehicle['power_cc'] = int(power_cc_match.group(1))
        
        # Color
        color_pattern = r'Colo[u]?r\s*[:\-]\s*([A-Za-z\s]+)'
        color_match = re.search(color_pattern, text, re.IGNORECASE)
        if color_match:
            vehicle['color'] = color_match.group(1).strip()
        
        # Keeper Name
        keeper_name_pattern = r'Keeper\s+Name\s*[:\-]\s*([A-Za-z\s\.]+)'
        keeper_name_match = re.search(keeper_name_pattern, text, re.IGNORECASE)
        if keeper_name_match:
            vehicle['keeper_name'] = keeper_name_match.group(1).strip()
        
        # Keeper Address
        keeper_address_pattern = r'Keeper\s+Address\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|$)'
        keeper_address_match = re.search(keeper_address_pattern, text, re.IGNORECASE | re.DOTALL)
        if keeper_address_match:
            vehicle['keeper_address'] = keeper_address_match.group(1).strip()
        
        # Accessories
        accessories_pattern = r'Accessories\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|$)'
        accessories_match = re.search(accessories_pattern, text, re.IGNORECASE | re.DOTALL)
        if accessories_match:
            vehicle['accessories'] = accessories_match.group(1).strip()
        
        # Accessories Sum Insured
        acc_sum_pattern = r'Accessories\s+Sum\s+Insured\s*[:\-]\s*(?:PKR|Rs\.?)?\s*([\d,\.]+)'
        acc_sum_match = re.search(acc_sum_pattern, text, re.IGNORECASE)
        if acc_sum_match:
            amount_str = acc_sum_match.group(1).replace(',', '')
            try:
                vehicle['accessories_sum_insured'] = float(amount_str)
            except ValueError:
                pass
        
        # License Number
        license_pattern = r'License\s*(?:Number|#|No\.?)\s*[:\-]\s*([A-Za-z0-9\-]+)'
        license_match = re.search(license_pattern, text, re.IGNORECASE)
        if license_match:
            vehicle['license_no'] = license_match.group(1).strip()
        
        # Purchase Order / Loan Number
        po_loan_pattern = r'(?:Purchase\s+Order|PO|Loan)\s*(?:Number|#|No\.?)?\s*[:\-]\s*([A-Za-z0-9\-]+)'
        po_loan_match = re.search(po_loan_pattern, text, re.IGNORECASE)
        if po_loan_match:
            vehicle['purchase_order_loan_no'] = po_loan_match.group(1).strip()
        
        # Mobile Phone
        mobile_pattern = r'(?:Vehicle\s+)?Mobile\s*(?:Phone)?\s*[:\-]\s*([\+\d\-\(\)\s]{10,20})'
        mobile_match = re.search(mobile_pattern, text, re.IGNORECASE)
        if mobile_match:
            vehicle['mobile_phone'] = mobile_match.group(1).strip()
        
        # Vehicle Email
        vehicle_email_pattern = r'Vehicle\s+Email\s*[:\-]\s*([\w\.\-]+@[\w\.\-]+\.\w+)'
        vehicle_email_match = re.search(vehicle_email_pattern, text, re.IGNORECASE)
        if vehicle_email_match:
            vehicle['email'] = vehicle_email_match.group(1).strip()
        
        # Other Information
        other_info_pattern = r'Other\s+Information\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|$)'
        other_info_match = re.search(other_info_pattern, text, re.IGNORECASE | re.DOTALL)
        if other_info_match:
            vehicle['other_information'] = other_info_match.group(1).strip()
        
        return vehicle
    
    def _extract_policy_info(self, text):
        """Extract policy information"""
        policy = {}
        
        # Base Document Number
        base_doc_pattern = r'Base\s+Document\s+(?:Number|No\.?)\s*[:\-]\s*([A-Za-z0-9\-/]+)'
        base_doc_match = re.search(base_doc_pattern, text, re.IGNORECASE)
        if base_doc_match:
            policy['base_document_no'] = base_doc_match.group(1).strip()
        
        # Document Number
        doc_no_pattern = r'Document\s+(?:Number|No\.?)\s*[:\-]\s*([A-Za-z0-9\-/]+)'
        doc_no_match = re.search(doc_no_pattern, text, re.IGNORECASE)
        if doc_no_match:
            policy['document_no'] = doc_no_match.group(1).strip()
        
        # Business Class
        business_class_pattern = r'Business\s+Class\s*[:\-]\s*([A-Za-z\s]+)'
        business_class_match = re.search(business_class_pattern, text, re.IGNORECASE)
        if business_class_match:
            policy['business_class'] = business_class_match.group(1).strip()
        
        # Policy Type
        policy_type_pattern = r'(?:Policy\s+)?Type\s*[:\-]\s*(New|Renewal|Endorsement)'
        policy_type_match = re.search(policy_type_pattern, text, re.IGNORECASE)
        if policy_type_match:
            policy['policy_type'] = policy_type_match.group(1).strip()
        
        # Region
        region_pattern = r'Region\s*[:\-]\s*([A-Za-z\s]+)'
        region_match = re.search(region_pattern, text, re.IGNORECASE)
        if region_match:
            policy['region'] = region_match.group(1).strip()
        
        # Installment Mode
        installment_pattern = r'Installment\s+Mode\s*[:\-]\s*(Single|Monthly|Quarterly|Half-Yearly|Yearly)'
        installment_match = re.search(installment_pattern, text, re.IGNORECASE)
        if installment_match:
            policy['installment_mode'] = installment_match.group(1).strip()
        
        # Geographical Limit
        geo_limit_pattern = r'Geographical\s+Limit\s*[:\-]\s*([A-Za-z\s]+)'
        geo_limit_match = re.search(geo_limit_pattern, text, re.IGNORECASE)
        if geo_limit_match:
            policy['geographical_limit'] = geo_limit_match.group(1).strip()
        else:
            policy['geographical_limit'] = 'Pakistan'  # Default
        
        # Bodily Injury LOL
        bodily_injury_pattern = r'Bodily\s+Injury\s+(?:LOL|Limit)\s*[:\-]\s*(?:PKR|Rs\.?)?\s*([\d,\.]+)'
        bodily_injury_match = re.search(bodily_injury_pattern, text, re.IGNORECASE)
        if bodily_injury_match:
            amount_str = bodily_injury_match.group(1).replace(',', '')
            try:
                policy['bodily_injury_lol'] = float(amount_str)
            except ValueError:
                pass
        
        # Property Damage LOL
        property_damage_pattern = r'Property\s+Damage\s+(?:LOL|Limit)\s*[:\-]\s*(?:PKR|Rs\.?)?\s*([\d,\.]+)'
        property_damage_match = re.search(property_damage_pattern, text, re.IGNORECASE)
        if property_damage_match:
            amount_str = property_damage_match.group(1).replace(',', '')
            try:
                policy['property_damage_lol'] = float(amount_str)
            except ValueError:
                pass
        
        # Currency
        currency_pattern = r'Currency\s*[:\-]\s*([A-Z]{3})'
        currency_match = re.search(currency_pattern, text, re.IGNORECASE)
        if currency_match:
            policy['currency'] = currency_match.group(1).strip().upper()
        else:
            policy['currency'] = 'PKR'  # Default
        
        # Sum Insured
        sum_insured_pattern = r'Sum\s+Insured\s*[:\-]\s*(?:PKR|Rs\.?)?\s*([\d,\.]+)'
        sum_insured_match = re.search(sum_insured_pattern, text, re.IGNORECASE)
        if sum_insured_match:
            amount_str = sum_insured_match.group(1).replace(',', '')
            try:
                policy['sum_insured'] = float(amount_str)
            except ValueError:
                pass
        
        # Gross Premium
        gross_premium_pattern = r'Gross\s+Premium\s*[:\-]\s*(?:PKR|Rs\.?)?\s*([\d,\.]+)'
        gross_premium_match = re.search(gross_premium_pattern, text, re.IGNORECASE)
        if gross_premium_match:
            amount_str = gross_premium_match.group(1).replace(',', '')
            try:
                policy['gross_premium'] = float(amount_str)
            except ValueError:
                pass
        
        # Premium Payable
        premium_payable_pattern = r'Premium\s+Payable\s*[:\-]\s*(?:PKR|Rs\.?)?\s*([\d,\.]+)'
        premium_payable_match = re.search(premium_payable_pattern, text, re.IGNORECASE)
        if premium_payable_match:
            amount_str = premium_payable_match.group(1).replace(',', '')
            try:
                policy['premium_payable'] = float(amount_str)
            except ValueError:
                pass
        
        # Coverage Period
        coverage_pattern = r'Coverage\s+Period\s*[:\-]\s*(\d+)\s*(months?|years?)'
        coverage_match = re.search(coverage_pattern, text, re.IGNORECASE)
        if coverage_match:
            period = int(coverage_match.group(1))
            unit = coverage_match.group(2).lower()
            if 'year' in unit:
                period *= 12
            policy['coverage_months'] = period
        
        # Commencement Date
        commence_pattern = r'Commencement\s+Date\s*[:\-]\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
        commence_match = re.search(commence_pattern, text, re.IGNORECASE)
        if commence_match:
            policy['commencement_date'] = commence_match.group(1).strip()
        
        # Issue Date
        issue_pattern = r'Issue\s+Date\s*[:\-]\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
        issue_match = re.search(issue_pattern, text, re.IGNORECASE)
        if issue_match:
            policy['issue_date'] = issue_match.group(1).strip()
        
        # Expiry Date
        expiry_pattern = r'Expiry\s+Date\s*[:\-]\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
        expiry_match = re.search(expiry_pattern, text, re.IGNORECASE)
        if expiry_match:
            policy['expiry_date'] = expiry_match.group(1).strip()
        
        return policy
    
    def _extract_notes(self, text):
        """Extract additional notes or special instructions"""
        notes_pattern = r'(?:Notes?|Additional\s+Information|Special\s+Instructions)\s*[:\-]\s*(.+?)(?=\n\n|\Z)'
        notes_match = re.search(notes_pattern, text, re.IGNORECASE | re.DOTALL)
        if notes_match:
            return notes_match.group(1).strip()
        return ""
    
    def get_parsed_data(self):
        """Get the parsed data"""
        return self.extracted_data
