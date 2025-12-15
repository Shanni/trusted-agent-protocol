#!/usr/bin/env python3
"""
Seed database with MonkeDAO Art products
Featuring Solana Monkey Business inspired pixel art collectibles
Prices: $0.00 - $0.30 USD
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database.database import SessionLocal, engine
from app.models.models import Base, Product
from sqlalchemy.orm import Session

# Create tables
Base.metadata.create_all(bind=engine)

def seed_monkedao_products():
    """Seed the database with MonkeDAO Art products"""
    db = SessionLocal()
    
    try:
        # Clear existing products
        db.query(Product).delete()
        
        # MonkeDAO Art Products - Solana Monkey Business inspired
        # All prices between $0.00 - $0.30 for micro-transactions
        # Using verified working image URLs: DiceBear pixel art API + quality monkey photos
        products = [
            {
                "name": "SMB Pixel Monke #001 - Blue Cap",
                "description": "Authentic pixel art avatar with unique traits! Generated with DiceBear pixel art style. Perfect for collectors who love retro 8-bit aesthetics and NFT culture.",
                "price": 0.25,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke001&size=400",
                "stock_quantity": 50
            },
            {
                "name": "SMB Pixel Monke #002 - Red Bandana",
                "description": "Classic pixel art character with vibrant colors! Unique deterministic generation ensures this monke is one-of-a-kind. True SMB spirit!",
                "price": 0.20,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke002&size=400",
                "stock_quantity": 50
            },
            {
                "name": "SMB Pixel Monke #003 - Golden Shades",
                "description": "Retro pixel art masterpiece! Reject humanity, return to monke! This 8-bit style avatar is perfect for minimalist collectors who love classic gaming aesthetics.",
                "price": 0.30,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke003&size=400",
                "stock_quantity": 30
            },
            {
                "name": "SMB Pixel Monke #004 - Green Vibes",
                "description": "Chill pixel art avatar with positive energy! Perfect for MonkeDAO community members and Solana enthusiasts who love fun retro collectibles.",
                "price": 0.15,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke004&size=400",
                "stock_quantity": 60
            },
            {
                "name": "SMB Pixel Monke #005 - Purple Crown",
                "description": "Royal pixel art edition with majestic presence! Limited edition from the SMB Gen2 collection style. Own a piece of MonkeDAO royalty!",
                "price": 0.28,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke005&size=400",
                "stock_quantity": 25
            },
            {
                "name": "SMB Pixel Monke #006 - Orange Energy",
                "description": "Vibrant pixel art character bursting with energy! This retro 8-bit avatar captures the playful spirit of Solana Monkey Business. Great for collectors who love bold pixel aesthetics.",
                "price": 0.18,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke006&size=400",
                "stock_quantity": 55
            },
            {
                "name": "SMB Pixel Monke #007 - Pink Paradise",
                "description": "Sweet pixel art edition with adorable 8-bit charm! This retro variant is perfect for collectors who appreciate classic gaming aesthetics. Cute and collectible!",
                "price": 0.22,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke007&size=400",
                "stock_quantity": 45
            },
            {
                "name": "SMB Pixel Monke #008 - Laser Eyes",
                "description": "Epic pixel art edition with legendary traits! Diamond hands approved. True builder status in the Solana ecosystem. Ultra-rare 8-bit collector's item!",
                "price": 0.30,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke008&size=400",
                "stock_quantity": 20
            },
            {
                "name": "SMB Pixel Monke #009 - Space Suit",
                "description": "AstroMonke pixel art ready for cosmic adventure! Retro 8-bit space vibes inspired by the legendary SMB Gen1 space collection. To the moon!",
                "price": 0.27,
                "category": "Space Collection",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke009&size=400",
                "stock_quantity": 35
            },
            {
                "name": "SMB Pixel Monke #010 - Yellow Smile",
                "description": "Sunshine pixel art edition spreading joy and positive vibes! Bright and cheerful 8-bit character perfect for MonkeDAO community members who love happy retro collectibles.",
                "price": 0.12,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke010&size=400",
                "stock_quantity": 70
            },
            {
                "name": "SMB Pixel Monke #011 - Cyber Punk",
                "description": "Futuristic pixel art edition with cool digital vibes! Web3 builder aesthetic in classic 8-bit style. Perfect for tech-savvy collectors in the Solana ecosystem.",
                "price": 0.24,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke011&size=400",
                "stock_quantity": 40
            },
            {
                "name": "SMB Pixel Monke #012 - Rainbow Rare",
                "description": "Ultra-rare pixel art edition with maximum retro vibrancy! One of the most sought-after 8-bit variants in the collection. Extremely limited supply!",
                "price": 0.30,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke012&size=400",
                "stock_quantity": 15
            },
            {
                "name": "SMB Pixel Monke #013 - Monkalien",
                "description": "Mysterious pixel art Monkalien from the Gen1 legacy collection. Cosmic 8-bit vibes and alien energy! Perfect for space-themed retro collectors.",
                "price": 0.29,
                "category": "Space Collection",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke013&size=400",
                "stock_quantity": 22
            },
            {
                "name": "SMB Pixel Monke #014 - Banana King",
                "description": "The legendary Banana King in glorious pixel art! Holding the sacred banana with 8-bit pride. MonkeDAO royalty edition for true believers.",
                "price": 0.26,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke014&size=400",
                "stock_quantity": 38
            },
            {
                "name": "SMB Pixel Monke #015 - OG Monke",
                "description": "Original OG Monke in vintage pixel art from the earliest days. True Solana pioneer status. Ultra-rare 8-bit airdrop edition for early believers!",
                "price": 0.30,
                "category": "OG Collection",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke015&size=400",
                "stock_quantity": 10
            },
            {
                "name": "SMB Pixel Monke #016 - Jungle Jam",
                "description": "Jungle Jam pixel art edition from the Audius collaboration! Music and monkes unite in this groovy 8-bit collectible. Retro gaming meets web3!",
                "price": 0.16,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke016&size=400",
                "stock_quantity": 65
            },
            {
                "name": "SMB Pixel Monke #017 - Diamond Hands",
                "description": "True diamond hands pixel art edition. HODL forever! Built different in the Solana community. For serious 8-bit collectors only.",
                "price": 0.25,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke017&size=400",
                "stock_quantity": 42
            },
            {
                "name": "SMB Pixel Monke #018 - Monkanician",
                "description": "Skilled Monkanician in retro pixel art from Gen1! Expert in all things technical and blockchain. Perfect for tech builders who love 8-bit aesthetics.",
                "price": 0.28,
                "category": "Space Collection",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke018&size=400",
                "stock_quantity": 28
            },
            {
                "name": "SMB Pixel Monke #019 - Chill Vibes",
                "description": "Relaxed pixel art edition with ultimate chill vibes. Perfect for laid-back collectors who appreciate zen 8-bit aesthetics and retro gaming culture.",
                "price": 0.10,
                "category": "Pixel Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke019&size=400",
                "stock_quantity": 80
            },
            {
                "name": "SMB Pixel Monke #020 - Gen3 Barrel",
                "description": "SMB Gen3 Barrel holder in stunning pixel art! Part of the 15,000 visually stunning Gen3 collection. Express your unique web3 identity with 8-bit style!",
                "price": 0.30,
                "category": "Gen3 Collection",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monke020&size=400",
                "stock_quantity": 18
            },
            {
                "name": "Monke Sticker Pack - 5 Pack",
                "description": "Collection of 5 random adorable pixel art monkey stickers! Perfect for decorating your laptop, water bottle, or phone case. Spread the retro monke love!",
                "price": 0.05,
                "category": "Collectibles",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monkestickers&size=400",
                "stock_quantity": 100
            },
            {
                "name": "Monke Digital Badge",
                "description": "Official MonkeDAO digital badge in pixel art style! Show your membership in the curated community of monkes. Display with pride on social media!",
                "price": 0.08,
                "category": "Collectibles",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monkebadge&size=400",
                "stock_quantity": 150
            },
            {
                "name": "Pixel Monke Wallpaper",
                "description": "High-quality pixel art monkey wallpaper for your desktop, phone, or tablet. Embrace the retro monke lifestyle 24/7! Instant download after purchase.",
                "price": 0.03,
                "category": "Digital Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monkewallpaper&size=400",
                "stock_quantity": 200
            },
            {
                "name": "Monke Avatar Pack",
                "description": "Set of 3 unique pixel art monkey avatars for Twitter, Discord, and Instagram! Stand out with authentic 8-bit MonkeDAO style. Perfect for web3 social presence.",
                "price": 0.07,
                "category": "Digital Art",
                "image_url": "https://api.dicebear.com/9.x/pixel-art/svg?seed=monkeavatar&size=400",
                "stock_quantity": 120
            }
        ]
        
        # Add products to database
        for product_data in products:
            product = Product(**product_data)
            db.add(product)
        
        db.commit()
        print(f"✅ Successfully seeded {len(products)} MonkeDAO Art products!")
        
        # Print summary
        print("\n📊 Product Categories:")
        categories = db.query(Product.category).distinct().all()
        for cat in categories:
            count = db.query(Product).filter(Product.category == cat[0]).count()
            print(f"  - {cat[0]}: {count} products")
        
        print(f"\n💰 Price Range: ${min(p['price'] for p in products):.2f} - ${max(p['price'] for p in products):.2f}")
        print(f"📦 Total Stock: {sum(p['stock_quantity'] for p in products)} items")
        print(f"\n🐵 Reject humanity, return to monke! 🍌")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🐵 Seeding MonkeDAO Art products...")
    print("🍌 Solana Monkey Business inspired collection")
    print("💎 All prices: $0.00 - $0.30 USD\n")
    seed_monkedao_products()
