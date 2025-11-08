# Content Security Policy (CSP) Fix

## Issue

The CDN proxy was blocking connections with this error:

```
Refused to connect because it violates the document's Content Security Policy
```

## Root Cause

The CDN proxy's CSP header was too restrictive:

```javascript
// OLD - Too restrictive
connect-src 'self' ws: wss:
```

This only allowed connections to:
- Same origin (`'self'` = `localhost:3001`)
- WebSocket connections (`ws:` and `wss:`)

But the CDN proxy needs to connect to:
- `localhost:3000` (React frontend)
- `localhost:8000` (Merchant backend)

## Fix Applied ✅

Updated CSP to allow connections to both upstream services:

**File:** `cdn-proxy/server.js` (line 98)

```javascript
// NEW - Allows proxy functionality
connect-src 'self' http://localhost:3000 http://localhost:8000 ws: wss: ws://localhost:* wss://localhost:*
```

Now allows:
- ✅ Same origin (`'self'`)
- ✅ React frontend (`http://localhost:3000`)
- ✅ Merchant backend (`http://localhost:8000`)
- ✅ WebSocket connections (`ws:`, `wss:`)
- ✅ All localhost WebSocket ports (`ws://localhost:*`, `wss://localhost:*`)

## How to Apply

**Restart the CDN proxy:**

```bash
cd cdn-proxy
npm start
```

The CSP error should now be resolved!

## Testing

1. **Start all services:**
   ```bash
   # Terminal 1: Agent Registry
   cd agent-registry && python main.py
   
   # Terminal 2: Merchant Backend
   cd merchant-backend && python -m uvicorn app.main:app --reload
   
   # Terminal 3: CDN Proxy (RESTART AFTER FIX)
   cd cdn-proxy && npm start
   
   # Terminal 4: Merchant Frontend
   cd merchant-frontend && npm run dev
   
   # Terminal 5: TAP Agent
   cd tap-agent && streamlit run agent_app.py
   ```

2. **Test in browser:**
   - Open http://localhost:3001
   - Check browser console - no CSP errors
   - Page should load correctly

## What is CSP?

**Content Security Policy (CSP)** is a security feature that helps prevent:
- Cross-Site Scripting (XSS) attacks
- Data injection attacks
- Unauthorized resource loading

It works by specifying which sources are allowed for:
- Scripts (`script-src`)
- Styles (`style-src`)
- Images (`img-src`)
- Network connections (`connect-src`)
- And more...

## CSP Directives Explained

Our current CSP:

```
default-src 'self'
  → Default: only same origin

script-src 'self' 'unsafe-inline' 'unsafe-eval'
  → Scripts: same origin + inline scripts + eval (needed for React dev)

style-src 'self' 'unsafe-inline'
  → Styles: same origin + inline styles (needed for React)

img-src 'self' data: blob: https: http:
  → Images: same origin + data URIs + blob + any HTTPS/HTTP (for product images)

font-src 'self'
  → Fonts: only same origin

connect-src 'self' http://localhost:3000 http://localhost:8000 ws: wss: ws://localhost:* wss://localhost:*
  → Connections: same origin + React + backend + WebSockets

frame-ancestors 'none'
  → Cannot be embedded in iframes (clickjacking protection)
```

## Production Considerations

⚠️ **For production**, you should:

1. **Remove `'unsafe-inline'` and `'unsafe-eval'`** from `script-src`
   - Use nonces or hashes instead
   - Build React in production mode

2. **Restrict `connect-src`** to specific domains:
   ```javascript
   connect-src 'self' https://api.yourdomain.com wss://api.yourdomain.com
   ```

3. **Restrict `img-src`** to trusted CDNs:
   ```javascript
   img-src 'self' https://cdn.yourdomain.com https://images.yourdomain.com
   ```

4. **Add `upgrade-insecure-requests`** directive:
   ```javascript
   upgrade-insecure-requests;
   ```

## Files Modified

✅ `cdn-proxy/server.js` (line 98)
   - Updated CSP `connect-src` directive to allow localhost:3000 and localhost:8000

## Related Issues

This fix complements:
- ✅ CDN proxy cache TTL fix (prevents replay attacks)
- ✅ Signature expiration fix (15-minute window)
- ✅ Product routing fix (routes to backend)
- ✅ Key mismatch fix (syncs correct public key)

All together, these fixes enable proper signature verification and proxying!
