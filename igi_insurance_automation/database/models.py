"""
SQLAlchemy database models for IGI Insurance Automation System
Complete Normalized Motor Insurance Schema
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Date, Numeric, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


# ========================================
# 1. CLIENT MANAGEMENT
# ========================================

class Client(Base):
    """Client Management"""
    __tablename__ = 'clients'
    
    client_id = Column(Integer, primary_key=True, autoincrement=True)
    client_code = Column(String(50), unique=True, index=True)
    client_name = Column(String(200), nullable=False)
    client_type = Column(String(50))  # Individual/Corporate
    cnic_no = Column(String(15), unique=True, index=True)
    old_nic_no = Column(String(15))
    ntn_no = Column(String(20))
    passport_no = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    addresses = relationship('ClientAddress', back_populates='client', cascade='all, delete-orphan')
    banks = relationship('ClientBank', back_populates='client', cascade='all, delete-orphan')
    policies = relationship('Policy', back_populates='client', cascade='all, delete-orphan')


class ClientAddress(Base):
    """Client Addresses"""
    __tablename__ = 'client_addresses'
    
    address_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.client_id'), nullable=False)
    address_type = Column(String(50))  # House/Office/Factory/Other
    address_line = Column(Text, nullable=False)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    phone_1 = Column(String(20))
    phone_2 = Column(String(20))
    fax = Column(String(20))
    email = Column(String(100))
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    client = relationship('Client', back_populates='addresses')


class ClientBank(Base):
    """Client Banks"""
    __tablename__ = 'client_banks'
    
    bank_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.client_id'), nullable=False)
    bank_type = Column(String(100), nullable=False)
    bank_limit = Column(Numeric(15, 2))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    client = relationship('Client', back_populates='banks')


# ========================================
# 2. PRODUCT SETUP
# ========================================

class Product(Base):
    """Product Setup"""
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(200), nullable=False)
    business_class = Column(String(100))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    perils = relationship('ProductPeril', back_populates='product', cascade='all, delete-orphan')
    charges = relationship('ProductCharge', back_populates='product', cascade='all, delete-orphan')
    policies = relationship('Policy', back_populates='product')


class ProductPeril(Base):
    """Product Perils"""
    __tablename__ = 'product_perils'
    
    peril_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    peril_name = Column(String(200), nullable=False)
    description = Column(Text)
    legal_liability_paid_driver = Column(Boolean, default=False)
    accident_to_passengers = Column(Boolean, default=False)
    insured_estimated_value = Column(Boolean, default=False)
    rssd_md_terrorism = Column(Boolean, default=False)
    basic_premium = Column(Numeric(15, 2))
    pa_to_insured = Column(Boolean, default=False)
    
    # Relationships
    product = relationship('Product', back_populates='perils')
    schedule_perils = relationship('SchedulePeril', back_populates='peril')


class ProductCharge(Base):
    """Product Charges"""
    __tablename__ = 'product_charges'
    
    charge_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    charge_type = Column(String(100), nullable=False)
    description = Column(Text)
    administrative_sub_charges = Column(Numeric(15, 2))
    sales_tax_services_fed = Column(Numeric(15, 2))
    federal_insurance_fee = Column(Numeric(15, 2))
    stamp_duty = Column(Numeric(15, 2))
    is_applicable = Column(Boolean, default=True)
    
    # Relationships
    product = relationship('Product', back_populates='charges')
    policy_charges = relationship('PolicyCharge', back_populates='charge')


# ========================================
# 3. POLICY MANAGEMENT
# ========================================

class Policy(Base):
    """Policy Management"""
    __tablename__ = 'policies'
    
    policy_id = Column(Integer, primary_key=True, autoincrement=True)
    base_document_no = Column(String(100))
    document_no = Column(String(100), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('clients.client_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    business_class = Column(String(100))
    issue_date = Column(Date, nullable=False)
    comm_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    policy_type = Column(String(50))  # New/Renewal/Endorsement
    renewal_valid_upto = Column(Date)
    region = Column(String(100))
    doc_reference = Column(String(100))
    introduced_by = Column(String(200))
    installment_mode = Column(String(50))  # Single/Monthly/Quarterly/Half-Yearly/Yearly
    on_our_share = Column(Boolean, default=False)
    claim_capping_status = Column(String(50))
    geographical_limit = Column(String(100), default='Pakistan')
    bodily_injury_lol = Column(Numeric(15, 2))
    property_damage_lol = Column(Numeric(15, 2))
    per_occurrence_claim = Column(Numeric(15, 2))
    annual_aggregate_limit = Column(Numeric(15, 2))
    merge_perils = Column(Boolean, default=False)
    premium_account = Column(String(100))
    development_office = Column(String(100))
    currency = Column(String(10), default='PKR')
    sum_insured = Column(Numeric(15, 2), nullable=False)
    gross_premium = Column(Numeric(15, 2), nullable=False)
    charges = Column(Numeric(15, 2))
    premium_payable = Column(Numeric(15, 2), nullable=False)
    commodity = Column(String(100))
    company_industry = Column(String(100))
    iap_industry = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship('Client', back_populates='policies')
    product = relationship('Product', back_populates='policies')
    schedules = relationship('PolicySchedule', back_populates='policy', cascade='all, delete-orphan')
    policy_clauses = relationship('PolicyClause', back_populates='policy', cascade='all, delete-orphan')
    warranties = relationship('Warranty', back_populates='policy', cascade='all, delete-orphan')
    policy_agents = relationship('PolicyAgent', back_populates='policy', cascade='all, delete-orphan')
    policy_charges = relationship('PolicyCharge', back_populates='policy', cascade='all, delete-orphan')
    computation_clauses = relationship('ComputationClause', back_populates='policy', cascade='all, delete-orphan')
    computation_warranties = relationship('ComputationWarranty', back_populates='policy', cascade='all, delete-orphan')
    documents = relationship('DocumentDescription', back_populates='policy', cascade='all, delete-orphan')
    discounts = relationship('PolicyDiscount', back_populates='policy', cascade='all, delete-orphan')


# ========================================
# 4. SCHEDULE/ITEM DETAILS
# ========================================

class PolicySchedule(Base):
    """Policy Schedules"""
    __tablename__ = 'policy_schedules'
    
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey('policies.policy_id'), nullable=False)
    item_no = Column(String(50), nullable=False)
    sum_insured = Column(Numeric(15, 2), nullable=False)
    basic_premium = Column(Numeric(15, 2), nullable=False)
    gross_premium = Column(Numeric(15, 2), nullable=False)
    risk_peril_type = Column(String(100))
    
    # Relationships
    policy = relationship('Policy', back_populates='schedules')
    perils = relationship('SchedulePeril', back_populates='schedule', cascade='all, delete-orphan')
    vehicle = relationship('VehicleDetail', back_populates='schedule', uselist=False, cascade='all, delete-orphan')
    discounts = relationship('PolicyDiscount', back_populates='schedule', cascade='all, delete-orphan')
    depreciation_excess = relationship('DepreciationExcess', back_populates='schedule', uselist=False, cascade='all, delete-orphan')
    deductible_insurance = relationship('DeductibleInsurance', back_populates='schedule', uselist=False, cascade='all, delete-orphan')
    warranties_schedule = relationship('Warranty', back_populates='schedule', cascade='all, delete-orphan')


class SchedulePeril(Base):
    """Schedule Perils"""
    __tablename__ = 'schedule_perils'
    
    sp_id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey('policy_schedules.schedule_id'), nullable=False)
    peril_id = Column(Integer, ForeignKey('product_perils.peril_id'), nullable=False)
    peril_name = Column(String(200), nullable=False)
    base_value = Column(Numeric(15, 2))
    rate_percent = Column(Float)
    percent_of_rate = Column(Float)
    calculation_basis = Column(String(50))  # Percent/Flat/Per Unit
    flat_amount = Column(Numeric(15, 2))
    basic_premium = Column(Numeric(15, 2))
    
    # Relationships
    schedule = relationship('PolicySchedule', back_populates='perils')
    peril = relationship('ProductPeril', back_populates='schedule_perils')


# ========================================
# 5. VEHICLE DETAILS (OD - Own Damage)
# ========================================

class VehicleDetail(Base):
    """Vehicle Details"""
    __tablename__ = 'vehicle_details'
    
    vehicle_id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey('policy_schedules.schedule_id'), nullable=False)
    sum_insured = Column(Numeric(15, 2), nullable=False)
    policy_type = Column(String(50))
    applied_for_registration = Column(String(10))  # Yes/No
    registration_no = Column(String(50), unique=True, index=True)
    engine_no = Column(String(100), unique=True, nullable=False, index=True)
    chassis_no = Column(String(100), unique=True, nullable=False, index=True)
    make_model = Column(String(200), nullable=False)
    passenger_capacity = Column(Integer)
    body_type = Column(String(100))
    power_cc = Column(Integer)  # in cubic centimeters
    color = Column(String(50))
    year_of_manufacturing = Column(Integer, nullable=False)
    vehicle_age = Column(Integer)  # Auto-calculated
    keeper_name = Column(String(200))
    keeper_address = Column(Text)
    accessories = Column(Text)
    accessories_sum_insured = Column(Numeric(15, 2))
    license_no = Column(String(50))
    purchase_order_loan_no = Column(String(100))
    other_information = Column(Text)
    mobile_phone = Column(String(20))
    email = Column(String(100))
    
    # Relationships
    schedule = relationship('PolicySchedule', back_populates='vehicle')


# ========================================
# 6. DISCOUNTS
# ========================================

class DiscountType(Base):
    """Discount Types"""
    __tablename__ = 'discount_types'
    
    discount_type_id = Column(Integer, primary_key=True, autoincrement=True)
    discount_name = Column(String(200), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    policy_discounts = relationship('PolicyDiscount', back_populates='discount_type')


class PolicyDiscount(Base):
    """Policy Discounts"""
    __tablename__ = 'policy_discounts'
    
    policy_discount_id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey('policies.policy_id'), nullable=False)
    schedule_id = Column(Integer, ForeignKey('policy_schedules.schedule_id'))
    discount_type_id = Column(Integer, ForeignKey('discount_types.discount_type_id'), nullable=False)
    rate_percent = Column(Float)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    policy = relationship('Policy', back_populates='discounts')
    schedule = relationship('PolicySchedule', back_populates='discounts')
    discount_type = relationship('DiscountType', back_populates='policy_discounts')


# ========================================
# 7. DEPRECIATION & EXCESS (D/E)
# ========================================

class DepreciationExcess(Base):
    """Depreciation & Excess"""
    __tablename__ = 'depreciation_excess'
    
    de_id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey('policy_schedules.schedule_id'), nullable=False)
    depreciation_rate = Column(Float)
    depreciation_amount = Column(Numeric(15, 2))
    excess_type = Column(String(50))  # Compulsory/Voluntary
    excess_amount = Column(Numeric(15, 2))
    remarks = Column(Text)
    
    # Relationships
    schedule = relationship('PolicySchedule', back_populates='depreciation_excess')


# ========================================
# 8. DEDUCTIBLE/INSURANCE (DI)
# ========================================

class DeductibleInsurance(Base):
    """Deductible Insurance"""
    __tablename__ = 'deductible_insurance'
    
    di_id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey('policy_schedules.schedule_id'), nullable=False)
    deductible_type = Column(String(50))  # Standard/High/Zero
    deductible_amount = Column(Numeric(15, 2))
    deductible_percent = Column(Float)
    applicable_to = Column(String(200))
    remarks = Column(Text)
    
    # Relationships
    schedule = relationship('PolicySchedule', back_populates='deductible_insurance')


# ========================================
# 9. CLAUSES
# ========================================

class ClauseMaster(Base):
    """Clause Master"""
    __tablename__ = 'clause_master'
    
    clause_id = Column(Integer, primary_key=True, autoincrement=True)
    clause_code = Column(String(50), unique=True, index=True)
    clause_name = Column(String(200), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    policy_clauses = relationship('PolicyClause', back_populates='clause')
    computation_clauses = relationship('ComputationClause', back_populates='clause')


class PolicyClause(Base):
    """Policy Clauses"""
    __tablename__ = 'policy_clauses'
    
    policy_clause_id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey('policies.policy_id'), nullable=False)
    clause_id = Column(Integer, ForeignKey('clause_master.clause_id'), nullable=False)
    clause_limit = Column(Numeric(15, 2))
    remarks = Column(Text)
    is_checked = Column(Boolean, default=False)
    
    # Relationships
    policy = relationship('Policy', back_populates='policy_clauses')
    clause = relationship('ClauseMaster', back_populates='policy_clauses')


# ========================================
# 10. WARRANTIES
# ========================================

class Warranty(Base):
    """Warranties"""
    __tablename__ = 'warranties'
    
    warranty_id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey('policies.policy_id'), nullable=False)
    schedule_id = Column(Integer, ForeignKey('policy_schedules.schedule_id'))
    warranty_type = Column(String(100))
    description = Column(Text, nullable=False)
    tracker_details = Column(Text)
    is_applicable = Column(Boolean, default=True)
    
    # Relationships
    policy = relationship('Policy', back_populates='warranties')
    schedule = relationship('PolicySchedule', back_populates='warranties_schedule')


# ========================================
# 11. AGENTS & COMMISSION
# ========================================

class Agent(Base):
    """Agents"""
    __tablename__ = 'agents'
    
    agent_id = Column(Integer, primary_key=True, autoincrement=True)
    agent_code = Column(String(50), unique=True, index=True)
    agent_name = Column(String(200), nullable=False)
    contact_no = Column(String(20))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    policy_agents = relationship('PolicyAgent', back_populates='agent', cascade='all, delete-orphan')


class PolicyAgent(Base):
    """Policy Agents"""
    __tablename__ = 'policy_agents'
    
    policy_agent_id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey('policies.policy_id'), nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.agent_id'), nullable=False)
    apportionment_rate_percent = Column(Float, nullable=False)
    commission_amount = Column(Numeric(15, 2), nullable=False)
    premium_share_percent = Column(Float, nullable=False)
    
    # Relationships
    policy = relationship('Policy', back_populates='policy_agents')
    agent = relationship('Agent', back_populates='policy_agents')


# ========================================
# 12. COMPUTATIONAL SHEET
# ========================================

class PolicyCharge(Base):
    """Policy Charges"""
    __tablename__ = 'policy_charges'
    
    policy_charge_id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey('policies.policy_id'), nullable=False)
    charge_id = Column(Integer, ForeignKey('product_charges.charge_id'), nullable=False)
    charge_amount = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    policy = relationship('Policy', back_populates='policy_charges')
    charge = relationship('ProductCharge', back_populates='policy_charges')


class ComputationClause(Base):
    """Computation Clauses"""
    __tablename__ = 'computation_clauses'
    
    comp_clause_id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey('policies.policy_id'), nullable=False)
    clause_id = Column(Integer, ForeignKey('clause_master.clause_id'), nullable=False)
    clause_limit = Column(Numeric(15, 2))
    remarks = Column(Text)
    is_checked = Column(Boolean, default=False)
    
    # Relationships
    policy = relationship('Policy', back_populates='computation_clauses')
    clause = relationship('ClauseMaster', back_populates='computation_clauses')


class ComputationWarranty(Base):
    """Computation Warranties"""
    __tablename__ = 'computation_warranties'
    
    comp_warranty_id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey('policies.policy_id'), nullable=False)
    description = Column(Text, nullable=False)
    
    # Relationships
    policy = relationship('Policy', back_populates='computation_warranties')


# ========================================
# 13. DOCUMENT MANAGEMENT
# ========================================

class DocumentDescription(Base):
    """Document Descriptions"""
    __tablename__ = 'document_descriptions'
    
    doc_desc_id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey('policies.policy_id'), nullable=False)
    document_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    file_path = Column(String(500))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    policy = relationship('Policy', back_populates='documents')


# ========================================
# 14. AUTOMATION LOGS
# ========================================

class AutomationLog(Base):
    """Automation Logs"""
    __tablename__ = 'automation_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    automation_type = Column(String(100))
    status = Column(String(50))
    message = Column(Text)
    details = Column(Text)
    executed_at = Column(DateTime, default=datetime.utcnow)
