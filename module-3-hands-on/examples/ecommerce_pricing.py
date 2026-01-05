"""
THE SCENARIO: The Hallucinated Black Friday Deal
==================================================

Setting: Online Electronics Store, Black Friday Morning - 6:00 AM

The CEO just enabled "AI-Powered Flash Deals" to respond to customer queries
about current promotions in real-time.

A customer asks: "What's the Black Friday discount on the new iPhone?"

THE DANGER: LLM invents discounts that don't exist in the database
THE CONSEQUENCE: Company loses $500,000 in revenue from fake 90% off deal

This example shows what happens when discounts aren't verified against actual data.
"""

from qwed_sdk import QWEDLocal
import logging
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PricingError(Exception):
    """Raised when pricing calculation fails verification"""
    pass


# ============================================================================
# SCENARIO 1: WITHOUT VERIFICATION (The Revenue Disaster)
# ============================================================================

def unsafe_pricing_bot(product: str, base_price: float) -> Dict:
    """
    DANGEROUS: LLM invents promotions that don't exist.
    
    This is what happens when you let AI generate prices without checking database.
    DO NOT USE IN PRODUCTION!
    """
    logger.warning("⚠️  UNSAFE MODE: No verification!")
    logger.warning(f"⚠️  Customer asks: 'What's the Black Friday discount on {product}?'")
    
    # Simulate LLM response - it "sounds" like Black Friday should have huge discounts
    # Real database: 15% off
    # LLM hallucinates: 90% off (sounds more "Black Friday"-ish!)
    
    hallucinated_discount = 90  # ❌ NOT IN DATABASE!
    final_price = base_price * (1 - hallucinated_discount / 100)
    
    logger.error(f"❌ LLM Invented Discount: {hallucinated_discount}% off")
    logger.error(f"   Real discount in database: 15% off")
    logger.error(f"   Told customer: ${final_price:.2f}")
    logger.error(f"   Actual price should be: ${base_price * 0.85:.2f}")
    logger.error(f"   Company loss per sale: ${(base_price * 0.85 - final_price):.2f}")
    logger.error(f"   📊 If 500 customers see this: ${(base_price * 0.85 - final_price) * 500:,.2f} LOST!")
    
    return {
        "product": product,
        "advertised_price": final_price,
        "hallucinated_discount": hallucinated_discount,
        "real_discount": 15,
        "revenue_loss_per_sale": (base_price * 0.85 - final_price)
    }


# ============================================================================
# SCENARIO 2: WITH QWED (The Safe Path)
# ============================================================================

class VerifiedPricingEngine:
    """
    SAFE: E-commerce pricing with discount validation against database.
    
    Every discount is verified against actual promotional data.
    Hallucinated deals are caught BEFORE reaching customers.
    """
    
    # This would come from your database in production
    VALID_PROMOTIONS = {
        "iphone_15": {"discount_percent": 15, "valid_until": "2024-12-01"},
        "macbook_pro": {"discount_percent": 20, "valid_until": "2024-12-01"},
        "airpods": {"discount_percent": 25, "valid_until": "2024-12-01"},
    }
    
    BULK_DISCOUNT_TIERS = [
        {"min_qty": 1, "discount_percent": 0},
        {"min_qty": 10, "discount_percent": 5},
        {"min_qty": 50, "discount_percent": 10},
        {"min_qty": 100, "discount_percent": 15}
    ]
    
    def __init__(self):
        """Initialize with verification enabled."""
        self.client = QWEDLocal(
            provider="openai",
            model="gpt-4o-mini",
            use_cache=True
        )
        self.pricing_log = []
    
    def calculate_customer_price(
        self,
        product_name: str,
        product_id: str,
        base_price: float,
        quantity: int = 1,
        tax_rate: float = 8.5,
        shipping: float = 0.0
    ) -> Dict:
        """
        Calculate final price with verified discount validation.
        
        CRITICAL: Discount must match database. No hallucinated promotions allowed!
        
        Args:
            product_name: Display name
            product_id: Product ID for promo lookup
            base_price: Base price before discounts
            quantity: Number of items
            tax_rate: Tax percentage
            shipping: Shipping cost
            
        Returns:
            Dict with verified pricing breakdown
            
        Raises:
            PricingError: If discount cannot be verified
        """
        logger.info(f"🛍️  Pricing request for: {product_name}")
        logger.info(f"   Base: ${base_price}, Qty: {quantity}")
        
        # Step 1: Get valid discount from database
        promo = self.VALID_PROMOTIONS.get(product_id, {})
        valid_discount = promo.get('discount_percent', 0)
        
        logger.info(f"📊 Database lookup: {valid_discount}% discount")
        
        # Step 2: Verify the math calculation
        query = f"""
        Calculate final e-commerce price:
        - Base price: ${base_price}
        - Quantity: {quantity}
        - Discount: {valid_discount}%
        - Tax rate: {tax_rate}%
        - Shipping: ${shipping}
        
        Formula: 
        subtotal = base * quantity
        after_discount = subtotal * (1 - discount/100)
        after_tax = (after_discount + shipping) * (1 + tax/100)
        
        Return final price.
        """
        
        try:
            result = self.client.verify_math(query)
            
            if not result.verified:
                logger.error(f"❌ Price calculation verification failed: {result.error}")
                raise PricingError(
                    f"Cannot verify pricing math. Error: {result.error}. "
                    "Manual calculation required."
                )
            
            final_price = round(result.value, 2)
            
            # Step 3: Generate breakdown
            subtotal = base_price * quantity
            discount_amount = subtotal * (valid_discount / 100)
            after_discount = subtotal - discount_amount
            tax_amount = (after_discount + shipping) * (tax_rate / 100)
            
            logger.info(f"✅ VERIFIED: ${final_price}")
            logger.info(f"   Discount applied: {valid_discount}% (from database)")
            logger.info(f"   Saved customer: ${discount_amount:.2f}")
            
            pricing_record = {
                "timestamp": datetime.now().isoformat(),
                "product": product_name,
                "product_id": product_id,
                "base_price": base_price,
                "quantity": quantity,
                "discount_percent": valid_discount,
                "discount_source": "database_verified",
                "final_price": final_price,
                "verified": True
            }
            
            self.pricing_log.append(pricing_record)
            
            return {
                "product_name": product_name,
                "base_price": base_price,
                "quantity": quantity,
                "subtotal": round(subtotal, 2),
                "discount_percent": valid_discount,
                "discount_amount": round(discount_amount, 2),
                "after_discount": round(after_discount, 2),
                "shipping": shipping,
                "tax_rate": tax_rate,
                "tax_amount": round(tax_amount, 2),
                "final_price": final_price,
                "verified": True,
                "confidence": 100.0,
                "discount_source": "✅ Database-verified promotion"
            }
            
        except PricingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected pricing error: {e}")
            raise PricingError(f"Pricing calculation failed: {e}")
    
    def validate_bulk_discount(self, quantity: int) -> Dict:
        """
        Verify bulk discount tier is correctly applied.
        
        Uses deterministic logic to ensure right tier for quantity.
        """
        # Find applicable tier
        applicable_tier = None
        for tier in sorted(self.BULK_DISCOUNT_TIERS, key=lambda x: x['min_qty'], reverse=True):
            if quantity >= tier['min_qty']:
                applicable_tier = tier
                break
        
        if not applicable_tier:
            return {"discount_percent": 0, "verified": True, "reason": "No tier"}
        
        # Verify with logic engine
        query = f"""
        Verify bulk discount logic:
        Quantity: {quantity}
        Tiers: {self.BULK_DISCOUNT_TIERS}
        Applied tier: {applicable_tier['discount_percent']}% at {applicable_tier['min_qty']}+ units
        
        Is this correct?
        """
        
        result = self.client.verify_logic(query)
        
        return {
            "discount_percent": applicable_tier['discount_percent'],
            "tier_min_qty": applicable_tier['min_qty'],
            "verified": result.verified,
            "quantity": quantity
        }


# ============================================================================
# THE DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("BLACK FRIDAY DISASTER: The Hallucinated 90% Off")
    print("=" * 70)
    
    product = "iPhone 15 Pro"
    base_price = 999.00
    
    print(f"\n📱 Product: {product}")
    print(f"💰 Base Price: ${base_price}")
    print(f"🎯 Real Black Friday Deal: 15% off (in database)")
    print(f"⏰ Time: Black Friday Morning, 6:00 AM")
    
    # ========================================================================
    # PATH 1: UNSAFE (What could go wrong)
    # ========================================================================
    print("\n" + "=" * 70)
    print("⚠️  PATH 1: WITHOUT VERIFICATION (DISASTER)")
    print("=" * 70)
    
    unsafe_result = unsafe_pricing_bot(product, base_price)
    
    print(f"\n💀 RESULTS:")
    print(f"   Customer asked: 'What's the Black Friday price?'")
    print(f"   LLM hallucinated: {unsafe_result['hallucinated_discount']}% off")
    print(f"   Told customer: ${unsafe_result['advertised_price']:.2f}")
    print(f"   Actual promo: {unsafe_result['real_discount']}% off")
    print(f\"   Should have said: ${base_price * 0.85:.2f}")
    print(f"   ")
    print(f"   📊 BUSINESS IMPACT:")
    print(f"   Loss per sale: ${unsafe_result['revenue_loss_per_sale']:.2f}")
    print(f"   If 500 customers: ${unsafe_result['revenue_loss_per_sale'] * 500:,.2f} LOST!")
    print(f"   ")
    print(f"   🏢 COMPANY OUTCOME: Revenue crisis, CEO fired")
    
    # ========================================================================
    # PATH 2: SAFE (With QWED verification)
    # ========================================================================
    print("\n" + "=" * 70)
    print("✅ PATH 2: WITH QWED VERIFICATION (SAFE)")
    print("=" * 70)
    
    engine = VerifiedPricingEngine()
    
    try:
        safe_result = engine.calculate_customer_price(
            product_name=product,
            product_id="iphone_15",
            base_price=base_price,
            quantity=1,
            tax_rate=8.5,
            shipping=0.0  # Free shipping promo
        )
        
        print(f"\n✅ SAFE RESULTS:")
        print(f"   Base Price: ${safe_result['base_price']}")
        print(f"   Discount: {safe_result['discount_percent']}% ({safe_result['discount_source']})")
        print(f"   Subtotal after discount: ${safe_result['after_discount']}")
        print(f"   Tax ({safe_result['tax_rate']}%): ${safe_result['tax_amount']}")
        print(f"   Final Price: ${safe_result['final_price']}")
        print(f"   Verified: {'✅' if safe_result['verified'] else '❌'}")
        print(f"   ")
        print(f"   🏢 COMPANY OUTCOME: Revenue protected, customers trust pricing")
        
    except PricingError as e:
        print(f"\n❌ PRICING ERROR (caught before reaching customer):")
        print(f"   {e}")
        print(f"   ↳ Escalated to pricing team for manual review")
    
    # ========================================================================
    # BONUS: Bulk Discount Verification
    # ========================================================================
    print("\n" + "=" * 70)
    print("📦 BONUS: Bulk Discount Tier Verification")
    print("=" * 70)
    
    for qty in [5, 15, 75, 150]:
        bulk_result = engine.validate_bulk_discount(qty)
        print(f"\nQuantity: {qty} units")
        print(f"  Applied Discount: {bulk_result['discount_percent']}%")
        print(f"  Tier Minimum: {bulk_result['tier_min_qty']} units")
        print(f"  Verified: {'✅' if bulk_result['verified'] else '❌'}")
    
    # ========================================================================
    # THE LESSON
    # ========================================================================
    print("\n" + "=" * 70)
    print("📚 THE LESSON")
    print("=" * 70)
    print("""
    Without Verification:
    - LLM invents promotions ("90% off sounds Black Friday-ish!")
    - Customers get wrong prices
    - Company loses massive revenue
    - Legal issues (advertised price vs actual)
    
    With QWED:
    - All discounts verified against database
    - Math calculations proven correct
    - Revenue protected
    - Customer trust maintained
    - Legal compliance ensured
    
    💡 In e-commerce: Every hallucinated discount costs real money.
    """)
    
    print("=" * 70)
