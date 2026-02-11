"""
Policy service for CRUD operations
Handles policy creation, updates, and validation
"""

from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from ..database.db import get_session
from ..database.models import (
    Client, Policy, Product, Vehicle, Discount, Clause, 
    Warranty, ComputationalSheet, AutomationLog
)


class PolicyService:
    """Service for managing policies"""
    
    def __init__(self):
        self.session = get_session()
    
    def create_client(self, client_data):
        """Create or update a client"""
        try:
            # Check if client exists by CNIC
            existing_client = self.session.query(Client).filter_by(
                cnic=client_data.get('cnic')
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
    
    def create_policy(self, policy_data, client_id, product_id=None):
        """Create a new policy with validation"""
        try:
            # Validation: Expiry date must be greater than commencement date
            commence_date = policy_data.get('commencement_date')
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
                product_id = product.id
            
            # Create policy
            policy = Policy(
                policy_number=self._generate_policy_number(),
                client_id=client_id,
                product_id=product_id,
                commencement_date=commence_date,
                expiry_date=expiry_date,
                sum_insured=sum_insured,
                status='Draft',
                gross_premium=policy_data.get('gross_premium', 0),
                net_premium=policy_data.get('net_premium', 0),
                premium_payable=policy_data.get('premium_payable', 0)
            )
            
            self.session.add(policy)
            self.session.commit()
            
            return True, "Policy created successfully", policy
        
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating policy: {str(e)}", None
    
    def create_vehicle(self, vehicle_data, policy_id):
        """Create vehicle with validation"""
        try:
            # Validation: Check for duplicate engine number
            if vehicle_data.get('engine_number'):
                existing = self.session.query(Vehicle).filter_by(
                    engine_number=vehicle_data['engine_number']
                ).first()
                if existing:
                    return False, "Engine number already exists", None
            
            # Validation: Check for duplicate chassis number
            if vehicle_data.get('chassis_number'):
                existing = self.session.query(Vehicle).filter_by(
                    chassis_number=vehicle_data['chassis_number']
                ).first()
                if existing:
                    return False, "Chassis number already exists", None
            
            # Calculate vehicle age
            if vehicle_data.get('year_of_manufacturing'):
                current_year = datetime.now().year
                vehicle_data['vehicle_age'] = current_year - vehicle_data['year_of_manufacturing']
            
            vehicle_data['policy_id'] = policy_id
            vehicle = Vehicle(**vehicle_data)
            
            self.session.add(vehicle)
            self.session.commit()
            
            return True, "Vehicle created successfully", vehicle
        
        except IntegrityError as e:
            self.session.rollback()
            return False, f"Integrity error: {str(e)}", None
        except Exception as e:
            self.session.rollback()
            return False, f"Error creating vehicle: {str(e)}", None
    
    def add_clauses(self, policy_id, clauses_list):
        """Add clauses to policy"""
        try:
            for clause_data in clauses_list:
                clause = Clause(
                    policy_id=policy_id,
                    clause_code=clause_data.get('code', ''),
                    clause_text=clause_data.get('text', ''),
                    is_applicable=clause_data.get('is_applicable', True)
                )
                self.session.add(clause)
            
            self.session.commit()
            return True, "Clauses added successfully"
        except Exception as e:
            self.session.rollback()
            return False, f"Error adding clauses: {str(e)}"
    
    def add_warranties(self, policy_id, warranties_list):
        """Add warranties to policy"""
        try:
            for warranty_data in warranties_list:
                warranty = Warranty(
                    policy_id=policy_id,
                    warranty_code=warranty_data.get('code', ''),
                    warranty_text=warranty_data.get('text', ''),
                    is_applicable=warranty_data.get('is_applicable', True)
                )
                self.session.add(warranty)
            
            self.session.commit()
            return True, "Warranties added successfully"
        except Exception as e:
            self.session.rollback()
            return False, f"Error adding warranties: {str(e)}"
    
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
            policy = self.session.query(Policy).filter_by(id=policy_id).first()
            if policy:
                return True, "Policy found", policy
            else:
                return False, "Policy not found", None
        except Exception as e:
            return False, f"Error retrieving policy: {str(e)}", None
    
    def _generate_policy_number(self):
        """Generate unique policy number"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"IGI-{timestamp}"
    
    def _get_or_create_default_product(self):
        """Get or create default product"""
        product = self.session.query(Product).filter_by(
            product_code='MOTOR-001'
        ).first()
        
        if not product:
            product = Product(
                product_name='Motor Insurance',
                product_code='MOTOR-001',
                category='Motor',
                description='Comprehensive motor vehicle insurance',
                is_active=True
            )
            self.session.add(product)
            self.session.commit()
        
        return product
    
    def close(self):
        """Close database session"""
        self.session.close()
