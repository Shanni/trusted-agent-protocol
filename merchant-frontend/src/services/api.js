/* © 2025 Shanni.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

import axios from 'axios';

// Use relative URL in development (proxy) or environment variable for production
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? '' : 'http://localhost:8000')

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Add request interceptor for debugging
api.interceptors.request.use(request => {
  console.log('🔵 API Request:', request.method?.toUpperCase(), request.url, request.data);
  return request;
});

// Add response interceptor for debugging
api.interceptors.response.use(
  response => {
    console.log('🟢 API Response:', response.status, response.config.url, response.data);
    return response;
  },
  error => {
    console.error('🔴 API Error:', error.response?.status, error.config?.url, error.message);
    return Promise.reject(error);
  }
);

// Products API
export const productsAPI = {
  searchProducts: (params = {}) => {
    const searchParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
        searchParams.append(key, params[key]);
      }
    });
    return api.get(`/api/products/?${searchParams.toString()}`);
  },
  
  getProduct: (id) => api.get(`/api/products/${id}`),
  
  createProduct: (productData) => api.post('/api/products/', productData),
};

// Cart API
export const cartAPI = {
  createCart: () => api.post('/api/cart/'),
  
  getCart: (sessionId) => api.get(`/api/cart/${sessionId}`),
  
  addItemToCart: (sessionId, item) => 
    api.post(`/api/cart/${sessionId}/items`, item),
  
  updateCartItem: (sessionId, productId, quantity) =>
    api.put(`/api/cart/${sessionId}/items/${productId}`, { quantity }),
  
  removeItemFromCart: (sessionId, productId) =>
    api.delete(`/api/cart/${sessionId}/items/${productId}`),
  
  clearCart: (sessionId) => api.delete(`/api/cart/${sessionId}`),
};

// Orders API
export const ordersAPI = {
  checkout: (sessionId, checkoutData) => api.post(`/api/cart/${sessionId}/checkout`, checkoutData),
  
  getOrders: (params = {}) => {
    const searchParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
        searchParams.append(key, params[key]);
      }
    });
    return api.get(`/api/orders/?${searchParams.toString()}`);
  },
  
  getOrder: (id) => api.get(`/api/orders/${id}`),
  
  getOrderByNumber: (orderNumber) => api.get(`/api/orders/number/${orderNumber}`),
  
  updateOrderStatus: (id, status) => 
    api.put(`/api/orders/${id}/status?status=${status}`),
  
  cancelOrder: (id) => api.delete(`/api/orders/${id}`),
};

// Solana Checkout API
export const solanaAPI = {
  requestQuote: (sessionId, payload) => api.post(`/api/cart/${sessionId}/solana/quote`, payload),
  confirmPayment: (sessionId, payload) => api.post(`/api/cart/${sessionId}/solana/confirm`, payload),
};

// Project Sienna Onchain Payment API
export const siennaPaymentAPI = {
  // Execute complete payment flow via backend
  requestPaymentQuote: async (amount, orderData = null, network = 'devnet') => {
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      console.log('💰 Executing Sienna payment via backend...');
      console.log(`   Amount: ${amount} USDC`);
      console.log(`   Network: ${network}`);
      
      const response = await fetch(`${apiBase}/api/payment/sienna/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: amount,
          orderData: orderData,
          network: network
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Payment failed with status ${response.status}`);
      }

      const result = await response.json();
      
      console.log('✅ Payment completed successfully');
      console.log('   Signature:', result.signature);

      return {
        success: result.success,
        signature: result.signature,
        explorerUrl: result.explorerUrl,
        amountReceived: result.amountReceived,
        paymentDetails: result.paymentDetails,
        error: result.error
      };

    } catch (error) {
      console.error('❌ Payment error:', error);
      throw error;
    }
  },

  // Get payment quote only (for display purposes)
  getPaymentQuote: async (amount) => {
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiBase}/api/payment/sienna/quote?amount=${amount}`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`Failed to get quote: ${response.status}`);
      }

      return await response.json();
      
    } catch (error) {
      console.error('Failed to get payment quote:', error);
      throw error;
    }
  },
};

// Individual exports for convenience
export const getProduct = (id) => productsAPI.getProduct(id).then(response => response.data);

export default api;
