import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from bson import ObjectId

async def seed_database():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'afromarket')]
    
    # Clear existing data
    await db.vendors.delete_many({})
    await db.products.delete_many({})
    
    print("Seeding vendors...")
    vendors = [
        {
            "businessName": "Surulere Foods London",
            "description": "Authentic African groceries from West Africa",
            "email": "info@surulerefoods.com",
            "phone": "+44 20 1234 5601",
            "address": "123 High Street",
            "city": "London",
            "postcode": "E1 1AA",
            "location": "London",
            "verified": True,
            "rating": 4.8,
            "totalSales": 1250,
            "commission": 1.0,
            "status": "approved",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "businessName": "Niyis African Store",
            "description": "Premium African food products and ingredients",
            "email": "contact@niyis.co.uk",
            "phone": "+44 161 234 5602",
            "address": "456 Market Road",
            "city": "Manchester",
            "postcode": "M1 1BB",
            "location": "Manchester",
            "verified": True,
            "rating": 4.9,
            "totalSales": 2100,
            "commission": 1.0,
            "status": "approved",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "businessName": "Owino Supermarket",
            "description": "One-stop shop for all African groceries",
            "email": "support@owinosupermarket.com",
            "phone": "+44 121 345 5603",
            "address": "789 Shop Lane",
            "city": "Birmingham",
            "postcode": "B1 1CC",
            "location": "Birmingham",
            "verified": True,
            "rating": 4.7,
            "totalSales": 890,
            "commission": 1.0,
            "status": "approved",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "businessName": "4Way Foods Market",
            "description": "Fresh and authentic African products",
            "email": "hello@4wayfoods.com",
            "phone": "+44 113 456 5604",
            "address": "321 Food Street",
            "city": "Leeds",
            "postcode": "LS1 1DD",
            "location": "Leeds",
            "verified": True,
            "rating": 4.6,
            "totalSales": 1560,
            "commission": 1.0,
            "status": "approved",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "businessName": "Wosiwosi Groceries",
            "description": "Quality African food at great prices",
            "email": "info@wosiwosi.co.uk",
            "phone": "+44 20 9876 5605",
            "address": "654 Commerce Road",
            "city": "London",
            "postcode": "SE1 1EE",
            "location": "London",
            "verified": True,
            "rating": 4.9,
            "totalSales": 1980,
            "commission": 1.0,
            "status": "approved",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
    ]
    
    vendor_results = await db.vendors.insert_many(vendors)
    vendor_ids = vendor_results.inserted_ids
    print(f"✓ Seeded {len(vendor_ids)} vendors")
    
    # Now seed products
    print("Seeding products...")
    products = [
        {
            "name": "Ayoola Poundo Yam Flour",
            "brand": "Ayoola",
            "description": "Premium quality poundo yam flour, perfect for making traditional pounded yam. 100% natural, no additives.",
            "price": 8.99,
            "originalPrice": 10.99,
            "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600",
            "images": [],
            "category": "Grains & Flours",
            "categoryId": 2,
            "vendorId": vendor_ids[0],
            "vendor": {
                "name": vendors[0]["businessName"],
                "rating": vendors[0]["rating"],
                "location": vendors[0]["location"],
                "totalSales": vendors[0]["totalSales"]
            },
            "rating": 4.7,
            "reviews": 124,
            "stock": 45,
            "weight": "1.5kg",
            "inStock": True,
            "featured": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "name": "Fresh Plantains (Bundle)",
            "brand": "Fresh Farms",
            "description": "Fresh ripe plantains, hand-selected for quality. Perfect for frying or boiling.",
            "price": 3.49,
            "image": "https://images.unsplash.com/photo-1610348725531-843dff563e2c?w=600",
            "images": [],
            "category": "Fresh Produce",
            "categoryId": 1,
            "vendorId": vendor_ids[1],
            "vendor": {
                "name": vendors[1]["businessName"],
                "rating": vendors[1]["rating"],
                "location": vendors[1]["location"],
                "totalSales": vendors[1]["totalSales"]
            },
            "rating": 4.9,
            "reviews": 89,
            "stock": 120,
            "weight": "1kg (4-5 pieces)",
            "inStock": True,
            "featured": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "name": "Tropical Sun Nigerian Curry Powder",
            "brand": "Tropical Sun",
            "description": "Authentic Nigerian curry powder blend. Rich flavor perfect for jollof rice, stews, and soups.",
            "price": 4.99,
            "originalPrice": 6.49,
            "image": "https://images.unsplash.com/photo-1505253716362-afaea1d3d1af?w=600",
            "images": [],
            "category": "Condiments & Seasonings",
            "categoryId": 3,
            "vendorId": vendor_ids[2],
            "vendor": {
                "name": vendors[2]["businessName"],
                "rating": vendors[2]["rating"],
                "location": vendors[2]["location"],
                "totalSales": vendors[2]["totalSales"]
            },
            "rating": 4.8,
            "reviews": 256,
            "stock": 78,
            "weight": "400g",
            "inStock": True,
            "featured": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "name": "Rombis Roasted Groundnuts",
            "brand": "Rombis",
            "description": "Crunchy roasted groundnuts with authentic African flavor. Perfect snack any time of day.",
            "price": 2.99,
            "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=600",
            "images": [],
            "category": "Snacks & Confectionery",
            "categoryId": 5,
            "vendorId": vendor_ids[3],
            "vendor": {
                "name": vendors[3]["businessName"],
                "rating": vendors[3]["rating"],
                "location": vendors[3]["location"],
                "totalSales": vendors[3]["totalSales"]
            },
            "rating": 4.6,
            "reviews": 67,
            "stock": 95,
            "weight": "250g",
            "inStock": True,
            "featured": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "name": "Golden Morn Cereal",
            "brand": "Nestle",
            "description": "Nutritious maize-based breakfast cereal fortified with vitamins. A family favorite!",
            "price": 6.49,
            "image": "https://images.unsplash.com/photo-1525385133512-2f3bdd039054?w=600",
            "images": [],
            "category": "Grains & Flours",
            "categoryId": 2,
            "vendorId": vendor_ids[4],
            "vendor": {
                "name": vendors[4]["businessName"],
                "rating": vendors[4]["rating"],
                "location": vendors[4]["location"],
                "totalSales": vendors[4]["totalSales"]
            },
            "rating": 4.9,
            "reviews": 198,
            "stock": 62,
            "weight": "500g",
            "inStock": True,
            "featured": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "name": "Fresh Okra",
            "brand": "Fresh Farms",
            "description": "Fresh okra vegetables, carefully selected. Essential for soups and stews.",
            "price": 2.49,
            "image": "https://images.unsplash.com/photo-1589621316382-008455f857cd?w=600",
            "images": [],
            "category": "Fresh Produce",
            "categoryId": 1,
            "vendorId": vendor_ids[0],
            "vendor": {
                "name": vendors[0]["businessName"],
                "rating": vendors[0]["rating"],
                "location": vendors[0]["location"],
                "totalSales": vendors[0]["totalSales"]
            },
            "rating": 4.7,
            "reviews": 45,
            "stock": 88,
            "weight": "500g",
            "inStock": True,
            "featured": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "name": "Frozen Tilapia Fish",
            "brand": "Ocean Fresh",
            "description": "Premium frozen tilapia fish, cleaned and ready to cook. Rich in protein and omega-3.",
            "price": 12.99,
            "originalPrice": 14.99,
            "image": "https://images.unsplash.com/photo-1544943910-4c1dc44aab44?w=600",
            "images": [],
            "category": "Frozen Foods & Meats",
            "categoryId": 4,
            "vendorId": vendor_ids[1],
            "vendor": {
                "name": vendors[1]["businessName"],
                "rating": vendors[1]["rating"],
                "location": vendors[1]["location"],
                "totalSales": vendors[1]["totalSales"]
            },
            "rating": 4.8,
            "reviews": 132,
            "stock": 34,
            "weight": "1kg",
            "inStock": True,
            "featured": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "name": "Dark & Lovely Hair Relaxer Kit",
            "brand": "Dark & Lovely",
            "description": "Professional hair relaxer system for smooth, manageable hair. Includes all essentials.",
            "price": 9.99,
            "image": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600",
            "images": [],
            "category": "Beauty & Household",
            "categoryId": 8,
            "vendorId": vendor_ids[2],
            "vendor": {
                "name": vendors[2]["businessName"],
                "rating": vendors[2]["rating"],
                "location": vendors[2]["location"],
                "totalSales": vendors[2]["totalSales"]
            },
            "rating": 4.5,
            "reviews": 87,
            "stock": 56,
            "weight": "1 Kit",
            "inStock": True,
            "featured": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "name": "Garri White (Cassava Flakes)",
            "brand": "Rombis",
            "description": "Premium white garri, finely processed cassava flakes. Perfect for eba or soaking.",
            "price": 5.49,
            "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600",
            "images": [],
            "category": "Grains & Flours",
            "categoryId": 2,
            "vendorId": vendor_ids[3],
            "vendor": {
                "name": vendors[3]["businessName"],
                "rating": vendors[3]["rating"],
                "location": vendors[3]["location"],
                "totalSales": vendors[3]["totalSales"]
            },
            "rating": 4.9,
            "reviews": 215,
            "stock": 71,
            "weight": "1kg",
            "inStock": True,
            "featured": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "name": "Suya Spice Mix",
            "brand": "Tropical Sun",
            "description": "Authentic suya spice blend with groundnuts and African spices. Perfect for grilled meats.",
            "price": 3.99,
            "image": "https://images.unsplash.com/photo-1505253716362-afaea1d3d1af?w=600",
            "images": [],
            "category": "Condiments & Seasonings",
            "categoryId": 3,
            "vendorId": vendor_ids[4],
            "vendor": {
                "name": vendors[4]["businessName"],
                "rating": vendors[4]["rating"],
                "location": vendors[4]["location"],
                "totalSales": vendors[4]["totalSales"]
            },
            "rating": 4.8,
            "reviews": 143,
            "stock": 92,
            "weight": "200g",
            "inStock": True,
            "featured": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "name": "Dried Crayfish",
            "brand": "Ocean Harvest",
            "description": "Premium dried crayfish, essential for authentic Nigerian soups and stews.",
            "price": 7.99,
            "image": "https://images.unsplash.com/photo-1599639957043-f4520e1a5586?w=600",
            "images": [],
            "category": "Dried & Preserved Foods",
            "categoryId": 7,
            "vendorId": vendor_ids[0],
            "vendor": {
                "name": vendors[0]["businessName"],
                "rating": vendors[0]["rating"],
                "location": vendors[0]["location"],
                "totalSales": vendors[0]["totalSales"]
            },
            "rating": 4.7,
            "reviews": 98,
            "stock": 43,
            "weight": "200g",
            "inStock": True,
            "featured": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "name": "Plantain Chips (Spicy)",
            "brand": "Afri Snacks",
            "description": "Crispy spicy plantain chips, made from fresh plantains. Addictively delicious!",
            "price": 2.49,
            "image": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=600",
            "images": [],
            "category": "Snacks & Confectionery",
            "categoryId": 5,
            "vendorId": vendor_ids[1],
            "vendor": {
                "name": vendors[1]["businessName"],
                "rating": vendors[1]["rating"],
                "location": vendors[1]["location"],
                "totalSales": vendors[1]["totalSales"]
            },
            "rating": 4.6,
            "reviews": 76,
            "stock": 104,
            "weight": "150g",
            "inStock": True,
            "featured": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
    ]
    
    product_results = await db.products.insert_many(products)
    print(f"✓ Seeded {len(product_results.inserted_ids)} products")
    
    print("\n✅ Database seeded successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
