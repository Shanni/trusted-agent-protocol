# TAP Agent V3 - Full Automated Shopping Flow

## Overview

**agent_app_v3.py** combines the best features:
- ✅ Browser automation (Playwright)
- ✅ Complex JSON editing for signature parameters
- ✅ RSA + Ed25519 support
- ✅ **Complete automated flow**: View Product → Add to Cart → Checkout

## What It Does

### Single-Click Automation

When you click "Start Automated Shopping", the agent automatically:

1. **🛍️ View Product** - Navigates to product page and extracts details
2. **🛒 Add to Cart** - Finds and clicks "Add to Cart" button
3. **📦 View Cart** - Navigates to cart page
4. **➡️ Proceed to Checkout** - Clicks "Proceed to Checkout"
5. **📝 Fill Form** - Auto-fills customer info, address, payment
6. **✅ Submit Order** - Clicks "Place Order" button
7. **🎉 Confirmation** - Extracts order number from success page

**All in one automated flow!**

---

## Running the Agent

```bash
cd tap-agent
streamlit run agent_app_v3.py
```

Opens at: `http://localhost:8501`

---

## Features

### 1. **Editable JSON Configuration**

```json
{
  "nonce": "abc-123-xyz",
  "created": 1704729600,
  "expires": 1704730500,
  "keyId": "primary-ed25519",
  "tag": "agent-shopping-flow",
  "algorithm": "ed25519"
}
```

- Edit directly in the UI
- Reset to defaults with one click
- Real-time validation

### 2. **Dual Algorithm Support**

**Ed25519:**
- Fast and secure
- Modern cryptography
- Recommended for production

**RSA-PSS-SHA256:**
- Traditional algorithm
- Wider compatibility
- Larger signatures

Switch between them with a radio button!

### 3. **Complete Checkout Configuration**

**Customer Information:**
- Name, Email, Phone
- All editable in UI

**Shipping Address:**
- Street, City, State, ZIP
- Pre-filled with defaults

**Payment Method:**
- Credit Card (traditional)
- x402 Delegation Token
- Choose in UI

### 4. **Real-Time Progress Tracking**

See each step as it happens:

```
✅ Navigate to Product - Page loaded successfully
✅ Extract Product Info - Found: Premium Wireless Headphones - $299.99
✅ Add to Cart - Product added to cart
✅ Navigate to Cart - Cart page loaded
✅ View Cart - Found 1 item(s) in cart
✅ Proceed to Checkout - Navigating to checkout
✅ Fill Checkout Form - Filled 12 form fields
✅ Submit Order - Order submitted
✅ Order Confirmation - Order Number: ORD-20250108-ABC123
🎉 Shopping Flow Complete - All steps finished
```

### 5. **Extracted Data Display**

After automation completes, see:

**Product Info:**
- Title
- Price

**Cart Info:**
- Number of items

**Order Info:**
- Order number
- Timestamp
- Success URL

---

## Usage Example

### Step 1: Configure

```
Product URL: http://localhost:3001/product/1
Agent ID: agent-shopping-bot-v1
Algorithm: ed25519 (recommended)
```

### Step 2: Edit Signature Parameters (Optional)

```json
{
  "nonce": "custom-nonce-123",
  "created": 1704729600,
  "expires": 1704730500,
  "keyId": "primary-ed25519",
  "tag": "agent-shopping-flow",
  "algorithm": "ed25519"
}
```

Or click "🔄 Reset to Defaults" to regenerate.

### Step 3: Fill Checkout Info

**Customer:**
- Name: John Doe
- Email: john.doe@example.com
- Phone: +1-555-0123

**Shipping:**
- Street: 123 Main Street
- City: New York
- State: NY
- ZIP: 10001

**Payment:**
- Credit Card (uses demo card 4111111111111111)
- OR x402 Token: del_sample_token_123

### Step 4: Launch!

Click **"🤖 Start Automated Shopping"**

Watch the browser:
- Opens automatically
- Navigates through pages
- Fills forms
- Completes purchase
- Closes automatically

Check the UI:
- See progress steps
- View extracted data
- Get order confirmation

---

## How It Works

### Signature Generation

```python
# 1. Parse product URL
authority = "localhost:3001"
path = "/product/1"

# 2. Get signature parameters from JSON
nonce = "abc-123-xyz"
created = 1704729600
expires = 1704730500

# 3. Create signature base string (RFC 9421)
signature_base = f'''
"@authority": {authority}
"@path": {path}
"@signature-params": ("@authority" "@path"); created={created}; expires={expires}; keyId="primary-ed25519"; alg="ed25519"; nonce="{nonce}"; tag="agent-shopping-flow"
'''

# 4. Sign with private key (Ed25519 or RSA)
signature = private_key.sign(signature_base)

# 5. Create headers
headers = {
    'Signature-Input': 'sig2=("@authority" "@path"); created=...; ...',
    'Signature': 'sig2=:base64_signature:'
}
```

### Browser Automation

```python
# 1. Launch browser with signature headers
context = browser.new_context(extra_http_headers=headers)
page = context.new_page()

# 2. Navigate to product
page.goto('http://localhost:3001/product/1')

# 3. Extract product info
title = page.query_selector('h1').inner_text()
price = page.query_selector('.price').inner_text()

# 4. Add to cart
page.query_selector('button:has-text("Add to Cart")').click()

# 5. Go to cart
page.goto('http://localhost:3001/cart')

# 6. Proceed to checkout
page.query_selector('button:has-text("Proceed to Checkout")').click()

# 7. Fill form
page.query_selector('#email').fill('john.doe@example.com')
page.query_selector('#firstName').fill('John')
# ... fill all fields ...

# 8. Submit order
page.query_selector('button:has-text("Place Order")').click()

# 9. Extract order number
order_number = extract_order_number(page.content())
```

### Signature Verification (CDN Proxy)

```javascript
// CDN proxy receives request with headers
const signatureInput = req.headers['signature-input'];
const signature = req.headers['signature'];

// Parse signature parameters
const { keyId, nonce, created, expires } = parseSignature(signatureInput);

// Fetch public key from Agent Registry
const publicKey = await fetch(`http://localhost:9002/keys/${keyId}`);

// Verify signature
const isValid = crypto.verify(publicKey, signatureBase, signature);

if (isValid) {
  // Forward to backend
  proxy.forward(req);
} else {
  // Reject
  return 403;
}
```

---

## Comparison: V1 vs V2 vs V3

| Feature | V1 | V2 | V3 |
|---------|----|----|-----|
| **Browser Automation** | ✅ Yes | ❌ No | ✅ Yes |
| **JSON Editing** | ✅ Yes | ❌ No | ✅ Yes |
| **RSA + Ed25519** | ✅ Both | ❌ Ed25519 only | ✅ Both |
| **Full Flow** | ⚠️ Partial | ❌ No | ✅ Complete |
| **Direct API** | ❌ No | ✅ Yes | ❌ No |
| **Complexity** | High | Low | Medium |
| **Best For** | Product extraction | API testing | **Complete automation** |

**V3 is the best of both worlds!**

---

## Advanced Features

### Custom Signature Parameters

Edit the JSON to customize:

```json
{
  "nonce": "my-custom-nonce",
  "created": 1704729600,
  "expires": 1704739600,  // 10 hours later
  "keyId": "my-custom-key",
  "tag": "special-agent-flow",
  "algorithm": "rsa-pss-sha256"  // Use RSA instead
}
```

### x402 Checkout

Select "x402 Token" payment method:

```
Delegation Token: del_abc123xyz
```

The agent will:
1. Fill form with customer info
2. Submit with delegation token
3. Backend calls Payment Facilitator
4. Order confirmed with x402 receipt

### Error Handling

If any step fails:
- ⚠️ Warning shown in step list
- Automation continues to next step
- Full error details in JSON results

Example:
```
⚠️ Add to Cart - Could not find 'Add to Cart' button, proceeding anyway
✅ Navigate to Cart - Cart page loaded
```

---

## Troubleshooting

### Browser Doesn't Open

**Error:** "Playwright not installed"

**Fix:**
```bash
pip install playwright
playwright install
```

### Signature Verification Failed

**Error:** 403 Forbidden from CDN proxy

**Fix:**
```bash
cd trusted-agent-protocol
python sync_tap_agent_key.py
```

### Form Fields Not Filled

**Cause:** Form selectors don't match your frontend

**Fix:** Update selectors in `agent_app_v3.py`:

```python
form_fields = {
    'email': ['#email', '[name="email"]', '[your-custom-selector]'],
    'firstName': ['#firstName', '[name="firstName"]', '[your-custom-selector]'],
    # ...
}
```

### Order Number Not Extracted

**Cause:** Order confirmation page format different

**Fix:** Update regex patterns in `agent_app_v3.py`:

```python
order_number_patterns = [
    r'ORD-\d+-[A-Z0-9]+',
    r'Your custom pattern here',
]
```

---

## Environment Setup

### Required .env File

```bash
# Ed25519 Keys (required)
ED25519_PRIVATE_KEY=your_ed25519_private_key_base64
ED25519_PUBLIC_KEY=your_ed25519_public_key_base64

# RSA Keys (required for RSA algorithm)
RSA_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
your_rsa_private_key_here
-----END PRIVATE KEY-----

RSA_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----
your_rsa_public_key_here
-----END PUBLIC KEY-----
```

### Generate Keys

```bash
cd trusted-agent-protocol
python generate_keys.py
```

---

## Real-World Use Cases

### 1. Automated Testing

Test your checkout flow end-to-end:
- Verify all pages load
- Ensure forms work correctly
- Confirm order creation
- Check signature verification

### 2. Agent Development

Develop AI shopping agents:
- Prototype agent behavior
- Test different products
- Validate payment flows
- Debug signature issues

### 3. Demo & Presentations

Show stakeholders:
- Complete automated shopping
- Security with signatures
- x402 payment integration
- Real-time progress tracking

### 4. Load Testing

Run multiple agents:
- Test concurrent checkouts
- Verify signature verification scales
- Stress test backend
- Monitor performance

---

## Next Steps

### Customize for Your Merchant

1. **Update URLs** - Change product, cart, checkout URLs
2. **Update Selectors** - Match your frontend elements
3. **Add Fields** - Include custom form fields
4. **Customize Extraction** - Extract additional data

### Integrate with Your Backend

1. **Update Payment Facilitator URL** - Point to your x402 service
2. **Add Webhooks** - Listen for order events
3. **Custom Validation** - Add business logic
4. **Analytics** - Track agent purchases

### Production Deployment

1. **Secure Keys** - Use key management service
2. **Error Handling** - Add retry logic
3. **Logging** - Comprehensive logging
4. **Monitoring** - Track agent performance

---

## Summary

**agent_app_v3.py** is the complete solution:

✅ **Browser Automation** - Full Playwright integration  
✅ **JSON Editing** - Customize signature parameters  
✅ **RSA + Ed25519** - Both algorithms supported  
✅ **Complete Flow** - View → Cart → Checkout → Order  
✅ **Real-Time Progress** - See each step  
✅ **Data Extraction** - Product, cart, order info  
✅ **x402 Support** - Delegation token checkout  
✅ **Error Handling** - Graceful failures  

**Perfect for:**
- Automated testing
- Agent development
- Demos & presentations
- Production deployments

🚀 **Start automating your shopping flows today!**
