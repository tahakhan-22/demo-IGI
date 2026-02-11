"""
Premium calculator service
Calculates insurance premiums based on various factors
"""


class PremiumCalculator:
    """Service for calculating insurance premiums"""
    
    # Base rates (PKR per year)
    BASE_RATES = {
        'comprehensive': 0.035,  # 3.5% of sum insured
        'third_party': 0.015,    # 1.5% of sum insured
    }
    
    # Age-based multipliers
    AGE_MULTIPLIERS = {
        (0, 1): 1.0,      # New vehicles
        (2, 5): 1.05,     # 2-5 years
        (6, 10): 1.10,    # 6-10 years
        (11, 15): 1.15,   # 11-15 years
        (16, 100): 1.25,  # 16+ years
    }
    
    # Standard charges (PKR)
    STANDARD_CHARGES = {
        'stamp_duty': 40,
        'fid_fee': 100,
        'provincial_tax_rate': 0.01,  # 1% of premium
    }
    
    def __init__(self):
        pass
    
    def calculate_motor_premium(self, sum_insured, vehicle_age=0, policy_type='comprehensive',
                               has_tracker=False, no_claim_discount=0):
        """
        Calculate motor insurance premium
        
        Args:
            sum_insured: Value of the vehicle
            vehicle_age: Age of vehicle in years
            policy_type: 'comprehensive' or 'third_party'
            has_tracker: Boolean indicating if vehicle has tracker
            no_claim_discount: NCD percentage (0-50)
        
        Returns:
            Dictionary with premium breakdown
        """
        # Get base rate
        base_rate = self.BASE_RATES.get(policy_type.lower(), self.BASE_RATES['comprehensive'])
        
        # Calculate basic premium
        basic_premium = sum_insured * base_rate
        
        # Apply age multiplier
        age_multiplier = self._get_age_multiplier(vehicle_age)
        basic_premium *= age_multiplier
        
        # Calculate gross premium
        gross_premium = basic_premium
        
        # Apply discounts
        total_discount = 0
        
        # No Claim Discount
        if no_claim_discount > 0:
            ncd_amount = gross_premium * (no_claim_discount / 100)
            total_discount += ncd_amount
        
        # Tracker discount (5%)
        if has_tracker:
            tracker_discount = gross_premium * 0.05
            total_discount += tracker_discount
        
        # Calculate net premium
        net_premium = gross_premium - total_discount
        
        # Calculate charges
        stamp_duty = self.STANDARD_CHARGES['stamp_duty']
        fid_fee = self.STANDARD_CHARGES['fid_fee']
        provincial_tax = net_premium * self.STANDARD_CHARGES['provincial_tax_rate']
        
        total_charges = stamp_duty + fid_fee + provincial_tax
        
        # Calculate premium payable
        premium_payable = net_premium + total_charges
        
        return {
            'basic_premium': round(basic_premium, 2),
            'gross_premium': round(gross_premium, 2),
            'total_discount': round(total_discount, 2),
            'net_premium': round(net_premium, 2),
            'stamp_duty': round(stamp_duty, 2),
            'fid_fee': round(fid_fee, 2),
            'provincial_tax': round(provincial_tax, 2),
            'total_charges': round(total_charges, 2),
            'premium_payable': round(premium_payable, 2),
            'breakdown': {
                'sum_insured': sum_insured,
                'base_rate': base_rate,
                'age_multiplier': age_multiplier,
                'no_claim_discount': no_claim_discount,
                'has_tracker': has_tracker
            }
        }
    
    def _get_age_multiplier(self, age):
        """Get age-based multiplier"""
        for age_range, multiplier in self.AGE_MULTIPLIERS.items():
            if age_range[0] <= age <= age_range[1]:
                return multiplier
        return self.AGE_MULTIPLIERS[(16, 100)]
    
    def validate_premium_calculation(self, gross_premium, total_discount):
        """
        Validate that total discount does not exceed gross premium
        
        Returns:
            (is_valid, message)
        """
        if total_discount > gross_premium:
            return False, "Total discount cannot exceed gross premium"
        return True, "Premium calculation is valid"
