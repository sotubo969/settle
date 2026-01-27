# Database Seed Script - Real African Grocery Products
import asyncio
from database import AsyncSessionLocal, Product, Vendor, PromoCode, Base, engine
from datetime import datetime, timedelta

# Real African grocery products with actual images
PRODUCTS_DATA = [
    # Fresh Produce
    {
        "name": "Fresh Plantains (Ripe)",
        "brand": "Tropical Fresh",
        "description": "Premium quality ripe plantains, perfect for frying (dodo) or roasting. Sweet and delicious when cooked. Hand-selected for quality.",
        "price": 3.49,
        "original_price": 4.29,
        "image": "https://images.unsplash.com/photo-1603052875302-d376b7c0638a?w=600",
        "images": [
            "https://images.unsplash.com/photo-1603052875302-d376b7c0638a?w=600",
            "https://images.unsplash.com/photo-1528825871115-3581a5387919?w=600"
        ],
        "category": "Fresh Produce",
        "category_id": 1,
        "stock": 150,
        "weight": "1kg (4-5 pieces)",
        "featured": True
    },
    {
        "name": "Fresh Cassava (Yuca)",
        "brand": "African Farms",
        "description": "Fresh cassava root, perfect for boiling, frying, or making fufu. Rich in carbohydrates and naturally gluten-free.",
        "price": 2.99,
        "image": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=600",
        "images": ["https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=600"],
        "category": "Fresh Produce",
        "category_id": 1,
        "stock": 80,
        "weight": "1kg",
        "featured": False
    },
    {
        "name": "Fresh Scotch Bonnet Peppers",
        "brand": "Spice Garden",
        "description": "Authentic Scotch Bonnet peppers with the perfect balance of heat and fruity flavor. Essential for Nigerian and Caribbean cooking.",
        "price": 1.99,
        "image": "https://images.unsplash.com/photo-1583119022894-919a68a3d0e3?w=600",
        "images": ["https://images.unsplash.com/photo-1583119022894-919a68a3d0e3?w=600"],
        "category": "Fresh Produce",
        "category_id": 1,
        "stock": 200,
        "weight": "200g",
        "featured": True
    },
    {
        "name": "Fresh Okra (Lady Fingers)",
        "brand": "Garden Fresh",
        "description": "Tender fresh okra, perfect for soups, stews, and fried dishes. Low in calories, high in fiber and vitamins.",
        "price": 2.49,
        "image": "https://images.unsplash.com/photo-1425543103986-22abb7d7e8d2?w=600",
        "images": ["https://images.unsplash.com/photo-1425543103986-22abb7d7e8d2?w=600"],
        "category": "Fresh Produce",
        "category_id": 1,
        "stock": 100,
        "weight": "500g",
        "featured": False
    },
    
    # Grains & Flours
    {
        "name": "Ayoola Poundo Yam Flour",
        "brand": "Ayoola",
        "description": "Premium quality poundo yam flour for making smooth, stretchy pounded yam. Just add hot water and stir. 100% natural, no additives.",
        "price": 8.99,
        "original_price": 10.99,
        "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600",
        "images": ["https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600"],
        "category": "Grains & Flours",
        "category_id": 2,
        "stock": 75,
        "weight": "1.8kg",
        "featured": True
    },
    {
        "name": "Ijebu Garri (White)",
        "brand": "Mama Gold",
        "description": "Premium white garri from Ijebu, Nigeria. Perfect for drinking (garri soakings) or making eba. Crispy texture with authentic taste.",
        "price": 5.99,
        "image": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600",
        "images": ["https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600"],
        "category": "Grains & Flours",
        "category_id": 2,
        "stock": 120,
        "weight": "1.5kg",
        "featured": True
    },
    {
        "name": "Semovita Semolina",
        "brand": "Semovita",
        "description": "Golden semolina flour for making smooth, fluffy semovita swallow. Premium quality wheat semolina.",
        "price": 6.49,
        "image": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600",
        "images": ["https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600"],
        "category": "Grains & Flours",
        "category_id": 2,
        "stock": 90,
        "weight": "1kg",
        "featured": False
    },
    {
        "name": "Nigerian Beans (Honey Beans)",
        "brand": "Oloyin",
        "description": "Premium Nigerian honey beans (oloyin). Sweet taste, cooks quickly. Perfect for moi moi, akara, and bean stews.",
        "price": 7.99,
        "image": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?w=600",
        "images": ["https://images.unsplash.com/photo-1551462147-ff29053bfc14?w=600"],
        "category": "Grains & Flours",
        "category_id": 2,
        "stock": 60,
        "weight": "1kg",
        "featured": False
    },
    {
        "name": "Ofada Rice (Local Nigerian Rice)",
        "brand": "Ofada Gold",
        "description": "Authentic Nigerian Ofada rice with unique aroma and taste. Perfect with Ayamase stew. Nutritious and filling.",
        "price": 9.99,
        "image": "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=600",
        "images": ["https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=600"],
        "category": "Grains & Flours",
        "category_id": 2,
        "stock": 45,
        "weight": "2kg",
        "featured": True
    },
    
    # Condiments & Seasonings
    {
        "name": "Maggi Cubes (Nigerian)",
        "brand": "Maggi",
        "description": "Original Nigerian Maggi seasoning cubes. Essential for authentic African cooking. Enhances flavor in soups, stews, and rice dishes.",
        "price": 2.99,
        "image": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600",
        "images": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600"],
        "category": "Condiments & Seasonings",
        "category_id": 3,
        "stock": 300,
        "weight": "100 cubes",
        "featured": True
    },
    {
        "name": "Ground Crayfish",
        "brand": "Mama Africa",
        "description": "Finely ground dried crayfish. Adds authentic umami flavor to Nigerian soups like egusi, ogbono, and okra soup.",
        "price": 4.99,
        "image": "https://images.unsplash.com/photo-1599639957043-f4520e1a5586?w=600",
        "images": ["https://images.unsplash.com/photo-1599639957043-f4520e1a5586?w=600"],
        "category": "Condiments & Seasonings",
        "category_id": 3,
        "stock": 85,
        "weight": "200g",
        "featured": False
    },
    {
        "name": "Iru (Locust Beans/Dawadawa)",
        "brand": "Traditional",
        "description": "Fermented locust beans for traditional Nigerian cooking. Adds deep, savory flavor to soups and stews.",
        "price": 3.49,
        "image": "https://images.unsplash.com/photo-1506807803488-8eafc15316c7?w=600",
        "images": ["https://images.unsplash.com/photo-1506807803488-8eafc15316c7?w=600"],
        "category": "Condiments & Seasonings",
        "category_id": 3,
        "stock": 70,
        "weight": "150g",
        "featured": False
    },
    {
        "name": "Suya Spice (Yaji)",
        "brand": "Spice Master",
        "description": "Authentic Nigerian suya spice blend. Perfect for grilled meat, chicken, and fish. Contains groundnut, ginger, and spices.",
        "price": 3.99,
        "image": "https://images.unsplash.com/photo-1596040033229-a0b1e2e89a7d?w=600",
        "images": ["https://images.unsplash.com/photo-1596040033229-a0b1e2e89a7d?w=600"],
        "category": "Condiments & Seasonings",
        "category_id": 3,
        "stock": 150,
        "weight": "100g",
        "featured": True
    },
    {
        "name": "Palm Oil (Zomi)",
        "brand": "Kings",
        "description": "Pure unrefined red palm oil. Rich in vitamins A and E. Essential for Nigerian soups, stews, and jollof rice.",
        "price": 6.99,
        "image": "https://images.unsplash.com/photo-1474979266404-7eaacdc50f6c?w=600",
        "images": ["https://images.unsplash.com/photo-1474979266404-7eaacdc50f6c?w=600"],
        "category": "Condiments & Seasonings",
        "category_id": 3,
        "stock": 100,
        "weight": "1 litre",
        "featured": True
    },
    
    # Frozen Foods & Meats
    {
        "name": "Frozen Goat Meat (Assorted)",
        "brand": "Halal Choice",
        "description": "Premium quality halal goat meat, cut into assorted pieces. Perfect for pepper soup, stews, and Nigerian dishes.",
        "price": 12.99,
        "image": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=600",
        "images": ["https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=600"],
        "category": "Frozen Foods & Meats",
        "category_id": 4,
        "stock": 40,
        "weight": "1kg",
        "featured": True
    },
    {
        "name": "Stockfish (Okporoko)",
        "brand": "Norwegian",
        "description": "Premium Norwegian stockfish. Essential for Nigerian soups like banga, egusi, and ogbono. Adds unique flavor.",
        "price": 15.99,
        "image": "https://images.unsplash.com/photo-1534604973900-c43ab4c2e0ab?w=600",
        "images": ["https://images.unsplash.com/photo-1534604973900-c43ab4c2e0ab?w=600"],
        "category": "Frozen Foods & Meats",
        "category_id": 4,
        "stock": 30,
        "weight": "500g",
        "featured": False
    },
    {
        "name": "Frozen Tilapia Fish (Whole)",
        "brand": "Ocean Fresh",
        "description": "Whole frozen tilapia, cleaned and ready to cook. Perfect for frying, grilling, or making fish stew.",
        "price": 8.99,
        "image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=600",
        "images": ["https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=600"],
        "category": "Frozen Foods & Meats",
        "category_id": 4,
        "stock": 50,
        "weight": "1kg (2-3 fish)",
        "featured": False
    },
    {
        "name": "Smoked Mackerel (Titus)",
        "brand": "Mama's Choice",
        "description": "Traditionally smoked mackerel fish. Ready to use in soups, stews, and sauces. Rich smoky flavor.",
        "price": 5.99,
        "image": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600",
        "images": ["https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600"],
        "category": "Frozen Foods & Meats",
        "category_id": 4,
        "stock": 80,
        "weight": "400g",
        "featured": True
    },
    
    # Snacks & Confectionery
    {
        "name": "Chin Chin (Nigerian)",
        "brand": "Nkatie",
        "description": "Crispy Nigerian chin chin snack. Lightly sweetened and perfectly fried. Great with drinks or as a snack.",
        "price": 3.99,
        "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=600",
        "images": ["https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=600"],
        "category": "Snacks & Confectionery",
        "category_id": 5,
        "stock": 120,
        "weight": "250g",
        "featured": True
    },
    {
        "name": "Plantain Chips (Salted)",
        "brand": "Tropical Snacks",
        "description": "Crunchy salted plantain chips. Delicious African snack made from ripe plantains. Addictively good!",
        "price": 2.49,
        "image": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=600",
        "images": ["https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=600"],
        "category": "Snacks & Confectionery",
        "category_id": 5,
        "stock": 180,
        "weight": "150g",
        "featured": True
    },
    {
        "name": "Kulikuli (Groundnut Snack)",
        "brand": "Traditional",
        "description": "Crunchy groundnut snack from Nigeria. High in protein, perfect with garri or as a standalone snack.",
        "price": 2.99,
        "image": "https://images.unsplash.com/photo-1478145046317-39f10e56b5e9?w=600",
        "images": ["https://images.unsplash.com/photo-1478145046317-39f10e56b5e9?w=600"],
        "category": "Snacks & Confectionery",
        "category_id": 5,
        "stock": 90,
        "weight": "200g",
        "featured": False
    },
    
    # Drinks & Beverages
    {
        "name": "Zobo Drink (Hibiscus)",
        "brand": "Chivita",
        "description": "Refreshing Nigerian zobo drink made from hibiscus flowers. Rich in antioxidants. Served chilled.",
        "price": 2.49,
        "image": "https://images.unsplash.com/photo-1544145945-35cd6b44be0b?w=600",
        "images": ["https://images.unsplash.com/photo-1544145945-35cd6b44be0b?w=600"],
        "category": "Drinks & Beverages",
        "category_id": 6,
        "stock": 200,
        "weight": "500ml",
        "featured": True
    },
    {
        "name": "Milo Chocolate Drink",
        "brand": "Nestle",
        "description": "Nigerian Milo chocolate malt drink. Nutritious and energizing. Perfect hot or cold.",
        "price": 7.99,
        "image": "https://images.unsplash.com/photo-1517578239113-b03992dcdd25?w=600",
        "images": ["https://images.unsplash.com/photo-1517578239113-b03992dcdd25?w=600"],
        "category": "Drinks & Beverages",
        "category_id": 6,
        "stock": 100,
        "weight": "400g",
        "featured": True
    },
    {
        "name": "Peak Evaporated Milk",
        "brand": "Peak",
        "description": "Creamy evaporated milk, a Nigerian household staple. Perfect for tea, coffee, and cereal.",
        "price": 1.99,
        "image": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600",
        "images": ["https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600"],
        "category": "Drinks & Beverages",
        "category_id": 6,
        "stock": 250,
        "weight": "410g",
        "featured": False
    },
    {
        "name": "Palm Wine (Authentic)",
        "brand": "Village Fresh",
        "description": "Authentic Nigerian palm wine. Sweet, slightly fermented natural drink. Refreshing and traditional.",
        "price": 5.99,
        "image": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600",
        "images": ["https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600"],
        "category": "Drinks & Beverages",
        "category_id": 6,
        "stock": 50,
        "weight": "1 litre",
        "featured": False
    },
    
    # Dried & Preserved Foods
    {
        "name": "Egusi Seeds (Ground)",
        "brand": "Mama's Kitchen",
        "description": "Finely ground melon seeds for making Nigerian egusi soup. Rich, nutty flavor. Just add to your soup base.",
        "price": 6.99,
        "image": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=600",
        "images": ["https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=600"],
        "category": "Dried & Preserved Foods",
        "category_id": 7,
        "stock": 100,
        "weight": "500g",
        "featured": True
    },
    {
        "name": "Ogbono Seeds (Ground)",
        "brand": "Traditional",
        "description": "Ground African mango seeds for making draw soup. Creates the signature thick, slippery texture.",
        "price": 7.99,
        "image": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=600",
        "images": ["https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=600"],
        "category": "Dried & Preserved Foods",
        "category_id": 7,
        "stock": 80,
        "weight": "400g",
        "featured": True
    },
    {
        "name": "Dried Bitter Leaf",
        "brand": "Mama Africa",
        "description": "Dried bitter leaf for making ofe onugbu (bitter leaf soup). Pre-washed and ready to cook.",
        "price": 4.49,
        "image": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600",
        "images": ["https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600"],
        "category": "Dried & Preserved Foods",
        "category_id": 7,
        "stock": 60,
        "weight": "100g",
        "featured": False
    },
    {
        "name": "Uziza Seeds",
        "brand": "Spice Master",
        "description": "Aromatic uziza seeds for Nigerian pepper soup and stews. Adds warmth and depth of flavor.",
        "price": 3.99,
        "image": "https://images.unsplash.com/photo-1506807803488-8eafc15316c7?w=600",
        "images": ["https://images.unsplash.com/photo-1506807803488-8eafc15316c7?w=600"],
        "category": "Dried & Preserved Foods",
        "category_id": 7,
        "stock": 90,
        "weight": "100g",
        "featured": False
    },
    
    # Beauty & Household
    {
        "name": "African Black Soap",
        "brand": "Dudu Osun",
        "description": "Authentic African black soap with shea butter and honey. Natural cleansing for face and body. Helps with acne and skin brightening.",
        "price": 4.99,
        "image": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600",
        "images": ["https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600"],
        "category": "Beauty & Household",
        "category_id": 8,
        "stock": 150,
        "weight": "150g",
        "featured": True
    },
    {
        "name": "Shea Butter (Raw/Unrefined)",
        "brand": "Pure African",
        "description": "100% raw unrefined shea butter from Ghana. Perfect for moisturizing skin and hair. Rich in vitamins A and E.",
        "price": 8.99,
        "image": "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=600",
        "images": ["https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=600"],
        "category": "Beauty & Household",
        "category_id": 8,
        "stock": 80,
        "weight": "500g",
        "featured": True
    },
    {
        "name": "African Chewing Stick (Orin)",
        "brand": "Natural Care",
        "description": "Traditional African chewing stick for natural teeth cleaning. Contains natural antibacterial properties.",
        "price": 1.99,
        "image": "https://images.unsplash.com/photo-1609840114035-3c981b782dfe?w=600",
        "images": ["https://images.unsplash.com/photo-1609840114035-3c981b782dfe?w=600"],
        "category": "Beauty & Household",
        "category_id": 8,
        "stock": 200,
        "weight": "5 sticks",
        "featured": False
    },
]

# Sample vendors
VENDORS_DATA = [
    {
        "business_name": "Mama Nkechi's African Store",
        "description": "Premium African groceries from Lagos to London. Family-run business since 2010.",
        "email": "mama.nkechi@afromarket.uk",
        "phone": "07712345678",
        "address": "123 High Street",
        "city": "London",
        "postcode": "E1 6AN",
        "location": "London",
        "verified": True,
        "rating": 4.8,
        "total_sales": 2540,
        "status": "approved"
    },
    {
        "business_name": "Wosiwosi Foods Ltd",
        "description": "Authentic West African groceries. Quality guaranteed.",
        "email": "info@wosiwosi.uk",
        "phone": "07823456789",
        "address": "45 Market Road",
        "city": "Manchester",
        "postcode": "M1 1AD",
        "location": "Manchester",
        "verified": True,
        "rating": 4.9,
        "total_sales": 3200,
        "status": "approved"
    },
    {
        "business_name": "African Food Warehouse",
        "description": "Wholesale and retail African food supplies. Best prices guaranteed.",
        "email": "orders@africanfoodwarehouse.co.uk",
        "phone": "07934567890",
        "address": "78 Industrial Estate",
        "city": "Birmingham",
        "postcode": "B1 2HN",
        "location": "Birmingham",
        "verified": True,
        "rating": 4.7,
        "total_sales": 1890,
        "status": "approved"
    }
]

# Promo codes
PROMO_CODES_DATA = [
    {
        "code": "WELCOME10",
        "discount_type": "percentage",
        "discount_value": 10,
        "min_order_amount": 20,
        "max_discount": 15,
        "usage_limit": 1000,
        "per_user_limit": 1,
        "valid_until": datetime.utcnow() + timedelta(days=90)
    },
    {
        "code": "AFRO20",
        "discount_type": "percentage",
        "discount_value": 20,
        "min_order_amount": 50,
        "max_discount": 30,
        "usage_limit": 500,
        "per_user_limit": 1,
        "valid_until": datetime.utcnow() + timedelta(days=30)
    },
    {
        "code": "FREEDELIVERY",
        "discount_type": "fixed",
        "discount_value": 4.99,
        "min_order_amount": 30,
        "usage_limit": 200,
        "per_user_limit": 2,
        "valid_until": datetime.utcnow() + timedelta(days=60)
    },
    {
        "code": "NEWCUSTOMER",
        "discount_type": "fixed",
        "discount_value": 5,
        "min_order_amount": 25,
        "usage_limit": None,
        "per_user_limit": 1,
        "valid_until": datetime.utcnow() + timedelta(days=365)
    }
]

async def seed_database():
    """Seed the database with products, vendors, and promo codes"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if already seeded
            from sqlalchemy import select, func
            result = await session.execute(select(func.count(Product.id)))
            product_count = result.scalar()
            
            if product_count > 0:
                print(f"Database already has {product_count} products. Skipping seed.")
                return
            
            # Create vendors
            vendors = []
            for vendor_data in VENDORS_DATA:
                vendor = Vendor(**vendor_data)
                session.add(vendor)
                vendors.append(vendor)
            
            await session.flush()
            print(f"Created {len(vendors)} vendors")
            
            # Create products (distribute among vendors)
            for i, product_data in enumerate(PRODUCTS_DATA):
                vendor = vendors[i % len(vendors)]
                product = Product(
                    **product_data,
                    vendor_id=vendor.id,
                    vendor_info={
                        "id": vendor.id,
                        "name": vendor.business_name,
                        "rating": vendor.rating,
                        "totalSales": vendor.total_sales,
                        "location": vendor.location,
                        "verified": vendor.verified
                    },
                    rating=round(4.0 + (i % 10) / 10, 1),
                    reviews=(i + 1) * 15
                )
                session.add(product)
            
            print(f"Created {len(PRODUCTS_DATA)} products")
            
            # Create promo codes
            for promo_data in PROMO_CODES_DATA:
                promo = PromoCode(**promo_data)
                session.add(promo)
            
            print(f"Created {len(PROMO_CODES_DATA)} promo codes")
            
            await session.commit()
            print("✅ Database seeded successfully!")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding database: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(seed_database())
