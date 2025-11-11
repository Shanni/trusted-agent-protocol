# © 2025 Visa.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel
from typing import Optional
import json
import base64
import os

router = APIRouter()

# Solana configuration (should be in environment variables in production)
RECIPIENT_WALLET = os.getenv("SOLANA_RECIPIENT_WALLET", "YOUR_WALLET_ADDRESS")
RECIPIENT_TOKEN_ACCOUNT = os.getenv("SOLANA_RECIPIENT_TOKEN_ACCOUNT", "YOUR_TOKEN_ACCOUNT")
USDC_MINT = os.getenv("SOLANA_USDC_MINT", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")  # USDC on mainnet
CLUSTER = os.getenv("SOLANA_CLUSTER", "devnet")

class OnchainPaymentQuote(BaseModel):
    amount: float

class OnchainPaymentFulfill(BaseModel):
    amount: float

@router.get("/api/payment/onchain/quote")
async def get_payment_quote(amount: float = Query(..., gt=0)):
    """
    Returns a 402 Payment Required response with payment details
    Following the x402 protocol for onchain payments
    """
    # Convert USD amount to USDC (assuming 1:1 for simplicity)
    amount_usdc = amount
    # USDC has 6 decimals
    amount_smallest_units = int(amount_usdc * 1_000_000)
    
    payment_info = {
        "payment": {
            "recipientWallet": RECIPIENT_WALLET,
            "tokenAccount": RECIPIENT_TOKEN_ACCOUNT,
            "mint": USDC_MINT,
            "amount": amount_smallest_units,
            "amountUSDC": amount_usdc,
            "cluster": CLUSTER,
            "message": f"Payment of {amount_usdc} USDC required"
        }
    }
    
    return payment_info

@router.post("/api/payment/onchain/fulfill")
async def fulfill_payment(
    payment_data: OnchainPaymentFulfill,
    x_payment: Optional[str] = Header(None)
):
    """
    Receives the signed transaction from the client and submits it to the Solana network
    Following the x402 protocol
    """
    if not x_payment:
        raise HTTPException(status_code=400, detail="X-Payment header is required")
    
    try:
        # Decode the X-Payment header
        payment_proof_json = base64.b64decode(x_payment).decode('utf-8')
        payment_proof = json.loads(payment_proof_json)
        
        # Validate payment proof structure
        if payment_proof.get('x402Version') != 1:
            raise HTTPException(status_code=400, detail="Invalid x402 version")
        
        if payment_proof.get('scheme') != 'exact':
            raise HTTPException(status_code=400, detail="Only 'exact' payment scheme is supported")
        
        serialized_tx = payment_proof.get('payload', {}).get('serializedTransaction')
        if not serialized_tx:
            raise HTTPException(status_code=400, detail="Missing serialized transaction")
        
        # In a real implementation, you would:
        # 1. Deserialize the transaction
        # 2. Verify it sends the correct amount to the correct recipient
        # 3. Submit it to the Solana network
        # 4. Wait for confirmation
        # 5. Return the transaction signature
        
        # For this example, we'll simulate a successful payment
        # You would need to use solana-py or similar library to actually submit the transaction
        
        # Simulated response
        signature = "simulated_signature_" + serialized_tx[:20]
        explorer_url = f"https://explorer.solana.com/tx/{signature}?cluster={CLUSTER}"
        
        return {
            "status": "success",
            "message": "Payment processed successfully",
            "paymentDetails": {
                "amountReceived": payment_data.amount * 1_000_000,  # in smallest units
                "amountUSDC": payment_data.amount,
                "signature": signature,
                "recipient": RECIPIENT_WALLET,
                "explorerUrl": explorer_url
            }
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid X-Payment header format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e)}")

@router.get("/api/payment/onchain/status/{signature}")
async def get_payment_status(signature: str):
    """
    Check the status of an onchain payment transaction
    """
    # In a real implementation, you would query the Solana network
    # to check the transaction status
    
    return {
        "signature": signature,
        "status": "confirmed",
        "confirmations": 32,
        "cluster": CLUSTER
    }
