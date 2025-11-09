#!/usr/bin/env python3
"""
Seed database with Shanni Art products
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database.database import SessionLocal, engine
from app.models.models import Base, Product
from sqlalchemy.orm import Session

# Create tables
Base.metadata.create_all(bind=engine)

def seed_shanni_art_products():
    """Seed the database with Shanni Art products"""
    db = SessionLocal()
    
    try:
        # Clear existing products
        db.query(Product).delete()
        
        # Shanni Art Products - Inspired by Instagram art style
        products = [
            {
                "name": "Daily Drawing #1 - Morning Coffee",
                "description": "A charming illustration capturing the peaceful moment of morning coffee. Hand-drawn with delicate lines and warm colors. Perfect for coffee lovers and art enthusiasts.",
                "price": 45.00,
                "category": "Illustrations",
                "image_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=800",
                "stock_quantity": 15
            },
            {
                "name": "Daily Drawing #2 - City Sunset",
                "description": "Urban landscape bathed in golden hour light. This piece captures the magic of city life at dusk with vibrant sienna and pink tones.",
                "price": 55.00,
                "category": "Illustrations",
                "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=800",
                "stock_quantity": 12
            },
            {
                "name": "Daily Drawing #3 - Floral Dreams",
                "description": "Delicate botanical illustration featuring soft petals and organic forms. Created with gentle strokes in beige and pink hues.",
                "price": 50.00,
                "category": "Botanical Art",
                "image_url": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=800",
                "stock_quantity": 20
            },
            {
                "name": "Daily Drawing #4 - Cozy Corner",
                "description": "An intimate scene of a reading nook with warm lighting. This illustration evokes feelings of comfort and tranquility.",
                "price": 48.00,
                "category": "Interior Scenes",
                "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800",
                "stock_quantity": 18
            },
            {
                "name": "Daily Drawing #5 - Abstract Thoughts",
                "description": "Contemporary abstract piece with flowing forms in sienna, beige, and rose tones. A meditation on color and movement.",
                "price": 65.00,
                "category": "Abstract Art",
                "image_url": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800",
                "stock_quantity": 10
            },
            {
                "name": "Daily Drawing #6 - Peaceful Garden",
                "description": "Serene garden scene with delicate flowers and soft shadows. Hand-illustrated with attention to every petal and leaf.",
                "price": 52.00,
                "category": "Botanical Art",
                "image_url": "https://images.unsplash.com/photo-1464047736614-af63643285bf?w=800",
                "stock_quantity": 16
            },
            {
                "name": "Daily Drawing #7 - Minimalist Portrait",
                "description": "Simple yet expressive portrait study. Clean lines and subtle shading create a timeless piece.",
                "price": 58.00,
                "category": "Portraits",
                "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=800",
                "stock_quantity": 14
            },
            {
                "name": "Daily Drawing #8 - Autumn Leaves",
                "description": "Celebration of fall colors with rich sienna and golden tones. Each leaf carefully rendered with unique character.",
                "price": 46.00,
                "category": "Nature Art",
                "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800",
                "stock_quantity": 22
            },
            {
                "name": "Daily Drawing #9 - Dreamy Landscape",
                "description": "Ethereal landscape with soft horizons and gentle color gradients. A peaceful escape into nature.",
                "price": 60.00,
                "category": "Landscapes",
                "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
                "stock_quantity": 11
            },
            {
                "name": "Daily Drawing #10 - Vintage Vibes",
                "description": "Nostalgic illustration with retro aesthetics. Warm earth tones and classic composition.",
                "price": 54.00,
                "category": "Vintage Art",
                "image_url": "https://images.unsplash.com/photo-1502691876148-a84978e59af8?w=800",
                "stock_quantity": 13
            },
            {
                "name": "Daily Drawing #11 - Geometric Harmony",
                "description": "Modern geometric design with balanced shapes and harmonious colors. Perfect for contemporary spaces.",
                "price": 62.00,
                "category": "Abstract Art",
                "image_url": "https://images.unsplash.com/photo-1549887534-1541e9326642?w=800",
                "stock_quantity": 9
            },
            {
                "name": "Daily Drawing #12 - Whimsical Characters",
                "description": "Playful character illustration with charming details. Brings joy and personality to any room.",
                "price": 49.00,
                "category": "Character Art",
                "image_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=800",
                "stock_quantity": 17
            },
            {
                "name": "Limited Edition Print Set",
                "description": "Exclusive set of 5 selected daily drawings. Each print signed and numbered. A collector's treasure.",
                "price": 225.00,
                "category": "Limited Edition",
                "image_url": "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=800",
                "stock_quantity": 5
            },
            {
                "name": "Daily Drawing #13 - Soft Pastels",
                "description": "Gentle pastel composition with dreamy quality. Soft pinks and beiges create a soothing atmosphere.",
                "price": 51.00,
                "category": "Abstract Art",
                "image_url": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800",
                "stock_quantity": 19
            },
            {
                "name": "Daily Drawing #14 - Urban Sketches",
                "description": "Quick sketches of city life capturing spontaneous moments. Raw and authentic urban energy.",
                "price": 44.00,
                "category": "Illustrations",
                "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=800",
                "stock_quantity": 21
            }
        ]
        
        # Add products to database
        for product_data in products:
            product = Product(**product_data)
            db.add(product)
        
        db.commit()
        print(f"✅ Successfully seeded {len(products)} Shanni Art products!")
        
        # Print summary
        print("\n📊 Product Categories:")
        categories = db.query(Product.category).distinct().all()
        for cat in categories:
            count = db.query(Product).filter(Product.category == cat[0]).count()
            print(f"  - {cat[0]}: {count} products")
        
        print(f"\n💰 Price Range: ${min(p['price'] for p in products):.2f} - ${max(p['price'] for p in products):.2f}")
        print(f"📦 Total Stock: {sum(p['stock_quantity'] for p in products)} items")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🎨 Seeding Shanni Art products...")
    seed_shanni_art_products()
