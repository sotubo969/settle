import asyncio
from database import AsyncSessionLocal, init_db, Vendor, Product
from datetime import datetime
import json

async def seed_sql_database():
    # Initialize database
    await init_db()
    print("Database tables created")
    
    async with AsyncSessionLocal() as session:
        # Clear existing data
        print("Clearing existing data...")
        
        print("Seeding vendors...")
        vendors_data = [
            {
                "business_name": "Surulere Foods London",
                "description": "Authentic African groceries from West Africa",
                "email": "info@surulerefoods.com",
                "phone": "+44 20 1234 5601",
                "address": "123 High Street",
                "city": "London",
                "postcode": "E1 1AA",
                "location": "England",
                "verified": True,
                "rating": 4.8,
                "total_sales": 1250,
                "commission": 1.0,
                "status": "approved"
            },
            {
                "business_name": "Niyis African Store",
                "description": "Premium African food products and ingredients",
                "email": "contact@niyis.co.uk",
                "phone": "+44 161 234 5602",
                "address": "456 Market Road",
                "city": "Manchester",
                "postcode": "M1 1BB",
                "location": "England",
                "verified": True,
                "rating": 4.9,
                "total_sales": 2100,
                "commission": 1.0,
                "status": "approved"
            },
            {
                "business_name": "Owino Supermarket",
                "description": "One-stop shop for all African groceries",
                "email": "support@owinosupermarket.com",
                "phone": "+44 121 345 5603",
                "address": "789 Shop Lane",
                "city": "Birmingham",
                "postcode": "B1 1CC",
                "location": "England",
                "verified": True,
                "rating": 4.7,
                "total_sales": 890,
                "commission": 1.0,
                "status": "approved"
            },
            {
                "business_name": "4Way Foods Market",
                "description": "Fresh and authentic African products",
                "email": "hello@4wayfoods.com",
                "phone": "+44 113 456 5604",
                "address": "321 Food Street",
                "city": "Leeds",
                "postcode": "LS1 1DD",
                "location": "England",
                "verified": True,
                "rating": 4.6,
                "total_sales": 1560,
                "commission": 1.0,
                "status": "approved"
            },
            {
                "business_name": "Wosiwosi Groceries",
                "description": "Quality African food at great prices",
                "email": "info@wosiwosi.co.uk",
                "phone": "+44 20 9876 5605",
                "address": "654 Commerce Road",
                "city": "London",
                "postcode": "SE1 1EE",
                "location": "England",
                "verified": True,
                "rating": 4.9,
                "total_sales": 1980,
                "commission": 1.0,
                "status": "approved"
            }
        ]
        
        vendors = []
        for v_data in vendors_data:
            vendor = Vendor(**v_data)
            session.add(vendor)
            vendors.append(vendor)
        
        await session.flush()
        print(f"✓ Seeded {len(vendors)} vendors")
        
        print("Seeding products...")
        products_data = [
            {
                "name": "Ayoola Poundo Yam Flour",
                "brand": "Ayoola",
                "description": "Premium quality poundo yam flour, perfect for making traditional pounded yam. 100% natural, no additives.",
                "price": 8.99,
                "original_price": 10.99,
                "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600",
                "category": "Grains & Flours",
                "category_id": 2,
                "vendor_id": 1,
                "rating": 4.7,
                "reviews": 124,
                "stock": 45,
                "weight": "1.5kg",
                "featured": True
            },
            {
                "name": "Fresh Plantains (Bundle)",
                "brand": "Fresh Farms",
                "description": "Fresh ripe plantains, hand-selected for quality. Perfect for frying or boiling.",
                "price": 3.49,
                "image": "https://images.unsplash.com/photo-1610348725531-843dff563e2c?w=600",
                "category": "Fresh Produce",
                "category_id": 1,
                "vendor_id": 2,
                "rating": 4.9,
                "reviews": 89,
                "stock": 120,
                "weight": "1kg (4-5 pieces)",
                "featured": True
            },
            {
                "name": "Tropical Sun Nigerian Curry Powder",
                "brand": "Tropical Sun",
                "description": "Authentic Nigerian curry powder blend. Rich flavor perfect for jollof rice, stews, and soups.",
                "price": 4.99,
                "original_price": 6.49,
                "image": "https://images.unsplash.com/photo-1596040033229-a0b1e2e89a7d?w=600",
                "category": "Condiments & Seasonings",
                "category_id": 3,
                "vendor_id": 3,
                "rating": 4.8,
                "reviews": 256,
                "stock": 78,
                "weight": "400g",
                "featured": True
            },
            {
                "name": "Rombis Roasted Groundnuts",
                "brand": "Rombis",
                "description": "Crunchy roasted groundnuts with authentic African flavor. Perfect snack any time of day.",
                "price": 2.99,
                "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=600",
                "category": "Snacks & Confectionery",
                "category_id": 5,
                "vendor_id": 4,
                "rating": 4.6,
                "reviews": 67,
                "stock": 95,
                "weight": "250g",
                "featured": False
            },
            {
                "name": "Golden Morn Cereal",
                "brand": "Nestle",
                "description": "Nutritious maize-based breakfast cereal fortified with vitamins. A family favorite!",
                "price": 6.49,
                "image": "https://images.unsplash.com/photo-1525385133512-2f3bdd039054?w=600",
                "category": "Grains & Flours",
                "category_id": 2,
                "vendor_id": 5,
                "rating": 4.9,
                "reviews": 198,
                "stock": 62,
                "weight": "500g",
                "featured": True
            },
            {
                "name": "Fresh Okra",
                "brand": "Fresh Farms",
                "description": "Fresh okra vegetables, carefully selected. Essential for soups and stews.",
                "price": 2.49,
                "image": "https://images.unsplash.com/photo-1589621316382-008455f857cd?w=600",
                "category": "Fresh Produce",
                "category_id": 1,
                "vendor_id": 1,
                "rating": 4.7,
                "reviews": 45,
                "stock": 88,
                "weight": "500g",
                "featured": False
            },
            {
                "name": "Frozen Tilapia Fish",
                "brand": "Ocean Fresh",
                "description": "Premium frozen tilapia fish, cleaned and ready to cook. Rich in protein and omega-3.",
                "price": 12.99,
                "original_price": 14.99,
                "image": "https://images.unsplash.com/photo-1544943910-4c1dc44aab44?w=600",
                "category": "Frozen Foods & Meats",
                "category_id": 4,
                "vendor_id": 2,
                "rating": 4.8,
                "reviews": 132,
                "stock": 34,
                "weight": "1kg",
                "featured": True
            },
            {
                "name": "Dark & Lovely Hair Relaxer Kit",
                "brand": "Dark & Lovely",
                "description": "Professional hair relaxer system for smooth, manageable hair. Includes all essentials.",
                "price": 9.99,
                "image": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600",
                "category": "Beauty & Household",
                "category_id": 8,
                "vendor_id": 3,
                "rating": 4.5,
                "reviews": 87,
                "stock": 56,
                "weight": "1 Kit",
                "featured": False
            },
            {
                "name": "Garri White (Cassava Flakes)",
                "brand": "Rombis",
                "description": "Premium white garri, finely processed cassava flakes. Perfect for eba or soaking.",
                "price": 5.49,
                "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600",
                "category": "Grains & Flours",
                "category_id": 2,
                "vendor_id": 4,
                "rating": 4.9,
                "reviews": 215,
                "stock": 71,
                "weight": "1kg",
                "featured": True
            },
            {
                "name": "Suya Spice Mix",
                "brand": "Tropical Sun",
                "description": "Authentic suya spice blend with groundnuts and African spices. Perfect for grilled meats.",
                "price": 3.99,
                "image": "https://images.unsplash.com/photo-1596040033229-a0b1e2e89a7d?w=600",
                "category": "Condiments & Seasonings",
                "category_id": 3,
                "vendor_id": 5,
                "rating": 4.8,
                "reviews": 143,
                "stock": 92,
                "weight": "200g",
                "featured": False
            },
            {
                "name": "Dried Crayfish",
                "brand": "Ocean Harvest",
                "description": "Premium dried crayfish, essential for authentic Nigerian soups and stews.",
                "price": 7.99,
                "image": "https://images.unsplash.com/photo-1599639957043-f4520e1a5586?w=600",
                "category": "Dried & Preserved Foods",
                "category_id": 7,
                "vendor_id": 1,
                "rating": 4.7,
                "reviews": 98,
                "stock": 43,
                "weight": "200g",
                "featured": False
            },
            {
                "name": "Plantain Chips (Spicy)",
                "brand": "Afri Snacks",
                "description": "Crispy spicy plantain chips, made from fresh plantains. Addictively delicious!",
                "price": 2.49,
                "image": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=600",
                "category": "Snacks & Confectionery",
                "category_id": 5,
                "vendor_id": 2,
                "rating": 4.6,
                "reviews": 76,
                "stock": 104,
                "weight": "150g",
                "featured": False
            }
        ]
        
        for idx, p_data in enumerate(products_data):
            vendor_idx = (p_data['vendor_id'] - 1) % len(vendors)
            vendor = vendors[vendor_idx]
            
            p_data['vendor_id'] = vendor.id
            p_data['vendor_info'] = {
                "name": vendor.business_name,
                "rating": vendor.rating,
                "location": vendor.location,
                "totalSales": vendor.total_sales
            }
            
            product = Product(**p_data)
            session.add(product)
        
        await session.commit()
        print(f"✓ Seeded {len(products_data)} products")
        
        print("\n✅ SQL Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_sql_database())
