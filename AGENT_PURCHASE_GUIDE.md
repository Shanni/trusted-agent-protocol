# Agent Purchase Guide - How AI Agents Make Purchases

## Overview

This guide explains how an AI agent makes a purchase using the Trusted Agent Protocol (TAP), including both traditional credit card checkout and x402 delegation token checkout.

---

## Part 1: Agent Purchase Flow (Traditional Checkout)

### Step 1: Browse Products (No Signature Required)

```python
import requests

# Agent browses products like a normal user
response = requests.get('http://merchant.com/api/products/')
products = response.json()['products']

# Agent selects a product
selected_product = products[0]
print(f"Selected: {selected_product['name']} - ${selected_product['price']}")
```

**No signature needed!** This is public browsing.

---

### Step 2: Add to Cart (No Signature Required)

```python
# Create a cart session
cart_response = requests.post('http://merchant.com/api/cart/')
session_id = cart_response.json()['session_id']

# Add items to cart
add_item_response = requests.post(
    f'http://merchant.com/api/cart/{session_id}/items',
    json={
        'product_id': selected_product['id'],
        'quantity': 1
    }
)

print(f"Cart session: {session_id}")
```

**No signature needed!** Adding to cart is a public operation.

---

### Step 3: Checkout (Signature Required!)

This is where the agent needs to prove its identity and authorization.

```python
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
import uuid
import time

# 1. Generate signature components
authority = "merchant.com"
path = f"/api/cart/{session_id}/checkout"
created = int(time.time())
expires = created + 900  # 15 minutes
nonce = str(uuid.uuid4())
key_id = "agent-shopping-bot-v1"

# 2. Build signature base string (RFC 9421)
signature_base = f'''"@authority": {authority}
"@path": {path}
"@signature-params": ("@authority" "@path"); created={created}; expires={expires}; keyId="{key_id}"; alg="ed25519"; nonce="{nonce}"; tag="agent-checkout"'''

# 3. Sign with agent's private key
private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
    base64.b64decode(AGENT_PRIVATE_KEY)
)
signature = private_key.sign(signature_base.encode('utf-8'))
signature_b64 = base64.b64encode(signature).decode('utf-8')

# 4. Create RFC 9421 headers
headers = {
    'Signature-Input': f'sig2=("@authority" "@path"); created={created}; expires={expires}; keyId="{key_id}"; alg="ed25519"; nonce="{nonce}"; tag="agent-checkout"',
    'Signature': f'sig2=:{signature_b64}:',
    'Content-Type': 'application/json'
}

# 5. Make checkout request with signature
checkout_response = requests.post(
    f'http://merchant.com/api/cart/{session_id}/checkout',
    headers=headers,
    json={
        'customer_email': 'user@example.com',
        'customer_name': 'John Doe',
        'customer_phone': '+1-555-0123',
        'shipping_address': {
            'street': '123 Main St',
            'city': 'San Francisco',
            'state': 'CA',
            'zip': '94102',
            'country': 'USA'
        },
        'billing_address': {
            'street': '123 Main St',
            'city': 'San Francisco',
            'state': 'CA',
            'zip': '94102',
            'country': 'USA'
        },
        'payment_method': {
            'type': 'credit_card',
            'card_number': '4111111111111111',  # Demo card
            'expiry_date': '12/25',
            'cvv': '123',
            'name_on_card': 'John Doe'
        },
        'special_instructions': 'Leave at front door'
    }
)

# 6. Handle response
if checkout_response.status_code == 200:
    order = checkout_response.json()
    print(f"✅ Order placed successfully!")
    print(f"Order Number: {order['order']['order_number']}")
    print(f"Total: ${order['order']['total_amount']}")
    print(f"Tracking: {order['fulfillment']['tracking_number']}")
else:
    print(f"❌ Checkout failed: {checkout_response.text}")
```

---

## Part 2: Agent Purchase Flow (x402 Delegation Token)

### What is x402?

**x402** is a protocol for machine-to-machine payments using **delegation tokens**. Instead of providing credit card details, the agent presents a pre-authorized token that allows it to spend on behalf of the user.

**Benefits:**
- ✅ No credit card data in transit
- ✅ Pre-authorized spending limits
- ✅ Revocable tokens
- ✅ Audit trail of agent purchases

---

### x402 Checkout Flow

```python
# Step 1: Agent obtains delegation token (from Payment Facilitator)
# This happens before the agent starts shopping
delegation_token = "del_abc123xyz..."  # Pre-authorized by user

# Step 2: Browse and add to cart (same as before)
cart_response = requests.post('http://merchant.com/api/cart/')
session_id = cart_response.json()['session_id']

requests.post(
    f'http://merchant.com/api/cart/{session_id}/items',
    json={'product_id': 1, 'quantity': 1}
)

# Step 3: x402 Checkout with delegation token (Signature Required!)
# Generate signature (same as before)
authority = "merchant.com"
path = f"/api/cart/{session_id}/x402/checkout"
created = int(time.time())
expires = created + 900
nonce = str(uuid.uuid4())
key_id = "agent-shopping-bot-v1"

signature_base = f'''"@authority": {authority}
"@path": {path}
"@signature-params": ("@authority" "@path"); created={created}; expires={expires}; keyId="{key_id}"; alg="ed25519"; nonce="{nonce}"; tag="agent-x402-checkout"'''

signature = private_key.sign(signature_base.encode('utf-8'))
signature_b64 = base64.b64encode(signature).decode('utf-8')

headers = {
    'Signature-Input': f'sig2=("@authority" "@path"); created={created}; expires={expires}; keyId="{key_id}"; alg="ed25519"; nonce="{nonce}"; tag="agent-x402-checkout"',
    'Signature': f'sig2=:{signature_b64}:',
    'Content-Type': 'application/json'
}

# Make x402 checkout request
x402_response = requests.post(
    f'http://merchant.com/api/cart/{session_id}/x402/checkout',
    headers=headers,
    json={
        'delegation_token': delegation_token,
        'agent_id': 'agent-shopping-bot-v1',
        'shipping_address': '123 Main St, San Francisco, CA 94102',
        'special_instructions': 'Leave at front door'
    }
)

# Handle response
if x402_response.status_code == 200:
    result = x402_response.json()
    print(f"✅ x402 Checkout successful!")
    print(f"Order Number: {result['order']['order_number']}")
    print(f"Total: ${result['order']['total_amount']}")
    print(f"Payment Method: {result['payment']['method']}")
    print(f"Receipt ID: {result['payment']['receipt_id']}")
    print(f"Remaining Delegation Limit: ${result['delegation']['remaining_limit']}")
else:
    print(f"❌ x402 Checkout failed: {x402_response.text}")
```

---

## Part 3: Backend x402 Implementation

### Current Implementation (merchant-backend/app/routes/cart.py)

The backend already has x402 checkout implemented at:
```
POST /api/cart/{session_id}/x402/checkout
```

**What it does:**

1. **Receives delegation token** from agent
2. **Validates cart** and calculates totals
3. **Calls Payment Facilitator** to settle payment:
   ```python
   settlement_request = {
       "delegation_token": delegation_token,
       "merchant_id": "merchant_123",
       "amount": total_amount,
       "items": [...],
       "merchant_signature": hmac_signature
   }
   
   response = requests.post(
       "http://localhost:8001/x402/settle",
       json=settlement_request
   )
   ```
4. **Creates order** if payment succeeds
5. **Returns order details** with receipt

---

## Part 4: Plugging in Your x402 System

### Integration Points

#### 1. Update Payment Facilitator URL

```python
# merchant-backend/app/routes/cart.py (line 836)

# BEFORE
facilitator_url = "http://localhost:8001"

# AFTER - Use your x402 service
facilitator_url = "https://your-x402-service.com"
```

#### 2. Customize Settlement Request Format

```python
# merchant-backend/app/routes/cart.py (lines 823-832)

settlement_request = {
    "delegation_token": delegation_token,
    "merchant_id": merchant_id,
    "merchant_name": merchant_name,
    "cart_id": session_id,
    "amount": total_amount,
    "currency": "USD",
    "items": items,
    "merchant_signature": merchant_signature,
    
    # ADD YOUR CUSTOM FIELDS HERE
    "merchant_account_id": "your_account_id",
    "webhook_url": "https://your-merchant.com/webhooks/x402",
    "metadata": {
        "order_source": "ai_agent",
        "agent_id": agent_id
    }
}
```

#### 3. Handle Settlement Response

```python
# merchant-backend/app/routes/cart.py (lines 839-860)

settlement_response = requests.post(
    f"{facilitator_url}/x402/settle",
    json=settlement_request,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {YOUR_API_KEY}"  # Add auth
    },
    timeout=30
)

if settlement_response.status_code != 200:
    # Handle different error codes
    if settlement_response.status_code == 402:
        # Insufficient funds
        raise HTTPException(
            status_code=402,
            detail="Insufficient delegation limit"
        )
    elif settlement_response.status_code == 403:
        # Invalid token
        raise HTTPException(
            status_code=403,
            detail="Invalid or expired delegation token"
        )
    else:
        # Other errors
        raise HTTPException(
            status_code=settlement_response.status_code,
            detail=settlement_response.text
        )

settlement_data = settlement_response.json()

# CUSTOMIZE: Extract fields from your x402 response
receipt = settlement_data.get("transaction_receipt", {})
transaction_id = receipt.get("transaction_id")
payment_rail = receipt.get("payment_rail_used", "unknown")
```

#### 4. Store x402 Payment Details

```python
# merchant-backend/app/routes/cart.py (lines 863-874)

order = OrderModel(
    order_number=generate_order_number(),
    customer_email=f"agent_{agent_id}@system.local",
    customer_name=f"Agent {agent_id}",
    total_amount=total_amount,
    status="confirmed",
    payment_method="x402_delegation",
    payment_status="processed",
    
    # Store x402-specific data
    card_last_four=None,  # Not applicable
    card_brand="x402_token",
    
    # ADD: Store additional x402 metadata
    # You might want to add these fields to your OrderModel:
    # x402_transaction_id=transaction_id,
    # x402_receipt_id=receipt.get("receipt_id"),
    # x402_payment_rail=payment_rail,
    # delegation_token_id=delegation_token[:20]  # Truncated for security
)
```

---

## Part 5: Complete Agent Example

### Full Working Agent Code

```python
import requests
import base64
import uuid
import time
from cryptography.hazmat.primitives.asymmetric import ed25519

class ShoppingAgent:
    def __init__(self, merchant_url, agent_key_id, private_key_b64):
        self.merchant_url = merchant_url
        self.agent_key_id = agent_key_id
        self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
            base64.b64decode(private_key_b64)
        )
    
    def generate_signature(self, path):
        """Generate RFC 9421 signature for a request"""
        authority = self.merchant_url.replace('http://', '').replace('https://', '')
        created = int(time.time())
        expires = created + 900
        nonce = str(uuid.uuid4())
        
        signature_base = f'''"@authority": {authority}
"@path": {path}
"@signature-params": ("@authority" "@path"); created={created}; expires={expires}; keyId="{self.agent_key_id}"; alg="ed25519"; nonce="{nonce}"; tag="agent-operation"'''
        
        signature = self.private_key.sign(signature_base.encode('utf-8'))
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return {
            'Signature-Input': f'sig2=("@authority" "@path"); created={created}; expires={expires}; keyId="{self.agent_key_id}"; alg="ed25519"; nonce="{nonce}"; tag="agent-operation"',
            'Signature': f'sig2=:{signature_b64}:'
        }
    
    def browse_products(self, query=None):
        """Browse products (no signature needed)"""
        url = f"{self.merchant_url}/api/products/"
        if query:
            url += f"?query={query}"
        
        response = requests.get(url)
        return response.json()['products']
    
    def create_cart(self):
        """Create a shopping cart (no signature needed)"""
        response = requests.post(f"{self.merchant_url}/api/cart/")
        return response.json()['session_id']
    
    def add_to_cart(self, session_id, product_id, quantity=1):
        """Add item to cart (no signature needed)"""
        response = requests.post(
            f"{self.merchant_url}/api/cart/{session_id}/items",
            json={'product_id': product_id, 'quantity': quantity}
        )
        return response.json()
    
    def checkout_x402(self, session_id, delegation_token, shipping_address):
        """Checkout using x402 delegation token (signature required!)"""
        path = f"/api/cart/{session_id}/x402/checkout"
        headers = self.generate_signature(path)
        headers['Content-Type'] = 'application/json'
        
        response = requests.post(
            f"{self.merchant_url}{path}",
            headers=headers,
            json={
                'delegation_token': delegation_token,
                'agent_id': self.agent_key_id,
                'shipping_address': shipping_address
            }
        )
        
        return response.json()

# Usage
agent = ShoppingAgent(
    merchant_url='http://localhost:3001',
    agent_key_id='agent-shopping-bot-v1',
    private_key_b64='YOUR_PRIVATE_KEY_BASE64'
)

# 1. Browse products
products = agent.browse_products(query='headphones')
print(f"Found {len(products)} products")

# 2. Create cart and add items
session_id = agent.create_cart()
agent.add_to_cart(session_id, product_id=products[0]['id'], quantity=1)

# 3. Checkout with x402
order = agent.checkout_x402(
    session_id=session_id,
    delegation_token='del_abc123xyz...',
    shipping_address='123 Main St, San Francisco, CA 94102'
)

print(f"✅ Order placed: {order['order']['order_number']}")
print(f"Total: ${order['order']['total_amount']}")
```

---

## Summary

### What Agent Needs to Purchase:

1. **Agent Identity** - Registered in Agent Registry with public key
2. **Private Key** - For signing checkout requests
3. **User Authorization** - Either:
   - Credit card details (traditional)
   - Delegation token (x402)
4. **Shipping Address** - Where to send the items
5. **RFC 9421 Signature** - For checkout operation only

### Key Differences:

| Aspect | Traditional Checkout | x402 Checkout |
|--------|---------------------|---------------|
| **Payment** | Credit card details | Delegation token |
| **Endpoint** | `/api/cart/{id}/checkout` | `/api/cart/{id}/x402/checkout` |
| **Signature** | Required | Required |
| **Settlement** | Direct card processing | Via Payment Facilitator |
| **Limits** | Card limit | Delegation limit |
| **Revocation** | Cancel card | Revoke token |

### Integration Steps for Your x402:

1. ✅ Update Payment Facilitator URL (line 836)
2. ✅ Customize settlement request format (lines 823-832)
3. ✅ Handle your x402 response format (lines 839-860)
4. ✅ Store x402 metadata in orders (lines 863-874)
5. ✅ Add authentication headers if needed
6. ✅ Test with your x402 service

The backend is already set up for x402! You just need to point it to your service and customize the request/response formats.
