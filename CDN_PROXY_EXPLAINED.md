# CDN Proxy Explained - Purpose & Agent Interaction

## Your Questions Answered

### 1. Why Does `/product` Need Signatures?

**Short Answer:** It doesn't! `/product` is a **frontend route** (React), not a protected API.

**The Confusion:**
The current CDN proxy configuration is **incorrect**. It's requiring signatures for `/product/*` routes, but these are just React pages that should be publicly accessible.

**What Should Require Signatures:**
Only **sensitive API operations** should require signatures:
- ❌ `/product/1` - Frontend page (React) - **NO signature needed**
- ✅ `/api/cart/checkout` - Payment operation - **Signature required**
- ✅ `/api/orders` - User's order history - **Signature required**
- ✅ `/api/premium/search` - Premium features - **Signature required**

**Current Code Issue:**
```javascript
// cdn-proxy/server.js - Line 651
const isProductsApiRoute = url.startsWith('/product/');

if (isProductsApiRoute) {
  // Signature required ❌ WRONG!
  if (!hasSignatureHeaders) {
    return 403; // Blocks normal users!
  }
}
```

This is blocking **normal users** from viewing product pages!

---

### 2. What's the Purpose of the CDN Proxy?

#### Real-World CDN Proxy Purpose

In production, a **CDN (Content Delivery Network)** sits between users and your origin servers:

```
User → CDN (Cloudflare, Akamai, etc.) → Origin Server
```

**CDN Benefits:**
- ⚡ **Speed**: Caches content closer to users
- 🛡️ **DDoS Protection**: Filters malicious traffic
- 🔐 **Bot Detection**: Blocks scrapers and bots
- 📊 **Analytics**: Tracks traffic patterns
- 🌍 **Global Distribution**: Serves from edge locations

#### TAP CDN Proxy Purpose (This Demo)

The CDN proxy in this project **simulates** how a real CDN would:

1. **Verify Agent Identity** - Distinguish trusted AI agents from bots
2. **Enforce Access Control** - Allow agents to access protected resources
3. **Prevent Fraud** - Block replay attacks and unauthorized requests
4. **Route Intelligently** - Forward verified requests to appropriate backends

**The Key Insight:**
```
Normal User → CDN → Frontend (React)
                ↓
              Backend API (public endpoints)

AI Agent → CDN (verifies signature) → Backend API (protected endpoints)
```

---

### 3. How Should Agents Interact with the Proxy?

#### Scenario 1: Agent Browsing Products (No Signature Needed)

**Use Case:** Agent wants to browse products like a normal user

```
AI Agent → CDN Proxy → React Frontend → Backend API (/api/products)
```

**No signature required!** The agent acts like a regular browser:
- Views product pages
- Searches products
- Reads descriptions

**Code:**
```python
# Agent just makes normal HTTP requests
response = requests.get('http://merchant.com/product/1')
# No special headers needed
```

---

#### Scenario 2: Agent Making Purchase (Signature Required)

**Use Case:** Agent wants to checkout on behalf of a user

```
AI Agent → CDN Proxy (verifies signature) → Backend API (/api/cart/checkout)
```

**Signature required!** The agent proves:
- ✅ It's a legitimate, registered agent
- ✅ It has user authorization
- ✅ The request is fresh (not replayed)

**Code:**
```python
# 1. Agent generates signature
signature_base = f'''
"@authority": merchant.com
"@path": /api/cart/checkout
"@signature-params": ("@authority" "@path"); created={now}; expires={now+900}; keyId="agent-key-123"; alg="ed25519"; nonce="{unique_nonce}"
'''

signature = agent_private_key.sign(signature_base)

# 2. Agent sends request with signature headers
response = requests.post(
    'http://merchant.com/api/cart/checkout',
    headers={
        'Signature-Input': 'sig2=("@authority" "@path"); created=...; keyId="agent-key-123"; ...',
        'Signature': f'sig2=:{base64.b64encode(signature).decode()}:',
        'Content-Type': 'application/json'
    },
    json={
        'user_id': 'user123',
        'payment_method': 'card_on_file',
        'items': [...]
    }
)
```

**CDN Proxy Verification:**
```javascript
// 1. Extract signature headers
const { keyId, nonce, created, expires } = parseSignature(req.headers);

// 2. Fetch agent's public key from registry
const publicKey = await fetch(`https://agent-registry.com/keys/${keyId}`);

// 3. Verify signature
const isValid = crypto.verify(publicKey, signatureBase, signature);

// 4. Check freshness
if (expires < now || nonce_already_used) {
  return 403; // Reject!
}

// 5. Forward to backend
proxy.forward('/api/cart/checkout', req);
```

---

## Correct CDN Proxy Configuration

### What Should Be Protected?

```javascript
// cdn-proxy/server.js

// Public routes (NO signature required)
const publicRoutes = [
  '/',              // Homepage
  '/product/*',     // Product pages (React)
  '/cart',          // Cart page (React)
  '/api/products',  // Product listing API
];

// Protected routes (signature REQUIRED)
const protectedRoutes = [
  '/api/cart/*/checkout',     // Checkout
  '/api/orders',              // Order history
  '/api/premium/*',           // Premium features
  '/api/user/*',              // User data
];

// Middleware
app.use((req, res, next) => {
  const isProtected = protectedRoutes.some(route => 
    matchRoute(req.path, route)
  );
  
  if (isProtected) {
    // Require signature
    return verifySignature(req, res, next);
  }
  
  // Public route - no signature needed
  next();
});
```

---

## Real-World Agent Interaction Flow

### Example: AI Agent Booking Travel

**Step 1: Agent Browses (No Signature)**
```
Agent: "Find flights from NYC to LAX"
  ↓
GET https://airline.com/api/flights?from=NYC&to=LAX
  ↓
CDN: Public API, no signature needed ✅
  ↓
Returns: [Flight 123, Flight 456, ...]
```

**Step 2: Agent Books (Signature Required)**
```
Agent: "Book Flight 123 for user@example.com"
  ↓
POST https://airline.com/api/bookings
Headers:
  Signature-Input: sig2=(...); keyId="agent-travel-bot-v1"; ...
  Signature: sig2=:base64signature:
Body:
  {
    "flight_id": 123,
    "user_email": "user@example.com",
    "payment_method": "card_on_file"
  }
  ↓
CDN: Verifies signature ✅
  - Checks agent is registered
  - Validates signature is fresh
  - Confirms user authorized this agent
  ↓
Backend: Processes booking
  ↓
Returns: { "booking_id": "ABC123", "status": "confirmed" }
```

---

## Why This Matters for Merchants

### Without TAP (Current State)

```
❌ Can't distinguish AI agents from bots
❌ Can't verify agent has user permission
❌ Risk of fraud and chargebacks
❌ Must block all automated traffic
```

**Result:** Merchants lose out on agent-driven commerce

### With TAP (Future State)

```
✅ Cryptographically verify agent identity
✅ Confirm user authorization
✅ Prevent replay attacks
✅ Enable secure agent commerce
```

**Result:** Merchants can safely accept agent purchases

---

## Fixing Your Current Setup

### Issue 1: `/product` Routes Blocked

**Problem:**
```javascript
// Current code blocks normal users!
if (url.startsWith('/product/')) {
  if (!hasSignatureHeaders) {
    return 403; // ❌ Blocks everyone!
  }
}
```

**Fix:**
```javascript
// Only protect sensitive operations
const protectedPaths = [
  '/api/cart/checkout',
  '/api/orders',
  '/api/premium'
];

const needsSignature = protectedPaths.some(path => 
  req.path.startsWith(path)
);

if (needsSignature && !hasSignatureHeaders) {
  return 403;
}

// Everything else is public
next();
```

### Issue 2: Path Rewriting Not Needed

**Problem:**
```javascript
// Rewriting /product -> /products
pathRewrite: { '^/product': '/products' }
```

**Why It's Wrong:**
- `/product/1` is a **React route** (frontend)
- React handles routing internally
- No need to rewrite to backend API

**Fix:**
```javascript
// Remove the /product proxy entirely!
// Let React handle all frontend routes

// Only proxy API routes to backend
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:8000',
  changeOrigin: true
}));

// Everything else goes to React
app.use('/', createProxyMiddleware({
  target: 'http://localhost:3000',
  changeOrigin: true
}));
```

---

## Summary

### Key Takeaways

1. **`/product` is a frontend route** - No signature needed! It's just a React page.

2. **CDN Proxy Purpose** - Verify agent identity for **sensitive operations** (checkout, payments), not for browsing.

3. **Agent Interaction**:
   - **Browsing** → No signature (acts like normal user)
   - **Transacting** → Signature required (proves identity & authorization)

4. **Current Setup is Wrong** - It's blocking normal users from viewing products!

### Recommended Fix

```javascript
// cdn-proxy/server.js

// Only require signatures for sensitive API operations
app.use((req, res, next) => {
  const sensitiveOperations = [
    '/api/cart/checkout',
    '/api/orders',
    '/api/premium'
  ];
  
  const needsSignature = sensitiveOperations.some(op => 
    req.path.startsWith(op)
  );
  
  if (needsSignature) {
    return verifySignature(req, res, next);
  }
  
  next(); // Public routes - no verification
});

// Proxy API calls to backend
app.use('/api', proxy('http://localhost:8000'));

// Proxy everything else to React
app.use('/', proxy('http://localhost:3000'));
```

This way:
- ✅ Normal users can browse products
- ✅ AI agents can browse without signatures
- ✅ AI agents need signatures only for checkout/payments
- ✅ Merchants get fraud protection where it matters
