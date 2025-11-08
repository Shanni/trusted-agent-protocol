# © 2025 Visa.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import uuid
import os
import streamlit as st
from dotenv import load_dotenv
import base64
import json
import time
import requests
from urllib.parse import urlparse
from cryptography.hazmat.primitives.asymmetric import ed25519

# Load environment variables
load_dotenv()

def get_ed25519_keys_from_env():
    """Get Ed25519 keys from environment variables"""
    private_key = os.getenv('ED25519_PRIVATE_KEY')
    public_key = os.getenv('ED25519_PUBLIC_KEY')
    
    if not private_key or not public_key:
        raise ValueError("ED25519_PRIVATE_KEY and ED25519_PUBLIC_KEY must be set in .env file")
    
    return private_key, public_key

def create_ed25519_signature(authority: str, path: str, keyid: str, nonce: str, created: int, expires: int, tag: str) -> tuple[str, str]:
    """Create Ed25519 HTTP Message Signature following RFC 9421"""
    try:
        # Get private key from environment
        private_key_b64, _ = get_ed25519_keys_from_env()
        
        # Create signature parameters string
        signature_params = f'("@authority" "@path"); created={created}; expires={expires}; keyId="{keyid}"; alg="ed25519"; nonce="{nonce}"; tag="{tag}"'
        
        # Create the signature base string following RFC 9421 format
        signature_base_lines = [
            f'"@authority": {authority}',
            f'"@path": {path}',
            f'"@signature-params": {signature_params}'
        ]
        signature_base = '\n'.join(signature_base_lines)
        
        print(f"🔐 RFC 9421 Signature Base String:\n{signature_base}")
        
        # Load Ed25519 private key
        private_key_bytes = base64.b64decode(private_key_b64)
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        
        # Sign the signature base string
        signature = private_key.sign(signature_base.encode('utf-8'))
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        # Format the signature-input header (RFC 9421 format)
        signature_input_header = f'sig2=("@authority" "@path"); created={created}; expires={expires}; keyId="{keyid}"; alg="ed25519"; nonce="{nonce}"; tag="{tag}"'
        
        # Format the signature header (RFC 9421 format)
        signature_header = f'sig2=:{signature_b64}:'
        
        print(f"✅ Created RFC 9421 compliant Ed25519 signature")
        
        return signature_input_header, signature_header
        
    except Exception as e:
        print(f"❌ Error creating Ed25519 signature: {str(e)}")
        return "", ""

def parse_url_components(url: str) -> tuple[str, str]:
    """Parse URL to extract authority and path components for RFC 9421"""
    try:
        parsed = urlparse(url)
        authority = parsed.netloc
        path = parsed.path
        if parsed.query:
            path += f"?{parsed.query}"
        
        print(f"🔍 Parsed URL: {url}")
        print(f"🌐 Authority: {authority}")
        print(f"📍 Path: {path}")
        
        return authority, path
    except Exception as e:
        print(f"❌ Error parsing URL: {str(e)}")
        return "", ""

def make_signed_request(url: str, method: str, headers: dict, json_data: dict = None):
    """Make an HTTP request with signature headers"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=json_data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="TAP Agent - Trusted Agent Protocol",
        page_icon="🔐",
        layout="wide"
    )
    
    st.title("🔐 TAP Agent - Trusted Agent Protocol")
    st.markdown("Demonstrate agent operations with RFC 9421 signatures")
    
    # Check for Ed25519 keys
    try:
        private_key_b64, public_key_b64 = get_ed25519_keys_from_env()
        st.success("✅ Ed25519 keys loaded from environment")
    except ValueError as e:
        st.error(f"❌ {str(e)}")
        st.stop()
    
    # Configuration
    st.header("⚙️ Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        merchant_url = st.text_input(
            "Merchant Base URL",
            value="http://localhost:3001",
            help="Base URL of the merchant (CDN proxy)"
        )
        
        agent_id = st.text_input(
            "Agent ID",
            value="agent-shopping-bot-v1",
            help="Your agent identifier"
        )
    
    with col2:
        key_id = st.text_input(
            "Key ID",
            value="primary-ed25519",
            help="Key identifier registered in Agent Registry"
        )
    
    # Operation Selection
    st.header("🎯 Select Operation")
    
    operation = st.radio(
        "Choose an operation:",
        options=[
            "1. View Product (No Signature)",
            "2. Browse Products (No Signature)",
            "3. Add to Cart (No Signature)",
            "4. Checkout (Signature Required)",
            "5. View Orders (Signature Required)"
        ],
        help="Different operations require different levels of authentication"
    )
    
    # Operation-specific configuration
    st.header("📋 Operation Details")
    
    if "View Product" in operation:
        st.info("**Public Operation** - No signature required. Anyone can view products.")
        product_id = st.number_input("Product ID", min_value=1, value=1)
        endpoint = f"{merchant_url}/product/{product_id}"
        requires_signature = False
        method = "GET"
        json_payload = None
        
    elif "Browse Products" in operation:
        st.info("**Public Operation** - No signature required. Browse product catalog.")
        search_query = st.text_input("Search Query (optional)", value="")
        if search_query:
            endpoint = f"{merchant_url}/api/products?query={search_query}"
        else:
            endpoint = f"{merchant_url}/api/products"
        requires_signature = False
        method = "GET"
        json_payload = None
        
    elif "Add to Cart" in operation:
        st.info("**Public Operation** - No signature required. Add items to shopping cart.")
        
        # First, create or get cart session
        if 'cart_session_id' not in st.session_state:
            if st.button("Create Cart Session"):
                response = requests.post(f"{merchant_url}/api/cart/")
                if response.status_code == 200:
                    st.session_state.cart_session_id = response.json()['session_id']
                    st.success(f"✅ Cart created: {st.session_state.cart_session_id}")
                    st.rerun()
                else:
                    st.error(f"Failed to create cart: {response.status_code}")
        
        if 'cart_session_id' in st.session_state:
            st.success(f"Cart Session: {st.session_state.cart_session_id}")
            product_id = st.number_input("Product ID", min_value=1, value=1)
            quantity = st.number_input("Quantity", min_value=1, value=1)
            endpoint = f"{merchant_url}/api/cart/{st.session_state.cart_session_id}/items"
            requires_signature = False
            method = "POST"
            json_payload = {"product_id": product_id, "quantity": quantity}
        else:
            st.warning("Please create a cart session first")
            endpoint = None
            requires_signature = False
            method = "POST"
            json_payload = None
            
    elif "Checkout" in operation:
        st.warning("**Protected Operation** - Signature required! Agent must prove identity.")
        
        if 'cart_session_id' not in st.session_state:
            st.error("❌ No cart session found. Please create a cart and add items first.")
            endpoint = None
            requires_signature = True
            method = "POST"
            json_payload = None
        else:
            st.info(f"Cart Session: {st.session_state.cart_session_id}")
            
            # Checkout type selection
            checkout_type = st.radio(
                "Checkout Method:",
                options=["Traditional (Credit Card)", "x402 (Delegation Token)"],
                help="Choose payment method"
            )
            
            if checkout_type == "Traditional (Credit Card)":
                endpoint = f"{merchant_url}/api/cart/{st.session_state.cart_session_id}/checkout"
                
                with st.expander("Customer Information"):
                    customer_email = st.text_input("Email", value="john.doe@example.com")
                    customer_name = st.text_input("Name", value="John Doe")
                    customer_phone = st.text_input("Phone", value="+1-555-0123")
                    shipping_address = st.text_area("Shipping Address", value="123 Main St, San Francisco, CA 94102")
                
                json_payload = {
                    "customer_email": customer_email,
                    "customer_name": customer_name,
                    "customer_phone": customer_phone,
                    "shipping_address": shipping_address,
                    "payment_method": {
                        "type": "credit_card",
                        "card_number": "4111111111111111",
                        "expiry_date": "12/25",
                        "cvv": "123",
                        "name_on_card": customer_name
                    }
                }
            else:  # x402
                endpoint = f"{merchant_url}/api/cart/{st.session_state.cart_session_id}/x402/checkout"
                
                with st.expander("x402 Configuration"):
                    delegation_token = st.text_input("Delegation Token", value="del_sample_token_123")
                    shipping_address = st.text_area("Shipping Address", value="123 Main St, San Francisco, CA 94102")
                
                json_payload = {
                    "delegation_token": delegation_token,
                    "agent_id": agent_id,
                    "shipping_address": shipping_address
                }
            
            requires_signature = True
            method = "POST"
            
    else:  # View Orders
        st.warning("**Protected Operation** - Signature required! View user's order history.")
        endpoint = f"{merchant_url}/api/orders"
        requires_signature = True
        method = "GET"
        json_payload = None
    
    # Execute Operation
    st.header("🚀 Execute")
    
    if endpoint is None:
        st.warning("Please complete the configuration above")
    else:
        st.code(f"{method} {endpoint}", language="bash")
        
        if requires_signature:
            st.info("🔐 This operation requires RFC 9421 signature")
        else:
            st.info("✅ This is a public operation (no signature needed)")
        
        if st.button(f"Execute {operation.split('.')[1].strip()}", type="primary"):
            with st.spinner("Executing..."):
                headers = {'Content-Type': 'application/json'}
                
                # Generate signature if required
                if requires_signature:
                    authority, path = parse_url_components(endpoint)
                    
                    if authority and path:
                        created = int(time.time())
                        expires = created + 900  # 15 minutes
                        nonce = str(uuid.uuid4())
                        tag = "agent-checkout" if "checkout" in operation.lower() else "agent-operation"
                        
                        signature_input, signature = create_ed25519_signature(
                            authority=authority,
                            path=path,
                            keyid=key_id,
                            nonce=nonce,
                            created=created,
                            expires=expires,
                            tag=tag
                        )
                        
                        if signature_input and signature:
                            headers['Signature-Input'] = signature_input
                            headers['Signature'] = signature
                            st.success("✅ Signature generated")
                        else:
                            st.error("❌ Failed to generate signature")
                            st.stop()
                    else:
                        st.error("❌ Failed to parse URL")
                        st.stop()
                
                # Make request
                response = make_signed_request(endpoint, method, headers, json_payload)
                
                if response:
                    st.subheader("📥 Response")
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if response.status_code == 200:
                            st.success(f"Status: {response.status_code}")
                        elif response.status_code == 403:
                            st.error(f"Status: {response.status_code} - Forbidden (Signature verification failed)")
                        elif response.status_code == 402:
                            st.error(f"Status: {response.status_code} - Payment Required")
                        else:
                            st.warning(f"Status: {response.status_code}")
                    
                    with col2:
                        st.write(f"**URL:** {response.url}")
                    
                    # Show response body
                    try:
                        response_json = response.json()
                        st.json(response_json)
                        
                        # Special handling for checkout success
                        if "checkout" in operation.lower() and response.status_code == 200:
                            if 'order' in response_json:
                                st.balloons()
                                st.success(f"🎉 Order placed successfully!")
                                st.metric("Order Number", response_json['order'].get('order_number', 'N/A'))
                                st.metric("Total Amount", f"${response_json['order'].get('total_amount', 0):.2f}")
                    except:
                        st.text(response.text)
                else:
                    st.error("❌ Request failed")
    
    # Help Section
    with st.expander("ℹ️ How It Works"):
        st.markdown("""
        ### TAP Agent Operations
        
        **Public Operations (No Signature):**
        - View Product - Browse product details
        - Browse Products - Search product catalog
        - Add to Cart - Add items to shopping cart
        
        **Protected Operations (Signature Required):**
        - Checkout - Complete purchase (requires RFC 9421 signature)
        - View Orders - Access order history (requires RFC 9421 signature)
        
        ### RFC 9421 Signature
        
        Protected operations require a cryptographic signature that proves:
        1. **Agent Identity** - The agent is registered and trusted
        2. **Request Integrity** - The request hasn't been tampered with
        3. **Freshness** - The request is recent (not replayed)
        
        The signature includes:
        - `@authority` - The merchant domain
        - `@path` - The API endpoint
        - `created` - Timestamp when signature was created
        - `expires` - When the signature expires
        - `nonce` - Unique value to prevent replay attacks
        - `keyId` - Which public key to use for verification
        
        ### x402 Checkout
        
        x402 is a protocol for machine-to-machine payments using delegation tokens:
        - Agent presents a pre-authorized token instead of credit card
        - Token has spending limits set by the user
        - Merchant settles payment through Payment Facilitator
        - User can revoke tokens at any time
        """)

if __name__ == "__main__":
    main()
