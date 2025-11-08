# TAP Agent V2 - Simplified Agent Interface

## What's New

**agent_app_v2.py** is a simplified, focused version of the TAP agent that clearly demonstrates:

1. **Public Operations** (no signature needed)
2. **Protected Operations** (signature required)
3. **x402 Checkout** integration
4. **Clear operation flow**

## Key Improvements

### ✅ Removed Unnecessary Configuration
- No more complex JSON editing
- No RSA key management (Ed25519 only)
- No browser automation complexity
- Simplified UI with clear operation types

### ✅ Clear Operation Categories

**Public Operations (No Signature):**
- View Product
- Browse Products  
- Add to Cart

**Protected Operations (Signature Required):**
- Checkout (Traditional or x402)
- View Orders

### ✅ Direct API Calls
- Makes HTTP requests directly (no Playwright)
- Shows request/response clearly
- Easy to understand what's happening

---

## Running the New Version

### Start the Agent

```bash
cd tap-agent
streamlit run agent_app_v2.py
```

Opens at: `http://localhost:8501`

---

## Usage Examples

### Example 1: Browse Products (Public)

1. Select: **"2. Browse Products (No Signature)"**
2. Enter search query (optional): `headphones`
3. Click **"Execute Browse Products"**
4. ✅ No signature needed!

**Result:**
```json
{
  "products": [
    {
      "id": 1,
      "name": "Premium Wireless Headphones",
      "price": 299.99,
      "category": "Electronics"
    }
  ]
}
```

---

### Example 2: Add to Cart (Public)

1. Select: **"3. Add to Cart (No Signature)"**
2. Click **"Create Cart Session"**
3. Enter Product ID: `1`
4. Enter Quantity: `1`
5. Click **"Execute Add to Cart"**
6. ✅ No signature needed!

**Result:**
```json
{
  "message": "Item added to cart",
  "cart_id": "cart_abc123",
  "items": [...]
}
```

---

### Example 3: Checkout with Credit Card (Signature Required)

1. Select: **"4. Checkout (Signature Required)"**
2. Choose: **"Traditional (Credit Card)"**
3. Fill in customer information (pre-filled with defaults)
4. Click **"Execute Checkout"**
5. 🔐 Signature automatically generated!

**What Happens:**
```
1. Agent generates RFC 9421 signature
2. CDN Proxy verifies signature
3. Backend processes payment
4. Order created
```

**Result:**
```json
{
  "status": "success",
  "order": {
    "order_number": "ORD-20250108-ABC123",
    "total_amount": 299.99,
    "status": "confirmed"
  }
}
```

---

### Example 4: x402 Checkout (Signature Required)

1. Select: **"4. Checkout (Signature Required)"**
2. Choose: **"x402 (Delegation Token)"**
3. Enter delegation token: `del_sample_token_123`
4. Enter shipping address
5. Click **"Execute Checkout"**
6. 🔐 Signature automatically generated!

**What Happens:**
```
1. Agent generates RFC 9421 signature
2. CDN Proxy verifies signature
3. Backend calls Payment Facilitator with delegation token
4. Payment Facilitator settles payment
5. Order created
```

**Result:**
```json
{
  "status": "success",
  "order": {
    "order_number": "ORD-20250108-XYZ789",
    "total_amount": 299.99,
    "payment_method": "x402_delegation"
  },
  "payment": {
    "receipt_id": "rcpt_abc123",
    "remaining_limit": 700.01
  }
}
```

---

## Configuration

### Required Environment Variables

Create `.env` file in `tap-agent/` directory:

```bash
# Ed25519 Keys (required)
ED25519_PRIVATE_KEY=your_private_key_base64
ED25519_PUBLIC_KEY=your_public_key_base64
```

### Agent Configuration in UI

- **Merchant Base URL**: `http://localhost:3001` (CDN proxy)
- **Agent ID**: `agent-shopping-bot-v1` (your agent identifier)
- **Key ID**: `primary-ed25519` (must match Agent Registry)

---

## Understanding Signatures

### When Are Signatures Required?

| Operation | Signature? | Why? |
|-----------|-----------|------|
| View Product | ❌ No | Public browsing |
| Browse Products | ❌ No | Public catalog |
| Add to Cart | ❌ No | Public shopping |
| **Checkout** | ✅ **Yes** | **Payment operation** |
| **View Orders** | ✅ **Yes** | **Private user data** |

### What Does the Signature Prove?

1. **Identity** - Agent is registered and trusted
2. **Authorization** - Agent has permission for this operation
3. **Integrity** - Request hasn't been tampered with
4. **Freshness** - Request is recent (not replayed)

### Signature Components

```
Signature-Input: sig2=("@authority" "@path"); 
  created=1704729600; 
  expires=1704730500; 
  keyId="primary-ed25519"; 
  alg="ed25519"; 
  nonce="abc-123-xyz"; 
  tag="agent-checkout"

Signature: sig2=:base64_encoded_signature:
```

---

## Troubleshooting

### Error: "Signature verification failed"

**Cause:** Public key mismatch between agent and registry

**Fix:**
```bash
cd trusted-agent-protocol
python sync_tap_agent_key.py
```

### Error: "Cart session not found"

**Cause:** Need to create cart before checkout

**Fix:**
1. Select "Add to Cart" operation
2. Click "Create Cart Session"
3. Then proceed with checkout

### Error: "Payment Facilitator unavailable"

**Cause:** x402 service not running (for x402 checkout)

**Fix:**
- Use traditional checkout instead, OR
- Update `merchant-backend/app/routes/cart.py` line 836 with your x402 service URL

---

## Comparison: V1 vs V2

| Feature | V1 (agent_app.py) | V2 (agent_app_v2.py) |
|---------|-------------------|----------------------|
| **UI Complexity** | Complex JSON editing | Simple operation selection |
| **Browser** | Playwright automation | Direct API calls |
| **Algorithms** | RSA + Ed25519 | Ed25519 only |
| **Operations** | Product extraction + Checkout | All 5 operations clearly shown |
| **Learning Curve** | Steep | Easy |
| **Use Case** | Demo signature + extraction | Demo full agent flow |

---

## Next Steps

### For Development

1. **Test Public Operations** - Verify browsing works without signatures
2. **Test Protected Operations** - Verify signatures are required and work
3. **Integrate x402** - Connect to your Payment Facilitator

### For Production

1. **Secure Key Storage** - Use secure key management (not .env files)
2. **Error Handling** - Add retry logic and better error messages
3. **Logging** - Add comprehensive logging for debugging
4. **Rate Limiting** - Implement rate limiting for API calls

---

## Summary

**agent_app_v2.py** provides a clean, educational interface for understanding:

✅ Which operations need signatures (checkout, orders)  
✅ Which operations are public (browsing, cart)  
✅ How RFC 9421 signatures work  
✅ How x402 checkout differs from traditional  
✅ Complete agent purchase flow  

**Use V2 for:**
- Learning TAP concepts
- Testing API integrations
- Demonstrating agent capabilities
- Developing new agent features

**Use V1 for:**
- Browser automation demos
- Product extraction testing
- Complex checkout flows
