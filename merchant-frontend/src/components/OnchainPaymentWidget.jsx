/* © 2025 Shanni.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

import React, { useState } from 'react';
import { siennaPaymentAPI } from '../services/api';

const OnchainPaymentWidget = ({ amount, orderData, onPaymentComplete, onError, network = 'devnet' }) => {
  const [processing, setProcessing] = useState(false);
  const [paymentDetails, setPaymentDetails] = useState(null);
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  // Handle onchain payment - automated flow
  const handleOnchainPayment = async () => {
    setProcessing(true);
    setPaymentDetails(null);
    setPaymentSuccess(false);
    
    try {
      console.log('💰 Initiating Sienna payment...');
      console.log('   Amount:', amount, 'USDC');
      console.log('   Network:', network);
      
      // The complete payment flow is now handled in the API
      // This includes: quote request, transaction creation, signing, and submission
      const result = await siennaPaymentAPI.requestPaymentQuote(amount, orderData, network);

      if (result.error) {
        throw new Error(result.error);
      }

      console.log('✅ Payment successful!');
      console.log('   Signature:', result.signature);
      console.log('   Explorer URL:', result.explorerUrl);

      // Store payment details to display
      setPaymentDetails({
        signature: result.signature,
        explorerUrl: result.explorerUrl,
        amountReceived: result.amountReceived,
        paymentDetails: result.paymentDetails,
      });
      setPaymentSuccess(true);

      // Payment successful - call the callback after a brief delay to show the details
      setTimeout(() => {
        onPaymentComplete({
          signature: result.signature,
          explorerUrl: result.explorerUrl,
          amountReceived: result.amountReceived,
          paymentMethod: 'onchain',
          paymentDetails: result.paymentDetails,
        });
      }, 2000);

    } catch (err) {
      console.error('❌ Payment failed:', err);
      onError('Onchain payment failed: ' + err.message);
      setProcessing(false);
    }
  };

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>Onchain Payment (USDC on Solana)</h3>
      
      <div style={styles.paymentSection}>
        {!paymentSuccess ? (
          <>
            <div style={styles.paymentInfo}>
              <div style={styles.infoRow}>
                <span style={styles.label}>Amount:</span>
                <span style={styles.value}>{amount} USDC</span>
              </div>
              <div style={styles.infoRow}>
                <span style={styles.label}>Network:</span>
                <span style={styles.value}>Solana {network === 'mainnet' ? 'Mainnet' : 'Devnet'}</span>
              </div>
              <div style={styles.infoRow}>
                <span style={styles.label}>Protocol:</span>
                <span style={styles.value}>x402 by Shanni</span>
              </div>
            </div>

            <button
              onClick={handleOnchainPayment}
              disabled={processing}
              style={{
                ...styles.payButton,
                ...(processing ? styles.payButtonDisabled : {}),
              }}
            >
              {processing ? '⏳ Processing Payment...' : `💳 Pay ${amount} USDC with Onchain`}
            </button>

            <p style={styles.helperText}>
              Automated onchain payment using USDC on Solana via x402 protocol
            </p>
          </>
        ) : (
          <div style={styles.successSection}>
            <div style={styles.successIcon}>✅</div>
            <h4 style={styles.successTitle}>Payment Successful!</h4>
            
            <div style={styles.transactionDetails}>
              <div style={styles.detailRow}>
                <span style={styles.detailLabel}>Amount Paid:</span>
                <span style={styles.detailValue}>{paymentDetails.amountReceived} USDC</span>
              </div>
              
              <div style={styles.detailRow}>
                <span style={styles.detailLabel}>Transaction Signature:</span>
                <div style={styles.signatureContainer}>
                  <code style={styles.signature}>
                    {paymentDetails.signature.slice(0, 8)}...{paymentDetails.signature.slice(-8)}
                  </code>
                  {paymentDetails.explorerUrl && (
                    <a 
                      href={paymentDetails.explorerUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={styles.explorerLink}
                    >
                      View on Explorer ↗
                    </a>
                  )}
                </div>
              </div>
              
              <div style={styles.detailRow}>
                <span style={styles.detailLabel}>Network:</span>
                <span style={styles.detailValue}>Solana {network === 'mainnet' ? 'Mainnet' : 'Devnet'}</span>
              </div>
            </div>
            
            <p style={styles.processingText}>
              🎉 Completing your order...
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: '1.5rem',
    backgroundColor: '#FAFAFA',
    borderRadius: '12px',
    border: '1px solid #E8E8E8',
    marginTop: '1rem',
  },
  title: {
    fontSize: '1.1rem',
    color: '#2C3E50',
    marginBottom: '1rem',
    fontWeight: 'bold',
  },
  paymentSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  paymentInfo: {
    backgroundColor: 'white',
    padding: '1rem',
    borderRadius: '8px',
    border: '1px solid #E0E0E0',
  },
  infoRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '0.75rem',
    fontSize: '0.95rem',
  },
  label: {
    color: '#666',
    fontWeight: '500',
  },
  value: {
    color: '#2C3E50',
    fontWeight: '600',
  },
  payButton: {
    background: 'linear-gradient(135deg, #3498db 0%, #5DADE2 100%)',
    color: 'white',
    border: 'none',
    padding: '0.875rem 1.5rem',
    borderRadius: '10px',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: 'bold',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 12px rgba(52, 152, 219, 0.3)',
  },
  payButtonDisabled: {
    backgroundColor: '#95a5a6',
    cursor: 'not-allowed',
  },
  helperText: {
    fontSize: '0.85rem',
    color: '#666',
    textAlign: 'center',
    margin: '0.5rem 0 0 0',
  },
  successSection: {
    textAlign: 'center',
    padding: '1rem',
  },
  successIcon: {
    fontSize: '3rem',
    marginBottom: '1rem',
  },
  successTitle: {
    fontSize: '1.3rem',
    color: '#27ae60',
    marginBottom: '1.5rem',
    fontWeight: 'bold',
  },
  transactionDetails: {
    backgroundColor: 'white',
    padding: '1.25rem',
    borderRadius: '8px',
    border: '1px solid #E0E0E0',
    marginBottom: '1rem',
    textAlign: 'left',
  },
  detailRow: {
    marginBottom: '1rem',
  },
  detailLabel: {
    display: 'block',
    fontSize: '0.85rem',
    color: '#666',
    marginBottom: '0.5rem',
    fontWeight: '500',
  },
  detailValue: {
    fontSize: '1rem',
    color: '#2C3E50',
    fontWeight: '600',
  },
  signatureContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  signature: {
    fontSize: '0.9rem',
    color: '#2C3E50',
    fontWeight: '600',
    fontFamily: 'monospace',
    backgroundColor: '#f8f9fa',
    padding: '0.5rem',
    borderRadius: '4px',
    display: 'block',
  },
  explorerLink: {
    color: '#3498db',
    textDecoration: 'none',
    fontSize: '0.9rem',
    fontWeight: '600',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.25rem',
  },
  processingText: {
    fontSize: '0.95rem',
    color: '#27ae60',
    fontWeight: '600',
    margin: '1rem 0 0 0',
  },
  agentSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  paymentDetails: {
    backgroundColor: 'white',
    padding: '1.25rem',
    borderRadius: '8px',
    border: '1px solid #E0E0E0',
  },
  detailsTitle: {
    fontSize: '1rem',
    color: '#2C3E50',
    marginBottom: '1rem',
    fontWeight: 'bold',
    borderBottom: '2px solid #E8E8E8',
    paddingBottom: '0.5rem',
  },
  detailRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '0.75rem',
    fontSize: '0.9rem',
    color: '#666',
  },
  detailValue: {
    fontWeight: '600',
    color: '#2C3E50',
  },
  detailValueMono: {
    fontWeight: '600',
    color: '#2C3E50',
    fontFamily: 'monospace',
    fontSize: '0.85rem',
  },
  messageBox: {
    marginTop: '1rem',
    padding: '0.75rem',
    backgroundColor: '#e3f2fd',
    borderRadius: '4px',
    fontSize: '0.85rem',
    color: '#1976d2',
    border: '1px solid #90caf9',
  },
  agentEntry: {
    backgroundColor: 'white',
    padding: '1.25rem',
    borderRadius: '8px',
    border: '2px solid #3498db',
  },
  inputLabel: {
    display: 'block',
    fontSize: '0.95rem',
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: '0.5rem',
  },
  required: {
    color: '#e74c3c',
    marginLeft: '0.25rem',
  },
  textarea: {
    width: '100%',
    padding: '0.75rem',
    border: '1px solid #E0E0E0',
    borderRadius: '8px',
    fontSize: '0.9rem',
    fontFamily: 'monospace',
    resize: 'vertical',
    boxSizing: 'border-box',
    backgroundColor: '#FAFAFA',
  },
  buttonGroup: {
    display: 'flex',
    gap: '1rem',
    justifyContent: 'flex-end',
  },
  cancelButton: {
    backgroundColor: '#95a5a6',
    color: 'white',
    border: 'none',
    padding: '0.75rem 1.5rem',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '0.95rem',
    fontWeight: 'bold',
    transition: 'all 0.3s ease',
  },
  submitButton: {
    background: 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)',
    color: 'white',
    border: 'none',
    padding: '0.75rem 1.5rem',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '0.95rem',
    fontWeight: 'bold',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 12px rgba(39, 174, 96, 0.3)',
  },
  submitButtonDisabled: {
    backgroundColor: '#95a5a6',
    cursor: 'not-allowed',
  },
};

export default OnchainPaymentWidget;
