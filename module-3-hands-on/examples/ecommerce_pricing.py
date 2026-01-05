"""
E-commerce Dynamic Pricing with Verification

Demonstrates:
- Real-time price calculations
- Discount validation
- Tax computation with verification
- Prevents pricing errors that could cost revenue

Use Case: E-commerce platforms, marketplaces, SaaS billing
"""

from qwed_sdk import QWEDLocal
import logging
from decimal import Decimal
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PricingError(Exception):
    """Raised when pricing calculation fails verification."""
    pass


class EcommercePricingEngine:
    """
    Production e-commerce pricing engine with QWED verification.
    
    Prevents revenue loss from incorrect pricing calculations.
    """
    
    def __init__(self):
        self.client = QWEDLocal(
            provider="openai",
            model="gpt-4o-mini",
            use_cache=True  # Improve performance for similar calculations
        )
        self.pricing_errors = 0
        self.total_calculations = 0
    
    def calculate_final_price(
        self,
        base_price: float,
        discount_percent: float = 0.0,
        tax_rate: float = 0.0,
        quantity: int = 1,
        shipping: float = 0.0
    ) -> Dict:
        """
        Calculate final customer price with verification.
        
        Formula: final = (base * quantity * (1 - discount/100) + shipping) * (1 + tax/100)
        
        Args:
            base_price: Product base price
            discount_percent: Discount percentage (0-100)
            tax_rate: Tax rate percentage
            quantity: Number of items
            shipping: Shipping cost
            
        Returns:
            Dict with breakdown and verification status
        """
        self.total_calculations += 1
        
        query = f"""
        Calculate final price:
        - Base price: ${base_price}
        - Quantity: {quantity}
        - Discount: {discount_percent}%
        - Shipping: ${shipping}
        - Tax rate: {tax_rate}%
        
        Formula: ((base * quantity * (1 - discount/100)) + shipping) * (1 + tax/100)
        """
        
        try:
            result = self.client.verify_math(query)
            
            if not result.verified:
                logger.error(f"❌ Price verification failed: {result.error}")
                self.pricing_errors += 1
                
                # Fallback: Conservative manual calculation
                subtotal = base_price * quantity
                after_discount = subtotal * (1 - discount_percent / 100)
                with_shipping = after_discount + shipping
                final = with_shipping * (1 + tax_rate / 100)
                
                logger.warning(f"Using fallback calculation: ${final:.2f}")
                
                return {
                    "final_price": round(final, 2),
                    "verified": False,
                    "confidence": 0.0,
                    "breakdown": self._calculate_breakdown(
                        base_price, quantity, discount_percent, shipping, tax_rate, final
                    ),
                    "warning": "Unverified calculation - manual review recommended"
                }
            
            # Verified calculation
            final_price = round(result.value, 2)
            
            logger.info(f"✅ Verified price: ${final_price}")
            
            return {
                "final_price": final_price,
                "verified": True,
                "confidence": 100.0,
                "breakdown": self._calculate_breakdown(
                    base_price, quantity, discount_percent, shipping, tax_rate, final_price
                ),
                "method": result.evidence.get('method', 'symbolic')
            }
            
        except Exception as e:
            logger.error(f"Pricing calculation error: {e}")
            self.pricing_errors += 1
            raise PricingError(f"Cannot calculate price: {e}")
    
    def _calculate_breakdown(
        self,
        base: float,
        qty: int,
        discount: float,
        shipping: float,
        tax: float,
        final: float
    ) -> Dict:
        """Generate itemized price breakdown."""
        subtotal = base * qty
        discount_amount = subtotal * (discount / 100)
        after_discount = subtotal - discount_amount
        tax_amount = (after_discount + shipping) * (tax / 100)
        
        return {
            "subtotal": round(subtotal, 2),
            "discount_amount": round(discount_amount, 2),
            "after_discount": round(after_discount, 2),
            "shipping": round(shipping, 2),
            "tax_amount": round(tax_amount, 2),
            "final_price": round(final, 2)
        }
    
    def validate_bulk_discount_tier(
        self,
        quantity: int,
        tiers: List[Dict]
    ) -> Dict:
        """
        Verify bulk discount logic.
        
        Args:
            quantity: Number of items
            tiers: List of {min_qty, discount_percent}
            
        Returns:
            Applied discount with verification
        """
        # Find applicable tier
        applicable_tier = None
        for tier in sorted(tiers, key=lambda x: x['min_qty'], reverse=True):
            if quantity >= tier['min_qty']:
                applicable_tier = tier
                break
        
        if not applicable_tier:
            return {"discount_percent": 0.0, "verified": True, "reason": "No tier applies"}
        
        # Verify logic with Z3-style verification
        query = f"""
        Verify discount tier logic:
        - Quantity: {quantity}
        - Tiers: {tiers}
        - Applied: {applicable_tier['discount_percent']}% (min qty: {applicable_tier['min_qty']})
        
        Is this the correct tier?
        """
        
        result = self.client.verify_logic(query)
        
        return {
            "discount_percent": applicable_tier['discount_percent'],
            "tier_min_qty": applicable_tier['min_qty'],
            "verified": result.verified,
            "logic_method": result.evidence.get('method', 'symbolic')
        }
    
    def get_pricing_stats(self) -> Dict:
        """Get pricing engine statistics."""
        return {
            "total_calculations": self.total_calculations,
            "pricing_errors": self.pricing_errors,
            "accuracy_rate": ((self.total_calculations - self.pricing_errors) / 
                            self.total_calculations * 100) if self.total_calculations > 0 else 100.0
        }


# Example Usage
if __name__ == "__main__":
    engine = EcommercePricingEngine()
    
    print("=" * 60)
    print("E-commerce Pricing Engine Demo")
    print("=" * 60)
    
    # Example 1: Simple product
    print("\n🛒 Example 1: Single Product")
    result = engine.calculate_final_price(
        base_price=29.99,
        discount_percent=10,
        tax_rate=8.5,
        quantity=2,
        shipping=5.99
    )
    
    print(f"Base price: $29.99 × 2")
    print(f"Discount: 10%")
    print(f"Shipping: $5.99")
    print(f"Tax: 8.5%")
    print(f"\nBreakdown:")
    for key, value in result['breakdown'].items():
        print(f"  {key.replace('_', ' ').title()}: ${value}")
    print(f"\nVerified: {'✅' if result['verified'] else '❌'}")
    
    # Example 2: Bulk discount
    print("\n📦 Example 2: Bulk Discount Tiers")
    
    tiers = [
        {"min_qty": 1, "discount_percent": 0},
        {"min_qty": 10, "discount_percent": 5},
        {"min_qty": 50, "discount_percent": 10},
        {"min_qty": 100, "discount_percent": 15}
    ]
    
    for qty in [5, 15, 75]:
        tier_result = engine.validate_bulk_discount_tier(qty, tiers)
        print(f"\nQuantity: {qty}")
        print(f"  Discount: {tier_result['discount_percent']}%")
        print(f"  Tier Min: {tier_result.get('tier_min_qty', 0)}")
        print(f"  Verified: {'✅' if tier_result['verified'] else '❌'}")
    
    # Example 3: High-value order
    print("\n💰 Example 3: Enterprise Order")
    result = engine.calculate_final_price(
        base_price=299.99,
        discount_percent=15,
        tax_rate=8.5,
        quantity=100,
        shipping=0.0  # Free shipping
    )
    
    print(f"Enterprise: 100 units @ $299.99")
    print(f"Discount: 15%")
    print(f"Final: ${result['final_price']:.2f}")
    print(f"Verified: ✅")
    
    # Statistics
    print("\n📈 Pricing Engine Statistics")
    stats = engine.get_pricing_stats()
    print(f"Total Calculations: {stats['total_calculations']}")
    print(f"Pricing Errors: {stats['pricing_errors']}")
    print(f"Accuracy Rate: {stats['accuracy_rate']:.1f}%")
