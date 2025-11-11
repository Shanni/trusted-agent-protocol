/* © 2025 Visa.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastProvider } from './context/ToastContext';
import { CartProvider } from './context/CartContext';
import Header from './components/Header';
import ProductsPage from './pages/ProductsPage';
import ProductDetailsPage from './pages/ProductDetailsPage';
import CartPage from './pages/CartPage';
import CheckoutPage from './pages/CheckoutPage';
import OrderSuccessPage from './pages/OrderSuccessPage';
import OrdersPage, { OrderDetailPage } from './pages/OrdersPage';


function App() {
  return (
    <ToastProvider>
      <CartProvider>
        <Router>
          <div style={styles.app}>
            <Header />
            <main style={styles.main}>
              <Routes>
                <Route path="/" element={<ProductsPage />} />
                <Route path="/product/:id" element={<ProductDetailsPage />} />
                <Route path="/cart" element={<CartPage />} />
                <Route path="/checkout" element={<CheckoutPage />} />
                <Route path="/order-success" element={<OrderSuccessPage />} />
                <Route path="/orders" element={<OrdersPage />} />
                <Route path="/order/:orderNumber" element={<OrderDetailPage />} />

              </Routes>
            </main>
            <footer style={styles.footer}>
              <div style={styles.footerContent}>
                <p style={styles.footerText}>🎨 Shanni Art</p>
                <p style={styles.footerSubtext}>Unique illustrations & art pieces by <a href="https://www.instagram.com/shanni_daily_drawing/" target="_blank" rel="noopener noreferrer" style={styles.footerLink}>@shanni_daily_drawing</a></p>
                <p style={styles.footerCopy}>&copy; 2025 Shanni. All rights reserved.</p>
              </div>
            </footer>
          </div>
        </Router>
      </CartProvider>
    </ToastProvider>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    background: 'linear-gradient(180deg, #FFF0F5 0%, #FFE4E8 50%, #F0F8F0 100%)',
    display: 'flex',
    flexDirection: 'column',
  },
  main: {
    flex: 1,
  },
  footer: {
    background: 'linear-gradient(135deg, #184623 0%, #2d5a3d 50%, #4A8F5D 100%)',
    color: 'white',
    padding: '3rem 0',
    marginTop: '4rem',
    position: 'relative',
    overflow: 'hidden',
  },
  footerContent: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 1rem',
    textAlign: 'center',
  },
  footerText: {
    fontSize: '2rem',
    fontWeight: '900',
    marginBottom: '0.5rem',
    fontFamily: '"Space Grotesk", -apple-system, sans-serif',
    textShadow: '2px 2px 0px rgba(255,182,193,0.5)',
  },
  footerSubtext: {
    fontSize: '1.1rem',
    marginBottom: '1rem',
    color: 'rgba(255,255,255,0.9)',
  },
  footerLink: {
    color: '#FFB6C1',
    textDecoration: 'none',
    fontWeight: 'bold',
    borderBottom: '2px solid #FFB6C1',
    transition: 'all 0.3s',
  },
  footerCopy: {
    fontSize: '0.9rem',
    opacity: 0.9,
  },
};

export default App;
