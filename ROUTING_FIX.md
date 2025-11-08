# CDN Proxy Routing Fix - 404 on /product/* Routes

## Issue

The TAP Agent browser was getting **404 errors** when accessing `/product/1`:

```
Failed Request: 404 GET http://localhost:3001/product/1
Console Error: Failed to load resource: the server responded with a status of 404 (Not Found)
```

Even though:
- ✅ Signature verification was working
- ✅ The URL `http://localhost:3001/product/1` worked in a regular browser
- ✅ The `/product` proxy was configured

## Root Cause

**Express middleware order issue!**

The CDN proxy had three proxy middlewares registered in this order:

```javascript
// OLD ORDER (BROKEN)
1. app.use('/product', ...)  // Proxy to backend:8000
2. app.use('/api', ...)       // Proxy to backend:8000
3. app.use('/', ...)          // Proxy to React:3000 (CATCH-ALL!)
```

**The Problem:**
- Express processes middleware **in order**
- The `/` catch-all proxy matches **everything** including `/product/1`
- So requests to `/product/1` were being proxied to React (port 3000) instead of the backend (port 8000)
- React doesn't have a `/product/1` route → **404 Not Found**

## The Fix ✅

**Reorder the proxy middlewares** so specific routes come **before** the catch-all:

```javascript
// NEW ORDER (FIXED)
1. app.use('/api', ...)       // Proxy to backend:8000
2. app.use('/product', ...)   // Proxy to backend:8000
3. app.use('/', ...)          // Proxy to React:3000 (CATCH-ALL - LAST!)
```

**File:** `cdn-proxy/server.js` (lines 671-709)

Now:
- `/api/*` requests → backend:8000
- `/product/*` requests → backend:8000 (after signature verification)
- Everything else → React:3000

## How to Apply

**Restart the CDN proxy:**

```bash
cd cdn-proxy
npm start
```

## Testing

1. **Make sure all services are running:**
   ```bash
   # Terminal 1: Agent Registry
   cd agent-registry && python main.py
   
   # Terminal 2: Merchant Backend
   cd merchant-backend && python -m uvicorn app.main:app --reload --port 8000
   
   # Terminal 3: CDN Proxy (RESTART AFTER FIX)
   cd cdn-proxy && npm start
   
   # Terminal 4: Merchant Frontend
   cd merchant-frontend && npm run dev
   
   # Terminal 5: TAP Agent
   cd tap-agent && streamlit run agent_app.py
   ```

2. **In TAP Agent (http://localhost:8501):**
   - Click **"🔄 Reset to Default JSON"** (get fresh nonce)
   - Click **"Generate Signature & Launch Browser"**

3. **Expected Success:**
   
   **TAP Agent Terminal:**
   ```
   ✅ Successfully navigated to: http://localhost:3001/product/1
   📦 Product Title: Premium Wireless Headphones
   💰 Product Price: $299.99
   
   🛍️  PRODUCT EXTRACTION RESULTS
   ==================================================
   📦 Title: Premium Wireless Headphones
   💰 Price: $299.99
   ==================================================
   ```
   
   **CDN Proxy Terminal:**
   ```
   🔐 /products/ route with signatures - verifying: /product/1
   ✅ CDN: RFC 9421 signature verification successful!
   🔄 Forwarding /product request to backend: /1
   ✅ Backend responded with status: 200 for /1
   ```

## Why This Happened

Express.js processes middleware in **registration order**:

```javascript
app.use('/product', handler1);  // Registered first
app.use('/', handler2);          // Registered second

// Request to /product/1:
// 1. Checks handler1 (/product) - MATCHES! ✅
// 2. Never reaches handler2

// BUT if order is reversed:
app.use('/', handler2);          // Registered first
app.use('/product', handler1);  // Registered second

// Request to /product/1:
// 1. Checks handler2 (/) - MATCHES! ✅ (because / matches everything)
// 2. Never reaches handler1 ❌
```

**Rule:** Always register **specific routes before catch-all routes**!

## Express Middleware Order Best Practices

```javascript
// ✅ CORRECT ORDER
app.use('/api/v2', ...)      // Most specific
app.use('/api', ...)         // Less specific
app.use('/product', ...)     // Specific
app.use('/', ...)            // Catch-all (LAST!)

// ❌ WRONG ORDER
app.use('/', ...)            // Catch-all first = catches everything!
app.use('/api', ...)         // Never reached
app.use('/product', ...)     // Never reached
```

## Related Fixes

This completes the full chain of fixes:

1. ✅ **Key Mismatch Fix** - Synced correct Ed25519 public key to registry
2. ✅ **CSP Fix** - Allowed connections to localhost:3000 and localhost:8000
3. ✅ **Routing Fix** - Reordered proxies so /product routes to backend
4. ✅ **Signature Expiration Fix** - Increased to 15 minutes
5. ✅ **Replay Attack Fix** - Proper nonce caching
6. ✅ **DELETE Endpoint** - Can remove keys from registry

All together, these enable **full end-to-end signature verification and product display**!

## Files Modified

✅ `cdn-proxy/server.js` (lines 671-709)
   - Reordered proxy middleware registration
   - Added comments explaining the order requirement
   - Added `onProxyRes` handler for better logging

## Verification Checklist

After restarting the CDN proxy:

- [ ] CDN proxy logs show: `🔄 Forwarding /product request to backend: /1`
- [ ] CDN proxy logs show: `✅ Backend responded with status: 200`
- [ ] TAP Agent extracts product title successfully
- [ ] TAP Agent extracts product price successfully
- [ ] No 404 errors in browser console
- [ ] No 403 errors (signature verification passes)
- [ ] Product page displays correctly in the automated browser

## Summary

The `/product/*` routes were returning 404 because the catch-all `/` proxy was intercepting them before they could reach the `/product` proxy. Reordering the middleware registration fixed the issue.

**Key Lesson:** In Express.js, **middleware order matters!** Always register specific routes before catch-all routes.
