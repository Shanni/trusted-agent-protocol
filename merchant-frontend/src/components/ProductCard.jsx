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
          <span style={styles.price}>🍌 ${product.price.toFixed(2)}</span>
          <button 
            onClick={handleAddToCart}
            disabled={product.stock_quantity === 0}
            style={styles.addButton}
          >
            {product.stock_quantity === 0 ? '😢 Out of Stock' : '🌸 Add to Cart'}
          </button>
        </div>
      </div>
    </div>
  );
};

const styles = {
  card: {
    borderRadius: '30px',
    overflow: 'hidden',
    background: 'white',
    boxShadow: '0 10px 30px rgba(0,0,0,0.15), 0 0 0 3px rgba(255,105,180,0.2)',
    transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    cursor: 'pointer',
    position: 'relative',
  },
  cardHovered: {
    transform: 'translateY(-12px) rotate(1deg)',
    boxShadow: '0 20px 50px rgba(0,0,0,0.25), 0 0 0 5px rgba(74,143,93,0.3)',
  },
  image: {
    width: '100%',
    height: '250px',
    objectFit: 'cover',
    transition: 'transform 0.4s',
  },
  content: {
    padding: '1.8rem',
    background: 'linear-gradient(180deg, #FFF 0%, #FFF0F5 100%)',
  },
  name: {
    margin: '0 0 0.8rem 0',
    fontSize: '1.4rem',
    fontWeight: '900',
    color: '#184623',
    fontFamily: '"Space Grotesk", -apple-system, sans-serif',
    lineHeight: '1.2',
  },
  description: {
    margin: '0 0 1.2rem 0',
    color: '#666',
    fontSize: '0.95rem',
    lineHeight: '1.6',
  },
  details: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1.2rem',
  },
  category: {
    background: 'linear-gradient(135deg, #4A8F5D 0%, #86C994 100%)',
    padding: '0.5rem 1rem',
    borderRadius: '50px',
    color: 'white',
    fontWeight: '800',
    fontSize: '0.75rem',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    boxShadow: '0 4px 12px rgba(74,143,93,0.3)',
  },
  stock: {
    color: '#184623',
    fontWeight: '700',
    fontSize: '0.9rem',
  },
  footer: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '1rem',
  },
  price: {
    fontSize: '2rem',
    fontWeight: '900',
    color: '#FF69B4',
    fontFamily: '"Space Grotesk", -apple-system, sans-serif',
    textShadow: '2px 2px 0px rgba(255,105,180,0.2)',
  },
  addButton: {
    background: 'linear-gradient(135deg, #FF69B4 0%, #FFB6C1 100%)',
    color: 'white',
    border: 'none',
    padding: '0.8rem 1.5rem',
    borderRadius: '50px',
    cursor: 'pointer',
    fontSize: '0.95rem',
    fontWeight: '800',
    transition: 'all 0.3s',
    boxShadow: '0 6px 20px rgba(255,105,180,0.4), inset 0 -3px 0 rgba(0,0,0,0.1)',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    ':hover': {
      background: 'linear-gradient(135deg, #4A8F5D 0%, #86C994 100%)',
      transform: 'scale(1.08) rotate(-2deg)',
      boxShadow: '0 8px 25px rgba(74,143,93,0.5)',
    },
  },
};

export default ProductCard;
