# 🎨 TAP Shanni Art Gallery - Quick Start

## One-Command Setup

```bash
./start_shanni_art.sh
```

This will seed the database with 15 beautiful art products!

---


## Access the Gallery

### 🎨 Shanni Art Gallery
**URL:** http://localhost:3000

**What you'll see:**
- Beautiful sienna and beige-pink theme
- 15 unique art products
- Elegant rounded design
- Instagram link to @shanni_daily_drawing

### 🤖 TAP Agent (Optional)
**URL:** http://localhost:8501

**What it does:**
- Automated shopping flow
- View product → Add to cart → Checkout
- RFC 9421 signatures
- Complete purchase automation

---

## 🎨 What's New?

### Visual Transformation

**Before:** TAP Sample Merchant
- Dark blue corporate theme
- Generic products
- Standard e-commerce look

**After:** TAP Shanni Art Gallery
- Warm sienna and beige-pink
- Art-focused products
- Gallery aesthetic

### Color Palette

```
Primary:   #A0522D (Sienna)
Accent:    #D2691E (Chocolate)
Light:     #FFF5EE (Seashell)
Pink:      #FFE4E1 (Misty Rose)
Dark:      #8B4513 (Saddle Brown)
```

### Products

- **Daily Drawing Series** - Charming illustrations
- **Botanical Art** - Floral and garden scenes
- **Abstract Art** - Contemporary pieces
- **Limited Editions** - Collector's items
- **And more!** - 15 unique products total

---  

### Agent Features
✅ Complete automation  
✅ RFC 9421 signatures  
✅ RSA + Ed25519 support  
✅ Real-time progress  
✅ Product extraction  
✅ Order confirmation  

---

## 🔧 Troubleshooting

### Database Not Seeded?

```bash
cd merchant-backend
python seed_shanni_art.py
```

### Frontend Not Starting?

```bash
cd merchant-frontend
npm install
npm start
```

### Agent Errors?

Make sure keys are configured:
```bash
cd tap-agent
cat .env
# Should have ED25519_PRIVATE_KEY and ED25519_PUBLIC_KEY
```
---

## 🌐 URLs Reference

| Service | URL | Purpose |
|---------|-----|---------|
| **Gallery** | http://localhost:3000 | Main art gallery |
| **Backend** | http://localhost:8000 | API server |
| **CDN Proxy** | http://localhost:3001 | Signature verification |
| **Agent Registry** | http://localhost:9002 | Key management |
| **TAP Agent** | http://localhost:8501 | Automated shopping |

---

## 🎯 Next Steps

### Test Agent Automation

1. Start all services
2. Open TAP Agent
3. Configure product URL
4. Run automated shopping
5. Watch complete flow!

---

## 📸 Visual Preview

### Header
```
┌────────────────────────────────────────────┐
│ 🎨 TAP Shanni Art    [Products] [Cart (0)] │
└────────────────────────────────────────────┘
[Sienna background, seashell text]
```

### Hero Section
```
╔══════════════════════════════════════════╗
║     🎨 Shanni Art Gallery                ║
║   Discover unique illustrations          ║
║        and art pieces                    ║
╚══════════════════════════════════════════╝
[Gradient background, chocolate border]
```

### Product Grid
```
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Art #1  │ │ Art #2  │ │ Art #3  │
│ $45.00  │ │ $55.00  │ │ $50.00  │
└─────────┘ └─────────┘ └─────────┘
[Rounded cards, sienna borders]
```

---

## 🎉 You're All Set!

Your TAP Shanni Art Gallery is ready to:

✨ Showcase beautiful artwork  
✨ Process secure payments  
✨ Support agent automation  
✨ Provide amazing UX  

**Enjoy your art gallery!** 🎨

---

## 📚 More Information

- **Full Guide:** `SHANNI_ART_TRANSFORMATION.md`
- **Agent Guide:** `tap-agent/AGENT_V3_GUIDE.md`
- **TAP Docs:** `README.md`

**Questions?** Check the documentation or Instagram: [@shanni_daily_drawing](https://www.instagram.com/shanni_daily_drawing/)
