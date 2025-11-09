/* © 2025 Visa.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';

const ProductCard = ({ product }) => {
  const { addToCart } = useCart();
  const navigate = useNavigate();
  const [isHovered, setIsHovered] = useState(false);

  const handleAddToCart = (e) => {
    e.stopPropagation(); // Prevent card click navigation
    addToCart(product.id, 1);
  };

  const handleCardClick = () => {
    navigate(`/product/${product.id}`);
  };

  return (
    <div 
      style={{
        ...styles.card,
        ...(isHovered ? styles.cardHovered : {})
      }}
      onClick={handleCardClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <img 
        src={product.image_url || '/placeholder/300/200'} 
        alt={product.name}
        style={styles.image}
        onError={(e) => {
          e.target.src = '/placeholder/300/200';
        }}
      />
      <div style={styles.content}>
        <h3 style={styles.name}>{product.name}</h3>
        <p style={styles.description}>{product.description}</p>
        <div style={styles.details}>
          <span style={styles.category}>{product.category}</span>
          <span style={styles.stock}>Stock: {product.stock_quantity}</span>
        </div>
        <div style={styles.footer}>
          <span style={styles.price}>${product.price.toFixed(2)}</span>
          <button 
            style={styles.addButton}
            onClick={handleAddToCart}
            disabled={product.stock_quantity === 0}
          >
            {product.stock_quantity === 0 ? 'Out of Stock' : 'Add to Cart'}
          </button>
        </div>
      </div>
    </div>
  );
};

const styles = {
  card: {
    border: '3px solid #D2691E',
    borderRadius: '20px',
    overflow: 'hidden',
    backgroundColor: '#FFF5EE',
    boxShadow: '0 4px 8px rgba(160,82,45,0.2)',
    transition: 'transform 0.3s, box-shadow 0.3s, border-color 0.3s',
    cursor: 'pointer',
  },
  cardHovered: {
    transform: 'translateY(-5px)',
    boxShadow: '0 8px 16px rgba(160,82,45,0.3)',
    borderColor: '#A0522D',
  },
  image: {
    width: '100%',
    height: '250px',
    objectFit: 'cover',
    borderBottom: '3px solid #D2691E',
  },
  content: {
    padding: '1.5rem',
    background: 'linear-gradient(to bottom, #FFF5EE 0%, #FFE4E1 100%)',
  },
  name: {
    margin: '0 0 0.5rem 0',
    fontSize: '1.2rem',
    fontWeight: 'bold',
    color: '#A0522D',
    fontFamily: 'Georgia, serif',
  },
  description: {
    margin: '0 0 1rem 0',
    color: '#8B4513',
    fontSize: '0.9rem',
    lineHeight: '1.5',
  },
  details: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '1rem',
    fontSize: '0.8rem',
  },
  category: {
    backgroundColor: '#D2691E',
    padding: '0.4rem 0.8rem',
    borderRadius: '15px',
    color: '#FFF5EE',
    fontWeight: '600',
    fontSize: '0.75rem',
  },
  stock: {
    color: '#A0522D',
    fontWeight: '500',
  },
  footer: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  price: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#A0522D',
    fontFamily: 'Georgia, serif',
  },
  addButton: {
    backgroundColor: '#A0522D',
    color: '#FFF5EE',
    border: '2px solid #D2691E',
    padding: '0.6rem 1.2rem',
    borderRadius: '20px',
    cursor: 'pointer',
    fontSize: '0.9rem',
    fontWeight: 'bold',
    transition: 'all 0.3s',
    ':hover': {
      backgroundColor: '#8B4513',
      transform: 'scale(1.05)',
    },
  },
};

export default ProductCard;
