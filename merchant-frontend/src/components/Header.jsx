/* © 2025 Visa.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';

const Header = () => {
  const { getCartItemCount } = useCart();

  return (
    <header style={styles.header}>
      <div style={styles.container}>
        <Link to="/" style={styles.logo}>
          🎨 TAP Shanni Art
        </Link>
        
        <nav style={styles.nav}>
          <Link to="/" style={styles.navLink}>Products</Link>
          <Link to="/orders" style={styles.navLink}>Orders</Link>
          <Link to="/signature-demo" style={styles.navLink}>Demo</Link>
          <Link to="/cart" style={styles.cartLink}>
            Cart ({getCartItemCount()})
          </Link>
        </nav>
      </div>
    </header>
  );
};

const styles = {
  header: {
    backgroundColor: '#A0522D',
    color: '#FFF5EE',
    padding: '1rem 0',
    boxShadow: '0 2px 4px rgba(160,82,45,0.3)',
    borderBottom: '3px solid #D2691E',
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 1rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#FFF5EE',
    textDecoration: 'none',
    fontFamily: 'Georgia, serif',
    letterSpacing: '0.5px',
  },
  nav: {
    display: 'flex',
    gap: '2rem',
    alignItems: 'center',
  },
  navLink: {
    color: '#FFF5EE',
    textDecoration: 'none',
    padding: '0.5rem 1rem',
    borderRadius: '20px',
    transition: 'all 0.3s',
    ':hover': {
      backgroundColor: '#8B4513',
    },
  },
  cartLink: {
    color: '#8B4513',
    textDecoration: 'none',
    padding: '0.5rem 1.5rem',
    backgroundColor: '#FFE4E1',
    borderRadius: '20px',
    fontWeight: 'bold',
    border: '2px solid #D2691E',
    transition: 'all 0.3s',
  },
};

export default Header;
