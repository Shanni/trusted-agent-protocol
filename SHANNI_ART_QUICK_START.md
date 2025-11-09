# 🎨 TAP Shanni Art Gallery - Quick Start

## One-Command Setup

```bash
./start_shanni_art.sh
```

This will seed the database with 15 beautiful art products!

---

## Start All Services

### Option 1: Manual (Recommended for Development)

```bash
# Terminal 1: Backend
cd merchant-backend
python main.py

# Terminal 2: Frontend  
cd merchant-frontend
npm start

# Terminal 3: CDN Proxy
cd cdn-proxy
node server.js

# Terminal 4: Agent Registry
cd agent-registry
python main.py

# Optional Terminal 5: TAP Agent
cd tap-agent
streamlit run agent_app_v3.py
```

### Option 2: Background Processes

```bash
# Start backend
cd merchant-backend && python main.py &

# Start frontend
cd merchant-frontend && npm start &

# Start CDN proxy
cd cdn-proxy && node server.js &

# Start agent registry
cd agent-registry && python main.py &
```

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

## 🛍️ Test Shopping Flow

### Manual Shopping

1. Visit http://localhost:3000
2. Browse the gallery
3. Click on any art piece
4. Add to cart
5. Proceed to checkout
6. Complete purchase

### Automated Shopping (with Agent)

1. Visit http://localhost:8501
2. Configure product URL: `http://localhost:3001/product/1`
3. Fill checkout information
4. Click "🤖 Start Automated Shopping"
5. Watch the magic! ✨

The agent will:
- Navigate to product page
- Extract product details
- Add to cart
- Fill checkout form
- Complete purchase
- Extract order number

---

## 📦 Sample Products

### Daily Drawing #1 - Morning Coffee
- **Price:** $45.00
- **Category:** Illustrations
- **Stock:** 15 available

### Daily Drawing #5 - Abstract Thoughts
- **Price:** $65.00
- **Category:** Abstract Art
- **Stock:** 10 available

### Limited Edition Print Set
- **Price:** $225.00
- **Category:** Limited Edition
- **Stock:** 5 available (exclusive!)

---

## 🎨 Features

### Gallery Features
✅ Beautiful art-focused design  
✅ Sienna and beige-pink theme  
✅ Rounded, elegant cards  
✅ Smooth hover effects  
✅ Instagram integration  
✅ Category badges  
✅ Stock indicators  

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

### Port Already in Use?

Check what's running:
```bash
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :3001  # CDN Proxy
lsof -i :9002  # Agent Registry
lsof -i :8501  # TAP Agent
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

### Customize Your Gallery

1. **Add Your Own Art**
   - Edit `merchant-backend/seed_shanni_art.py`
   - Add your product data
   - Run the seed script

2. **Change Colors**
   - Find/replace `#A0522D` (sienna)
   - Find/replace `#FFE4E1` (pink)
   - Update in all frontend files

3. **Update Branding**
   - Change logo in `Header.jsx`
   - Update footer in `App.jsx`
   - Modify hero in `ProductsPage.jsx`

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
