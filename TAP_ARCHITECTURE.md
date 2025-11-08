# TAP (Trusted Agent Protocol) Architecture & Flow

## Quick Fix Summary

**Issue:** Backend returning 404 for `/product/1`
**Cause:** Path mismatch - proxy sent `/product/1`, backend expects `/products/1` (plural)
**Fix:** Added `pathRewrite: { '^/product': '/products' }` to CDN proxy

---

## System Architecture

```
┌─────────────┐
│  TAP Agent  │ (Port 8501 - Streamlit)
│  Generates  │ • Creates Ed25519 signatures
│  Signatures │ • Launches browser with headers
└──────┬──────┘
       │ Signature Headers
       ▼
┌─────────────────────────────────────────────────┐
│           Browser (Playwright)                   │
│  • Carries signature headers                     │
│  • Navigates to: http://localhost:3001/product/1│
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│         CDN Proxy (Port 3001 - Node.js)          │
│  1. Receives request with signature headers      │
│  2. Verifies signature against Agent Registry    │
│  3. Routes to appropriate backend                │
└────┬─────────────────────────────────────────┬───┘
     │                                         │
     │ /product/* (after verification)         │ /* (everything else)
     ▼                                         ▼
┌─────────────────┐                    ┌──────────────┐
│ Merchant Backend│ (Port 8000)        │ React Frontend│ (Port 3000)
│ FastAPI         │                    │ Vite + React  │
│ • /products/    │                    │ • UI pages    │
│ • /api/         │                    │ • Static files│
└─────────────────┘                    └──────────────┘
     │
     │ Key lookup
     ▼
┌─────────────────┐
│ Agent Registry  │ (Port 9002)
│ • Stores keys   │
│ • /keys/{id}    │
└─────────────────┘
```

---

## How TAP Agent Works

### 1. **Signature Generation** (tap-agent/agent_app.py)

```python
# User inputs URL: http://localhost:3001/product/1
# Agent parses it:
authority = "localhost:3001"
path = "/product/1"

# Creates signature base string (RFC 9421):
signature_base = f'''
"@authority": {authority}
"@path": {path}
"@signature-params": ("@authority" "@path"); created={created}; expires={expires}; keyId="{keyId}"; alg="ed25519"; nonce="{nonce}"; tag="{tag}"
'''

# Signs with Ed25519 private key:
signature = private_key.sign(signature_base.encode('utf-8'))
signature_b64 = base64.b64encode(signature)

# Creates headers:
Signature-Input: sig2=("@authority" "@path"); created=...; expires=...; keyId="primary-ed25519"; alg="ed25519"; nonce="..."; tag="agent-browser-auth"
Signature: sig2=:base64-signature:
```

### 2. **Browser Launch** (Playwright)

```python
# Launches browser with signature headers
context = browser.new_context(extra_http_headers={
    'Signature-Input': signature_input_header,
    'Signature': signature_header
})

# Browser carries these headers on ALL requests
page = context.new_page()
page.goto('http://localhost:3001/product/1')
```

### 3. **CDN Proxy Verification** (cdn-proxy/server.js)

```javascript
// Step 1: Check if /product/* route
if (url.startsWith('/product/')) {
  // Signature required!
  if (!hasSignatureHeaders) {
    return 403; // Forbidden
  }
  verifySignature(req, res, next);
}

// Step 2: Verify signature
async function verifySignature(req, res, next) {
  // Parse signature headers
  const { keyId, nonce, created, expires, algorithm } = parseSignature(req.headers);
  
  // Fetch public key from Agent Registry
  const keyInfo = await fetch(`http://localhost:9002/keys/${keyId}`);
  
  // Validate timing
  if (created > now || expires < now) {
    return 403; // Expired or future-dated
  }
  
  // Check nonce (prevent replay attacks)
  if (nonceCache.has(nonce)) {
    return 403; // Replay attack!
  }
  nonceCache.set(nonce, Date.now());
  
  // Build signature base string (same as agent)
  const signatureBase = buildSignatureBase(req);
  
  // Verify signature
  const isValid = crypto.verify(publicKey, signatureBase, signature);
  
  if (!isValid) {
    return 403; // Invalid signature
  }
  
  // Success! Forward request
  next();
}

// Step 3: Route to backend
app.use('/product', createProxyMiddleware({
  target: 'http://localhost:8000',
  pathRewrite: { '^/product': '/products' }  // /product/1 -> /products/1
}));
```

### 4. **Backend Response** (merchant-backend)

```python
# Backend receives: GET /products/1
@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Returns JSON:
{
  "id": 1,
  "name": "Premium Wireless Headphones",
  "price": 299.99,
  "description": "...",
  "category": "Electronics"
}
```

### 5. **Product Extraction** (TAP Agent)

```python
# Browser now shows the product page
# Agent extracts data using selectors:

title_selectors = ['h1', '.product-title', '[data-testid="product-title"]']
price_selectors = ['.price', '[data-testid="price"]', 'span:has-text("$")']

# Extracts:
product_info = {
  'title': 'Premium Wireless Headphones',
  'price': '$299.99'
}

# Displays in Streamlit UI
st.success(f"📦 Title: {title}")
st.success(f"💰 Price: {price}")
```

---

## Key Components

### CDN Proxy (cdn-proxy/server.js)

**Purpose:** Simulates a CDN that verifies RFC 9421 signatures before allowing access

**Key Features:**
- ✅ RFC 9421 HTTP Message Signature verification
- ✅ Ed25519 and RSA-PSS-SHA256 support
- ✅ Nonce-based replay attack prevention
- ✅ Timestamp validation (15-minute window)
- ✅ Agent Registry integration
- ✅ Path rewriting (/product → /products)
- ✅ CSP headers for security

**Routing Logic:**
```javascript
// Order matters! Specific routes before catch-all
1. /api/*     → backend:8000 (no signature required)
2. /product/* → backend:8000 (signature required, path rewritten)
3. /*         → React:3000 (catch-all)
```

### TAP Agent (tap-agent/agent_app.py)

**Purpose:** Generates RFC 9421 signatures and launches browser with headers

**Key Features:**
- ✅ Ed25519 signature generation
- ✅ RSA-PSS-SHA256 signature generation
- ✅ Nonce generation (UUID v4)
- ✅ Timestamp management (created/expires)
- ✅ Playwright browser automation
- ✅ Product data extraction
- ✅ Streamlit UI for testing

**Signature Flow:**
```
1. User inputs URL
2. Parse authority and path
3. Generate nonce (unique per request)
4. Set created (now) and expires (now + 15 min)
5. Build signature base string
6. Sign with private key
7. Encode as base64
8. Create RFC 9421 headers
9. Launch browser with headers
10. Extract product info from page
```

---

## Path Rewriting Fix

### The Problem

```
Browser:     GET http://localhost:3001/product/1
             ↓
CDN Proxy:   Forwards to http://localhost:8000/product/1  ❌
             ↓
Backend:     No route for /product/1 → 404 Not Found
```

Backend expects: `/products/{id}` (plural)

### The Solution

```javascript
// cdn-proxy/server.js
app.use('/product', createProxyMiddleware({
  target: 'http://localhost:8000',
  pathRewrite: {
    '^/product': '/products'  // Regex: /product/1 → /products/1
  }
}));
```

Now:
```
Browser:     GET http://localhost:3001/product/1
             ↓
CDN Proxy:   Rewrites to http://localhost:8000/products/1  ✅
             ↓
Backend:     Route found! Returns product data
```

---

## Security Features

### 1. **Signature Verification**
- Cryptographic proof of request origin
- Prevents unauthorized access to /product/* routes
- Uses Ed25519 (fast, secure) or RSA-PSS-SHA256

### 2. **Replay Attack Prevention**
- Each request must have unique nonce
- Nonces cached for 5 minutes
- Duplicate nonce = 403 Forbidden

### 3. **Timestamp Validation**
- Signature must not be from the future
- Signature must not be expired (15-minute window)
- Prevents old signatures from being reused

### 4. **Content Security Policy (CSP)**
- Restricts script sources
- Prevents XSS attacks
- Allows only trusted connections

### 5. **Agent Registry**
- Centralized key management
- Key rotation support
- Active/inactive key states

---

## Testing Flow

### Complete Test Sequence

```bash
# 1. Start all services
cd agent-registry && python main.py          # Port 9002
cd merchant-backend && uvicorn app.main:app  # Port 8000
cd cdn-proxy && npm start                     # Port 3001
cd merchant-frontend && npm run dev           # Port 3000
cd tap-agent && streamlit run agent_app.py   # Port 8501

# 2. Sync keys (if needed)
python sync_tap_agent_key.py

# 3. Test in TAP Agent
# - Open http://localhost:8501
# - Click "🔄 Reset to Default JSON"
# - Click "Generate Signature & Launch Browser"

# 4. Verify logs
# CDN Proxy should show:
✅ CDN: RFC 9421 signature verification successful!
🔄 Forwarding /product request to backend /products: /1
✅ Backend responded with status: 200 for /1

# TAP Agent should show:
📦 Product Title: Premium Wireless Headphones
💰 Product Price: $299.99
```

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| 403 Forbidden | Invalid signature | Run `sync_tap_agent_key.py` |
| 403 Replay Attack | Nonce reused | Click "Reset to Default JSON" |
| 403 Expired | Signature too old | Increase expiration time |
| 404 Not Found | Path mismatch | Add pathRewrite to proxy |
| CSP Error | Restrictive policy | Update connect-src in CSP |
| Key Not Found | Registry missing key | Populate registry or sync |

---

## Files Modified in This Session

1. ✅ `cdn-proxy/server.js` (line 691-693)
   - Added `pathRewrite: { '^/product': '/products' }`

2. ✅ `cdn-proxy/server.js` (line 98)
   - Updated CSP to allow localhost connections

3. ✅ `cdn-proxy/server.js` (lines 671-709)
   - Reordered proxy middleware (specific before catch-all)

4. ✅ `agent-registry/main.py` (lines 321-355)
   - Added DELETE endpoint for keys

5. ✅ `sync_tap_agent_key.py` (new file)
   - Automated key synchronization script

---

## Summary

The TAP system demonstrates **RFC 9421 HTTP Message Signatures** for secure, authenticated requests:

1. **TAP Agent** generates cryptographic signatures
2. **Browser** carries signatures in headers
3. **CDN Proxy** verifies signatures before routing
4. **Backend** serves protected resources
5. **Agent Registry** manages public keys

The path rewriting fix ensures `/product/1` routes correctly to `/products/1` on the backend.
