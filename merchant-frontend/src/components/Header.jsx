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
          🎨 🐵 Shanni x MonkeDAO
        </Link>
        
        <nav style={styles.nav}>
          <Link to="/" style={styles.navLink}>Products</Link>
          <Link to="/orders" style={styles.navLink}>Orders</Link>
          <Link to="/cart" style={styles.cartLink}>
            🛒 Cart ({getCartItemCount()})
          </Link>
        </nav>
      </div>
    </header>
  );
};

const styles = {
  header: {
    background: 'linear-gradient(135deg, #184623 0%, #4A8F5D 100%)',
    color: 'white',
    padding: '1.5rem 0',
    boxShadow: '0 8px 32px rgba(24,70,35,0.4)',
    position: 'sticky',
    top: 0,
    zIndex: 1000,
    backdropFilter: 'blur(10px)',
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
    fontSize: '1.8rem',
    fontWeight: '900',
    color: 'white',
    textDecoration: 'none',
    fontFamily: '"Space Grotesk", -apple-system, sans-serif',
    letterSpacing: '-0.5px',
    textShadow: '3px 3px 0px rgba(255,182,193,0.5), 6px 6px 0px rgba(134,201,148,0.3)',
    transition: 'all 0.3s ease',
  },
  nav: {
    display: 'flex',
    gap: '2rem',
    alignItems: 'center',
  },
  navLink: {
    color: 'white',
    textDecoration: 'none',
    padding: '0.6rem 1.2rem',
    borderRadius: '12px',
    transition: 'all 0.3s',
    fontWeight: '600',
    fontSize: '1rem',
    position: 'relative',
    ':hover': {
      backgroundColor: 'rgba(255,255,255,0.15)',
      transform: 'translateY(-2px)',
    },
  },
  cartLink: {
    color: 'white',
    textDecoration: 'none',
    padding: '0.7rem 1.8rem',
    background: 'linear-gradient(135deg, #FF69B4 0%, #FFB6C1 100%)',
    borderRadius: '30px',
    fontWeight: '800',
    fontSize: '1.1rem',
    transition: 'all 0.3s',
    boxShadow: '0 4px 15px rgba(255,105,180,0.4), inset 0 -2px 0 rgba(0,0,0,0.1)',
    transform: 'rotate(-2deg)',
    ':hover': {
      transform: 'rotate(0deg) scale(1.05)',
      boxShadow: '0 6px 20px rgba(255,105,180,0.6)',
    },
  },
};

export default Header;
