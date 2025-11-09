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
        <h1 style={styles.title}>🎨 Shanni Art Gallery</h1>
        <p style={styles.subtitle}>Discover unique illustrations and art pieces</p>
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
    textAlign: 'center',
    padding: '3rem 1rem',
    background: 'linear-gradient(135deg, #FFE4E1 0%, #FFF5EE 100%)',
    borderRadius: '20px',
    marginBottom: '2rem',
    border: '3px solid #D2691E',
  },
  title: {
    fontSize: '2.5rem',
    marginBottom: '0.5rem',
    color: '#A0522D',
    fontFamily: 'Georgia, serif',
    fontWeight: 'bold',
  },
  subtitle: {
    fontSize: '1.2rem',
    color: '#8B4513',
    fontStyle: 'italic',
  },
  loading: {
    textAlign: 'center',
    fontSize: '1.2rem',
    color: '#A0522D',
    padding: '3rem',
  },
  error: {
    textAlign: 'center',
    color: '#8B4513',
    padding: '2rem',
    backgroundColor: '#FFE4E1',
    borderRadius: '20px',
    border: '2px solid #D2691E',
  },
  retryButton: {
    marginTop: '1rem',
    backgroundColor: '#A0522D',
    color: '#FFF5EE',
    border: '2px solid #D2691E',
    padding: '0.75rem 1.5rem',
    borderRadius: '20px',
    cursor: 'pointer',
    fontWeight: 'bold',
    transition: 'all 0.3s',
  },
  resultsInfo: {
    marginBottom: '1rem',
    color: '#8B4513',
    fontSize: '0.9rem',
    fontWeight: '500',
  },
  noProducts: {
    textAlign: 'center',
    color: '#A0522D',
    padding: '3rem',
    fontSize: '1.1rem',
    backgroundColor: '#FFE4E1',
    borderRadius: '20px',
    border: '2px solid #D2691E',
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
