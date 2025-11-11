# © 2025 Visa.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Modified for Project Sienna - Enhanced TAP Agent with improved order confirmation handling

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
        
        print(f"🔐 RFC 9421 RSA Signature Base String:\n{signature_base}")
        
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
        
        print(f"✅ Created RFC 9421 compliant RSA signature")
        
        return signature_input_header, signature_header
        
    except Exception as e:
        print(f"❌ Error creating RSA signature: {str(e)}")
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
        
        print(f"🔐 RFC 9421 Ed25519 Signature Base String:\n{signature_base}")
        
        private_key_bytes = base64.b64decode(private_key_b64)
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        
        signature = private_key.sign(signature_base.encode('utf-8'))
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        signature_input_header = f'sig2=("@authority" "@path"); created={created}; expires={expires}; keyId="{keyid}"; alg="ed25519"; nonce="{nonce}"; tag="{tag}"'
        signature_header = f'sig2=:{signature_b64}:'
        
        print(f"✅ Created RFC 9421 compliant Ed25519 signature")
        
        return signature_input_header, signature_header
        
    except Exception as e:
        print(f"❌ Error creating Ed25519 signature: {str(e)}")
        return "", ""

def perform_api_checkout(session_id: str, checkout_data: dict, headers: dict) -> dict:
    """Perform direct API checkout and return order information"""
    try:
        # Extract base URL from product URL to build API endpoint
        parsed = urlparse(f"http://localhost:3001/product/1")  # Default merchant URL
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # For localhost:3001, the API is at localhost:8000
        if "localhost:3001" in base_url:
            api_base_url = "http://localhost:8000"
        else:
            api_base_url = base_url
        
        # Build checkout endpoint URL
        checkout_url = f"{api_base_url}/api/cart/{session_id}/checkout"
        
        print(f"🔄 Performing direct API checkout to {checkout_url}")
        
        # Make API call with signature headers
        response = requests.post(
            checkout_url,
            json=checkout_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract order information from response
            order_info = response_data.get("data", {}).get("order", {}) or response_data.get("order", {})
            order_number = order_info.get("order_number", "Unknown")
            
            print(f"✅ API checkout successful. Order Number: {order_number}")
            
            return {
                "success": True,
                "order_number": order_number,
                "order_info": order_info,
                "full_response": response_data
            }
        else:
            print(f"❌ API checkout failed with status {response.status_code}: {response.text}")
            return {
                "success": False,
                "error": f"API checkout failed with status {response.status_code}",
                "status_code": response.status_code,
                "response_text": response.text
            }
            
    except Exception as e:
        print(f"❌ Error during API checkout: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

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

def run_full_shopping_flow(product_url: str, headers: dict, checkout_data: dict):
    """Run complete shopping flow: view product → add to cart → checkout"""
    try:
        from playwright.sync_api import sync_playwright
        import re
        
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
            print(f"{status} {step_name}: {details}")
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(
                headless=False,
                args=[
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--ignore-certificate-errors'
                ]
            )
            
            # Create context with signature headers
            context = browser.new_context(
                extra_http_headers=headers,
                ignore_https_errors=True,
                viewport={'width': 1280, 'height': 800}
            )
            
            page = context.new_page()
            
            print("="*60)
            print("🤖 STARTING AUTOMATED SHOPPING FLOW")
            print("="*60)
            
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
                page.goto(cart_url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(2)
                add_step("Navigate to Cart", "✅", "Cart page loaded")
                
                # Extract cart info
                try:
                    cart_items = page.query_selector_all('.cart-item, [data-testid="cart-item"]')
                    _automation_results['cart_info'] = {
                        'item_count': len(cart_items),
                        'items': []
                    }
                    add_step("View Cart", "✅", f"Found {len(cart_items)} item(s) in cart")
                except:
                    add_step("View Cart", "⚠️", "Could not extract cart details")
                
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
                    page.goto(checkout_url, wait_until='domcontentloaded', timeout=30000)
                    time.sleep(2)
                    add_step("Proceed to Checkout", "✅", "Checkout page loaded")
                
                # STEP 5: Fill Checkout Form
                add_step("Fill Checkout Form", "🔄", "Filling customer information")
                
                form_fields = {
                    'email': checkout_data.get('customer_email', 'john.doe@example.com'),
                    'firstName': checkout_data.get('first_name', 'John'),
                    'lastName': checkout_data.get('last_name', 'Doe'),
                    'phone': checkout_data.get('customer_phone', '+1-555-0123'),
                    'address1': checkout_data.get('address', '123 Main Street'),
                    'city': checkout_data.get('city', 'New York'),
                    'state': checkout_data.get('state', 'NY'),
                    'zipCode': checkout_data.get('zip', '10001'),
                    'cardNumber': '4111111111111111',
                    'expiryDate': '12/25',
                    'cvv': '123',
                    'nameOnCard': checkout_data.get('customer_name', 'John Doe')
                }
                
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
                
                # STEP 6: Submit Order
                # Try direct API checkout first for better order number extraction
                # Note: This is a simplified implementation. In a full implementation, 
                # you would need to properly manage cart session IDs
                add_step("Submit Order", "🔄", "Attempting direct API checkout (simplified demo implementation)")
                
                # Extract session ID from cart URL
                # For demo purposes, we'll use a placeholder - in a real implementation, 
                # you would extract this from the cart page or previous API calls
                session_id = "demo-session-id"  # This would need to be properly extracted
                
                api_result = perform_api_checkout(session_id, checkout_data, headers)
                
                if api_result["success"]:
                    add_step("Submit Order", "✅", f"Order submitted via API. Order Number: {api_result['order_number']}")
                    order_submitted = True
                    
                    # Update results with API-extracted order number
                    _automation_results['order_info'] = {
                        'order_number': api_result['order_number'],
                        'success_url': page.url,
                        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                        'source': 'api_checkout'
                    }
                    
                    add_step("Order Confirmation", "✅", f"Order Number: {api_result['order_number']}")
                else:
                    # Fallback to UI automation if API checkout fails
                    add_step("Submit Order", "⚠️", "API checkout failed, falling back to UI automation. Error: " + str(api_result.get("error", "Unknown error")))
                    
                    submit_selectors = [
                        'button:has-text("Place Order")',
                        'button:has-text("Complete Order")',
                        'button:has-text("Submit Order")',
                        '[data-testid="place-order"]',
                        '[type="submit"]'
                    ]
                    
                    order_submitted = False
                    for selector in submit_selectors:
                        try:
                            button = page.query_selector(selector)
                            if button and button.is_visible():
                                button.click()
                                order_submitted = True
                                add_step("Submit Order", "✅", "Order submitted via UI")
                                time.sleep(5)  # Wait for order processing
                                break
                        except:
                            continue
                    
                    if order_submitted:
                        # STEP 7: Extract Order Confirmation
                        add_step("Order Confirmation", "🔄", "Extracting order details")
                        
                        # For React SPAs, order numbers are rendered dynamically
                        # Try to find order number in page content, but also note this may not work
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
                            'source': 'ui_automation'
                        }
                        
                        if order_number:
                            add_step("Order Confirmation", "✅", f"Order Number: {order_number}")
                        else:
                            # For React SPAs, we might not be able to extract order number from page content
                            # This is a known limitation when using browser automation with dynamic JavaScript frameworks
                            add_step("Order Confirmation", "⚠️", "Order placed but number not found in page content (expected limitation with React SPAs). For production use, consider direct API integration for reliable order number extraction.")
                    else:
                        add_step("Submit Order", "❌", "Could not submit order")
                
                # Wait a moment before closing
                time.sleep(3)
                
                _automation_results['status'] = 'completed'
                add_step("Shopping Flow Complete", "🎉", "All steps finished")
                
            except Exception as e:
                add_step("Error", "❌", str(e))
                _automation_results['status'] = 'error'
                _automation_results['error'] = str(e)
            
            finally:
                print("="*60)
                print("🔒 Closing browser...")
                browser.close()
                
    except ImportError:
        _automation_results = {
            'status': 'error',
            'error': 'Playwright not installed. Run: pip install playwright && playwright install'
        }
    except Exception as e:
        _automation_results = {
            'status': 'error',
            'error': str(e)
        }

def main():
    global _automation_results
    st.set_page_config(
        page_title="TAP Agent - Full Shopping Flow",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 TAP Agent - Automated Shopping Flow")
    st.markdown("Complete end-to-end shopping automation with RFC 9421 signatures")
    
    # Load keys
    try:
        rsa_private, rsa_public = get_rsa_keys_from_env()
        ed25519_private, ed25519_public = get_ed25519_keys_from_env()
        st.success("✅ RSA and Ed25519 keys loaded from environment")
    except ValueError as e:
        st.error(f"❌ {str(e)}")
        st.stop()
    
    # Configuration Section
    st.header("⚙️ Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Merchant Settings")
        product_url = st.text_input(
            "Product URL",
            value="http://localhost:3001/product/1",
            help="Starting point - the product page to purchase"
        )
        
        agent_id = st.text_input(
            "Agent ID",
            value="agent-shopping-bot-v1",
            help="Your agent identifier"
        )
    
    with col2:
        st.subheader("Signature Algorithm")
        algorithm = st.radio(
            "Select algorithm:",
            options=["ed25519", "rsa-pss-sha256"],
            index=0,
            help="Ed25519 is faster and more secure",
            horizontal=True
        )
        
        if algorithm == "ed25519":
            key_id = "primary-ed25519"
            st.info("🚀 Using Ed25519 - Fast and secure")
        else:
            key_id = "primary"
            st.info("🔒 Using RSA-PSS-SHA256 - Traditional")
    
    # Signature Parameters
    st.header("🔐 Signature Parameters")
    
    # Initialize session state
    if 'signature_params' not in st.session_state:
        st.session_state.signature_params = {
            "nonce": str(uuid.uuid4()),
            "created": int(time.time()),
            "expires": int(time.time()) + 900,
            "keyId": key_id,
            "tag": "agent-shopping-flow",
            "algorithm": algorithm
        }
    
    # Update keyId and algorithm if changed
    if st.session_state.signature_params['keyId'] != key_id:
        st.session_state.signature_params['keyId'] = key_id
    if st.session_state.signature_params['algorithm'] != algorithm:
        st.session_state.signature_params['algorithm'] = algorithm
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Signature Data (Editable JSON)")
        signature_json = st.text_area(
            "Edit signature parameters:",
            value=json.dumps(st.session_state.signature_params, indent=2),
            height=200,
            help="Modify nonce, timestamps, or other parameters"
        )
        
        try:
            st.session_state.signature_params = json.loads(signature_json)
        except json.JSONDecodeError:
            st.error("Invalid JSON format")
    
    with col2:
        st.subheader("Actions")
        
        if st.button("🔄 Reset to Defaults"):
            st.session_state.signature_params = {
                "nonce": str(uuid.uuid4()),
                "created": int(time.time()),
                "expires": int(time.time()) + 900,
                "keyId": key_id,
                "tag": "agent-shopping-flow",
                "algorithm": algorithm
            }
            st.rerun()
        
        st.markdown("---")
        
        # Show current values
        st.metric("Created", time.strftime("%H:%M:%S", time.localtime(st.session_state.signature_params['created'])))
        st.metric("Expires", time.strftime("%H:%M:%S", time.localtime(st.session_state.signature_params['expires'])))
    
    # Checkout Data
    st.header("📋 Checkout Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Customer Info")
        customer_name = st.text_input("Name", value="John Doe")
        customer_email = st.text_input("Email", value="john.doe@example.com")
        customer_phone = st.text_input("Phone", value="+1-555-0123")
    
    with col2:
        st.subheader("Shipping Address")
        address = st.text_input("Street", value="123 Main Street")
        city = st.text_input("City", value="New York")
        state = st.text_input("State", value="NY")
        zip_code = st.text_input("ZIP", value="10001")
    
    with col3:
        st.subheader("Payment Method")
        payment_type = st.radio(
            "Type:",
            options=["Credit Card", "x402 Token"],
            help="Choose payment method"
        )
        
        if payment_type == "x402 Token":
            delegation_token = st.text_input("Delegation Token", value="del_sample_token_123")
    
    checkout_data = {
        'customer_name': customer_name,
        'customer_email': customer_email,
        'customer_phone': customer_phone,
        'first_name': customer_name.split()[0] if customer_name else 'John',
        'last_name': customer_name.split()[-1] if customer_name else 'Doe',
        'address': address,
        'city': city,
        'state': state,
        'zip': zip_code,
        'payment_type': payment_type
    }
    
    if payment_type == "x402 Token":
        checkout_data['delegation_token'] = delegation_token
    
    # Launch Section
    st.header("🚀 Launch Automated Shopping Flow")
    
    st.info("""
    **This will automate the complete shopping process:**
    1. 🛍️ View Product - Navigate and extract product details
    2. 🛒 Add to Cart - Click "Add to Cart" button
    3. 📦 View Cart - Navigate to cart page
    4. ➡️ Proceed to Checkout - Navigate to checkout
    5. 📝 Fill Form - Auto-fill customer and payment info
    6. ✅ Submit Order - Complete the purchase
    7. 🎉 Confirmation - Extract order number
    """)
    
    if st.button("🤖 Start Automated Shopping", type="primary", use_container_width=True):
        with st.spinner("🔐 Generating signature and launching browser..."):
            # Parse URL for signature
            authority, path = parse_url_components(product_url)
            
            if not authority or not path:
                st.error("❌ Failed to parse product URL")
                st.stop()
            
            # Get signature parameters
            params = st.session_state.signature_params
            
            # Generate signature
            if algorithm == "ed25519":
                sig_input, sig_header = create_ed25519_signature(
                    private_key_b64=ed25519_private,
                    authority=authority,
                    path=path,
                    keyid=params['keyId'],
                    nonce=params['nonce'],
                    created=params['created'],
                    expires=params['expires'],
                    tag=params['tag']
                )
            else:
                sig_input, sig_header = create_rsa_signature(
                    private_key_pem=rsa_private,
                    authority=authority,
                    path=path,
                    keyid=params['keyId'],
                    nonce=params['nonce'],
                    created=params['created'],
                    expires=params['expires'],
                    tag=params['tag']
                )
            
            if not sig_input or not sig_header:
                st.error("❌ Failed to generate signature")
                st.stop()
            
            # Create headers
            headers = {
                'Signature-Input': sig_input,
                'Signature': sig_header
            }
            
            st.success("✅ Signature generated successfully")
            
            # Launch browser automation in background thread
            automation_thread = threading.Thread(
                target=run_full_shopping_flow,
                args=(product_url, headers, checkout_data),
                daemon=True
            )
            automation_thread.start()
            
            st.success("🚀 Browser launched! Check the browser window for automation progress.")
            st.info("💡 Check the terminal/console for detailed logs.")
            
            # Wait a moment for results to start populating
            time.sleep(2)
            st.rerun()
    
    # Results Section
    if _automation_results and _automation_results.get('status'):
        st.header("📊 Automation Results")
        
        status = _automation_results['status']
        
        if status == 'running':
            st.info("🔄 Automation in progress...")
        elif status == 'completed':
            st.success("✅ Automation completed successfully!")
        elif status == 'error':
            st.error(f"❌ Automation failed: {_automation_results.get('error', 'Unknown error')}")
        
        # Show steps
        if _automation_results.get('steps'):
            st.subheader("🔄 Execution Steps")
            
            for step in _automation_results['steps']:
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.write(step['status'])
                with col2:
                    st.write(f"**{step['name']}**")
                    if step.get('details'):
                        st.caption(step['details'])
                with col3:
                    st.caption(step['timestamp'])
        
        # Show extracted data
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if _automation_results.get('product_info'):
                st.subheader("📦 Product Info")
                product = _automation_results['product_info']
                if product.get('title'):
                    st.write(f"**Title:** {product['title']}")
                if product.get('price'):
                    st.write(f"**Price:** {product['price']}")
        
        with col2:
            if _automation_results.get('cart_info'):
                st.subheader("🛒 Cart Info")
                cart = _automation_results['cart_info']
                st.metric("Items in Cart", cart.get('item_count', 0))
        
        with col3:
            if _automation_results.get('order_info'):
                st.subheader("✅ Order Info")
                order = _automation_results['order_info']
                if order.get('order_number'):
                    st.metric("Order Number", order['order_number'])
                if order.get('timestamp'):
                    st.caption(f"Completed: {order['timestamp']}")
        
        # Full results in expander
        with st.expander("🔍 Full Automation Results (JSON)"):
            st.json(_automation_results)
        
        # Clear button
        if st.button("🗑️ Clear Results"):
            _automation_results = {}
            st.rerun()

if __name__ == "__main__":
    main()
