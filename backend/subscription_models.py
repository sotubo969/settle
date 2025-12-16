"""
Subscription Models & Payment Integration
Handles vendor tiers, premium memberships, and billing
"""
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional

class VendorTier(str, Enum):
    """Vendor subscription tiers"""
    BASIC = "basic"           # Free - 15% commission
    PROFESSIONAL = "professional"  # £99/mo - 10% commission
    ELITE = "elite"           # £199/mo - 8% commission

class MembershipTier(str, Enum):
    """Customer membership tiers"""
    FREE = "free"             # Standard customer
    PLUS = "plus"             # £9.99/mo - Premium benefits

# Subscription Pricing
VENDOR_PRICING = {
    VendorTier.BASIC: {
        "price": 0,
        "commission_rate": 0.15,  # 15%
        "max_products": 50,
        "featured_products": 0,
        "analytics": "basic",
        "support": "standard",
        "features": [
            "List up to 50 products",
            "15% commission per sale",
            "Basic analytics",
            "Standard support",
            "Profile page",
            "Order management"
        ]
    },
    VendorTier.PROFESSIONAL: {
        "price": 99.00,
        "commission_rate": 0.10,  # 10%
        "max_products": -1,  # Unlimited
        "featured_products": 1,
        "analytics": "advanced",
        "support": "priority",
        "features": [
            "Unlimited products",
            "10% commission (save 5%)",
            "1 featured product on homepage",
            "Advanced analytics",
            "Priority support",
            "Custom store branding",
            "Bulk upload tools",
            "Email marketing integration",
            "Sales reports",
            "Customer insights"
        ]
    },
    VendorTier.ELITE: {
        "price": 199.00,
        "commission_rate": 0.08,  # 8%
        "max_products": -1,  # Unlimited
        "featured_products": 3,
        "analytics": "enterprise",
        "support": "dedicated",
        "features": [
            "Everything in Professional",
            "8% commission (save 7%)",
            "3 featured products on homepage",
            "Top placement in search results",
            "Dedicated account manager",
            "Custom analytics dashboard",
            "API access for inventory",
            "Automated marketing campaigns",
            "Priority customer support badge",
            "Promotional tools",
            "Social media integration",
            "Advanced SEO optimization"
        ]
    }
}

CUSTOMER_PRICING = {
    MembershipTier.FREE: {
        "price": 0,
        "delivery_discount": 0,
        "purchase_discount": 0,
        "loyalty_multiplier": 1,
        "features": [
            "Browse all products",
            "Standard delivery rates",
            "Basic customer support",
            "Wishlist",
            "Order tracking"
        ]
    },
    MembershipTier.PLUS: {
        "price": 9.99,
        "delivery_discount": 1.0,  # 100% off = free delivery
        "purchase_discount": 0.05,  # 5% off all purchases
        "loyalty_multiplier": 2,    # 2x points
        "features": [
            "FREE delivery on all orders",
            "5% discount on all purchases",
            "Early access to new products",
            "Priority customer support",
            "Exclusive deals & flash sales",
            "Wishlist notifications",
            "Monthly recipe box (digital)",
            "Loyalty points 2x multiplier",
            "Birthday bonus",
            "Member-only events"
        ]
    }
}

# Featured Listing Pricing
FEATURED_PRICING = {
    "homepage": {
        "price": 99.00,
        "impressions": 10000,
        "placement": "homepage",
        "badge": "Featured"
    },
    "category": {
        "price": 49.00,
        "impressions": 5000,
        "placement": "category_top",
        "badge": "Promoted"
    },
    "search": {
        "price": 29.00,
        "impressions": 3000,
        "placement": "search_boost",
        "badge": "Sponsored"
    }
}

# Advertising Pricing
ADVERTISING_PRICING = {
    "homepage_banner": {
        "price": 499.00,
        "impressions": 20000,
        "size": "1200x300",
        "duration": "30_days"
    },
    "category_banner": {
        "price": 299.00,
        "impressions": 10000,
        "size": "800x200",
        "duration": "30_days"
    },
    "mobile_banner": {
        "price": 199.00,
        "impressions": 15000,
        "size": "600x150",
        "duration": "30_days"
    },
    "sponsored_product": {
        "price": 149.00,
        "impressions": 5000,
        "placement": "search_results",
        "duration": "30_days"
    }
}

# Service Fees
SERVICE_FEE_RATE = 0.02  # 2% platform service fee
DELIVERY_FEES = {
    "standard": {
        "under_30": 5.99,
        "30_to_50": 3.99,
        "50_to_80": 1.99,
        "over_80": 0.00
    },
    "express": {
        "surcharge": 3.00
    }
}

def calculate_commission(sale_amount: float, vendor_tier: VendorTier) -> float:
    """Calculate commission based on vendor tier"""
    rate = VENDOR_PRICING[vendor_tier]["commission_rate"]
    return round(sale_amount * rate, 2)

def calculate_service_fee(transaction_amount: float) -> float:
    """Calculate platform service fee"""
    return round(transaction_amount * SERVICE_FEE_RATE, 2)

def calculate_delivery_fee(order_total: float, is_express: bool = False, is_premium: bool = False) -> float:
    """Calculate delivery fee based on order total and membership"""
    if is_premium:
        return 0.00  # Free delivery for premium members
    
    # Standard delivery based on order total
    if order_total >= 80:
        base_fee = 0.00
    elif order_total >= 50:
        base_fee = 1.99
    elif order_total >= 30:
        base_fee = 3.99
    else:
        base_fee = 5.99
    
    # Add express surcharge if applicable
    if is_express:
        base_fee += DELIVERY_FEES["express"]["surcharge"]
    
    return round(base_fee, 2)

def calculate_premium_discount(order_total: float, membership_tier: MembershipTier) -> float:
    """Calculate premium membership discount"""
    if membership_tier == MembershipTier.PLUS:
        discount_rate = CUSTOMER_PRICING[MembershipTier.PLUS]["purchase_discount"]
        return round(order_total * discount_rate, 2)
    return 0.00

def get_vendor_benefits(tier: VendorTier) -> dict:
    """Get all benefits for a vendor tier"""
    return VENDOR_PRICING[tier]

def get_customer_benefits(tier: MembershipTier) -> dict:
    """Get all benefits for a customer tier"""
    return CUSTOMER_PRICING[tier]

def calculate_roi_for_vendor(current_sales: float, current_tier: VendorTier, target_tier: VendorTier) -> dict:
    """Calculate ROI when upgrading vendor tier"""
    current_commission = calculate_commission(current_sales, current_tier)
    target_commission = calculate_commission(current_sales, target_tier)
    
    commission_saved = current_commission - target_commission
    subscription_cost = VENDOR_PRICING[target_tier]["price"]
    
    net_benefit = commission_saved - subscription_cost
    roi_percentage = (net_benefit / subscription_cost * 100) if subscription_cost > 0 else 0
    
    return {
        "current_commission": current_commission,
        "target_commission": target_commission,
        "commission_saved": commission_saved,
        "subscription_cost": subscription_cost,
        "net_benefit": net_benefit,
        "roi_percentage": roi_percentage,
        "breakeven_sales": subscription_cost / (VENDOR_PRICING[current_tier]["commission_rate"] - VENDOR_PRICING[target_tier]["commission_rate"]) if current_tier != target_tier else 0
    }

def calculate_customer_roi(monthly_orders: int, avg_order_value: float) -> dict:
    """Calculate ROI for premium membership"""
    monthly_spending = monthly_orders * avg_order_value
    
    # Free delivery savings
    delivery_saved = monthly_orders * 5.00  # Average £5 per order
    
    # 5% discount savings
    discount_saved = monthly_spending * 0.05
    
    # Total savings
    total_saved = delivery_saved + discount_saved
    
    # Membership cost
    membership_cost = CUSTOMER_PRICING[MembershipTier.PLUS]["price"]
    
    # Net benefit
    net_benefit = total_saved - membership_cost
    roi_percentage = (net_benefit / membership_cost * 100)
    
    return {
        "monthly_spending": monthly_spending,
        "delivery_saved": delivery_saved,
        "discount_saved": discount_saved,
        "total_saved": total_saved,
        "membership_cost": membership_cost,
        "net_benefit": net_benefit,
        "roi_percentage": roi_percentage,
        "payback_orders": membership_cost / (avg_order_value * 0.05 + 5.00) if avg_order_value > 0 else 0
    }

# Loyalty Points System
POINTS_PER_POUND = 1  # 1 point per £1 spent
POINTS_TO_POUND = 100  # 100 points = £1 discount

def calculate_loyalty_points(purchase_amount: float, membership_tier: MembershipTier) -> int:
    """Calculate loyalty points earned"""
    multiplier = CUSTOMER_PRICING[membership_tier]["loyalty_multiplier"]
    return int(purchase_amount * POINTS_PER_POUND * multiplier)

def convert_points_to_discount(points: int) -> float:
    """Convert loyalty points to discount amount"""
    return round(points / POINTS_TO_POUND, 2)
