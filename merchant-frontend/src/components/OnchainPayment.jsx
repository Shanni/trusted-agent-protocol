/* © 2025 Visa.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

import React, { useState } from 'react';

const OnchainPayment = ({ amount, onPaymentComplete, onError }) => {
  const [walletAddress, setWalletAddress] = useState('');
  const [processing, setProcessing] = useState(false);
  const [paymentDetails, setPaymentDetails] = useState(null);

  const handleConnectWallet = async () => {
    try {
      // Check if Phantom wallet is installed
      if (window.solana && window.solana.isPhantom) {
        const response = await window.solana.connect();
        setWalletAddress(response.publicKey.toString());
      } else {
        onError('Please install Phantom wallet to use onchain payment');
      }
    } catch (err) {
      onError('Failed to connect wallet: ' + err.message);
    }
  };

  const handlePayment = async () => {
    if (!walletAddress) {
      onError('Please connect your wallet first');
      return;
    }

    setProcessing(true);
    try {
      // Step 1: Request payment quote from server
      const quoteResponse = await fetch(`/api/payment/onchain/quote?amount=${amount}`);
      
      if (quoteResponse.status !== 402) {
        throw new Error('Failed to get payment quote');
      }

      const quote = await quoteResponse.json();
      
      setPaymentDetails({
        recipientWallet: quote.payment.recipientWallet,
        tokenAccount: quote.payment.tokenAccount,
        mint: quote.payment.mint,
        amount: quote.payment.amount,
        amountUSDC: quote.payment.amountUSDC,
        cluster: quote.payment.cluster,
      });

      // Step 2: Create and sign transaction using Phantom wallet
      const { Connection, PublicKey, Transaction } = await import('@solana/web3.js');
      const { 
        createTransferInstruction, 
        getOrCreateAssociatedTokenAccount,
        getAccount 
      } = await import('@solana/spl-token');

      const connection = new Connection(
        quote.payment.cluster === 'devnet' 
          ? 'https://api.devnet.solana.com' 
          : 'https://api.mainnet-beta.solana.com',
        'confirmed'
      );

      const recipientTokenAccount = new PublicKey(quote.payment.tokenAccount);
      const mint = new PublicKey(quote.payment.mint);
      const payerPublicKey = new PublicKey(walletAddress);

      // Get payer's token account
      const payerTokenAccount = await getOrCreateAssociatedTokenAccount(
        connection,
        window.solana, // Use wallet as signer
        mint,
        payerPublicKey
      );

      // Check balance
      const balance = await connection.getTokenAccountBalance(payerTokenAccount.address);
      if (Number(balance.value.amount) < quote.payment.amount) {
        throw new Error(`Insufficient USDC balance. Have: ${balance.value.uiAmountString}, Need: ${quote.payment.amountUSDC}`);
      }

      // Create transaction
      const { blockhash } = await connection.getLatestBlockhash();
      const tx = new Transaction({
        feePayer: payerPublicKey,
        blockhash,
        lastValidBlockHeight: (await connection.getLatestBlockhash()).lastValidBlockHeight,
      });

      // Check if recipient account exists
      let recipientAccountExists = false;
      try {
        await getAccount(connection, recipientTokenAccount);
        recipientAccountExists = true;
      } catch (error) {
        // Account doesn't exist, will need to create it
      }

      // Add create account instruction if needed
      if (!recipientAccountExists) {
        const { createAssociatedTokenAccountInstruction } = await import('@solana/spl-token');
        const recipientWallet = new PublicKey(quote.payment.recipientWallet);
        
        const createAccountIx = createAssociatedTokenAccountInstruction(
          payerPublicKey,
          recipientTokenAccount,
          recipientWallet,
          mint
        );
        tx.add(createAccountIx);
      }

      // Add transfer instruction
      const transferIx = createTransferInstruction(
        payerTokenAccount.address,
        recipientTokenAccount,
        payerPublicKey,
        quote.payment.amount
      );
      tx.add(transferIx);

      // Sign transaction with Phantom wallet
      const signedTx = await window.solana.signTransaction(tx);
      const serializedTx = signedTx.serialize().toString('base64');

      // Step 3: Send payment proof to server
      const paymentProof = {
        x402Version: 1,
        scheme: 'exact',
        network: quote.payment.cluster === 'devnet' ? 'solana:devnet' : 'solana:mainnet',
        payload: {
          serializedTransaction: serializedTx,
        },
      };

      const xPaymentHeader = btoa(JSON.stringify(paymentProof));

      const paymentResponse = await fetch('/api/payment/onchain/fulfill', {
        method: 'POST',
        headers: {
          'X-Payment': xPaymentHeader,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: amount,
        }),
      });

      const result = await paymentResponse.json();

      if (result.error) {
        throw new Error(result.error);
      }

      // Payment successful
      onPaymentComplete({
        signature: result.paymentDetails.signature,
        explorerUrl: result.paymentDetails.explorerUrl,
        amountReceived: result.paymentDetails.amountReceived,
      });

    } catch (err) {
      onError('Payment failed: ' + err.message);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>Pay with Crypto (USDC on Solana)</h3>
      
      {!walletAddress ? (
        <div style={styles.connectSection}>
          <p style={styles.description}>
            Connect your Solana wallet to pay with USDC
          </p>
          <button 
            onClick={handleConnectWallet}
            style={styles.connectButton}
          >
            Connect Phantom Wallet
          </button>
        </div>
      ) : (
        <div style={styles.paymentSection}>
          <div style={styles.walletInfo}>
            <span style={styles.label}>Connected Wallet:</span>
            <span style={styles.address}>
              {walletAddress.slice(0, 4)}...{walletAddress.slice(-4)}
            </span>
          </div>
          
          {paymentDetails && (
            <div style={styles.details}>
              <div style={styles.detailRow}>
                <span>Amount:</span>
                <span>{paymentDetails.amountUSDC} USDC</span>
              </div>
              <div style={styles.detailRow}>
                <span>Network:</span>
                <span>{paymentDetails.cluster}</span>
              </div>
            </div>
          )}
          
          <button
            onClick={handlePayment}
            disabled={processing}
            style={{
              ...styles.payButton,
              ...(processing ? styles.payButtonDisabled : {}),
            }}
          >
            {processing ? 'Processing Payment...' : `Pay ${amount} USDC`}
          </button>
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
    marginBottom: '1rem',
    fontWeight: 'bold',
  },
  connectSection: {
    textAlign: 'center',
  },
  description: {
    color: '#666',
    marginBottom: '1rem',
  },
  connectButton: {
    backgroundColor: '#9945FF',
    color: 'white',
    border: 'none',
    padding: '0.75rem 1.5rem',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: 'bold',
    transition: 'background-color 0.2s',
  },
  paymentSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  walletInfo: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '0.75rem',
    backgroundColor: 'white',
    borderRadius: '4px',
    border: '1px solid #ddd',
  },
  label: {
    fontSize: '0.9rem',
    color: '#666',
  },
  address: {
    fontSize: '0.9rem',
    fontFamily: 'monospace',
    color: '#2c3e50',
    fontWeight: 'bold',
  },
  details: {
    backgroundColor: 'white',
    padding: '1rem',
    borderRadius: '4px',
    border: '1px solid #ddd',
  },
  detailRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '0.5rem',
    fontSize: '0.9rem',
  },
  payButton: {
    backgroundColor: '#27ae60',
    color: 'white',
    border: 'none',
    padding: '0.75rem 1.5rem',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: 'bold',
    transition: 'background-color 0.2s',
  },
  payButtonDisabled: {
    backgroundColor: '#95a5a6',
    cursor: 'not-allowed',
  },
};

export default OnchainPayment;
