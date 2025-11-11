/* © 2025 Visa.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

import React, { useState, useEffect } from 'react';
import ProductCard from '../components/ProductCard';
import SearchFilters from '../components/SearchFilters';
import { productsAPI } from '../services/api';

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);
  const [currentFilters, setCurrentFilters] = useState({});

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async (filters = {}) => {
    setLoading(true);
    setError(null);
    try {
      const response = await productsAPI.searchProducts(filters);
      setProducts(response.data.products);
      setTotal(response.data.total);
    } catch (err) {
      setError('Failed to load products. Please try again.');
      console.error('Error loading products:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query) => {
    const filters = { ...currentFilters, query };
    setCurrentFilters(filters);
    loadProducts(filters);
  };

  const handleFilter = (filterData) => {
    const filters = { ...currentFilters, ...filterData };
    setCurrentFilters(filters);
    loadProducts(filters);
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading products...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>
          {error}
          <button onClick={() => loadProducts()} style={styles.retryButton}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.hero}>
        <div style={styles.heroBackground}></div>
        <div style={styles.heroEmojis}>
          <span style={styles.heroEmoji}>🍌</span>
          <span style={{...styles.heroEmoji, top: '20%', left: '15%', animationDelay: '0.5s'}}>🌸</span>
          <span style={{...styles.heroEmoji, top: '70%', left: '10%', animationDelay: '1s'}}>🍌</span>
          <span style={{...styles.heroEmoji, top: '30%', right: '10%', animationDelay: '1.5s'}}>🌸</span>
          <span style={{...styles.heroEmoji, top: '80%', right: '15%', animationDelay: '2s'}}>🍌</span>
          <span style={{...styles.heroEmoji, top: '50%', left: '5%', animationDelay: '2.5s'}}>🌸</span>
          <span style={{...styles.heroEmoji, top: '60%', right: '5%', animationDelay: '3s'}}>🐵</span>
        </div>
        <div style={styles.heroContent}>
          <h1 style={styles.title}>🍌 🎨 🐵 Shanni x MonkeDAO 🌸</h1>
          <p style={styles.subtitle}>🌸 Discover unique illustrations and art pieces 🍌</p>
          <div style={styles.paymentOptions}>
            <span style={styles.paymentBadge}>💳 Visa Card</span>
            <span style={styles.paymentBadge}>🔗 USDC Onchain</span>
          </div>
        </div>
      </div>
      
      <SearchFilters onSearch={handleSearch} onFilter={handleFilter} />
      
      <div style={styles.resultsInfo}>
        Showing {products.length} of {total} products
      </div>

      {products.length === 0 ? (
        <div style={styles.noProducts}>
          No products found. Try adjusting your search or filters.
        </div>
      ) : (
        <div style={styles.productsGrid}>
          {products.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '2rem 1rem',
  },
  hero: {
    position: 'relative',
    textAlign: 'center',
    padding: '4rem 2rem',
    marginBottom: '3rem',
    overflow: 'hidden',
    borderRadius: '30px',
    background: 'linear-gradient(135deg, #FF69B4 0%, #FFB6C1 30%, #86C994 70%, #4A8F5D 100%)',
    boxShadow: '0 20px 60px rgba(24,70,35,0.3), inset 0 -5px 20px rgba(0,0,0,0.1)',
  },
  heroBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.05) 10px, rgba(255,255,255,0.05) 20px)',
    pointerEvents: 'none',
  },
  heroEmojis: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    pointerEvents: 'none',
  },
  heroEmoji: {
    position: 'absolute',
    fontSize: '3rem',
    opacity: 0.3,
    animation: 'bounce 2s ease-in-out infinite',
    top: '10%',
    left: '20%',
  },
  heroContent: {
    position: 'relative',
    zIndex: 1,
  },
  title: {
    fontSize: '3.5rem',
    marginBottom: '1rem',
    color: 'white',
    fontFamily: '"Space Grotesk", -apple-system, sans-serif',
    fontWeight: '900',
    textShadow: '4px 4px 0px rgba(24,70,35,0.3), 8px 8px 0px rgba(0,0,0,0.1)',
    letterSpacing: '-1px',
    transform: 'rotate(-1deg)',
    lineHeight: '1.1',
  },
  subtitle: {
    fontSize: '1.5rem',
    color: 'white',
    marginBottom: '2rem',
    fontWeight: '600',
    textShadow: '2px 2px 4px rgba(0,0,0,0.2)',
  },
  paymentOptions: {
    display: 'flex',
    justifyContent: 'center',
    gap: '1.5rem',
    flexWrap: 'wrap',
  },
  paymentBadge: {
    background: 'white',
    color: '#184623',
    padding: '0.8rem 1.8rem',
    borderRadius: '50px',
    fontSize: '1rem',
    fontWeight: '800',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.5rem',
    boxShadow: '0 8px 20px rgba(0,0,0,0.2), inset 0 -3px 0 rgba(0,0,0,0.1)',
    transform: 'rotate(2deg)',
    transition: 'all 0.3s',
  },
  loading: {
    textAlign: 'center',
    fontSize: '1.5rem',
    color: '#4A8F5D',
    padding: '4rem',
    fontWeight: '700',
  },
  error: {
    textAlign: 'center',
    color: 'white',
    padding: '3rem',
    background: 'linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%)',
    borderRadius: '30px',
    boxShadow: '0 10px 30px rgba(255,107,107,0.3)',
  },
  retryButton: {
    marginTop: '1.5rem',
    background: 'white',
    color: '#FF6B6B',
    border: 'none',
    padding: '1rem 2rem',
    borderRadius: '50px',
    cursor: 'pointer',
    fontWeight: '800',
    fontSize: '1rem',
    transition: 'all 0.3s',
    boxShadow: '0 6px 20px rgba(0,0,0,0.2)',
  },
  resultsInfo: {
    marginBottom: '1.5rem',
    color: '#184623',
    fontSize: '1rem',
    fontWeight: '700',
  },
  noProducts: {
    textAlign: 'center',
    color: 'white',
    padding: '4rem',
    fontSize: '1.3rem',
    background: 'linear-gradient(135deg, #FFB6C1 0%, #FF69B4 100%)',
    borderRadius: '30px',
    fontWeight: '700',
    boxShadow: '0 10px 30px rgba(255,105,180,0.3)',
  },
  productsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '2rem',
    marginTop: '2rem',
    padding: '1rem 0',
  },
};

export default ProductsPage;
