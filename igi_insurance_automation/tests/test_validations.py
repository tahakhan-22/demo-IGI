"""
Test script to validate all critical validation rules
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db import init_db, get_session
from database.models import Client, Policy, Vehicle
from services.policy_service import PolicyService
from services.premium_calculator import PremiumCalculator
from datetime import datetime, timedelta

print("=" * 80)
print("IGI Insurance Automation - Validation Rules Test")
print("=" * 80)
print()

# Initialize database
init_db()
print("✅ Database initialized")
print()

# Test 1: Engine Number Uniqueness
print("Test 1: Engine Number Must Be Unique")
print("-" * 80)
service = PolicyService()

# Create first client and policy
client_data = {
    'name': 'Test Client 1',
    'cnic': '12345-1234567-1',
    'phone': '+92-300-1234567',
    'email': 'test1@example.com',
    'address': 'Test Address',
    'city': 'Islamabad',
    'client_type': 'Individual'
}
success, message, client1 = service.create_client(client_data)
print(f"Client 1 Created: {success}")

policy_data = {
    'commencement_date': datetime.now().date(),
    'expiry_date': datetime.now().date() + timedelta(days=365),
    'sum_insured': 1000000,
    'gross_premium': 35000,
    'net_premium': 33000,
    'premium_payable': 35000
}
success, message, policy1 = service.create_policy(policy_data, client1.id)
print(f"Policy 1 Created: {success}")

vehicle_data1 = {
    'make': 'Honda',
    'model': 'Civic',
    'year_of_manufacturing': 2020,
    'engine_number': 'ENG123456',
    'chassis_number': 'CHS123456',
    'registration_number': 'ABC-123',
    'color': 'White',
    'fuel_type': 'Petrol',
    'sum_insured': 1000000
}
success, message, vehicle1 = service.create_vehicle(vehicle_data1, policy1.id)
print(f"Vehicle 1 Created: {success} - {message}")

# Try to create second vehicle with same engine number
client_data2 = {
    'name': 'Test Client 2',
    'cnic': '54321-7654321-2',
    'phone': '+92-321-9876543',
    'email': 'test2@example.com',
    'address': 'Test Address 2',
    'city': 'Karachi',
    'client_type': 'Individual'
}
success, message, client2 = service.create_client(client_data2)
print(f"Client 2 Created: {success}")

policy_data2 = {
    'commencement_date': datetime.now().date(),
    'expiry_date': datetime.now().date() + timedelta(days=365),
    'sum_insured': 1200000,
    'gross_premium': 40000,
    'net_premium': 38000,
    'premium_payable': 40000
}
success, message, policy2 = service.create_policy(policy_data2, client2.id)
print(f"Policy 2 Created: {success} - {message if not success else 'Success'}")

vehicle_data2 = {
    'make': 'Toyota',
    'model': 'Corolla',
    'year_of_manufacturing': 2021,
    'engine_number': 'ENG123456',  # Same engine number!
    'chassis_number': 'CHS789012',
    'registration_number': 'XYZ-789',
    'color': 'Black',
    'fuel_type': 'Petrol',
    'sum_insured': 1200000
}
success, message, vehicle2 = service.create_vehicle(vehicle_data2, policy2.id)
if not success and "Engine number already exists" in message:
    print("✅ PASS: Engine number uniqueness validation working")
else:
    print(f"❌ FAIL: Engine number validation failed - {message}")
print()

# Test 2: Chassis Number Uniqueness
print("Test 2: Chassis Number Must Be Unique")
print("-" * 80)
vehicle_data3 = {
    'make': 'Suzuki',
    'model': 'Alto',
    'year_of_manufacturing': 2022,
    'engine_number': 'ENG999999',
    'chassis_number': 'CHS123456',  # Same chassis number!
    'registration_number': 'LMN-456',
    'color': 'Red',
    'fuel_type': 'Petrol',
    'sum_insured': 800000
}
success, message, vehicle3 = service.create_vehicle(vehicle_data3, policy2.id)
if not success and "Chassis number already exists" in message:
    print("✅ PASS: Chassis number uniqueness validation working")
else:
    print(f"❌ FAIL: Chassis number validation failed - {message}")
print()

# Test 3: Vehicle Age Auto-calculation
print("Test 3: Vehicle Age Auto-Calculation")
print("-" * 80)
client_data3 = {
    'name': 'Test Client 3',
    'cnic': '11111-2222222-3',
    'phone': '+92-333-1111111',
    'email': 'test3@example.com',
    'address': 'Test Address 3',
    'city': 'Lahore',
    'client_type': 'Individual'
}
success, message, client3 = service.create_client(client_data3)

policy_data3 = {
    'commencement_date': datetime.now().date(),
    'expiry_date': datetime.now().date() + timedelta(days=365),
    'sum_insured': 900000,
    'gross_premium': 32000,
    'net_premium': 30000,
    'premium_payable': 32000
}
success, message, policy3 = service.create_policy(policy_data3, client3.id)

vehicle_data4 = {
    'make': 'Kia',
    'model': 'Sportage',
    'year_of_manufacturing': 2018,
    'engine_number': 'ENG888888',
    'chassis_number': 'CHS888888',
    'registration_number': 'PQR-789',
    'color': 'Silver',
    'fuel_type': 'Diesel',
    'sum_insured': 900000
}
success, message, vehicle4 = service.create_vehicle(vehicle_data4, policy3.id)
if success:
    expected_age = datetime.now().year - 2018
    if vehicle4.vehicle_age == expected_age:
        print(f"✅ PASS: Vehicle age auto-calculated correctly ({expected_age} years)")
    else:
        print(f"❌ FAIL: Vehicle age incorrect. Expected {expected_age}, got {vehicle4.vehicle_age}")
else:
    print(f"❌ FAIL: Could not create vehicle - {message}")
print()

# Test 4: Expiry Date Must Be Greater Than Commencement Date
print("Test 4: Expiry Date Must Be Greater Than Commencement Date")
print("-" * 80)
invalid_policy_data = {
    'commencement_date': datetime.now().date(),
    'expiry_date': datetime.now().date() - timedelta(days=10),  # Invalid: past date
    'sum_insured': 1000000,
    'gross_premium': 35000,
    'net_premium': 33000,
    'premium_payable': 35000
}
success, message, invalid_policy = service.create_policy(invalid_policy_data, client1.id)
if not success and "Expiry date must be greater than commencement date" in message:
    print("✅ PASS: Date validation working")
else:
    print(f"❌ FAIL: Date validation failed - {message}")
print()

# Test 5: Sum Insured Must Be Greater Than Zero
print("Test 5: Sum Insured Must Be Greater Than Zero")
print("-" * 80)
invalid_policy_data2 = {
    'commencement_date': datetime.now().date(),
    'expiry_date': datetime.now().date() + timedelta(days=365),
    'sum_insured': 0,  # Invalid: zero
    'gross_premium': 35000,
    'net_premium': 33000,
    'premium_payable': 35000
}
success, message, invalid_policy2 = service.create_policy(invalid_policy_data2, client1.id)
if not success and "Sum insured must be greater than zero" in message:
    print("✅ PASS: Sum insured validation working")
else:
    print(f"❌ FAIL: Sum insured validation failed - {message}")
print()

# Test 6: Premium Calculation Validation
print("Test 6: Premium Calculation - Total Discount Cannot Exceed Gross Premium")
print("-" * 80)
calculator = PremiumCalculator()
is_valid, msg = calculator.validate_premium_calculation(
    gross_premium=35000,
    total_discount=40000  # Invalid: discount > gross premium
)
if not is_valid:
    print(f"✅ PASS: Premium validation working - {msg}")
else:
    print(f"❌ FAIL: Premium validation should have failed")
print()

# Test 7: Valid Premium Calculation
print("Test 7: Valid Premium Calculation")
print("-" * 80)
is_valid, msg = calculator.validate_premium_calculation(
    gross_premium=35000,
    total_discount=5000  # Valid
)
if is_valid:
    print(f"✅ PASS: Valid premium calculation accepted - {msg}")
else:
    print(f"❌ FAIL: Valid premium calculation rejected - {msg}")
print()

# Close service
service.close()

print("=" * 80)
print("All Validation Tests Completed")
print("=" * 80)
