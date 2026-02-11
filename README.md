# IGI Insurance Automation System

A complete Python-based insurance automation system demonstrating how repetitive insurance processing tasks can be automated using Streamlit, SQLAlchemy, Gmail API, and RPA.

## 🎯 Project Overview

This system demonstrates automation capabilities for:
- **Email Processing**: Automated reading and parsing of insurance application emails
- **Payment Reminders**: CSV-based due payment scanning and automated email reminders
- **Policy Management**: Complete CRUD operations with validation
- **Cover Letter Generation**: Automated document generation with PDF export
- **RPA Integration**: Template-based form filling and submission
- **Database Management**: Comprehensive SQLAlchemy schema for insurance operations

## 🏗️ Architecture

```
igi_insurance_automation/
│
├── app.py                          # Main Streamlit dashboard
├── config.py                       # Configuration settings
├── database/
│   ├── __init__.py
│   ├── models.py                   # Full SQLAlchemy schema (15+ tables)
│   └── db.py                       # Database engine/session management
│
├── automation/
│   ├── __init__.py
│   ├── gmail_service.py            # Gmail API integration (OAuth 2.0)
│   ├── csv_scanner.py              # CSV due payment scanner
│   ├── email_parser.py             # Email-to-form NLP extraction
│   └── rpa_engine.py               # Selenium RPA engine
│
├── services/
│   ├── __init__.py
│   ├── policy_service.py           # Policy CRUD operations
│   ├── premium_calculator.py       # Premium calculation logic
│   └── cover_letter_generator.py   # Cover letter generation + PDF
│
├── templates/
│   ├── __init__.py
│   └── email_templates.py          # Email template strings
│
└── data/
    └── dues.csv                    # Sample CSV for payment reminders
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Google Cloud account (for Gmail API)
- Chrome/Chromium browser (for RPA)

### Installation

1. **Clone the repository**
   ```bash
   cd demo-IGI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Cloud OAuth (for Gmail API)**
   
   a. Go to [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Create a new project or select existing one
   
   c. Enable Gmail API:
      - Navigate to "APIs & Services" → "Library"
      - Search for "Gmail API"
      - Click "Enable"
   
   d. Create OAuth 2.0 Credentials:
      - Go to "APIs & Services" → "Credentials"
      - Click "Create Credentials" → "OAuth client ID"
      - Select "Desktop app" as application type
      - Name it "IGI Automation"
      - Download the credentials file
   
   e. Rename downloaded file to `credentials.json` and place it in the project root:
      ```bash
      mv ~/Downloads/client_secret_*.json /path/to/demo-IGI/credentials.json
      ```

### Running the Application

```bash
streamlit run igi_insurance_automation/app.py
```

The application will open in your browser at `http://localhost:8501`

## 📋 Features & Modules

### 1. 🏠 Dashboard
- System status indicators (Gmail, RPA, Database)
- Real-time automation logs
- Quick access to all modules

### 2. 📧 Email Automation
- OAuth 2.0 Gmail authentication
- Read unread emails
- Mark emails as read
- Automated email parsing

### 3. 💰 Payment Reminder Automation
- Scans CSV file for due payments
- Identifies payments due within 30 days
- Sends automated email reminders
- Logs all activities to database

**CSV Format** (`data/dues.csv`):
```csv
client_name,email,phone,due_date,amount_due
Ahmed Ali,ahmed.ali@example.com,+92-300-1234567,2026-02-20,15000
```

### 4. 📄 Policy Processing (Email → Form → RPA)
- Fetches latest unread email
- Parses email content using regex
- Auto-fills policy form with extracted data
- Calculates premium automatically
- Saves to database with validation
- Executes RPA workflow

**Email Parser Extracts:**
- Client: Name, CNIC, Phone, Email, Address, City
- Vehicle: Make, Model, Year, Engine#, Chassis#, Registration, Color, Fuel Type
- Policy: Type, Sum Insured, Coverage Period, Commencement Date

### 5. 🧾 Cover Letter Generator
- Generates structured cover letters
- Displays formatted text
- Exports to PDF
- Includes all policy details:
  - Client information
  - Vehicle details
  - Policy terms
  - Premium breakdown
  - Clauses and warranties

### 6. 📊 Database Viewer
- View all policies
- Browse clients
- Check vehicle records
- Filter and search capabilities

## 🗄️ Database Schema

The system includes a comprehensive SQLAlchemy schema with 15+ tables:

**Core Tables:**
- `clients`: Client management
- `products`: Insurance products
- `policies`: Policy records
- `vehicles`: Vehicle details
- `agents`: Agent information

**Supporting Tables:**
- `coverage_types`: Product coverage options
- `schedule_items`: Policy schedule items
- `discounts`: Policy discounts
- `depreciation_excess`: D/E records
- `deductible_insurance`: DI records
- `clauses`: Policy clauses
- `warranties`: Policy warranties
- `agent_commissions`: Commission records
- `computational_sheets`: Premium calculations
- `documents`: Document management
- `automation_logs`: Automation activity logs

## ✅ Validation Rules

The system enforces critical validation rules:

1. ✅ **Engine Number** must be unique
2. ✅ **Chassis Number** must be unique
3. ✅ **Vehicle Age** auto-calculated from manufacturing year
4. ✅ **Expiry Date** must be greater than Commencement Date
5. ✅ **Premium Payable** = Gross Premium + Charges - Discounts
6. ✅ **Sum Insured** must be greater than zero
7. ✅ **Total Discount** cannot exceed Gross Premium

## 🔧 Configuration

Edit `config.py` to customize:
- Database path
- Gmail API scopes
- Due payment threshold (default: 30 days)
- Company information
- RPA settings (timeout, headless mode)
- PDF output directory

## 📊 Premium Calculation

The premium calculator includes:
- Base rates for comprehensive and third-party insurance
- Age-based multipliers
- No Claim Discount (NCD)
- Tracker discount (5%)
- Standard charges:
  - Stamp Duty: PKR 40
  - FID Fee: PKR 100
  - Provincial Tax: 1% of net premium

**Example:**
```python
calculator = PremiumCalculator()
premium = calculator.calculate_motor_premium(
    sum_insured=1000000,
    vehicle_age=3,
    policy_type='comprehensive',
    has_tracker=True,
    no_claim_discount=20
)
# Returns: gross_premium, net_premium, total_charges, premium_payable
```

## 🤖 RPA Engine

The RPA engine supports template-based automation:

```python
template = {
    'url': 'https://example.com/form',
    'actions': [
        {'type': 'fill', 'selector': 'input[name="name"]', 'value': 'John Doe'},
        {'type': 'click', 'selector': 'button[type="submit"]'},
        {'type': 'wait', 'seconds': 2}
    ]
}

rpa = RPAEngine()
rpa.initialize_browser()
rpa.execute_automation_template(template)
rpa.close_browser()
```

## 📧 Email Templates

Predefined templates for:
- Payment reminders
- Policy confirmation
- Claim acknowledgment
- Renewal reminders

## 🔐 Security

- OAuth 2.0 for Gmail authentication
- Credentials stored in `.gitignore`
- Database connection pooling
- Input validation on all forms
- Unique constraints on critical fields

## 🐛 Troubleshooting

### Gmail Authentication Issues
- Ensure `credentials.json` is in the project root
- Check OAuth 2.0 scopes are correctly configured
- Delete `token.json` and re-authenticate if needed

### ChromeDriver Issues
- The system automatically downloads ChromeDriver via `webdriver-manager`
- If issues persist, manually install Chrome/Chromium

### Database Errors
- Database is automatically created on first run
- If corruption occurs, delete `igi_insurance.db` and restart

### Module Import Errors
- Ensure all `__init__.py` files exist in subdirectories
- Check Python path includes project root

## 📝 Usage Examples

### Example 1: Send Payment Reminders
1. Navigate to "💰 Payment Reminders"
2. Review upcoming due payments
3. Click "🚀 Send Payment Reminders"
4. System scans CSV and sends emails automatically

### Example 2: Process Email to Policy
1. Send a test email to your Gmail with policy details
2. Navigate to "📄 Policy Processing"
3. Click "📥 Fetch Latest Email"
4. Click "🔍 Parse Email Data"
5. Review auto-filled form
6. Click "✅ Complete Policy"

### Example 3: Generate Cover Letter
1. Navigate to "🧾 Cover Letter Generator"
2. Select a policy from dropdown
3. Click "📄 Generate Cover Letter"
4. Click "📥 Download as PDF"

## 🎓 Learning Resources

This project demonstrates:
- Streamlit application development
- SQLAlchemy ORM with complex relationships
- Gmail API OAuth 2.0 integration
- Selenium-based RPA
- PDF generation with FPDF2
- CSV processing with Pandas
- Email parsing with regex
- Business logic validation
- Database-driven automation logging

## 📄 License

This is a demonstration project for IGI Insurance stakeholders.

## 👥 Contributors

Developed as a proof-of-concept for automating insurance operations.

## 📞 Support

For issues or questions about this automation system, please contact the development team.

---

**Note**: This system is designed for demonstration purposes to showcase automation capabilities. For production deployment, additional security hardening, error handling, and scalability considerations would be required.