"""
Delivery Service for AfroMarket UK
Distance-based delivery pricing with free delivery threshold
"""

import os
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# UK Delivery Zones based on distance from London (hub city)
# Prices are in GBP

@dataclass
class DeliveryZone:
    name: str
    base_price: float
    price_per_kg: float
    estimated_days: str

# Define delivery zones
DELIVERY_ZONES = {
    "local": DeliveryZone("Local (London)", 2.99, 0.50, "Same day - Next day"),
    "near": DeliveryZone("Near (South East)", 4.99, 0.75, "1-2 days"),
    "mid": DeliveryZone("Mid Distance", 6.99, 1.00, "2-3 days"),
    "far": DeliveryZone("Far Distance", 8.99, 1.25, "3-4 days"),
    "remote": DeliveryZone("Remote Areas", 12.99, 1.50, "4-5 days"),
}

# Postcode area mapping to zones
# London and immediate surroundings
LOCAL_POSTCODES = [
    "E", "EC", "N", "NW", "SE", "SW", "W", "WC",  # Central London
    "BR", "CR", "DA", "EN", "HA", "IG", "KT", "RM", "SM", "TW", "UB"  # Greater London
]

# South East England
NEAR_POSTCODES = [
    "AL", "BN", "CB", "CM", "CO", "CT", "GU", "HP", "LU", "ME", "MK", 
    "OX", "RG", "RH", "SG", "SL", "SS", "TN", "WD"
]

# Midlands and nearby
MID_POSTCODES = [
    "B", "BA", "BD", "BS", "CV", "DE", "DY", "GL", "HR", "LE", "NG",
    "NN", "NR", "PE", "PO", "SO", "SP", "ST", "SN", "WR", "WS", "WV"
]

# North England and Wales
FAR_POSTCODES = [
    "BB", "BL", "CA", "CF", "CH", "CW", "DN", "FY", "HD", "HG", "HU",
    "HX", "L", "LA", "LD", "LL", "LN", "LS", "M", "NE", "NP", "OL",
    "PR", "S", "SA", "SK", "SR", "SY", "TS", "WA", "WF", "WN", "YO"
]

# Scotland and remote areas
REMOTE_POSTCODES = [
    "AB", "DD", "DG", "DH", "DL", "EH", "FK", "G", "HS", "IV", "KA",
    "KW", "KY", "ML", "PA", "PH", "TD", "ZE", "BT", "IM", "JE", "GY"
]

# Free delivery threshold
FREE_DELIVERY_THRESHOLD = 100.00  # £100

# Express delivery options
EXPRESS_OPTIONS = {
    "standard": {"name": "Standard Delivery", "multiplier": 1.0, "days_reduction": 0},
    "express": {"name": "Express Delivery", "multiplier": 1.5, "days_reduction": 1},
    "next_day": {"name": "Next Day Delivery", "multiplier": 2.0, "days_reduction": 2},
}


def get_postcode_area(postcode: str) -> str:
    """Extract the area code from a UK postcode"""
    # Remove spaces and convert to uppercase
    postcode = postcode.replace(" ", "").upper()
    
    # Extract letters from the beginning
    area = ""
    for char in postcode:
        if char.isalpha():
            area += char
        else:
            break
    
    return area


def get_delivery_zone(postcode: str) -> Tuple[str, DeliveryZone]:
    """Determine delivery zone based on postcode"""
    area = get_postcode_area(postcode)
    
    if area in LOCAL_POSTCODES:
        return "local", DELIVERY_ZONES["local"]
    elif area in NEAR_POSTCODES:
        return "near", DELIVERY_ZONES["near"]
    elif area in MID_POSTCODES:
        return "mid", DELIVERY_ZONES["mid"]
    elif area in FAR_POSTCODES:
        return "far", DELIVERY_ZONES["far"]
    elif area in REMOTE_POSTCODES:
        return "remote", DELIVERY_ZONES["remote"]
    else:
        # Default to mid distance for unknown postcodes
        return "mid", DELIVERY_ZONES["mid"]


def calculate_delivery_cost(
    postcode: str,
    subtotal: float,
    total_weight_kg: float = 1.0,
    delivery_option: str = "standard"
) -> Dict:
    """
    Calculate delivery cost based on postcode, subtotal, and weight
    
    Args:
        postcode: UK postcode for delivery
        subtotal: Order subtotal in GBP
        total_weight_kg: Total weight of items in kg
        delivery_option: standard, express, or next_day
        
    Returns:
        Dict with delivery details including cost and estimated time
    """
    
    # Get delivery zone
    zone_key, zone = get_delivery_zone(postcode)
    
    # Check for free delivery
    qualifies_for_free = subtotal >= FREE_DELIVERY_THRESHOLD
    amount_to_free = max(0, FREE_DELIVERY_THRESHOLD - subtotal) if not qualifies_for_free else 0
    
    # Calculate base delivery cost
    if qualifies_for_free:
        base_cost = 0.0
        weight_cost = 0.0
    else:
        base_cost = zone.base_price
        # Add weight-based cost for orders over 2kg
        weight_cost = max(0, (total_weight_kg - 2)) * zone.price_per_kg
    
    total_delivery = base_cost + weight_cost
    
    # Apply express option multiplier
    express = EXPRESS_OPTIONS.get(delivery_option, EXPRESS_OPTIONS["standard"])
    if not qualifies_for_free:
        total_delivery *= express["multiplier"]
    
    # Round to 2 decimal places
    total_delivery = round(total_delivery, 2)
    
    return {
        "zone": zone_key,
        "zone_name": zone.name,
        "base_cost": round(base_cost, 2),
        "weight_cost": round(weight_cost, 2),
        "delivery_cost": total_delivery,
        "estimated_days": zone.estimated_days,
        "delivery_option": express["name"],
        "free_delivery": qualifies_for_free,
        "free_delivery_threshold": FREE_DELIVERY_THRESHOLD,
        "amount_to_free_delivery": round(amount_to_free, 2),
        "postcode_area": get_postcode_area(postcode)
    }


def get_delivery_options(postcode: str, subtotal: float, total_weight_kg: float = 1.0) -> Dict:
    """
    Get all available delivery options with prices
    
    Returns dict with all delivery options and their costs
    """
    zone_key, zone = get_delivery_zone(postcode)
    qualifies_for_free = subtotal >= FREE_DELIVERY_THRESHOLD
    
    options = []
    
    for option_key, option in EXPRESS_OPTIONS.items():
        if qualifies_for_free:
            cost = 0.0
        else:
            base_cost = zone.base_price
            weight_cost = max(0, (total_weight_kg - 2)) * zone.price_per_kg
            cost = round((base_cost + weight_cost) * option["multiplier"], 2)
        
        # Adjust estimated days based on express option
        days = zone.estimated_days
        if option_key == "express" and zone_key in ["local", "near"]:
            days = "Next day"
        elif option_key == "next_day" and zone_key in ["local", "near", "mid"]:
            days = "Next day (guaranteed)"
        elif option_key == "next_day":
            days = "1-2 days"
        
        options.append({
            "key": option_key,
            "name": option["name"],
            "cost": cost,
            "estimated_days": days,
            "free": cost == 0
        })
    
    return {
        "zone": zone_key,
        "zone_name": zone.name,
        "options": options,
        "free_delivery_threshold": FREE_DELIVERY_THRESHOLD,
        "qualifies_for_free": qualifies_for_free,
        "amount_to_free_delivery": round(max(0, FREE_DELIVERY_THRESHOLD - subtotal), 2)
    }


# Singleton instance
delivery_service = None

def get_delivery_service():
    global delivery_service
    if delivery_service is None:
        delivery_service = DeliveryService()
    return delivery_service


class DeliveryService:
    """Service class for delivery calculations"""
    
    def __init__(self):
        self.free_threshold = FREE_DELIVERY_THRESHOLD
    
    def calculate(self, postcode: str, subtotal: float, weight_kg: float = 1.0, option: str = "standard"):
        return calculate_delivery_cost(postcode, subtotal, weight_kg, option)
    
    def get_options(self, postcode: str, subtotal: float, weight_kg: float = 1.0):
        return get_delivery_options(postcode, subtotal, weight_kg)
    
    def get_zones_info(self):
        """Get information about all delivery zones"""
        return {
            zone_key: {
                "name": zone.name,
                "base_price": zone.base_price,
                "price_per_kg": zone.price_per_kg,
                "estimated_days": zone.estimated_days
            }
            for zone_key, zone in DELIVERY_ZONES.items()
        }
