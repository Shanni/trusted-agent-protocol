/* © 2025 Visa.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

import React, { useState } from 'react';
import OnchainPayment from './OnchainPayment';

const OnchainPaymentAgent = ({ amount, onPaymentComplete, onError, orderData }) => {
  const [paymentMode, setPaymentMode] = useState('agent'); // 'agent' or 'raw'
  const [agentUrl, setAgentUrl] = useState('http://localhost:8501');
  const [agentStatus, setAgentStatus] = useState('idle'); // 'idle', 'waiting', 'completed', 'failed'

  const handleAgentPayment = async () => {
    setAgentStatus('waiting');
    
    try {
      // Create payment request for agent
      const paymentRequest = {
        amount: amount,
        currency: 'USDC',
        network: 'solana:devnet',
        orderData: orderData,
        merchantUrl: window.location.origin,
        timestamp: Date.now()
      };

      // In a real implementation, this would:
      // 1. Send payment request to agent
      // 2. Agent would handle the payment flow
      // 3. Receive confirmation from agent
      
      // For now, we'll simulate the agent flow
      console.log('Payment request sent to agent:', paymentRequest);
      console.log('Agent URL:', agentUrl);
      
      // Simulate agent processing
      setTimeout(() => {
        // In production, you would poll for agent completion or use webhooks
        const mockAgentResponse = {
          success: true,
          signature: 'agent_tx_' + Date.now(),
          explorerUrl: `https://explorer.solana.com/tx/agent_tx_${Date.now()}?cluster=devnet`,
          amountReceived: amount
        };
        
        setAgentStatus('completed');
        onPaymentComplete(mockAgentResponse);
      }, 3000);
      
    } catch (err) {
      setAgentStatus('failed');
      onError('Agent payment failed: ' + err.message);
    }
  };

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>Onchain Payment (USDC on Solana)</h3>
      
      {/* Payment Mode Selection */}
      <div style={styles.modeSelection}>
        <label style={styles.modeLabel}>
          <input
            type="radio"
            name="paymentMode"
            value="agent"
            checked={paymentMode === 'agent'}
            onChange={(e) => setPaymentMode(e.target.value)}
          />
          <span style={styles.modeText}>
            🤖 Agent-Based Payment
            <span style={styles.modeDescription}>
              Let a trusted agent handle the payment
            </span>
          </span>
        </label>
        
        <label style={styles.modeLabel}>
          <input
            type="radio"
            name="paymentMode"
            value="raw"
            checked={paymentMode === 'raw'}
            onChange={(e) => setPaymentMode(e.target.value)}
          />
          <span style={styles.modeText}>
            🔐 Direct Wallet Payment
            <span style={styles.modeDescription}>
              Pay directly with your Phantom wallet
            </span>
          </span>
        </label>
      </div>

      {/* Agent Payment Mode */}
      {paymentMode === 'agent' && (
        <div style={styles.agentSection}>
          <div style={styles.agentInfo}>
            <p style={styles.infoText}>
              An authorized agent will complete the payment on your behalf using the x402 protocol.
            </p>
            
            <div style={styles.inputGroup}>
              <label style={styles.inputLabel}>Agent URL:</label>
              <input
                type="text"
                value={agentUrl}
                onChange={(e) => setAgentUrl(e.target.value)}
                style={styles.input}
                placeholder="http://localhost:8501"
              />
            </div>

            <div style={styles.paymentDetails}>
              <div style={styles.detailRow}>
                <span>Amount:</span>
                <span style={styles.detailValue}>{amount} USDC</span>
              </div>
              <div style={styles.detailRow}>
                <span>Network:</span>
                <span style={styles.detailValue}>Solana Devnet</span>
              </div>
              <div style={styles.detailRow}>
                <span>Protocol:</span>
                <span style={styles.detailValue}>x402 by Project Sienna</span>
              </div>
            </div>

            {agentStatus === 'idle' && (
              <button
                onClick={handleAgentPayment}
                style={styles.agentButton}
              >
                Request Agent Payment
              </button>
            )}

            {agentStatus === 'waiting' && (
              <div style={styles.statusBox}>
                <div style={styles.spinner}></div>
                <p style={styles.statusText}>
                  Waiting for agent to complete payment...
                </p>
                <p style={styles.statusSubtext}>
                  The agent is processing your payment request
                </p>
              </div>
            )}

            {agentStatus === 'completed' && (
              <div style={styles.successBox}>
                <span style={styles.successIcon}>✅</span>
                <p style={styles.successText}>Payment completed by agent!</p>
              </div>
            )}

            {agentStatus === 'failed' && (
              <div style={styles.errorBox}>
                <span style={styles.errorIcon}>❌</span>
                <p style={styles.errorText}>Agent payment failed</p>
                <button
                  onClick={() => setAgentStatus('idle')}
                  style={styles.retryButton}
                >
                  Try Again
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Raw Transaction Mode */}
      {paymentMode === 'raw' && (
        <div style={styles.rawSection}>
          <OnchainPayment
            amount={amount}
            onPaymentComplete={onPaymentComplete}
            onError={onError}
          />
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: '1.5rem',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    border: '1px solid #e9ecef',
  },
  title: {
    fontSize: '1.1rem',
    color: '#2c3e50',
    marginBottom: '1.5rem',
    fontWeight: 'bold',
  },
  modeSelection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
    marginBottom: '1.5rem',
    padding: '1rem',
    backgroundColor: 'white',
    borderRadius: '8px',
    border: '1px solid #ddd',
  },
  modeLabel: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '0.75rem',
    cursor: 'pointer',
    padding: '0.75rem',
    borderRadius: '6px',
    transition: 'background-color 0.2s',
  },
  modeText: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.25rem',
    fontSize: '1rem',
    fontWeight: '500',
    color: '#2c3e50',
  },
  modeDescription: {
    fontSize: '0.85rem',
    color: '#666',
    fontWeight: 'normal',
  },
  agentSection: {
    backgroundColor: 'white',
    padding: '1.5rem',
    borderRadius: '8px',
    border: '1px solid #ddd',
  },
  agentInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  infoText: {
    color: '#666',
    fontSize: '0.9rem',
    lineHeight: '1.5',
    margin: 0,
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  inputLabel: {
    fontSize: '0.9rem',
    fontWeight: '500',
    color: '#2c3e50',
  },
  input: {
    padding: '0.75rem',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '0.9rem',
    fontFamily: 'monospace',
  },
  paymentDetails: {
    backgroundColor: '#f8f9fa',
    padding: '1rem',
    borderRadius: '6px',
    border: '1px solid #e9ecef',
  },
  detailRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '0.5rem',
    fontSize: '0.9rem',
    color: '#666',
  },
  detailValue: {
    fontWeight: '600',
    color: '#2c3e50',
  },
  agentButton: {
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    padding: '0.75rem 1.5rem',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: 'bold',
    transition: 'background-color 0.2s',
  },
  statusBox: {
    textAlign: 'center',
    padding: '2rem 1rem',
    backgroundColor: '#e3f2fd',
    borderRadius: '6px',
    border: '1px solid #90caf9',
  },
  spinner: {
    width: '40px',
    height: '40px',
    margin: '0 auto 1rem',
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #3498db',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  statusText: {
    fontSize: '1rem',
    fontWeight: '600',
    color: '#1976d2',
    margin: '0 0 0.5rem 0',
  },
  statusSubtext: {
    fontSize: '0.85rem',
    color: '#666',
    margin: 0,
  },
  successBox: {
    textAlign: 'center',
    padding: '2rem 1rem',
    backgroundColor: '#e8f5e9',
    borderRadius: '6px',
    border: '1px solid #81c784',
  },
  successIcon: {
    fontSize: '3rem',
    display: 'block',
    marginBottom: '0.5rem',
  },
  successText: {
    fontSize: '1.1rem',
    fontWeight: '600',
    color: '#2e7d32',
    margin: 0,
  },
  errorBox: {
    textAlign: 'center',
    padding: '2rem 1rem',
    backgroundColor: '#ffebee',
    borderRadius: '6px',
    border: '1px solid #ef5350',
  },
  errorIcon: {
    fontSize: '3rem',
    display: 'block',
    marginBottom: '0.5rem',
  },
  errorText: {
    fontSize: '1rem',
    fontWeight: '600',
    color: '#c62828',
    marginBottom: '1rem',
  },
  retryButton: {
    backgroundColor: '#e74c3c',
    color: 'white',
    border: 'none',
    padding: '0.5rem 1rem',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.9rem',
  },
  rawSection: {
    marginTop: '1rem',
  },
};

// Add keyframe animation for spinner
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
document.head.appendChild(styleSheet);

export default OnchainPaymentAgent;
