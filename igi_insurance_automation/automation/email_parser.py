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
        
        # Name extraction (look for "Name:" or "Client Name:")
        name_pattern = r'(?:Client\s+)?Name\s*[:\-]\s*([A-Za-z\s\.]+)'
        name_match = re.search(name_pattern, text, re.IGNORECASE)
        if name_match:
            client['name'] = name_match.group(1).strip()
        
        # CNIC extraction (format: 12345-1234567-1 or 1234512345671)
        cnic_pattern = r'CNIC\s*[:\-]\s*(\d{5}[\-]?\d{7}[\-]?\d{1})'
        cnic_match = re.search(cnic_pattern, text, re.IGNORECASE)
        if cnic_match:
            client['cnic'] = cnic_match.group(1).strip()
        
        # Phone extraction
        phone_pattern = r'(?:Phone|Mobile|Contact)\s*[:\-]\s*([\+\d\-\(\)\s]{10,20})'
        phone_match = re.search(phone_pattern, text, re.IGNORECASE)
        if phone_match:
            client['phone'] = phone_match.group(1).strip()
        
        # Email extraction
        email_pattern = r'Email\s*[:\-]\s*([\w\.\-]+@[\w\.\-]+\.\w+)'
        email_match = re.search(email_pattern, text, re.IGNORECASE)
        if email_match:
            client['email'] = email_match.group(1).strip()
        
        # Address extraction
        address_pattern = r'Address\s*[:\-]\s*([A-Za-z0-9\s\,\.]+(?:\n[A-Za-z0-9\s\,\.]+)?)'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            client['address'] = address_match.group(1).strip()
        
        # City extraction
        city_pattern = r'City\s*[:\-]\s*([A-Za-z\s]+)'
        city_match = re.search(city_pattern, text, re.IGNORECASE)
        if city_match:
            client['city'] = city_match.group(1).strip()
        
        return client
    
    def _extract_vehicle_info(self, text):
        """Extract vehicle information"""
        vehicle = {}
        
        # Vehicle Make
        make_pattern = r'(?:Vehicle\s+)?Make\s*[:\-]\s*([A-Za-z\s]+)'
        make_match = re.search(make_pattern, text, re.IGNORECASE)
        if make_match:
            vehicle['make'] = make_match.group(1).strip()
        
        # Vehicle Model
        model_pattern = r'Model\s*[:\-]\s*([A-Za-z0-9\s\-]+)'
        model_match = re.search(model_pattern, text, re.IGNORECASE)
        if model_match:
            vehicle['model'] = model_match.group(1).strip()
        
        # Year
        year_pattern = r'(?:Year|Manufacturing\s+Year)\s*[:\-]\s*(\d{4})'
        year_match = re.search(year_pattern, text, re.IGNORECASE)
        if year_match:
            vehicle['year'] = int(year_match.group(1))
        
        # Engine Number
        engine_pattern = r'Engine\s*(?:Number|#|No\.?)\s*[:\-]\s*([A-Za-z0-9\-]+)'
        engine_match = re.search(engine_pattern, text, re.IGNORECASE)
        if engine_match:
            vehicle['engine_number'] = engine_match.group(1).strip()
        
        # Chassis Number
        chassis_pattern = r'Chassis\s*(?:Number|#|No\.?)\s*[:\-]\s*([A-Za-z0-9\-]+)'
        chassis_match = re.search(chassis_pattern, text, re.IGNORECASE)
        if chassis_match:
            vehicle['chassis_number'] = chassis_match.group(1).strip()
        
        # Registration Number
        reg_pattern = r'Registration\s*(?:Number|#|No\.?)\s*[:\-]\s*([A-Za-z0-9\-\s]+)'
        reg_match = re.search(reg_pattern, text, re.IGNORECASE)
        if reg_match:
            vehicle['registration_number'] = reg_match.group(1).strip()
        
        # Color
        color_pattern = r'Color\s*[:\-]\s*([A-Za-z\s]+)'
        color_match = re.search(color_pattern, text, re.IGNORECASE)
        if color_match:
            vehicle['color'] = color_match.group(1).strip()
        
        # Fuel Type
        fuel_pattern = r'Fuel\s*(?:Type)?\s*[:\-]\s*(Petrol|Diesel|Electric|Hybrid|CNG)'
        fuel_match = re.search(fuel_pattern, text, re.IGNORECASE)
        if fuel_match:
            vehicle['fuel_type'] = fuel_match.group(1).strip()
        
        return vehicle
    
    def _extract_policy_info(self, text):
        """Extract policy information"""
        policy = {}
        
        # Policy Type
        policy_type_pattern = r'(?:Policy\s+)?Type\s*[:\-]\s*([A-Za-z\s]+)'
        policy_type_match = re.search(policy_type_pattern, text, re.IGNORECASE)
        if policy_type_match:
            policy['policy_type'] = policy_type_match.group(1).strip()
        
        # Sum Insured
        sum_insured_pattern = r'Sum\s+Insured\s*[:\-]\s*(?:PKR|Rs\.?)?\s*([\d,\.]+)'
        sum_insured_match = re.search(sum_insured_pattern, text, re.IGNORECASE)
        if sum_insured_match:
            amount_str = sum_insured_match.group(1).replace(',', '')
            try:
                policy['sum_insured'] = float(amount_str)
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
