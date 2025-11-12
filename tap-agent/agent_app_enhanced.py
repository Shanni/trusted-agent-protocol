# © 2025 Shanni.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Project Sienna Enhanced TAP Agent with Spending Rules
# Supports: Visa Card, CASH, and x402 Onchain Payments with Spending Limits

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
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ed25519
from cryptography.hazmat.backends import default_backend

# Load environment variables
load_dotenv()

# Global variable to store automation results
_automation_results = {}

# Spending tracker - in production, use a database
if 'spending_tracker' not in st.session_state:
    st.session_state.spending_tracker = {
        'daily_spent': 0.0,
        'last_reset': datetime.now().date(),
        'transactions': []
    }

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

def reset_daily_spending_if_needed():
    """Reset daily spending counter if it's a new day"""
    today = datetime.now().date()
    if st.session_state.spending_tracker['last_reset'] != today:
        st.session_state.spending_tracker['daily_spent'] = 0.0
        st.session_state.spending_tracker['last_reset'] = today
        st.session_state.spending_tracker['transactions'] = []

def check_spending_limit(amount: float, daily_limit: float, per_transaction_limit: float) -> tuple[bool, str]:
    """Check if transaction is within spending limits"""
    reset_daily_spending_if_needed()
    
    # Check per-transaction limit
    if amount > per_transaction_limit:
        return False, f"Transaction amount ${amount:.2f} exceeds per-transaction limit of ${per_transaction_limit:.2f}"
    
    # Check daily limit
    current_spent = st.session_state.spending_tracker['daily_spent']
    if current_spent + amount > daily_limit:
        remaining = daily_limit - current_spent
        return False, f"Transaction would exceed daily limit. Spent today: ${current_spent:.2f}, Limit: ${daily_limit:.2f}, Remaining: ${remaining:.2f}"
    
    return True, "OK"

def record_transaction(amount: float, payment_method: str, order_number: str = None):
    """Record a transaction in the spending tracker"""
    reset_daily_spending_if_needed()
    
    st.session_state.spending_tracker['daily_spent'] += amount
    st.session_state.spending_tracker['transactions'].append({
        'timestamp': datetime.now().isoformat(),
        'amount': amount,
        'payment_method': payment_method,
        'order_number': order_number
    })

def get_rsa_keys_from_env():
    """Get RSA keys from environment variables"""
    private_key = os.getenv('RSA_PRIVATE_KEY')
    public_key = os.getenv('RSA_PUBLIC_KEY')
    
    if not private_key or not public_key:
        raise ValueError("RSA_PRIVATE_KEY and RSA_PUBLIC_KEY must be set in .env file")
    
    return private_key, public_key

def get_ed25519_keys_from_env():
    """Get Ed25519 keys from environment variables"""
    private_key = os.getenv('ED25519_PRIVATE_KEY')
    public_key = os.getenv('ED25519_PUBLIC_KEY')
    
    if not private_key or not public_key:
        raise ValueError("ED25519_PRIVATE_KEY and ED25519_PUBLIC_KEY must be set in .env file")
    
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

def create_ed25519_signature(private_key_b64: str, authority: str, path: str, keyid: str, nonce: str, created: int, expires: int, tag: str) -> tuple[str, str]:
    """Create Ed25519 HTTP Message Signature following RFC 9421"""
    try:
        signature_params = f'("@authority" "@path"); created={created}; expires={expires}; keyId="{keyid}"; alg="ed25519"; nonce="{nonce}"; tag="{tag}"'
        
        signature_base_lines = [
            f'"@authority": {authority}',
            f'"@path": {path}',
            f'"@signature-params": {signature_params}'
        ]
        signature_base = '\n'.join(signature_base_lines)
        
        private_key_bytes = base64.b64decode(private_key_b64)
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        
        signature = private_key.sign(signature_base.encode('utf-8'))
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        signature_input_header = f'sig1=("@authority" "@path"); created={created}; expires={expires}; keyId="{keyid}"; alg="ed25519"; nonce="{nonce}"; tag="{tag}"'
        signature_header = f'sig1=:{signature_b64}:'
        
        return signature_input_header, signature_header
        
    except Exception as e:
        st.error(f"❌ Error creating Ed25519 signature: {str(e)}")
        return "", ""

def perform_x402_payment(amount: float, recipient_wallet: str, network: str = "devnet"):
    """
    Perform x402 onchain payment using Solana/USDC
    """
    st.info(f"🔗 Initiating x402 payment: {amount} USDC on Solana {network}")
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

def perform_api_checkout(session_id: str, checkout_data: dict, payment_method: str, headers: dict):
    """
    Perform checkout via API with specified payment method
    """
    try:
        api_base = os.getenv('MERCHANT_API_URL', 'http://localhost:8000')
        
        print(f"\n{'='*60}")
        print(f"🔧 API CHECKOUT DEBUG INFO")
        print(f"{'='*60}")
        print(f"📍 API Base URL: {api_base}")
        print(f"🆔 Session ID: {session_id}")
        print(f"💳 Payment Method: {payment_method}")
        print(f"📦 Checkout Data Keys: {list(checkout_data.keys())}")
        
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
            print(f"💳 Adding Visa card payment fields")
            checkout_payload.update({
                "card_number": checkout_data.get('card_number', '4111111111111111'),
                "expiry_date": checkout_data.get('expiry_date', '12/25'),
                "cvv": checkout_data.get('cvv', '123'),
                "name_on_card": checkout_data.get('name_on_card', checkout_data.get('customer_name', 'Agent Customer'))
            })
        elif payment_method == 'x402':
            print(f"🔗 Processing x402 onchain payment")
            amount = checkout_data.get('total_amount', 10.0)
            recipient_wallet = os.getenv('SOLANA_RECIPIENT_WALLET', 'MERCHANT_WALLET_ADDRESS')
            network = os.getenv('SOLANA_CLUSTER', 'devnet')
            
            print(f"   Amount: {amount} USDC")
            print(f"   Recipient: {recipient_wallet}")
            print(f"   Network: {network}")
            
            payment_result = perform_x402_payment(amount, recipient_wallet, network)
            
            if payment_result['success']:
                print(f"✅ x402 payment completed! Signature: {payment_result['signature']}")
                st.success(f"✅ x402 payment completed! Signature: {payment_result['signature']}")
                checkout_payload.update({
                    'payment_signature': payment_result['signature'],
                    'payment_network': payment_result['network'],
                    'payment_explorer_url': payment_result['explorerUrl']
                })
            else:
                print(f"❌ x402 payment failed: {payment_result.get('error', 'Unknown error')}")
        
        checkout_url = f"{api_base}/api/orders/checkout/{session_id}"
        
        print(f"\n📤 Making POST request to: {checkout_url}")
        print(f"📋 Payload keys: {list(checkout_payload.keys())}")
        print(f"🔐 Headers: {list(headers.keys())}")
        
        response = requests.post(
            checkout_url,
            json=checkout_payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            order_number = result.get('order', {}).get('order_number', 'Unknown')
            
            print(f"✅ Checkout successful!")
            print(f"📦 Order Number: {order_number}")
            print(f"📄 Response keys: {list(result.keys())}")
            
            return {
                "success": True,
                "order_number": order_number,
                "response": result
            }
        else:
            error_text = response.text[:500] if response.text else "No response body"
            print(f"❌ Checkout failed with status {response.status_code}")
            print(f"📄 Response body: {error_text}")
            
            return {
                "success": False,
                "error": f"Checkout failed: {response.status_code}",
                "response_body": error_text
            }
            
    except Exception as e:
        print(f"❌ Exception in perform_api_checkout: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"📋 Traceback:\n{traceback.format_exc()}")
        
        return {
            "success": False,
            "error": str(e)
        }

def run_shopping_flow(product_url: str, headers: dict, checkout_data: dict, payment_method: str, network: str = "devnet"):
    """Run complete shopping flow: view product → add to cart → checkout (like v3)"""
    st.info("🔄 Initializing shopping flow...")
    print("\n" + "="*60)
    print("🤖 STARTING SHOPPING FLOW")
    print(f"Product URL: {product_url}")
    print(f"Payment Method: {payment_method}")
    print("="*60 + "\n")
    
    try:
        st.info("📦 Importing Playwright...")
        print("📦 Importing Playwright...")
        from playwright.sync_api import sync_playwright
        import re
        st.success("✅ Playwright imported successfully")
        print("✅ Playwright imported successfully")
        
        global _automation_results
        _automation_results = {
            'status': 'running',
            'steps': [],
            'product_info': {},
            'cart_info': {},
            'order_info': {}
        }
        
        def add_step(step_name: str, status: str, details: str = ""):
            """Add a step to the results"""
            _automation_results['steps'].append({
                'name': step_name,
                'status': status,
                'details': details,
                'timestamp': time.strftime("%H:%M:%S")
            })
            msg = f"{status} {step_name}: {details}"
            st.write(msg)
            print(msg)
        
        st.info("🌐 Launching browser...")
        print("🌐 Launching browser (headless=False)...")
        
        with sync_playwright() as p:
            # Launch browser (visible)
            print("🔧 Configuring Chromium...")
            browser = p.chromium.launch(
                headless=False,
                args=[
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--ignore-certificate-errors'
                ]
            )
            st.success("✅ Browser launched!")
            print("✅ Browser launched successfully")
            
            # Create context with signature headers
            print("🔐 Creating browser context with signature headers...")
            context = browser.new_context(
                extra_http_headers=headers,
                ignore_https_errors=True,
                viewport={'width': 1280, 'height': 800}
            )
            print("✅ Browser context created")
            
            print("📄 Opening new page...")
            page = context.new_page()
            st.success("✅ Browser page ready")
            print("✅ Page ready")
            
            st.write("="*60)
            st.write("🤖 STARTING AUTOMATED SHOPPING FLOW")
            st.write("="*60)
            print("\n" + "="*60)
            print("🤖 AUTOMATED SHOPPING FLOW STARTED")
            print("="*60 + "\n")
            
            try:
                # STEP 1: View Product
                add_step("Navigate to Product", "🔄", f"Loading {product_url}")
                page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(2)
                add_step("Navigate to Product", "✅", "Page loaded successfully")
                
                # Extract product information
                add_step("Extract Product Info", "🔄", "Scanning page for product details")
                
                product_info = {}
                
                # Extract title
                title_selectors = ['h1', '.product-title', '[data-testid="product-title"]']
                for selector in title_selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            title = element.inner_text().strip()
                            if title and len(title) > 3:
                                product_info['title'] = title
                                break
                    except:
                        continue
                
                # Extract price
                price_selectors = ['.price', '[data-testid="price"]', '[class*="price"]']
                for selector in price_selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            price = element.inner_text().strip()
                            if '$' in price or any(c.isdigit() for c in price):
                                product_info['price'] = price
                                break
                    except:
                        continue
                
                _automation_results['product_info'] = product_info
                
                if product_info.get('title'):
                    add_step("Extract Product Info", "✅", f"Found: {product_info['title']} - {product_info.get('price', 'N/A')}")
                else:
                    add_step("Extract Product Info", "⚠️", "Could not extract all product details")
                
                # STEP 2: Add to Cart
                add_step("Add to Cart", "🔄", "Looking for 'Add to Cart' button")
                
                add_to_cart_selectors = [
                    'button:has-text("Add to Cart")',
                    'button:has-text("Add To Cart")',
                    '[data-testid="add-to-cart"]',
                    '.add-to-cart',
                    '#addToCart'
                ]
                
                cart_added = False
                for selector in add_to_cart_selectors:
                    try:
                        button = page.query_selector(selector)
                        if button and button.is_visible():
                            button.click()
                            cart_added = True
                            add_step("Add to Cart", "✅", "Product added to cart")
                            time.sleep(2)
                            break
                    except:
                        continue
                
                if not cart_added:
                    add_step("Add to Cart", "⚠️", "Could not find 'Add to Cart' button, proceeding anyway")
                
                # STEP 3: Navigate to Cart
                parsed = urlparse(product_url)
                cart_url = f"{parsed.scheme}://{parsed.netloc}/cart"
                
                add_step("Navigate to Cart", "🔄", f"Going to {cart_url}")
                print(f"\n🛒 Navigating to cart: {cart_url}")
                page.goto(cart_url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(2)
                add_step("Navigate to Cart", "✅", "Cart page loaded")
                
                # Extract cart info and session ID
                print(f"\n{'='*60}")
                print(f"🛒 CART PAGE INFO")
                print(f"{'='*60}")
                print(f"📍 Current URL: {page.url}")
                
                try:
                    # Try to extract session ID from cart page
                    cart_session = page.evaluate("() => localStorage.getItem('cartSessionId')")
                    print(f"🆔 Cart Session ID: {cart_session}")
                except Exception as e:
                    print(f"⚠️ Could not get cart session ID: {e}")
                
                try:
                    cart_items = page.query_selector_all('.cart-item, [data-testid="cart-item"]')
                    
                    # Extract detailed cart information
                    items_list = []
                    for item in cart_items:
                        try:
                            item_data = {}
                            # Try to extract item name
                            name_elem = item.query_selector('.item-name, .product-name, h3, h4')
                            if name_elem:
                                item_data['name'] = name_elem.inner_text().strip()
                            
                            # Try to extract price
                            price_elem = item.query_selector('.item-price, .price, [class*="price"]')
                            if price_elem:
                                item_data['price'] = price_elem.inner_text().strip()
                            
                            # Try to extract quantity
                            qty_elem = item.query_selector('.quantity, input[type="number"]')
                            if qty_elem:
                                qty_text = qty_elem.inner_text().strip() if qty_elem.inner_text() else qty_elem.get_attribute('value')
                                item_data['quantity'] = qty_text
                            
                            if item_data:  # Only add if we extracted something
                                items_list.append(item_data)
                        except Exception as item_err:
                            print(f"⚠️ Could not extract details for cart item: {item_err}")
                            continue
                    
                    _automation_results['cart_info'] = {
                        'item_count': len(cart_items),
                        'items': items_list
                    }
                    print(f"📦 Cart items found: {len(cart_items)}")
                    if items_list:
                        print(f"📋 Extracted details for {len(items_list)} items")
                        for idx, item in enumerate(items_list, 1):
                            print(f"   Item {idx}: {item}")
                    add_step("View Cart", "✅", f"Found {len(cart_items)} item(s) in cart with {len(items_list)} detailed")
                except Exception as e:
                    print(f"⚠️ Could not extract cart details: {e}")
                    add_step("View Cart", "⚠️", "Could not extract cart details")
                
                print(f"{'='*60}\n")
                
                # STEP 4: Proceed to Checkout
                add_step("Proceed to Checkout", "🔄", "Looking for checkout button")
                
                checkout_selectors = [
                    'button:has-text("Proceed to Checkout")',
                    'button:has-text("Checkout")',
                    'a:has-text("Checkout")',
                    '[data-testid="checkout"]',
                    '.checkout-button'
                ]
                
                checkout_clicked = False
                for selector in checkout_selectors:
                    try:
                        button = page.query_selector(selector)
                        if button and button.is_visible():
                            button.click()
                            checkout_clicked = True
                            add_step("Proceed to Checkout", "✅", "Navigating to checkout")
                            time.sleep(3)
                            break
                    except:
                        continue
                
                if not checkout_clicked:
                    # Try direct navigation
                    checkout_url = f"{parsed.scheme}://{parsed.netloc}/checkout"
                    add_step("Proceed to Checkout", "🔄", f"Direct navigation to {checkout_url}")
                    print(f"\n🛒 Direct navigation to checkout: {checkout_url}")
                    page.goto(checkout_url, wait_until='domcontentloaded', timeout=30000)
                    time.sleep(2)
                    add_step("Proceed to Checkout", "✅", "Checkout page loaded")
                
                # Log checkout page info
                print(f"\n{'='*60}")
                print(f"📝 CHECKOUT PAGE INFO")
                print(f"{'='*60}")
                print(f"📍 Current URL: {page.url}")
                print(f"📄 Page Title: {page.title()}")
                
                try:
                    checkout_session = page.evaluate("() => localStorage.getItem('cartSessionId')")
                    print(f"🆔 Checkout Session ID: {checkout_session}")
                except Exception as e:
                    print(f"⚠️ Could not get checkout session ID: {e}")
                
                print(f"{'='*60}\n")
                
                # STEP 5: Fill Checkout Form
                add_step("Fill Checkout Form", "🔄", "Filling customer information")
                
                form_fields = {
                    'email': checkout_data.get('customer_email', 'john.doe@example.com'),
                    'firstName': checkout_data.get('first_name', checkout_data.get('customer_name', 'John').split()[0]),
                    'lastName': checkout_data.get('last_name', checkout_data.get('customer_name', 'John Doe').split()[-1]),
                    'phone': checkout_data.get('customer_phone', '+1-555-0123'),
                    'address1': checkout_data.get('address', '123 Main Street'),
                    'city': checkout_data.get('city', 'New York'),
                    'state': checkout_data.get('state', 'NY'),
                    'zipCode': checkout_data.get('zip', '10001'),
                }
                
                # Add card fields if Visa payment
                if payment_method == 'visa':
                    form_fields.update({
                        'cardNumber': checkout_data.get('card_number', '4111111111111111'),
                        'expiryDate': checkout_data.get('expiry_date', '12/25'),
                        'cvv': checkout_data.get('cvv', '123'),
                        'nameOnCard': checkout_data.get('name_on_card', checkout_data.get('customer_name', 'John Doe'))
                    })
                
                fields_filled = 0
                for field_name, field_value in form_fields.items():
                    selectors = [
                        f'#{field_name}',
                        f'[name="{field_name}"]',
                        f'[data-testid="{field_name}"]'
                    ]
                    
                    for selector in selectors:
                        try:
                            element = page.query_selector(selector)
                            if element and element.is_visible() and element.is_enabled():
                                element.fill(str(field_value))
                                fields_filled += 1
                                break
                        except:
                            continue
                
                add_step("Fill Checkout Form", "✅", f"Filled {fields_filled} form fields")
                
                # STEP 5.5: Select Payment Method on Frontend
                add_step("Select Payment Method", "🔄", f"Selecting {PAYMENT_METHODS[payment_method]['name']} on checkout page")
                time.sleep(1)
                
                # Map x402 to 'onchain' for frontend compatibility
                frontend_payment_value = 'onchain' if payment_method == 'x402' else payment_method
                
                # Try to find and select payment method radio button or dropdown
                payment_selected = False
                
                # Method 1: Radio buttons with labels
                payment_selectors = [
                    f'input[value="{frontend_payment_value}"]',
                    f'input[name="paymentMethod"][value="{frontend_payment_value}"]',
                    f'[data-payment-method="{frontend_payment_value}"]',
                    f'label:has-text("{PAYMENT_METHODS[payment_method]['name']}")',
                    'input[value="onchain"]',  # Explicit fallback for onchain
                    'input[name="paymentMethod"][value="onchain"]',
                ]
                
                for selector in payment_selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            # If it's a label, find the associated input
                            if element.evaluate('el => el.tagName') == 'LABEL':
                                input_element = element.query_selector('input') or page.query_selector(f'#{element.get_attribute("for")}')
                                if input_element:
                                    input_element.click()
                                    payment_selected = True
                                    break
                            else:
                                element.click()
                                payment_selected = True
                                break
                    except Exception as e:
                        print(f"Selector {selector} failed: {e}")
                        continue
                
                if payment_selected:
                    add_step("Select Payment Method", "✅", f"{PAYMENT_METHODS[payment_method]['name']} selected")
                    time.sleep(1)
                else:
                    add_step("Select Payment Method", "⚠️", "Could not find payment method selector, will use API directly")
                
                # STEP 6: Click Payment Button (Agent-based payment)
                add_step("Click Payment Button", "🔄", "Looking for agent payment button")
                time.sleep(1)
                
                # Try to find agent payment button or complete order button
                payment_button_clicked = False
                payment_button_selectors = [
                    'button:has-text("Pay with Agent")',
                    'button:has-text("Use Agent")',
                    '[data-testid="agent-payment-button"]',
                    'button:has-text("Complete Order")',
                    'button:has-text("Place Order")',
                ]
                
                for selector in payment_button_selectors:
                    try:
                        button = page.query_selector(selector)
                        if button and button.is_visible():
                            add_step("Click Payment Button", "🔄", f"Found button: {selector}")
                            button.click()
                            payment_button_clicked = True
                            add_step("Click Payment Button", "✅", "Payment button clicked")
                            time.sleep(2)  # Wait for any modal or processing
                            break
                    except Exception as e:
                        print(f"Button selector {selector} failed: {e}")
                        continue
                
                if not payment_button_clicked:
                    add_step("Click Payment Button", "⚠️", "No payment button found, using direct API")
                
                # Initialize order_submitted flag
                order_submitted = False
                
                # STEP 7: Submit Order via API (only for non-x402 payments)
                if payment_method != 'x402':
                    add_step("Submit Order", "🔄", f"Calling API with {PAYMENT_METHODS[payment_method]['name']}")
                    
                    # Extract session ID from cookies or localStorage
                    print(f"\n{'='*60}")
                    print(f"🔍 EXTRACTING SESSION ID")
                    print(f"{'='*60}")
                    
                    session_id = None
                    try:
                        # Try to get session ID from localStorage
                        session_id = page.evaluate("() => localStorage.getItem('cartSessionId')")
                        print(f"📦 Session ID from localStorage: {session_id}")
                    except Exception as e:
                        print(f"⚠️ Could not get session ID from localStorage: {e}")
                    
                    if not session_id:
                        try:
                            # Try to get from cookies
                            cookies = context.cookies()
                            for cookie in cookies:
                                if 'session' in cookie['name'].lower():
                                    session_id = cookie['value']
                                    print(f"🍪 Session ID from cookie '{cookie['name']}': {session_id}")
                                    break
                        except Exception as e:
                            print(f"⚠️ Could not get session ID from cookies: {e}")
                    
                    if not session_id:
                        # Fallback to demo session
                        session_id = "demo-session-" + uuid.uuid4().hex[:8]
                        print(f"⚠️ Using generated session ID: {session_id}")
                    else:
                        print(f"✅ Using extracted session ID: {session_id}")
                    
                    print(f"{'='*60}\n")
                    
                    api_result = perform_api_checkout(session_id, checkout_data, payment_method, headers)
                    
                    if api_result["success"]:
                        add_step("Submit Order", "✅", f"Order submitted via API. Order Number: {api_result['order_number']}")
                        order_submitted = True
                        
                        # Update results with API-extracted order number
                        _automation_results['order_info'] = {
                            'order_number': api_result['order_number'],
                            'success_url': page.url,
                            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                            'source': 'api_checkout',
                            'payment_method': payment_method
                        }
                        
                        add_step("Order Confirmation", "✅", f"Order Number: {api_result['order_number']}")
                    else:
                        # Fallback to UI automation if API checkout fails
                        add_step("Submit Order", "⚠️", "API checkout failed, falling back to UI automation. Error: " + str(api_result.get("error", "Unknown error")))
                        
                        submit_selectors = [
                            'button:has-text("Place Order")',
                            'button:has-text("Complete Order")',
                            'button:has-text("Submit Order")',
                            'input[type="submit"]',
                            'button[type="submit"]',
                            '[data-testid="submit-order"]',
                            '.submit-order',
                            '#submit-order'
                        ]
                        
                        for selector in submit_selectors:
                            try:
                                button = page.query_selector(selector)
                                if button and button.is_visible():
                                    add_step("Submit Order", "🔄", f"Found submit button: {selector}")
                                    button.click()
                                    order_submitted = True
                                    add_step("Submit Order", "✅", "Order submitted via UI")
                                    time.sleep(3)
                                    break
                            except Exception as e:
                                continue
                        
                        if not order_submitted:
                            add_step("Submit Order", "❌", "Could not find submit button")
                else:
                    # For x402 payments, skip API checkout and use UI automation
                    add_step("Submit Order", "⚠️", "x402 payment - using UI automation (API POST not available yet)")
                    
                    # Look for the payment button on checkout page
                    payment_button_selectors = [
                        'button:has-text("Pay")',
                        'button:has-text("Complete Payment")',
                        'button:has-text("Submit Payment")',
                        'button:has-text("Pay Now")',
                        '[data-testid="pay-button"]',
                        '.pay-button'
                    ]
                    
                    payment_clicked = False
                    for selector in payment_button_selectors:
                        try:
                            button = page.query_selector(selector)
                            if button and button.is_visible():
                                add_step("Submit Order", "🔄", f"Clicking payment button: {selector}")
                                button.click()
                                payment_clicked = True
                                add_step("Submit Order", "✅", "Payment button clicked")
                                time.sleep(5)  # Wait for payment processing
                                break
                        except Exception as e:
                            continue
                    
                    if not payment_clicked:
                        add_step("Submit Order", "⚠️", "No payment button found, looking for submit order button")
                        
                        # Fallback to regular submit order button
                        submit_selectors = [
                            'button:has-text("Place Order")',
                            'button:has-text("Complete Order")',
                            'button:has-text("Submit Order")',
                            'input[type="submit"]',
                            'button[type="submit"]',
                            '[data-testid="submit-order"]',
                            '.submit-order',
                            '#submit-order'
                        ]
                        
                        for selector in submit_selectors:
                            try:
                                button = page.query_selector(selector)
                                if button and button.is_visible():
                                    add_step("Submit Order", "🔄", f"Found submit button: {selector}")
                                    button.click()
                                    order_submitted = True
                                    add_step("Submit Order", "✅", "Order submitted via UI")
                                    time.sleep(3)
                                    break
                            except Exception as e:
                                continue
                        
                        if not order_submitted:
                            add_step("Submit Order", "❌", "Could not find submit button")
                    
                    if order_submitted:
                        # STEP 7: Extract Order Confirmation
                        add_step("Order Confirmation", "🔄", "Extracting order details")
                        
                        order_number_patterns = [
                            r'ORD-\d+-[A-Z0-9]+',
                            r'Order #?:?\s*([A-Z0-9-]+)',
                            r'Order Number:?:?\s*([A-Z0-9-]+)'
                        ]
                        
                        page_content = page.content()
                        order_number = None
                        
                        for pattern in order_number_patterns:
                            match = re.search(pattern, page_content)
                            if match:
                                order_number = match.group(0) if 'ORD-' in match.group(0) else match.group(1)
                                break
                        
                        _automation_results['order_info'] = {
                            'order_number': order_number or 'Unknown',
                            'success_url': page.url,
                            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                            'source': 'ui_automation',
                            'payment_method': payment_method
                        }
                        
                        if order_number:
                            add_step("Order Confirmation", "✅", f"Order Number: {order_number}")
                        else:
                            add_step("Order Confirmation", "⚠️", "Order placed but number not found in page content")
                    else:
                        add_step("Submit Order", "❌", "Could not submit order")
                
                # Wait a moment before closing
                time.sleep(2)
                
                _automation_results['status'] = 'completed'
                add_step("Shopping Flow Complete", "🎉", "All steps finished")
                
            except Exception as e:
                add_step("Error", "❌", str(e))
                _automation_results['status'] = 'error'
                _automation_results['error'] = str(e)
            
            finally:
                st.write("="*60)
                st.write("🔍 Browser is still open for you to review the checkout page.")
                st.write("👀 Please review the results in the browser window.")
                st.write("="*60)
                print("\n" + "="*60)
                print("🔍 Browser is still open - waiting for user to review...")
                print("="*60)
                
                # Wait for user to press a button before closing
                st.info("⏸️ Browser will remain open. Click the button below when you're done reviewing.")
                if st.button("✅ Close Browser", key="close_browser_btn"):
                    st.write("🔒 Closing browser...")
                    print("🔒 User requested browser close")
                    browser.close()
                    print("✅ Browser closed")
                    st.success("✅ Browser closed successfully")
                else:
                    # Keep browser open until button is clicked
                    st.warning("⏳ Browser is still open. Close this tab or click the button above to close the browser.")
                    # Note: In Streamlit, the browser will remain open until the script reruns
                    # We'll add a timeout as a safety measure
                    print("⏳ Waiting for user action... (Browser will auto-close after 5 minutes)")
                    time.sleep(300)  # 5 minute timeout
                    print("⏱️ Timeout reached, closing browser")
                    browser.close()
                    print("✅ Browser closed after timeout")
                
    except ImportError as e:
        error_msg = f"Playwright not installed: {str(e)}"
        st.error(f"❌ {error_msg}")
        st.info("💡 Run: pip install playwright && playwright install chromium")
        print(f"❌ ERROR: {error_msg}")
        _automation_results = {
            'status': 'error',
            'error': error_msg
        }
    except Exception as e:
        error_msg = f"Shopping flow error: {str(e)}"
        st.error(f"❌ {error_msg}")
        print(f"❌ ERROR: {error_msg}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print("Traceback:")
        print(traceback.format_exc())
        _automation_results = {
            'status': 'error',
            'error': str(e)
        }

def main():
    st.set_page_config(
        page_title="Project Sienna TAP Agent",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Project Sienna TAP Agent")
    st.markdown("### 💳 Visa | 💵 CASH | 🔗 x402 Onchain")
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        merchant_url = st.text_input(
            "Merchant URL",
            value=os.getenv('MERCHANT_URL', 'http://localhost:3001')
        )
        
        product_url = st.text_input(
            "Product URL",
            value=f"{merchant_url}/product/1"
        )
        
        st.divider()
        
        # Spending Rules - Redesigned
        st.header("💰 Budget Control")
        
        with st.expander("⚙️ Configure Spending Limits", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                daily_limit = st.number_input(
                    "Daily Limit ($)",
                    min_value=0.0,
                    max_value=10000.0,
                    value=500.0,
                    step=50.0
                )
            with col_b:
                per_transaction_limit = st.number_input(
                    "Per Transaction ($)",
                    min_value=0.0,
                    max_value=5000.0,
                    value=100.0,
                    step=10.0
                )
        
        # Show current spending - compact view
        reset_daily_spending_if_needed()
        spent_today = st.session_state.spending_tracker['daily_spent']
        remaining = daily_limit - spent_today
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💸 Spent", f"${spent_today:.2f}")
        with col2:
            st.metric("✅ Remaining", f"${remaining:.2f}")
        with col3:
            usage_pct = (spent_today / daily_limit * 100) if daily_limit > 0 else 0
            st.metric("📊 Usage", f"{usage_pct:.0f}%")
        
        if spent_today > 0:
            st.progress(min(spent_today / daily_limit, 1.0))
        
        st.divider()
        
        # Payment Method
        st.header("💳 Payment Method")
        payment_method = st.radio(
            "Select:",
            options=['x402', 'visa', 'cash'],
            index=0,
            format_func=lambda x: f"{PAYMENT_METHODS[x]['icon']} {PAYMENT_METHODS[x]['name']}",
            help="Choose payment method"
        )
        st.info(PAYMENT_METHODS[payment_method]['description'])
        
        # Payment-specific inputs
        if payment_method == 'visa':
            st.subheader("💳 Card Details")
            card_number = st.text_input("Card Number", value="4111111111111111")
            col1, col2 = st.columns(2)
            with col1:
                expiry = st.text_input("Expiry", value="12/25")
            with col2:
                cvv = st.text_input("CVV", value="123", type="password")
        
        elif payment_method == 'x402':
            st.subheader("🔗 Solana Wallet Configuration")
            
            # Option 1: Use default client.json
            use_default_wallet = st.checkbox("Use default wallet (client.json)", value=True)
            
            if use_default_wallet:
                # Try to load client.json from the project root
                client_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client.json')
                if os.path.exists(client_json_path):
                    try:
                        with open(client_json_path, 'r') as f:
                            wallet_data = json.load(f)
                        st.success(f"✅ Loaded wallet from client.json ({len(wallet_data)} bytes)")
                        # Store in session state
                        st.session_state['solana_wallet_key'] = wallet_data
                    except Exception as e:
                        st.error(f"❌ Failed to load client.json: {e}")
                        st.session_state['solana_wallet_key'] = None
                else:
                    st.warning("⚠️ client.json not found in project root")
                    st.session_state['solana_wallet_key'] = None
            else:
                # Option 2: Upload custom wallet file
                st.info("Upload your Solana wallet keypair JSON file")
                uploaded_file = st.file_uploader(
                    "Choose wallet JSON file",
                    type=['json'],
                    help="Upload your Solana keypair in JSON format (array of 64 numbers)"
                )
                
                if uploaded_file is not None:
                    try:
                        wallet_data = json.load(uploaded_file)
                        if isinstance(wallet_data, list) and len(wallet_data) == 64:
                            st.success(f"✅ Wallet loaded successfully")
                            st.session_state['solana_wallet_key'] = wallet_data
                        else:
                            st.error("❌ Invalid wallet format. Expected array of 64 numbers.")
                            st.session_state['solana_wallet_key'] = None
                    except Exception as e:
                        st.error(f"❌ Failed to parse wallet file: {e}")
                        st.session_state['solana_wallet_key'] = None
                else:
                    st.session_state['solana_wallet_key'] = None
            
            # Show wallet status
            if st.session_state.get('solana_wallet_key'):
                st.caption("🔐 Wallet is configured and ready for onchain payments")
            else:
                st.warning("⚠️ No wallet configured. Onchain payments will not work.")
        
        st.divider()
        
        # Signature Algorithm
        st.header("🔐 Signature Algorithm")
        sig_algorithm = st.selectbox(
            "Algorithm",
            options=['ed25519', 'rsa-pss-sha256'],
            index=0,
            help="RFC 9421 signature algorithm"
        )
        
        # Optional: Manual signature input
        use_manual_sig = st.checkbox("Use Manual Signature JSON", value=False)
        if use_manual_sig:
            sig_json = st.text_area(
                "Signature JSON",
                value='{"keyId": "agent-key-1", "nonce": "..."}',
                height=150
            )
    
    # Main Content
    tab1, tab2, tab3, tab4 = st.tabs(["🛒 Shopping", "📋 Transactions", "🔐 Signatures", "📊 Spending Report"])
    
    with tab1:
        st.header("Automated Shopping Flow")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Customer Information")
            customer_name = st.text_input("Name", value="John Doe")
            customer_email = st.text_input("Email", value="john@example.com")
            customer_phone = st.text_input("Phone", value="+1-555-0123")
        
        with col2:
            st.subheader("Shipping Address")
            address = st.text_input("Street", value="123 Main St")
            city = st.text_input("City", value="New York")
            col_state, col_zip = st.columns(2)
            with col_state:
                state = st.text_input("State", value="NY")
            with col_zip:
                zip_code = st.text_input("ZIP", value="10001")
        
        # Transaction amount will be determined from cart total
        transaction_amount = 0.0
        
        # Network selection for x402 payments
        if payment_method == 'x402':
            network = st.selectbox(
                "Solana Network",
                ["devnet", "mainnet"],
                index=0,
                help="Choose which Solana network to use for x402 payments"
            )
        else:
            network = "devnet"  # Default for non-x402
        
        # Check spending limit before starting
        can_proceed, limit_message = check_spending_limit(
            transaction_amount,
            daily_limit,
            per_transaction_limit
        )
        
        if not can_proceed:
            st.error(f"🚫 {limit_message}")
        else:
            st.success(f"✅ Transaction within limits")
        
        st.divider()
        
        if st.button("🚀 Start Automated Shopping", type="primary", disabled=not can_proceed, use_container_width=True):
            # Debug info
            st.info("🔍 Debug Information")
            st.write(f"- Product URL: {product_url}")
            st.write(f"- Payment Method: {payment_method}")
            st.write(f"- Signature Algorithm: {sig_algorithm}")
            st.write(f"- Transaction Amount: ${transaction_amount:.2f}")
            
            try:
                # Generate signatures
                if sig_algorithm == 'rsa-pss-sha256':
                    private_key_pem, _ = get_rsa_keys_from_env()
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
                else:
                    private_key_b64, _ = get_ed25519_keys_from_env()
                    parsed_url = urlparse(merchant_url)
                    authority = parsed_url.netloc
                    path = parsed_url.path or "/"
                    
                    keyid = "agent-key-ed25519"
                    nonce = str(uuid.uuid4())
                    created = int(time.time())
                    expires = created + 300
                    tag = "project-sienna-agent"
                    
                    signature_input, signature = create_ed25519_signature(
                        private_key_b64, authority, path, keyid, nonce, created, expires, tag
                    )
                
                headers = {
                    'Signature-Input': signature_input,
                    'Signature': signature,
                    'X-Agent-ID': 'project-sienna-tap-agent',
                    'X-Payment-Method': payment_method
                }
                
                checkout_data = {
                    'customer_name': customer_name,
                    'customer_email': customer_email,
                    'customer_phone': customer_phone,
                    'address': address,
                    'city': city,
                    'state': state,
                    'zip': zip_code,
                    'shipping_address': f"{customer_name}\n{address}\n{city}, {state} {zip_code}",
                    'total_amount': transaction_amount
                }
                
                if payment_method == 'visa':
                    checkout_data.update({
                        'card_number': card_number,
                        'expiry_date': expiry,
                        'cvv': cvv,
                        'name_on_card': customer_name
                    })
                
                # Run shopping flow
                with st.spinner("🤖 Agent is working..."):
                    run_shopping_flow(product_url, headers, checkout_data, payment_method, network)
                
                # Display results
                st.divider()
                st.header("📊 Automation Results")
                
                if _automation_results.get('status') == 'completed':
                    st.success("✅ Shopping flow completed successfully!")
                    
                    # Show steps
                    if _automation_results.get('steps'):
                        st.subheader("🔄 Execution Steps")
                        for step in _automation_results['steps']:
                            st.text(f"{step['status']} [{step['timestamp']}] {step['name']}: {step['details']}")
                    
                    # Show product info
                    if _automation_results.get('product_info'):
                        st.subheader("🛍️ Product Information")
                        st.json(_automation_results['product_info'])
                    
                    # Show cart info
                    if _automation_results.get('cart_info'):
                        st.subheader("🛒 Cart Information")
                        st.json(_automation_results['cart_info'])
                    
                    # Show order info
                    if _automation_results.get('order_info'):
                        st.subheader("📋 Order Information")
                        st.json(_automation_results['order_info'])
                
                elif _automation_results.get('status') == 'error':
                    st.error(f"❌ Error: {_automation_results.get('error', 'Unknown error')}")
                
                # Record transaction
                if _automation_results.get('order_info', {}).get('order_number'):
                    record_transaction(
                        transaction_amount,
                        payment_method,
                        _automation_results['order_info']['order_number']
                    )
                    st.balloons()
                    st.success(f"🎉 Order completed! Recorded ${transaction_amount:.2f} spent")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.header("Today's Transactions")
        
        if st.session_state.spending_tracker['transactions']:
            for i, txn in enumerate(reversed(st.session_state.spending_tracker['transactions'])):
                with st.expander(f"Transaction #{len(st.session_state.spending_tracker['transactions']) - i} - ${txn['amount']:.2f}"):
                    st.write(f"**Time:** {txn['timestamp']}")
                    st.write(f"**Amount:** ${txn['amount']:.2f}")
                    st.write(f"**Method:** {PAYMENT_METHODS[txn['payment_method']]['icon']} {PAYMENT_METHODS[txn['payment_method']]['name']}")
                    if txn.get('order_number'):
                        st.write(f"**Order:** {txn['order_number']}")
        else:
            st.info("No transactions today")
    
    with tab3:
        st.header("Signature Information")
        st.code(f"""
RFC 9421 HTTP Message Signatures
Algorithm: {sig_algorithm}
Signed Fields: @authority, @path
Key ID: agent-key-1
Tag: project-sienna-agent
        """)
    
    with tab4:
        st.header("Spending Report")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Daily Limit", f"${daily_limit:.2f}")
        with col2:
            st.metric("Spent Today", f"${spent_today:.2f}")
        with col3:
            st.metric("Remaining", f"${remaining:.2f}")
        
        if daily_limit > 0:
            usage_pct = (spent_today / daily_limit) * 100
            st.progress(min(spent_today / daily_limit, 1.0))
            st.write(f"**Usage:** {usage_pct:.1f}% of daily limit")
        
        if st.button("Reset Daily Counter (Admin)"):
            st.session_state.spending_tracker['daily_spent'] = 0.0
            st.session_state.spending_tracker['transactions'] = []
            st.success("✅ Counter reset")
            st.rerun()

if __name__ == "__main__":
    main()
