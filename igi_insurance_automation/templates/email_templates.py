"""
Email templates for various automation scenarios
"""


class EmailTemplates:
    """Email templates for IGI Insurance automation"""
    
    @staticmethod
    def payment_reminder(client_name, amount_due, due_date):
        """Payment reminder email template"""
        subject = "Policy Payment Reminder"
        body = f"""Dear {client_name},

Your policy payment of PKR {amount_due} is due on {due_date}.
Please ensure payment to avoid lapse.

Regards,
IGI Insurance"""
        return subject, body
    
    @staticmethod
    def policy_confirmation(client_name, policy_number, commencement_date, expiry_date):
        """Policy confirmation email"""
        subject = f"Policy Confirmation - {policy_number}"
        body = f"""Dear {client_name},

Your insurance policy has been successfully issued.

Policy Number: {policy_number}
Coverage Period: {commencement_date} to {expiry_date}

Please review your policy documents attached with this email.

For any queries, please contact us at +92-51-111-444-111.

Best Regards,
IGI Insurance Limited"""
        return subject, body
    
    @staticmethod
    def claim_acknowledgment(client_name, claim_number):
        """Claim acknowledgment email"""
        subject = f"Claim Acknowledgment - {claim_number}"
        body = f"""Dear {client_name},

We have received your claim submission.

Claim Number: {claim_number}

Our claims team will review your submission and contact you within 2-3 business days.

Thank you for choosing IGI Insurance.

Best Regards,
Claims Department
IGI Insurance Limited"""
        return subject, body
    
    @staticmethod
    def renewal_reminder(client_name, policy_number, expiry_date):
        """Policy renewal reminder"""
        subject = f"Policy Renewal Reminder - {policy_number}"
        body = f"""Dear {client_name},

Your insurance policy is due for renewal.

Policy Number: {policy_number}
Expiry Date: {expiry_date}

Please contact us to renew your policy and ensure continuous coverage.

Contact: +92-51-111-444-111
Email: info@igi.com.pk

Best Regards,
IGI Insurance Limited"""
        return subject, body
