#!/usr/bin/env python3
"""
Test script to verify Playwright is installed and working
"""

print("🔍 Testing Playwright installation...")
print("="*60)

try:
    print("📦 Importing Playwright...")
    from playwright.sync_api import sync_playwright
    print("✅ Playwright imported successfully!")
    
    print("\n🌐 Launching browser...")
    with sync_playwright() as p:
        print("🔧 Configuring Chromium (headless=False)...")
        browser = p.chromium.launch(headless=False)
        print("✅ Browser launched!")
        
        print("📄 Creating new page...")
        page = browser.new_page()
        print("✅ Page created!")
        
        print("\n🔗 Navigating to example.com...")
        page.goto("https://example.com")
        print("✅ Page loaded!")
        
        print(f"📋 Page title: {page.title()}")
        
        print("\n⏳ Waiting 3 seconds...")
        import time
        time.sleep(3)
        
        print("🔒 Closing browser...")
        browser.close()
        print("✅ Browser closed!")
    
    print("\n" + "="*60)
    print("🎉 SUCCESS! Playwright is working correctly!")
    print("="*60)
    
except ImportError as e:
    print(f"\n❌ ERROR: Playwright not installed")
    print(f"Details: {e}")
    print("\n💡 To install, run:")
    print("   pip install playwright")
    print("   playwright install chromium")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"Exception type: {type(e).__name__}")
    import traceback
    print("\nFull traceback:")
    print(traceback.format_exc())
    print("\n💡 Try running:")
    print("   playwright install chromium")
