"""
SQLAlchemy database models for IGI Insurance Automation System
Complete schema with all tables and relationships
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Date, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Client(Base):
    """Client Management"""
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    cnic = Column(String(15), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    address = Column(Text)
    city = Column(String(100))
    client_type = Column(String(50))  # Individual, Corporate, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    policies = relationship('Policy', back_populates='client', cascade='all, delete-orphan')


class Product(Base):
    """Product Setup"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    product_name = Column(String(200), nullable=False)
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(100))  # Motor, Health, Property, etc.
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    coverage_types = relationship('CoverageType', back_populates='product', cascade='all, delete-orphan')
    policies = relationship('Policy', back_populates='product')


class CoverageType(Base):
    """Coverage Types for Products"""
    __tablename__ = 'coverage_types'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    coverage_name = Column(String(200), nullable=False)
    description = Column(Text)
    base_rate = Column(Float)
    
    # Relationships
    product = relationship('Product', back_populates='coverage_types')


class Policy(Base):
    """Policy Management"""
    __tablename__ = 'policies'
    
    id = Column(Integer, primary_key=True)
    policy_number = Column(String(50), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    status = Column(String(50), default='Draft')  # Draft, Active, Expired, Cancelled
    commencement_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    sum_insured = Column(Float, nullable=False)
    gross_premium = Column(Float)
    net_premium = Column(Float)
    premium_payable = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship('Client', back_populates='policies')
    product = relationship('Product', back_populates='policies')
    schedule_items = relationship('ScheduleItem', back_populates='policy', cascade='all, delete-orphan')
    vehicles = relationship('Vehicle', back_populates='policy', cascade='all, delete-orphan')
    discounts = relationship('Discount', back_populates='policy', cascade='all, delete-orphan')
    depreciation_excess = relationship('DepreciationExcess', back_populates='policy', cascade='all, delete-orphan')
    deductible_insurance = relationship('DeductibleInsurance', back_populates='policy', cascade='all, delete-orphan')
    clauses = relationship('Clause', back_populates='policy', cascade='all, delete-orphan')
    warranties = relationship('Warranty', back_populates='policy', cascade='all, delete-orphan')
    agent_commissions = relationship('AgentCommission', back_populates='policy', cascade='all, delete-orphan')
    computational_sheets = relationship('ComputationalSheet', back_populates='policy', cascade='all, delete-orphan')
    documents = relationship('Document', back_populates='policy', cascade='all, delete-orphan')


class ScheduleItem(Base):
    """Schedule / Item Details"""
    __tablename__ = 'schedule_items'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    item_description = Column(Text)
    item_value = Column(Float)
    item_rate = Column(Float)
    item_premium = Column(Float)
    
    # Relationships
    policy = relationship('Policy', back_populates='schedule_items')


class Vehicle(Base):
    """Vehicle Details"""
    __tablename__ = 'vehicles'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    make = Column(String(100))
    model = Column(String(100))
    variant = Column(String(100))
    year_of_manufacturing = Column(Integer)
    vehicle_age = Column(Integer)  # Auto-calculated
    engine_number = Column(String(100), unique=True, index=True)
    chassis_number = Column(String(100), unique=True, index=True)
    registration_number = Column(String(50))
    color = Column(String(50))
    seating_capacity = Column(Integer)
    cubic_capacity = Column(Integer)
    fuel_type = Column(String(50))  # Petrol, Diesel, Electric, Hybrid
    vehicle_type = Column(String(50))  # Private, Commercial
    tracker_installed = Column(Boolean, default=False)
    sum_insured = Column(Float)
    
    # Relationships
    policy = relationship('Policy', back_populates='vehicles')


class Discount(Base):
    """Discounts"""
    __tablename__ = 'discounts'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    discount_type = Column(String(100))  # NCD, Volume, Loyalty, etc.
    discount_percentage = Column(Float)
    discount_amount = Column(Float)
    reason = Column(Text)
    
    # Relationships
    policy = relationship('Policy', back_populates='discounts')


class DepreciationExcess(Base):
    """Depreciation & Excess (D/E)"""
    __tablename__ = 'depreciation_excess'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    de_type = Column(String(100))  # Type of D/E
    percentage = Column(Float)
    amount = Column(Float)
    description = Column(Text)
    
    # Relationships
    policy = relationship('Policy', back_populates='depreciation_excess')


class DeductibleInsurance(Base):
    """Deductible Insurance (DI)"""
    __tablename__ = 'deductible_insurance'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    di_type = Column(String(100))
    deductible_amount = Column(Float)
    description = Column(Text)
    
    # Relationships
    policy = relationship('Policy', back_populates='deductible_insurance')


class Clause(Base):
    """Clauses"""
    __tablename__ = 'clauses'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    clause_code = Column(String(50))
    clause_text = Column(Text)
    is_applicable = Column(Boolean, default=True)
    
    # Relationships
    policy = relationship('Policy', back_populates='clauses')


class Warranty(Base):
    """Warranties"""
    __tablename__ = 'warranties'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    warranty_code = Column(String(50))
    warranty_text = Column(Text)
    is_applicable = Column(Boolean, default=True)
    
    # Relationships
    policy = relationship('Policy', back_populates='warranties')


class Agent(Base):
    """Agents & Commission"""
    __tablename__ = 'agents'
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(200), nullable=False)
    agent_code = Column(String(50), unique=True, nullable=False, index=True)
    license_number = Column(String(50))
    phone = Column(String(20))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    commissions = relationship('AgentCommission', back_populates='agent', cascade='all, delete-orphan')


class AgentCommission(Base):
    """Agent Commission"""
    __tablename__ = 'agent_commissions'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    commission_percentage = Column(Float)
    commission_amount = Column(Float)
    
    # Relationships
    policy = relationship('Policy', back_populates='agent_commissions')
    agent = relationship('Agent', back_populates='commissions')


class ComputationalSheet(Base):
    """Computational Sheet"""
    __tablename__ = 'computational_sheets'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    basic_premium = Column(Float)
    additional_premium = Column(Float)
    total_gross_premium = Column(Float)
    total_discounts = Column(Float)
    net_premium = Column(Float)
    taxes = Column(Float)
    stamps = Column(Float)
    fees = Column(Float)
    total_charges = Column(Float)
    premium_payable = Column(Float)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    policy = relationship('Policy', back_populates='computational_sheets')


class Document(Base):
    """Document Management"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False)
    document_type = Column(String(100))  # Cover Letter, Policy Document, etc.
    file_name = Column(String(255))
    file_path = Column(String(500))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    policy = relationship('Policy', back_populates='documents')


class AutomationLog(Base):
    """Automation Logs"""
    __tablename__ = 'automation_logs'
    
    id = Column(Integer, primary_key=True)
    automation_type = Column(String(100))  # Email Parser, CSV Scanner, RPA, etc.
    status = Column(String(50))  # Success, Failed, Running
    message = Column(Text)
    details = Column(Text)  # JSON or additional details
    executed_at = Column(DateTime, default=datetime.utcnow)
