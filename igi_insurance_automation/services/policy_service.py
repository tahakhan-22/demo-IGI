"""
Policy service for CRUD operations
Handles policy creation, updates, and validation
Complete implementation for normalized schema
"""

import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

# Handle imports for both module and direct execution
try:
    from ..database.db import get_session
    from ..database.models import (
        Client, ClientAddress, ClientBank, Policy, Product, ProductPeril, ProductCharge,
        PolicySchedule, SchedulePeril, VehicleDetail, DiscountType, PolicyDiscount,
        DepreciationExcess, DeductibleInsurance, ClauseMaster, PolicyClause,
        Warranty, Agent, PolicyAgent, PolicyCharge, ComputationClause,
        ComputationWarranty, DocumentDescription, AutomationLog
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database.db import get_session
    from database.models import (
        Client, ClientAddress, ClientBank, Policy, Product, ProductPeril, ProductCharge,
        PolicySchedule, SchedulePeril, VehicleDetail, DiscountType, PolicyDiscount,
        DepreciationExcess, DeductibleInsurance, ClauseMaster, PolicyClause,
        Warranty, Agent, PolicyAgent, PolicyCharge, ComputationClause,
        ComputationWarranty, DocumentDescription, AutomationLog
    )


class PolicyService:
    """Service for managing policies and related entities"""
    
    def __init__(self):
        self.session = get_session()
    
    # ========================================
    # CLIENT MANAGEMENT
    # ========================================
    
    def create_client(self, client_data):
        """Create or update a client"""
        try:
            # Check if client exists by CNIC or client_code
            existing_client = None
            if client_data.get('cnic_no'):
                existing_client = self.session.query(Client).filter_by(
                    cnic_no=client_data.get('cnic_no')
                ).first()
            elif client_data.get('client_code'):
                existing_client = self.session.query(Client).filter_by(
                    client_code=client_data.get('client_code')
                ).first()
            
            if existing_client:
                # Update existing client
                for key, value in client_data.items():
                    if hasattr(existing_client, key) and value:
                        setattr(existing_client, key, value)
                existing_client.updated_at = datetime.utcnow()
                self.session.commit()
                return True, "Client updated successfully", existing_client
            else:
                # Generate client_code if not provided
                if not client_data.get('client_code'):
                    client_data['client_code'] = self._generate_client_code()
                
                # Create new client
                client = Client(**client_data)
                self.session.add(client)
                self.session.commit()
                return True, "Client created successfully", client
        
        except IntegrityError as e:
            self.session.rollback()
            return False, f"Integrity error: {str(e)}", None
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating client: {str(e)}", None
    
    def create_client_address(self, address_data, client_id):
        """Create client address"""
        try:
            address_data['client_id'] = client_id
            address = ClientAddress(**address_data)
            self.session.add(address)
            self.session.commit()
            return True, "Address created successfully", address
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating address: {str(e)}", None
    
    def create_client_bank(self, bank_data, client_id):
        """Create client bank"""
        try:
            bank_data['client_id'] = client_id
            bank = ClientBank(**bank_data)
            self.session.add(bank)
            self.session.commit()
            return True, "Bank created successfully", bank
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating bank: {str(e)}", None
    
    # ========================================
    # PRODUCT MANAGEMENT
    # ========================================
    
    def _get_or_create_default_product(self):
        """Get or create default product"""
        product = self.session.query(Product).filter_by(
            product_name='Motor Insurance'
        ).first()
        
        if not product:
            product = Product(
                product_name='Motor Insurance',
                business_class='Motor',
                description='Comprehensive motor vehicle insurance',
                is_active=True
            )
            self.session.add(product)
            self.session.commit()
        
        return product
    
    # ========================================
    # POLICY MANAGEMENT
    # ========================================
    
    def create_policy(self, policy_data, client_id, product_id=None):
        """Create a new policy with validation"""
        try:
            # Validation: Expiry date must be greater than commencement date
            commence_date = policy_data.get('comm_date')
            expiry_date = policy_data.get('expiry_date')
            
            if isinstance(commence_date, str):
                commence_date = datetime.strptime(commence_date, '%Y-%m-%d').date()
            if isinstance(expiry_date, str):
                expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            
            if expiry_date <= commence_date:
                return False, "Expiry date must be greater than commencement date", None
            
            # Validation: Sum insured must be greater than zero
            sum_insured = policy_data.get('sum_insured', 0)
            if sum_insured <= 0:
                return False, "Sum insured must be greater than zero", None
            
            # Get or create default product if not provided
            if not product_id:
                product = self._get_or_create_default_product()
                product_id = product.product_id
            
            # Generate document_no if not provided
            if not policy_data.get('document_no'):
                policy_data['document_no'] = self._generate_policy_number()
            
            # Set issue_date to today if not provided
            if not policy_data.get('issue_date'):
                policy_data['issue_date'] = datetime.now().date()
            
            # Create policy
            policy = Policy(
                document_no=policy_data.get('document_no'),
                base_document_no=policy_data.get('base_document_no'),
                client_id=client_id,
                product_id=product_id,
                business_class=policy_data.get('business_class'),
                issue_date=policy_data.get('issue_date'),
                comm_date=commence_date,
                expiry_date=expiry_date,
                policy_type=policy_data.get('policy_type', 'New'),
                region=policy_data.get('region'),
                installment_mode=policy_data.get('installment_mode', 'Single'),
                geographical_limit=policy_data.get('geographical_limit', 'Pakistan'),
                currency=policy_data.get('currency', 'PKR'),
                sum_insured=sum_insured,
                gross_premium=policy_data.get('gross_premium', 0),
                charges=policy_data.get('charges', 0),
                premium_payable=policy_data.get('premium_payable', 0),
                bodily_injury_lol=policy_data.get('bodily_injury_lol'),
                property_damage_lol=policy_data.get('property_damage_lol')
            )
            
            self.session.add(policy)
            self.session.commit()
            
            return True, "Policy created successfully", policy
        
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating policy: {str(e)}", None
    
    # ========================================
    # SCHEDULE MANAGEMENT
    # ========================================
    
    def create_policy_schedule(self, schedule_data, policy_id):
        """Create policy schedule"""
        try:
            schedule_data['policy_id'] = policy_id
            schedule = PolicySchedule(**schedule_data)
            self.session.add(schedule)
            self.session.commit()
            return True, "Schedule created successfully", schedule
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating schedule: {str(e)}", None
    
    def create_schedule_peril(self, peril_data, schedule_id, peril_id):
        """Create schedule peril"""
        try:
            peril_data['schedule_id'] = schedule_id
            peril_data['peril_id'] = peril_id
            schedule_peril = SchedulePeril(**peril_data)
            self.session.add(schedule_peril)
            self.session.commit()
            return True, "Schedule peril created successfully", schedule_peril
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating schedule peril: {str(e)}", None
    
    # ========================================
    # VEHICLE MANAGEMENT
    # ========================================
    
    def create_vehicle(self, vehicle_data, schedule_id):
        """Create vehicle with validation"""
        try:
            # Validation: Check for duplicate engine number
            if vehicle_data.get('engine_no'):
                existing = self.session.query(VehicleDetail).filter_by(
                    engine_no=vehicle_data['engine_no']
                ).first()
                if existing:
                    return False, "Engine number already exists", None
            
            # Validation: Check for duplicate chassis number
            if vehicle_data.get('chassis_no'):
                existing = self.session.query(VehicleDetail).filter_by(
                    chassis_no=vehicle_data['chassis_no']
                ).first()
                if existing:
                    return False, "Chassis number already exists", None
            
            # Calculate vehicle age
            if vehicle_data.get('year_of_manufacturing'):
                current_year = datetime.now().year
                vehicle_data['vehicle_age'] = current_year - vehicle_data['year_of_manufacturing']
            
            vehicle_data['schedule_id'] = schedule_id
            vehicle = VehicleDetail(**vehicle_data)
            
            self.session.add(vehicle)
            self.session.commit()
            
            return True, "Vehicle created successfully", vehicle
        
        except IntegrityError as e:
            self.session.rollback()
            return False, f"Integrity error: {str(e)}", None
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating vehicle: {str(e)}", None
    
    # ========================================
    # DISCOUNT MANAGEMENT
    # ========================================
    
    def create_policy_discount(self, discount_data, policy_id, schedule_id=None):
        """Create policy discount"""
        try:
            discount_data['policy_id'] = policy_id
            if schedule_id:
                discount_data['schedule_id'] = schedule_id
            discount = PolicyDiscount(**discount_data)
            self.session.add(discount)
            self.session.commit()
            return True, "Discount created successfully", discount
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating discount: {str(e)}", None
    
    # ========================================
    # D/E & DI MANAGEMENT
    # ========================================
    
    def create_depreciation_excess(self, de_data, schedule_id):
        """Create depreciation & excess"""
        try:
            de_data['schedule_id'] = schedule_id
            de = DepreciationExcess(**de_data)
            self.session.add(de)
            self.session.commit()
            return True, "Depreciation/Excess created successfully", de
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating D/E: {str(e)}", None
    
    def create_deductible_insurance(self, di_data, schedule_id):
        """Create deductible insurance"""
        try:
            di_data['schedule_id'] = schedule_id
            di = DeductibleInsurance(**di_data)
            self.session.add(di)
            self.session.commit()
            return True, "Deductible Insurance created successfully", di
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating DI: {str(e)}", None
    
    # ========================================
    # CLAUSE MANAGEMENT
    # ========================================
    
    def create_policy_clause(self, clause_data, policy_id, clause_id):
        """Create policy clause"""
        try:
            clause_data['policy_id'] = policy_id
            clause_data['clause_id'] = clause_id
            policy_clause = PolicyClause(**clause_data)
            self.session.add(policy_clause)
            self.session.commit()
            return True, "Policy clause created successfully", policy_clause
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating policy clause: {str(e)}", None
    
    def add_clauses(self, policy_id, clauses_list):
        """Add multiple clauses to policy"""
        try:
            for clause_data in clauses_list:
                clause = PolicyClause(
                    policy_id=policy_id,
                    clause_id=clause_data.get('clause_id'),
                    clause_limit=clause_data.get('clause_limit'),
                    remarks=clause_data.get('remarks'),
                    is_checked=clause_data.get('is_checked', False)
                )
                self.session.add(clause)
            
            self.session.commit()
            return True, "Clauses added successfully"
        except Exception as e:
            self.session.rollback()
            return False, f"Error adding clauses: {str(e)}"
    
    # ========================================
    # WARRANTY MANAGEMENT
    # ========================================
    
    def create_warranty(self, warranty_data, policy_id, schedule_id=None):
        """Create warranty"""
        try:
            warranty_data['policy_id'] = policy_id
            if schedule_id:
                warranty_data['schedule_id'] = schedule_id
            warranty = Warranty(**warranty_data)
            self.session.add(warranty)
            self.session.commit()
            return True, "Warranty created successfully", warranty
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating warranty: {str(e)}", None
    
    def add_warranties(self, policy_id, warranties_list):
        """Add multiple warranties to policy"""
        try:
            for warranty_data in warranties_list:
                warranty = Warranty(
                    policy_id=policy_id,
                    warranty_type=warranty_data.get('warranty_type'),
                    description=warranty_data.get('description'),
                    tracker_details=warranty_data.get('tracker_details'),
                    is_applicable=warranty_data.get('is_applicable', True)
                )
                self.session.add(warranty)
            
            self.session.commit()
            return True, "Warranties added successfully"
        except Exception as e:
            self.session.rollback()
            return False, f"Error adding warranties: {str(e)}"
    
    # ========================================
    # AGENT MANAGEMENT
    # ========================================
    
    def create_policy_agent(self, agent_data, policy_id, agent_id):
        """Create policy agent"""
        try:
            agent_data['policy_id'] = policy_id
            agent_data['agent_id'] = agent_id
            policy_agent = PolicyAgent(**agent_data)
            self.session.add(policy_agent)
            self.session.commit()
            return True, "Policy agent created successfully", policy_agent
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating policy agent: {str(e)}", None
    
    # ========================================
    # CHARGE MANAGEMENT
    # ========================================
    
    def create_policy_charge(self, charge_data, policy_id, charge_id):
        """Create policy charge"""
        try:
            charge_data['policy_id'] = policy_id
            charge_data['charge_id'] = charge_id
            policy_charge = PolicyCharge(**charge_data)
            self.session.add(policy_charge)
            self.session.commit()
            return True, "Policy charge created successfully", policy_charge
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating policy charge: {str(e)}", None
    
    # ========================================
    # DOCUMENT MANAGEMENT
    # ========================================
    
    def create_document_description(self, doc_data, policy_id):
        """Create document description"""
        try:
            doc_data['policy_id'] = policy_id
            document = DocumentDescription(**doc_data)
            self.session.add(document)
            self.session.commit()
            return True, "Document description created successfully", document
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating document description: {str(e)}", None
    
    # ========================================
    # QUERY METHODS
    # ========================================
    
    def get_all_policies(self):
        """Get all policies"""
        try:
            policies = self.session.query(Policy).all()
            return True, "Policies retrieved successfully", policies
        except Exception as e:
            return False, f"Error retrieving policies: {str(e)}", []
    
    def get_policy_by_id(self, policy_id):
        """Get policy by ID"""
        try:
            policy = self.session.query(Policy).filter_by(policy_id=policy_id).first()
            if policy:
                return True, "Policy found", policy
            else:
                return False, "Policy not found", None
        except Exception as e:
            return False, f"Error retrieving policy: {str(e)}", None
    
    def get_policy_by_document_no(self, document_no):
        """Get policy by document number"""
        try:
            policy = self.session.query(Policy).filter_by(document_no=document_no).first()
            if policy:
                return True, "Policy found", policy
            else:
                return False, "Policy not found", None
        except Exception as e:
            return False, f"Error retrieving policy: {str(e)}", None
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def _generate_policy_number(self):
        """Generate unique policy number"""
        import random
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = random.randint(1000, 9999)
        return f"IGI-{timestamp}-{random_suffix}"
    
    def _generate_client_code(self):
        """Generate unique client code"""
        import random
        timestamp = datetime.now().strftime('%Y%m%d')
        random_suffix = random.randint(100, 999)
        return f"CLT-{timestamp}-{random_suffix}"
    
    def close(self):
        """Close database session"""
        self.session.close()
