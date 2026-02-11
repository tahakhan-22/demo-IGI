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
        letter.append(f"  Name: {client.get('name', 'N/A')}")
        letter.append(f"  CNIC: {client.get('cnic', 'N/A')}")
        letter.append(f"  Address: {client.get('address', 'N/A')}")
        letter.append(f"  Phone: {client.get('phone', 'N/A')}")
        letter.append(f"  Email: {client.get('email', 'N/A')}")
        letter.append("")
        
        # Vehicle Details
        if 'vehicle' in policy_data:
            letter.append("VEHICLE DETAILS:")
            vehicle = policy_data['vehicle']
            letter.append(f"  Make & Model: {vehicle.get('make', 'N/A')} {vehicle.get('model', 'N/A')}")
            letter.append(f"  Year of Manufacturing: {vehicle.get('year_of_manufacturing', 'N/A')}")
            letter.append(f"  Engine Number: {vehicle.get('engine_number', 'N/A')}")
            letter.append(f"  Chassis Number: {vehicle.get('chassis_number', 'N/A')}")
            letter.append(f"  Registration Number: {vehicle.get('registration_number', 'N/A')}")
            letter.append(f"  Color: {vehicle.get('color', 'N/A')}")
            letter.append(f"  Fuel Type: {vehicle.get('fuel_type', 'N/A')}")
            letter.append("")
        
        # Policy Terms
        letter.append("POLICY TERMS:")
        policy = policy_data.get('policy', {})
        letter.append(f"  Policy Number: {policy.get('policy_number', 'N/A')}")
        letter.append(f"  Coverage Type: {policy.get('coverage_type', 'Comprehensive')}")
        letter.append(f"  Commencement Date: {policy.get('commencement_date', 'N/A')}")
        letter.append(f"  Expiry Date: {policy.get('expiry_date', 'N/A')}")
        letter.append(f"  Sum Insured: PKR {policy.get('sum_insured', 0):,.2f}")
        letter.append("")
        
        # Premium Summary
        letter.append("PREMIUM SUMMARY:")
        premium = policy_data.get('premium', {})
        letter.append(f"  Basic Premium: PKR {premium.get('basic_premium', 0):,.2f}")
        letter.append(f"  Gross Premium: PKR {premium.get('gross_premium', 0):,.2f}")
        letter.append(f"  Total Discounts: PKR {premium.get('total_discount', 0):,.2f}")
        letter.append(f"  Net Premium: PKR {premium.get('net_premium', 0):,.2f}")
        letter.append("")
        letter.append("  Charges:")
        letter.append(f"    Stamp Duty: PKR {premium.get('stamp_duty', 0):,.2f}")
        letter.append(f"    FID Fee: PKR {premium.get('fid_fee', 0):,.2f}")
        letter.append(f"    Provincial Tax: PKR {premium.get('provincial_tax', 0):,.2f}")
        letter.append(f"  Total Charges: PKR {premium.get('total_charges', 0):,.2f}")
        letter.append("")
        letter.append(f"  PREMIUM PAYABLE: PKR {premium.get('premium_payable', 0):,.2f}")
        letter.append("")
        
        # Clauses
        if 'clauses' in policy_data and policy_data['clauses']:
            letter.append("POLICY CLAUSES:")
            for clause in policy_data['clauses']:
                if clause.get('is_applicable', True):
                    letter.append(f"  [{clause.get('clause_code', '')}] {clause.get('clause_text', '')}")
            letter.append("")
        
        # Warranties
        if 'warranties' in policy_data and policy_data['warranties']:
            letter.append("WARRANTIES:")
            for warranty in policy_data['warranties']:
                if warranty.get('is_applicable', True):
                    letter.append(f"  [{warranty.get('warranty_code', '')}] {warranty.get('warranty_text', '')}")
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
