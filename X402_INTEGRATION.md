# x402 Integration Quick Reference

## Current Implementation

The backend **already has x402 checkout implemented** at:
```
POST /api/cart/{session_id}/x402/checkout
```

Location: `merchant-backend/app/routes/cart.py` (lines 761-956)

---

## How It Works Now

```
Agent → CDN Proxy (verifies signature) → Backend → Payment Facilitator → Backend → Agent
                                            ↓
                                    POST /x402/settle
                                    {
                                      "delegation_token": "...",
                                      "merchant_id": "merchant_123",
                                      "amount": 299.99,
                                      "items": [...]
                                    }
```

**Current Payment Facilitator URL:** `http://localhost:8001`

---

## Integration Checklist

### 1. Update Payment Facilitator URL ✅

```python
# File: merchant-backend/app/routes/cart.py
# Line: 836

# CHANGE THIS:
facilitator_url = "http://localhost:8001"

# TO YOUR x402 SERVICE:
facilitator_url = "https://your-x402-service.com"
```

### 2. Add Authentication (if needed) ✅

```python
# File: merchant-backend/app/routes/cart.py
# Line: 839-844

settlement_response = requests.post(
    f"{facilitator_url}/x402/settle",
    json=settlement_request,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {YOUR_API_KEY}",  # ADD THIS
        "X-Merchant-ID": "merchant_123"             # ADD THIS
    },
    timeout=30
)
```

### 3. Customize Settlement Request ✅

```python
# File: merchant-backend/app/routes/cart.py
# Lines: 823-832

settlement_request = {
    # REQUIRED FIELDS (already included)
    "delegation_token": delegation_token,
    "merchant_id": merchant_id,
    "amount": total_amount,
    "currency": "USD",
    "items": items,
    
    # ADD YOUR CUSTOM FIELDS HERE:
    "merchant_account_id": "your_account_id",
    "webhook_url": "https://your-merchant.com/webhooks/x402",
    "idempotency_key": str(uuid.uuid4()),
    "metadata": {
        "order_source": "ai_agent",
        "agent_id": agent_id,
        "cart_id": session_id
    }
}
```

### 4. Handle Your Response Format ✅

```python
# File: merchant-backend/app/routes/cart.py
# Lines: 853-860

settlement_data = settlement_response.json()

# CUSTOMIZE: Map your response fields
receipt = settlement_data.get("transaction_receipt", {})

# If your response format is different:
receipt = {
    "receipt_id": settlement_data.get("id"),
    "transaction_id": settlement_data.get("txn_id"),
    "payment_rail_used": settlement_data.get("payment_method"),
    "amount": settlement_data.get("total"),
    "processing_fee": settlement_data.get("fee", 0),
    "net_amount": settlement_data.get("net", total_amount)
}
```

### 5. Error Handling ✅

```python
# File: merchant-backend/app/routes/cart.py
# Lines: 846-860

if settlement_response.status_code != 200:
    # Map your error codes
    error_mapping = {
        402: "Insufficient delegation limit",
        403: "Invalid or expired delegation token",
        404: "Delegation token not found",
        409: "Duplicate transaction",
        422: "Invalid request format"
    }
    
    error_detail = error_mapping.get(
        settlement_response.status_code,
        settlement_response.text
    )
    
    raise HTTPException(
        status_code=402,  # Always return 402 for payment failures
        detail=f"Payment settlement failed: {error_detail}"
    )
```

---

## Testing Your Integration

### 1. Start Your x402 Service

```bash
# Make sure your x402 service is running and accessible
curl https://your-x402-service.com/health
```

### 2. Update Backend Configuration

```python
# merchant-backend/app/routes/cart.py
facilitator_url = "https://your-x402-service.com"
```

### 3. Test with Agent

```python
import requests

# Create cart
cart_response = requests.post('http://localhost:3001/api/cart/')
session_id = cart_response.json()['session_id']

# Add items
requests.post(
    f'http://localhost:3001/api/cart/{session_id}/items',
    json={'product_id': 1, 'quantity': 1}
)

# Checkout with x402 (with signature)
headers = {
    'Signature-Input': '...',  # Generate RFC 9421 signature
    'Signature': '...',
    'Content-Type': 'application/json'
}

response = requests.post(
    f'http://localhost:3001/api/cart/{session_id}/x402/checkout',
    headers=headers,
    json={
        'delegation_token': 'YOUR_TEST_TOKEN',
        'agent_id': 'test-agent'
    }
)

print(response.json())
```

### 4. Check Logs

**Backend logs should show:**
```
POST /api/cart/{session_id}/x402/checkout
Calling Payment Facilitator: https://your-x402-service.com/x402/settle
Payment settled successfully
Order created: ORD-20250108-ABC123
```

**Your x402 service logs should show:**
```
POST /x402/settle
Delegation token: del_abc123...
Amount: $299.99
Settlement successful
```

---

## API Contract

### Your x402 Service Should Accept:

```json
POST /x402/settle
Content-Type: application/json

{
  "delegation_token": "del_abc123xyz...",
  "merchant_id": "merchant_123",
  "merchant_name": "Reference Merchant",
  "cart_id": "cart_session_id",
  "amount": 299.99,
  "currency": "USD",
  "items": [
    {
      "product_id": 1,
      "name": "Premium Wireless Headphones",
      "quantity": 1,
      "price": 299.99
    }
  ],
  "merchant_signature": "hmac_sha256_signature"
}
```

### Your x402 Service Should Return:

**Success (200 OK):**
```json
{
  "transaction_receipt": {
    "receipt_id": "rcpt_abc123",
    "transaction_id": "txn_xyz789",
    "payment_rail_used": "visa_card",
    "amount": 299.99,
    "processing_fee": 2.99,
    "net_amount": 297.00,
    "status": "completed",
    "timestamp": "2025-01-08T10:30:00Z"
  },
  "remaining_delegation_limit": 700.01
}
```

**Failure (402 Payment Required):**
```json
{
  "error": "insufficient_funds",
  "message": "Delegation limit exceeded",
  "remaining_limit": 50.00,
  "requested_amount": 299.99
}
```

---

## Environment Variables (Optional)

Add to `.env` file:

```bash
# x402 Configuration
X402_FACILITATOR_URL=https://your-x402-service.com
X402_API_KEY=your_api_key_here
X402_MERCHANT_ID=merchant_123
X402_WEBHOOK_URL=https://your-merchant.com/webhooks/x402
```

Then update code:

```python
import os
from dotenv import load_dotenv

load_dotenv()

facilitator_url = os.getenv('X402_FACILITATOR_URL', 'http://localhost:8001')
api_key = os.getenv('X402_API_KEY')
merchant_id = os.getenv('X402_MERCHANT_ID', 'merchant_123')
```

---

## Webhook Support (Optional)

If your x402 service sends webhooks for async settlement:

```python
# Add to merchant-backend/app/routes/cart.py

@router.post("/x402/webhook")
async def x402_webhook(webhook_data: dict, db: Session = Depends(get_db)):
    """
    Handle x402 settlement webhooks
    """
    # Verify webhook signature
    signature = webhook_data.get('signature')
    # ... verify signature ...
    
    # Update order status
    transaction_id = webhook_data.get('transaction_id')
    status = webhook_data.get('status')
    
    # Find order by transaction_id and update
    order = db.query(OrderModel).filter(
        OrderModel.x402_transaction_id == transaction_id
    ).first()
    
    if order:
        order.payment_status = status
        db.commit()
    
    return {"status": "received"}
```

---

## Summary

**Your x402 integration requires:**

1. ✅ Update `facilitator_url` to your service
2. ✅ Add authentication headers if needed
3. ✅ Customize request format (optional)
4. ✅ Map response fields (optional)
5. ✅ Test end-to-end

**The backend is ready!** It already:
- ✅ Accepts delegation tokens
- ✅ Calls Payment Facilitator
- ✅ Creates orders on success
- ✅ Returns comprehensive receipts
- ✅ Handles errors properly

Just point it to your x402 service and you're done! 🎉
