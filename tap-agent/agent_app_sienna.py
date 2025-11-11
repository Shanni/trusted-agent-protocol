# © 2025 Visa.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Project Sienna Enhanced TAP Agent
# Supports: Visa Card, CASH, and x402 Onchain Payments

import uuid
import os
import streamlit as st
from dotenv import load_dotenv
import base64
import json
import time
import threading
import requests
from urllib.parse import urlparse
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ed25519
from cryptography.hazmat.backends import default_backend

# Load environment variables
load_dotenv()

# Global variable to store automation results
_automation_results = {}

# Payment method configurations
PAYMENT_METHODS = {
    'visa': {
        'name': 'Visa Card',
        'icon': '💳',
        'description': 'Pay with Visa credit/debit card',
        'requires_card': True
    },
    'cash': {
        'name': 'Cash',
        'icon': '💵',
        'description': 'Cash on delivery',
        'requires_card': False
    },
    'x402': {
        'name': 'x402 by Project Sienna',
        'icon': '🔗',
        'description': 'Onchain payment with USDC on Solana',
        'requires_wallet': True
    }
}

def get_rsa_keys_from_env():
    """Get RSA keys from environment variables"""
    private_key = os.getenv('RSA_PRIVATE_KEY')
    public_key = os.getenv('RSA_PUBLIC_KEY')
    
    if not private_key or not public_key:
        raise ValueError("RSA_PRIVATE_KEY and RSA_PUBLIC_KEY must be set in .env file")
    
    return private_key, public_key

def create_rsa_signature(private_key_pem: str, authority: str, path: str, keyid: str, nonce: str, created: int, expires: int, tag: str) -> tuple[str, str]:
    """Create RSA-PSS-SHA256 HTTP Message Signature following RFC 9421"""
    try:
        signature_params = f'("@authority" "@path"); created={created}; expires={expires}; keyId="{keyid}"; alg="rsa-pss-sha256"; nonce="{nonce}"; tag="{tag}"'
        
        signature_base_lines = [
            f'"@authority": {authority}',
            f'"@path": {path}',
            f'"@signature-params": {signature_params}'
        ]
        signature_base = '\n'.join(signature_base_lines)
        
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        signature = private_key.sign(
            signature_base.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        signature_input_header = f'sig2=("@authority" "@path"); created={created}; expires={expires}; keyId="{keyid}"; alg="rsa-pss-sha256"; nonce="{nonce}"; tag="{tag}"'
        signature_header = f'sig2=:{signature_b64}:'
        
        return signature_input_header, signature_header
        
    except Exception as e:
        st.error(f"❌ Error creating RSA signature: {str(e)}")
        return "", ""

def perform_x402_payment(amount: float, recipient_wallet: str, network: str = "devnet"):
    """
    Perform x402 onchain payment using Solana/USDC
    This is a simplified implementation - in production, you would integrate with actual Solana SDK
    """
    st.info(f"🔗 Initiating x402 payment: {amount} USDC on Solana {network}")
    
    # In production, this would:
    # 1. Connect to Solana network
    # 2. Get or create token accounts
    # 3. Create and sign transaction
    # 4. Submit to network
    # 5. Wait for confirmation
    
    # Simulated payment for demo
    time.sleep(2)
    
    payment_result = {
        'success': True,
        'signature': f'x402_tx_{int(time.time())}_{uuid.uuid4().hex[:8]}',
        'amount': amount,
        'network': network,
        'recipient': recipient_wallet,
        'explorerUrl': f'https://explorer.solana.com/tx/simulated_{int(time.time())}?cluster={network}'
    }
    
    return payment_result

def perform_checkout_with_payment_method(session_id: str, checkout_data: dict, payment_method: str, headers: dict):
    """
    Perform checkout with specified payment method
    """
    try:
        api_base = os.getenv('MERCHANT_API_URL', 'http://localhost:8000')
        
        # Prepare checkout payload based on payment method
        checkout_payload = {
            "customer_name": checkout_data.get('customer_name', 'Agent Customer'),
            "customer_email": checkout_data.get('customer_email', 'agent@example.com'),
            "shipping_address": checkout_data.get('shipping_address', '123 Agent St, Agent City, AC 12345'),
            "billing_address": checkout_data.get('billing_address'),
            "phone": checkout_data.get('customer_phone', '+1-555-AGENT'),
            "special_instructions": checkout_data.get('special_instructions'),
            "payment_method": payment_method,
        }
        
        # Add payment-specific fields
        if payment_method == 'visa':
            # For Visa, include card details (in production, use tokenization)
            checkout_payload.update({
                "card_number": checkout_data.get('card_number', '4111111111111111'),
                "expiry_date": checkout_data.get('expiry_date', '12/25'),
                "cvv": checkout_data.get('cvv', '123'),
                "name_on_card": checkout_data.get('name_on_card', checkout_data.get('customer_name', 'Agent Customer'))
            })
        elif payment_method == 'cash':
            # Cash on delivery - no additional fields needed
            checkout_payload['special_instructions'] = (checkout_payload.get('special_instructions', '') + 
                                                       ' | Payment Method: Cash on Delivery').strip()
        elif payment_method == 'x402':
            # For x402, perform onchain payment first
            st.info("🔗 Processing x402 onchain payment...")
            
            # Get payment details from merchant
            amount = checkout_data.get('total_amount', 10.0)
            recipient_wallet = os.getenv('SOLANA_RECIPIENT_WALLET', 'MERCHANT_WALLET_ADDRESS')
            network = os.getenv('SOLANA_CLUSTER', 'devnet')
            
            # Perform x402 payment
            payment_result = perform_x402_payment(amount, recipient_wallet, network)
            
            if payment_result['success']:
                st.success(f"✅ x402 payment completed! Signature: {payment_result['signature']}")
                st.info(f"🔍 View on explorer: {payment_result['explorerUrl']}")
                
                # Add payment proof to checkout
                checkout_payload.update({
                    'payment_signature': payment_result['signature'],
                    'payment_network': payment_result['network'],
                    'payment_explorer_url': payment_result['explorerUrl']
                })
            else:
                raise Exception("x402 payment failed")
        
        # Submit checkout to merchant API
        checkout_url = f"{api_base}/api/orders/checkout/{session_id}"
        
        st.info(f"📤 Submitting order with {PAYMENT_METHODS[payment_method]['name']}...")
        
        response = requests.post(
            checkout_url,
            json=checkout_payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            order_number = result.get('order', {}).get('order_number', 'Unknown')
            
            st.success(f"✅ Order placed successfully!")
            st.success(f"📋 Order Number: {order_number}")
            st.success(f"💳 Payment Method: {PAYMENT_METHODS[payment_method]['name']}")
            
            return {
                "success": True,
                "order_number": order_number,
                "payment_method": payment_method,
                "response": result
            }
        else:
            error_msg = f"Checkout failed: {response.status_code} - {response.text}"
            st.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
            
    except Exception as e:
        error_msg = f"Checkout error: {str(e)}"
        st.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

def main():
    st.set_page_config(
        page_title="Project Sienna TAP Agent",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Project Sienna TAP Agent")
    st.markdown("### Multi-Payment Method Support: Visa | CASH | x402")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Merchant URL
        merchant_url = st.text_input(
            "Merchant URL",
            value=os.getenv('MERCHANT_URL', 'http://localhost:3003'),
            help="The merchant's website URL"
        )
        
        # API URL
        api_url = st.text_input(
            "Merchant API URL",
            value=os.getenv('MERCHANT_API_URL', 'http://localhost:8000'),
            help="The merchant's API endpoint"
        )
        
        # Product URL
        product_url = st.text_input(
            "Product URL",
            value=f"{merchant_url}/products/1",
            help="Direct link to a product page"
        )
        
        st.divider()
        
        # Payment Method Selection
        st.header("💳 Payment Method")
        payment_method = st.radio(
            "Select payment method:",
            options=['visa', 'cash', 'x402'],
            format_func=lambda x: f"{PAYMENT_METHODS[x]['icon']} {PAYMENT_METHODS[x]['name']}",
            help="Choose how the agent should pay"
        )
        
        st.info(PAYMENT_METHODS[payment_method]['description'])
        
        # Payment-specific inputs
        if payment_method == 'visa':
            st.subheader("💳 Card Details")
            card_number = st.text_input("Card Number", value="4111111111111111")
            col1, col2 = st.columns(2)
            with col1:
                expiry = st.text_input("Expiry (MM/YY)", value="12/25")
            with col2:
                cvv = st.text_input("CVV", value="123", type="password")
            card_name = st.text_input("Name on Card", value="Agent User")
        
        elif payment_method == 'x402':
            st.subheader("🔗 Solana Configuration")
            solana_network = st.selectbox("Network", ["devnet", "mainnet-beta"], index=0)
            recipient_wallet = st.text_input(
                "Recipient Wallet",
                value=os.getenv('SOLANA_RECIPIENT_WALLET', 'MERCHANT_WALLET_ADDRESS'),
                help="Merchant's Solana wallet address"
            )
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["🛒 Shopping Flow", "📋 Order Details", "🔐 Signatures"])
    
    with tab1:
        st.header("Automated Shopping Flow")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Customer Information")
            customer_name = st.text_input("Name", value="John Doe")
            customer_email = st.text_input("Email", value="john.doe@example.com")
            customer_phone = st.text_input("Phone", value="+1-555-0123")
        
        with col2:
            st.subheader("Shipping Address")
            address = st.text_input("Street Address", value="123 Main Street")
            city = st.text_input("City", value="New York")
            col_state, col_zip = st.columns(2)
            with col_state:
                state = st.text_input("State", value="NY")
            with col_zip:
                zip_code = st.text_input("ZIP", value="10001")
        
        st.divider()
        
        # Start shopping button
        if st.button("🚀 Start Automated Shopping", type="primary", use_container_width=True):
            # Generate signatures
            try:
                private_key_pem, public_key_pem = get_rsa_keys_from_env()
                
                parsed_url = urlparse(merchant_url)
                authority = parsed_url.netloc
                path = parsed_url.path or "/"
                
                keyid = "agent-key-1"
                nonce = str(uuid.uuid4())
                created = int(time.time())
                expires = created + 300
                tag = "project-sienna-agent"
                
                signature_input, signature = create_rsa_signature(
                    private_key_pem, authority, path, keyid, nonce, created, expires, tag
                )
                
                headers = {
                    'Signature-Input': signature_input,
                    'Signature': signature,
                    'X-Agent-ID': 'project-sienna-tap-agent',
                    'X-Agent-Version': '1.0-sienna',
                    'X-Payment-Method': payment_method
                }
                
                # Prepare checkout data
                checkout_data = {
                    'customer_name': customer_name,
                    'customer_email': customer_email,
                    'customer_phone': customer_phone,
                    'address': address,
                    'city': city,
                    'state': state,
                    'zip': zip_code,
                    'shipping_address': f"{customer_name}\n{address}\n{city}, {state} {zip_code}",
                }
                
                # Add payment-specific data
                if payment_method == 'visa':
                    checkout_data.update({
                        'card_number': card_number,
                        'expiry_date': expiry,
                        'cvv': cvv,
                        'name_on_card': card_name
                    })
                elif payment_method == 'x402':
                    checkout_data['total_amount'] = 10.0  # This would be calculated from cart
                
                # Show progress
                progress_container = st.container()
                
                with progress_container:
                    st.info("🤖 Agent is working...")
                    
                    # Simulate shopping flow
                    with st.spinner("Step 1: Viewing product..."):
                        time.sleep(1)
                        st.success("✅ Product viewed")
                    
                    with st.spinner("Step 2: Adding to cart..."):
                        time.sleep(1)
                        st.success("✅ Added to cart")
                    
                    with st.spinner("Step 3: Proceeding to checkout..."):
                        time.sleep(1)
                        st.success("✅ Checkout page loaded")
                    
                    with st.spinner(f"Step 4: Processing payment with {PAYMENT_METHODS[payment_method]['name']}..."):
                        # Perform checkout with selected payment method
                        session_id = "demo-session-" + uuid.uuid4().hex[:8]
                        result = perform_checkout_with_payment_method(
                            session_id, checkout_data, payment_method, headers
                        )
                        
                        if result['success']:
                            st.balloons()
                            st.success(f"🎉 Order completed successfully!")
                            st.success(f"📋 Order Number: {result['order_number']}")
                            st.success(f"💳 Payment: {PAYMENT_METHODS[payment_method]['name']}")
                        else:
                            st.error(f"❌ Order failed: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.header("Order Details")
        st.info("Order details will appear here after completing a purchase")
        
        if '_automation_results' in globals() and _automation_results.get('order_info'):
            order_info = _automation_results['order_info']
            st.json(order_info)
    
    with tab3:
        st.header("Signature Information")
        st.info("RFC 9421 HTTP Message Signatures are used to authenticate the agent")
        
        st.code("""
Signature Components:
- Algorithm: RSA-PSS-SHA256
- Signed Fields: @authority, @path
- Key ID: agent-key-1
- Tag: project-sienna-agent
        """)

if __name__ == "__main__":
    main()
