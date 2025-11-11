# Onchain Payment Setup Guide

This guide explains how to set up and use the onchain payment feature (USDC on Solana) in the merchant application.

## Overview

The merchant application now supports two payment methods:
1. **Credit Card (Visa)** - Traditional card payment
2. **Onchain Payment (USDC on Solana)** - Cryptocurrency payment using USDC on the Solana blockchain

## Prerequisites

### For Users (Customers)
- **Phantom Wallet** browser extension installed ([Download here](https://phantom.app/))
- USDC tokens in your Solana wallet (on devnet for testing)

### For Merchants (Backend Setup)
- Solana wallet address to receive payments
- Associated USDC token account

## Backend Configuration

1. **Update Environment Variables**

   Copy the `.env.example` file to `.env` in the `merchant-backend` directory:
   ```bash
   cd merchant-backend
   cp .env.example .env
   ```

2. **Configure Solana Settings**

   Edit the `.env` file and update the following variables:
   ```env
   SOLANA_RECIPIENT_WALLET=YOUR_SOLANA_WALLET_ADDRESS
   SOLANA_RECIPIENT_TOKEN_ACCOUNT=YOUR_USDC_TOKEN_ACCOUNT_ADDRESS
   SOLANA_USDC_MINT=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
   SOLANA_CLUSTER=devnet
   ```

   - `SOLANA_RECIPIENT_WALLET`: Your Solana wallet public key
   - `SOLANA_RECIPIENT_TOKEN_ACCOUNT`: Your USDC associated token account address
   - `SOLANA_USDC_MINT`: USDC mint address (default is mainnet USDC)
   - `SOLANA_CLUSTER`: Use `devnet` for testing, `mainnet` for production

3. **Get Your Token Account Address**

   If you don't have a USDC token account yet, you can create one using:
   ```bash
   # Using Solana CLI
   spl-token create-account EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
   ```

## Frontend Setup

1. **Install Dependencies**

   The required Solana dependencies are already added to `package.json`:
   ```bash
   cd merchant-frontend
   npm install
   ```

   This will install:
   - `@solana/web3.js` - Solana blockchain interaction
   - `@solana/spl-token` - SPL token operations

2. **No additional frontend configuration needed** - The frontend will automatically detect and use the Phantom wallet.

## How It Works

### Payment Flow

1. **Customer selects onchain payment** at checkout
2. **Customer connects Phantom wallet** by clicking "Connect Phantom Wallet"
3. **Backend generates payment quote** with:
   - Recipient wallet address
   - Token account address
   - Amount in USDC
   - Network (devnet/mainnet)

4. **Frontend creates transaction**:
   - Gets customer's token account
   - Checks USDC balance
   - Creates transfer instruction
   - Signs with Phantom wallet

5. **Transaction submitted to backend**:
   - Backend receives signed transaction via X-Payment header (x402 protocol)
   - Backend verifies and submits to Solana network
   - Returns transaction signature and explorer link

6. **Order completed** with transaction confirmation

### X402 Protocol

The implementation follows the x402 protocol for onchain payments:

```json
{
  "x402Version": 1,
  "scheme": "exact",
  "network": "solana:devnet",
  "payload": {
    "serializedTransaction": "base64_encoded_transaction"
  }
}
```

## Testing on Devnet

1. **Get Devnet SOL** (for transaction fees):
   ```bash
   solana airdrop 1 YOUR_WALLET_ADDRESS --url devnet
   ```

2. **Get Devnet USDC**:
   - Use a devnet USDC faucet
   - Or mint test USDC tokens using Solana CLI

3. **Test the Payment Flow**:
   - Browse products on the merchant site
   - Add items to cart
   - Go to checkout
   - Select "Onchain Payment (USDC on Solana)"
   - Connect Phantom wallet
   - Complete the payment

## Production Deployment

For production deployment:

1. **Update to Mainnet**:
   ```env
   SOLANA_CLUSTER=mainnet
   ```

2. **Use Mainnet USDC Mint**:
   ```env
   SOLANA_USDC_MINT=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
   ```

3. **Implement Transaction Verification**:
   - The current backend implementation is simplified
   - For production, add proper transaction verification
   - Verify amount, recipient, and token mint before accepting payment

4. **Add Transaction Monitoring**:
   - Monitor transaction confirmations
   - Handle failed transactions
   - Implement retry logic

## Security Considerations

1. **Never expose private keys** in the frontend or backend
2. **Verify all transactions** on the backend before accepting payment
3. **Use environment variables** for sensitive configuration
4. **Implement rate limiting** to prevent abuse
5. **Monitor for suspicious activity**

## Troubleshooting

### "Please install Phantom wallet"
- Install the Phantom browser extension from [phantom.app](https://phantom.app/)

### "Insufficient USDC balance"
- Ensure you have enough USDC in your wallet
- On devnet, get test USDC from a faucet

### "Failed to connect wallet"
- Check that Phantom is unlocked
- Refresh the page and try again
- Check browser console for errors

### Transaction fails
- Ensure you have enough SOL for transaction fees
- Check that the recipient token account exists
- Verify network connectivity

## API Endpoints

### Get Payment Quote
```
GET /api/payment/onchain/quote?amount=10.00
```

Returns payment details including recipient address and amount.

### Fulfill Payment
```
POST /api/payment/onchain/fulfill
Headers: X-Payment: base64_encoded_payment_proof
Body: { "amount": 10.00 }
```

Submits the signed transaction and returns confirmation.

### Check Payment Status
```
GET /api/payment/onchain/status/{signature}
```

Checks the status of a transaction.

## References

- [Solana Documentation](https://docs.solana.com/)
- [SPL Token Documentation](https://spl.solana.com/token)
- [Phantom Wallet Documentation](https://docs.phantom.app/)
- [x402 Protocol Specification](https://github.com/visanetwork/x402-protocol)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Solana and Phantom documentation
3. Check browser console for error messages
4. Verify environment configuration
