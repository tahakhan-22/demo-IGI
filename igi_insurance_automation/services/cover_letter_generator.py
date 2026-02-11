"""
Cover letter generator with PDF export
Generates structured insurance cover letters
"""

import sys
import os
from datetime import datetime
from fpdf import FPDF

# Handle imports for both module and direct execution
try:
    from ..config import COMPANY_NAME, COMPANY_ADDRESS, COMPANY_PHONE, COMPANY_EMAIL, PDF_OUTPUT_DIR
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import COMPANY_NAME, COMPANY_ADDRESS, COMPANY_PHONE, COMPANY_EMAIL, PDF_OUTPUT_DIR


class CoverLetterGenerator:
    """Generate insurance cover letters"""
    
    def __init__(self):
        self.pdf_output_dir = PDF_OUTPUT_DIR
    
    def generate_cover_letter(self, policy_data):
        """
        Generate cover letter content
        
        Args:
            policy_data: Dictionary containing all policy information
        
        Returns:
            String containing formatted cover letter
        """
        letter = []
        
        # Header
        letter.append("=" * 80)
        letter.append(f"{COMPANY_NAME}")
        letter.append(f"{COMPANY_ADDRESS}")
        letter.append(f"Phone: {COMPANY_PHONE} | Email: {COMPANY_EMAIL}")
        letter.append("=" * 80)
        letter.append("")
        letter.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
        letter.append("")
        
        # Client Details
        letter.append("INSURANCE COVER NOTE")
        letter.append("-" * 80)
        letter.append("")
        letter.append("CLIENT DETAILS:")
        client = policy_data.get('client', {})
        letter.append(f"  Client Code: {client.get('client_code', 'N/A')}")
        letter.append(f"  Name: {client.get('name', 'N/A')}")
        letter.append(f"  CNIC: {client.get('cnic', 'N/A')}")
        if client.get('ntn'):
            letter.append(f"  NTN: {client.get('ntn', 'N/A')}")
        letter.append(f"  Address: {client.get('address', 'N/A')}")
        letter.append(f"  City: {client.get('city', 'N/A')}")
        letter.append(f"  Phone: {client.get('phone', 'N/A')}")
        letter.append(f"  Email: {client.get('email', 'N/A')}")
        letter.append("")
        
        # Vehicle Details
        if 'vehicle' in policy_data:
            letter.append("VEHICLE DETAILS:")
            vehicle = policy_data['vehicle']
            letter.append(f"  Make & Model: {vehicle.get('make_model', 'N/A')}")
            letter.append(f"  Year of Manufacturing: {vehicle.get('year_of_manufacturing', 'N/A')}")
            letter.append(f"  Vehicle Age: {vehicle.get('vehicle_age', 'N/A')} years")
            letter.append(f"  Engine Number: {vehicle.get('engine_number', 'N/A')}")
            letter.append(f"  Chassis Number: {vehicle.get('chassis_number', 'N/A')}")
            letter.append(f"  Registration Number: {vehicle.get('registration_number', 'N/A')}")
            letter.append(f"  Color: {vehicle.get('color', 'N/A')}")
            if vehicle.get('passenger_capacity'):
                letter.append(f"  Passenger Capacity: {vehicle.get('passenger_capacity', 'N/A')}")
            if vehicle.get('body_type'):
                letter.append(f"  Body Type: {vehicle.get('body_type', 'N/A')}")
            if vehicle.get('power_cc'):
                letter.append(f"  Engine Capacity: {vehicle.get('power_cc', 'N/A')} cc")
            if vehicle.get('keeper_name'):
                letter.append(f"  Keeper Name: {vehicle.get('keeper_name', 'N/A')}")
            if vehicle.get('accessories') and vehicle['accessories'] != 'N/A':
                letter.append(f"  Accessories: {vehicle.get('accessories', 'N/A')}")
            letter.append("")
        
        # Policy Terms
        letter.append("POLICY TERMS:")
        policy = policy_data.get('policy', {})
        letter.append(f"  Policy Number: {policy.get('policy_number', 'N/A')}")
        if policy.get('base_document_no'):
            letter.append(f"  Base Document No: {policy.get('base_document_no', 'N/A')}")
        letter.append(f"  Business Class: {policy.get('business_class', 'Motor')}")
        letter.append(f"  Policy Type: {policy.get('policy_type', 'New')}")
        letter.append(f"  Coverage Type: {policy.get('coverage_type', 'Comprehensive')}")
        letter.append(f"  Issue Date: {policy.get('issue_date', 'N/A')}")
        letter.append(f"  Commencement Date: {policy.get('commencement_date', 'N/A')}")
        letter.append(f"  Expiry Date: {policy.get('expiry_date', 'N/A')}")
        letter.append(f"  Geographical Limit: {policy.get('geographical_limit', 'Pakistan')}")
        if policy.get('region'):
            letter.append(f"  Region: {policy.get('region', 'N/A')}")
        currency = policy.get('currency', 'PKR')
        letter.append(f"  Sum Insured: {currency} {policy.get('sum_insured', 0):,.2f}")
        if policy.get('bodily_injury_lol'):
            letter.append(f"  Bodily Injury Limit: {currency} {policy.get('bodily_injury_lol', 0):,.2f}")
        if policy.get('property_damage_lol'):
            letter.append(f"  Property Damage Limit: {currency} {policy.get('property_damage_lol', 0):,.2f}")
        letter.append("")
        
        # Premium Summary
        letter.append("PREMIUM SUMMARY:")
        premium = policy_data.get('premium', {})
        letter.append(f"  Basic Premium: {currency} {premium.get('basic_premium', 0):,.2f}")
        letter.append(f"  Gross Premium: {currency} {premium.get('gross_premium', 0):,.2f}")
        if premium.get('total_discount', 0) > 0:
            letter.append(f"  Total Discounts: {currency} {premium.get('total_discount', 0):,.2f}")
            letter.append(f"  Net Premium: {currency} {premium.get('net_premium', 0):,.2f}")
        letter.append("")
        letter.append("  Charges:")
        letter.append(f"    Total Charges: {currency} {premium.get('total_charges', 0):,.2f}")
        letter.append("")
        letter.append(f"  PREMIUM PAYABLE: {currency} {premium.get('premium_payable', 0):,.2f}")
        letter.append("")
        
        # Clauses
        if 'clauses' in policy_data and policy_data['clauses']:
            letter.append("POLICY CLAUSES:")
            for clause in policy_data['clauses']:
                if clause.get('is_applicable', True):
                    clause_line = f"  [{clause.get('clause_code', '')}] {clause.get('clause_text', '')}"
                    if clause.get('limit'):
                        clause_line += f" - Limit: {currency} {clause.get('limit'):,.2f}"
                    letter.append(clause_line)
            letter.append("")
        
        # Warranties
        if 'warranties' in policy_data and policy_data['warranties']:
            letter.append("WARRANTIES:")
            for warranty in policy_data['warranties']:
                if warranty.get('is_applicable', True):
                    warranty_line = f"  [{warranty.get('warranty_code', '')}] {warranty.get('warranty_text', '')}"
                    if warranty.get('tracker_details'):
                        warranty_line += f" - {warranty.get('tracker_details')}"
                    letter.append(warranty_line)
            letter.append("")
        
        # Footer
        letter.append("-" * 80)
        letter.append("This cover note is subject to the terms and conditions of the policy.")
        letter.append("Please review all details carefully.")
        letter.append("")
        letter.append("For any queries, please contact us at the above mentioned contact details.")
        letter.append("")
        letter.append("=" * 80)
        
        return "\n".join(letter)
    
    def generate_pdf(self, policy_data, filename=None):
        """
        Generate PDF cover letter
        
        Args:
            policy_data: Dictionary containing all policy information
            filename: Optional filename for PDF
        
        Returns:
            (success, message, file_path)
        """
        try:
            # Generate filename if not provided
            if not filename:
                policy_number = policy_data.get('policy', {}).get('policy_number', 'UNKNOWN')
                filename = f"cover_letter_{policy_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            file_path = os.path.join(self.pdf_output_dir, filename)
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            
            # Header
            pdf.cell(0, 10, COMPANY_NAME, 0, 1, 'C')
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, COMPANY_ADDRESS, 0, 1, 'C')
            pdf.cell(0, 5, f"Phone: {COMPANY_PHONE} | Email: {COMPANY_EMAIL}", 0, 1, 'C')
            pdf.ln(10)
            
            # Title
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'INSURANCE COVER NOTE', 0, 1, 'C')
            pdf.ln(5)
            
            # Date
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, f"Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1)
            pdf.ln(5)
            
            # Client Details
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'CLIENT DETAILS:', 0, 1)
            pdf.set_font('Arial', '', 10)
            client = policy_data.get('client', {})
            pdf.cell(0, 5, f"Name: {client.get('name', 'N/A')}", 0, 1)
            pdf.cell(0, 5, f"CNIC: {client.get('cnic', 'N/A')}", 0, 1)
            pdf.cell(0, 5, f"Address: {client.get('address', 'N/A')}", 0, 1)
            pdf.cell(0, 5, f"Phone: {client.get('phone', 'N/A')}", 0, 1)
            pdf.cell(0, 5, f"Email: {client.get('email', 'N/A')}", 0, 1)
            pdf.ln(5)
            
            # Vehicle Details
            if 'vehicle' in policy_data:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, 'VEHICLE DETAILS:', 0, 1)
                pdf.set_font('Arial', '', 10)
                vehicle = policy_data['vehicle']
                pdf.cell(0, 5, f"Make & Model: {vehicle.get('make', 'N/A')} {vehicle.get('model', 'N/A')}", 0, 1)
                pdf.cell(0, 5, f"Year: {vehicle.get('year_of_manufacturing', 'N/A')}", 0, 1)
                pdf.cell(0, 5, f"Engine No: {vehicle.get('engine_number', 'N/A')}", 0, 1)
                pdf.cell(0, 5, f"Chassis No: {vehicle.get('chassis_number', 'N/A')}", 0, 1)
                pdf.cell(0, 5, f"Registration: {vehicle.get('registration_number', 'N/A')}", 0, 1)
                pdf.ln(5)
            
            # Policy Terms
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'POLICY TERMS:', 0, 1)
            pdf.set_font('Arial', '', 10)
            policy = policy_data.get('policy', {})
            pdf.cell(0, 5, f"Policy Number: {policy.get('policy_number', 'N/A')}", 0, 1)
            pdf.cell(0, 5, f"Coverage: {policy.get('coverage_type', 'Comprehensive')}", 0, 1)
            pdf.cell(0, 5, f"Commencement: {policy.get('commencement_date', 'N/A')}", 0, 1)
            pdf.cell(0, 5, f"Expiry: {policy.get('expiry_date', 'N/A')}", 0, 1)
            pdf.cell(0, 5, f"Sum Insured: PKR {policy.get('sum_insured', 0):,.2f}", 0, 1)
            pdf.ln(5)
            
            # Premium Summary
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'PREMIUM SUMMARY:', 0, 1)
            pdf.set_font('Arial', '', 10)
            premium = policy_data.get('premium', {})
            pdf.cell(0, 5, f"Gross Premium: PKR {premium.get('gross_premium', 0):,.2f}", 0, 1)
            pdf.cell(0, 5, f"Total Discounts: PKR {premium.get('total_discount', 0):,.2f}", 0, 1)
            pdf.cell(0, 5, f"Net Premium: PKR {premium.get('net_premium', 0):,.2f}", 0, 1)
            pdf.cell(0, 5, f"Total Charges: PKR {premium.get('total_charges', 0):,.2f}", 0, 1)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 5, f"PREMIUM PAYABLE: PKR {premium.get('premium_payable', 0):,.2f}", 0, 1)
            pdf.ln(10)
            
            # Footer
            pdf.set_font('Arial', 'I', 9)
            pdf.multi_cell(0, 5, "This cover note is subject to the terms and conditions of the policy. Please review all details carefully.")
            
            # Save PDF
            pdf.output(file_path)
            
            return True, "PDF generated successfully", file_path
        
        except Exception as e:
            return False, f"Error generating PDF: {str(e)}", None
