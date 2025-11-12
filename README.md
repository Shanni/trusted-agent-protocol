# Agent Commerce via x402 Protocol
### by Project Sienna

**Establishing a universal trust standard between AI agents and merchants for the next era of autonomous commerce.**

---

## 🎯 THE PROBLEM

### The Agentic Commerce Dilemma

AI agents are transforming e-commerce, but merchants face a new trust crisis.

**Today:**
- AI agents can browse, compare, and purchase autonomously.
- Merchants have no way to verify who the agent is or who it represents.
- Legacy payment systems cannot handle agent-to-merchant transactions.

**Merchants must ask:**
- ❓ Is this a legitimate, authorized AI agent?
- ❓ Is it acting for a real, verified user?
- ❓ Can I safely process this payment?

**Without a standard:**
- ❌ Merchants block agent transactions, losing future revenue
- ⚠️ Accepting them exposes fraud, chargebacks, and compliance risk
- 🧱 Traditional rails (Visa, PayPal) weren't built for AI-native commerce

---

## 📊 MARKET OPPORTUNITY

### The Emergence of Agentic Commerce

Autonomous agents are redefining how transactions occur — and the market is exploding.

| Market | 2024 | 2030+ | CAGR |
|--------|------|-------|------|
| **AI Agents** | $5.25B | $52.6B | 46.3% |
| **Autonomous AI** | $6.8B | $103B (2034) | 30.3% |
| **eCommerce Fraud Prevention** | $5.9B | $25.9B (2032) | 20.4% |

**Key Drivers:**
- 60%+ labor reduction via agent automation
- Enterprises integrating agents (Microsoft, Salesforce, Google)
- Financial institutions using AI for fraud and compliance
- Traditional payments unfit for machine identity or crypto-native commerce

---

## 💡 OUR SOLUTION: Trusted Agent Protocol (TAP)

**A cryptographic trust and payment standard for AI-to-merchant commerce — built on the x402 Payment Rail.**

### Three Core Components

#### 1. Agent Identity Verification (RFC 9421)
- Cryptographic signatures (Ed25519, RSA-PSS-SHA256)
- Timestamped, nonce-protected validation
- Agent identity proven and verifiable

#### 2. x402 Payment Integration
- Uses HTTP 402 "Payment Required" status code
- Onchain USDC settlements (blockchain-agnostic)
- Instant **2s settlement** — no accounts or OAuth required
- **0% protocol fees**

#### 3. Spending Rules & Authorization
- User-delegated spending caps
- Real-time transaction tracking and auditing
- Full transparency and accountability

**Workflow:**
```
User → Delegates Agent → Agent → TAP Verification → x402 Payment → Merchant Fulfillment
```

---

## 🔒 SECURITY & TRUST FRAMEWORK

### Four Layers of Defense

| Layer | Protections |
|-------|-------------|
| **Cryptographic Verification** | RFC 9421 Signatures, Domain Binding, Nonce/Timestamp Validation |
| **Agent Registry** | Public key management, Reputation scoring, Key rotation |
| **Spending Protection** | Pre-checks, Daily limits, Auto-resets, Audit trails |
| **Payment Security** | Immutable onchain ledger, No chargebacks, Wallet-to-wallet transparency |

---

## 🏗️ TECHNICAL ARCHITECTURE

**TAP Agent:** Generates cryptographic proofs, manages spending rules, executes purchases

**CDN Gateway:** Verifies signatures, fetches keys, enforces bindings

**Merchant Backend:** Handles verified requests, processes x402 payments, creates receipts

**Agent Registry:** Stores and manages agent keys, reputations, metadata

**x402 Payment Facilitator:** Executes 2-second onchain settlements

---

## 💰 BUSINESS MODEL

### Multi-Sided Platform

**Revenue Streams:**
- Merchant processing fees (0.5–1%)
- Enterprise SaaS subscriptions
- Agent Registry hosting fees

**Value-Added Services:**
- Premium agent verification tiers ($99–$499/mo)
- Fraud analytics dashboards
- Compliance and audit tools

**Example Economics:**
- AOV: $50 → Fee: $0.375 → Cost: $0.02 → **Margin: 95%**
- 10M tx/mo = $3.75M revenue
- 100M tx/mo = $37.5M revenue

---

## 🚀 GO-TO-MARKET STRATEGY

### Phase 1 (0–6 mo): Foundation
- Open-source TAP protocol + SDK
- 50–100 pilot merchants
- 5–10 AI platform partners
- **Goal:** 10K+ verified transactions

### Phase 2 (6–18 mo): Expansion
- Integrate with Stripe, Square, Cloudflare
- Merchant certification, multi-chain support
- **Goal:** 1M+ tx/mo, $50M+ volume

### Phase 3 (18–36 mo): Scale
- Enterprise integrations (Amazon, Shopify)
- Global Registry federation
- Regulatory certification, EU/APAC rollout
- **Goal:** 100M+ tx/mo, $5B+ volume

---

## 🧠 COMPETITIVE EDGE

| Category | TAP Advantage |
|----------|---------------|
| **Open Standard** | Not platform-locked, RFC 9421 compliant |
| **Economics** | Zero protocol fees, instant settlement |
| **Security** | Cryptographic proof of identity, onchain audit |
| **Dev Experience** | SDKs, docs, and live demos |
| **Network Effects** | More agents → more merchants → stronger ecosystem |

---

## 🏆 COMPETITIVE LANDSCAPE

| Competitor | Weakness |
|------------|----------|
| Visa Trusted Agent | Closed, 2.9% fees |
| Google AP2 | Platform-locked |
| PayPal Agent Commerce | Requires accounts |
| Mastercard Framework | Complex integration |

**TAP Differentiation:**
- ✅ Open, blockchain-agnostic
- ✅ Zero fees, instant settlement
- ✅ Frictionless setup
- ✅ Standards-based trust

---

## 📈 FINANCIAL PROJECTIONS

| Year | Merchants | Agents | Tx/Mo | Revenue | Growth |
|------|-----------|--------|-------|---------|--------|
| Y1 | 500 | 50K | 500K | $1.8M | — |
| Y2 | 2,000 | 500K | 5M | $20.3M | 11x |
| Y3 | 10,000 | 5M | 50M | $225M | 11x |
| Y4 | 50,000 | 50M | 500M | $2.5B | 11x |
| Y5 | 200,000 | 500M | 2B | $10.8B | 4.3x |

**Break-even:** Month 18 | **Cash Flow Positive:** Month 24 | **95% gross margin**

---

## 👥 TEAM & ADVISORS

**Core Expertise:**
- Protocol design, blockchain architecture, compliance
- E-commerce & payment systems
- B2B and platform partnerships

**Advisory Network:**
- Visa/Mastercard experts
- AI & agentic researchers
- Regulatory and legal counsel

---

## 💵 FUNDING & USE OF PROCEEDS

### Seed Round: $5M

| Allocation | Focus |
|------------|-------|
| **Engineering (40%)** | Protocol dev, SDKs, security |
| **Operations (25%)** | Infrastructure & registry |
| **GTM (25%)** | Merchant & developer onboarding |
| **Legal (10%)** | Compliance, IP, standards |

**Series A Target:** $20M (18–24 months)

---

## ⚠️ RISKS & MITIGATION

| Risk | Mitigation |
|------|------------|
| Regulation | Compliance-first, proactive engagement |
| Incumbent resistance | Open ecosystem partnerships |
| Slow adoption | 1-line merchant integration, pilot ROI |
| Security | Audits, bounties, formal verification |
| Blockchain scalability | Multi-chain, L2, fallback rails |

---

## 🌍 VISION & IMPACT

### Building the Trust Fabric of Agentic Commerce

**Today:** Fragmented identity, friction, and fraud.

**Tomorrow (with TAP):**
- Universal agent trust standard
- Instant, fee-free transactions
- Secure, transparent agent ecosystems

**Impact:**
- 60%+ lower fraud
- 90% faster checkouts
- 50% lower merchant costs
- Universal agent acceptance

---

## 🔮 ROADMAP

### 2025:
- **Q1:** TAP v1.0 + 50 pilots
- **Q2:** Registry live, SDK launch
- **Q3:** Stripe/Square integrations
- **Q4:** 1M tx processed, Series A

### 2026:
- 10K+ merchants, 100M tx
- 5+ blockchain support
- Enterprise white-label

### 2027:
- Global Registry federation
- 1B+ tx annually
- Profitability milestone

---

## 📞 CALL TO ACTION

**Join us in building the identity and payment layer for AI commerce.**

**We're seeking:**
- Strategic investors (payments, e-commerce, AI)
- Merchant and agent partners
- Advisors from Visa, Mastercard, Stripe

---

## 🚀 Quick Start

### The Challenge (Legacy)

AI agents are becoming part of everyday commerce, capable of executing complex tasks like booking travel or managing subscriptions. As agent capabilities evolve, merchants need visibility into their identities and actions more than ever.

**For an agent to make a purchase, merchants must answer:**

- Is this a legitimate, trusted, and recognized AI agent?
- Is it acting on behalf of a specific, authenticated user?
- Does the agent carry valid instructions from the user to make this purchase?
-  Is it acting on behalf of a specific, authenticated user?
-  Does the agent carry valid instructions from the user to make this purchase?

**Without a standard, merchants face an impossible choice:**
-  Block potentially valuable agent-driven commerce
-  Accept significant operational and security risks from unverified agents

## The Solution

Visa's **Trusted Agent Protocol** provides a standardized, cryptographic method for an AI agent to prove its identity and associated authorization directly to merchants. By presenting a secure digital signature with every interaction, a merchant can verify that an agent is legitimate and has the user's permission to act.

For merchants, the Trusted Agent Protocol describes a standardized set of mechanisms enabling merchants to:

- **Cryptographically Verify Agent Intent:** Instantly distinguish a legitimate, credentialed agent from an anonymous bot. The agent presents a secure signature that includes timestamps, a unique session identifier, key identifier, and algorithm identifier, allowing you to verify that the signature is current and prevent relays or replays. 

- **Confirm Transaction-Specific Authorization:** Ensure the agent is authorized for the specific action it is taking  (browsing or payment) as the signature is bound to your domain and the specific operation being performed.

- **Receive Trusted User & Payment Identifiers:** Securely receive key information needed for checkout via query parameters. This can include, as consented by the consumer, verifiable consumer identifiers, Payment Account References (PARs) for cards on file, or other identifiers like loyalty numbers, emails and phone numbers, allowing you to streamline or pre-fill the customer experience.

- **Reduce Fraud:** By trusting the agent's identity and intentions, merchants can create a more seamless path to purchase for customers using agents. This cryptographic proof of identity and intent provides a powerful new tool to reduce fraud and minimize chargebacks from unauthorized transactions.

## Key Benefits

- **Differentiate from Malicious Actors:** The Trusted Agent Protocol provides a definitive way for you to distinguish legitimate, authorized AI agents from other automated traffic. This allows you to confidently welcome agent-driven commerce while protecting your site from harmful bots.

- **Context-Bound Security:** Every request from a trusted agent is cryptographically locked to a merchant's specific website and the exact page with which the agent is interacting . This ensures that an agent's authorization cannot be misused elsewhere.

- **Protection Against Replay Attacks:** The protocol is designed to prevent bad actors from capturing and reusing old requests. Each signature includes unique, time-sensitive elements that ensure every request is fresh and valid only for a single use.

- **Securely Receive Customer & Payment Identifiers:** The protocol defines a standardized way for a verified agent to pass essential customer information directly to merchants. This allows merchants to streamline the checkout process by receiving trusted data to pre-fill forms or identify the customer.

## Example Agent Verification for Payments
![](./assets/trusted-agent-protocol-flow.png)

## Quick Start

This repository contains a complete sample implementation demonstrating the Trusted Agent Protocol across multiple components:

### 🚀 **Running the Sample**

1. **Install Dependencies** (from root directory):
   ```bash
   pip install -r requirements.txt
   ```

2. **Start All Services**:
   ```bash
   # Terminal 1: Agent Registry (port 8001)
   cd agent-registry && python main.py
   
   # Terminal 2: Merchant Backend (port 8000)
   cd merchant-backend && python -m uvicorn app.main:app --reload
   
   # Terminal 3: CDN Proxy (port 3002)
   cd cdn-proxy && npm install && npm start
   
   # Terminal 4: Merchant Frontend (port 3001)
   cd merchant-frontend && npm install && npm run dev
   
   # Terminal 5: TAP Agent (port 8501)
   cd tap-agent && streamlit run agent_app.py
   ```

3. **Try the Demo**:
   - Open the TAP Agent at http://localhost:8501
   - Configure merchant URL: http://localhost:3001
   - Generate signatures and interact with the sample merchant

### 📚 **Component Documentation**

Each component has detailed setup instructions:

- **[TAP Agent](./tap-agent/README.md)** - Streamlit app demonstrating agent signature generation
- **[Merchant Frontend](./merchant-frontend/README.md)** - React e-commerce sample with TAP integration  
- **[Merchant Backend](./merchant-backend/README.md)** - FastAPI backend with signature verification
- **[CDN Proxy](./cdn-proxy/README.md)** - Node.js proxy implementing RFC 9421 signature verification
- **[Agent Registry](./agent-registry/README.md)** - Public key registry service for agent verification

### 🏗️ **Architecture Overview**

The sample demonstrates a complete TAP ecosystem:
1. **TAP Agent** generates RFC 9421 compliant signatures
2. **Merchant Frontend** provides the e-commerce interface
3. **CDN Proxy** intercepts and verifies agent signatures  
4. **Merchant Backend** processes verified requests
5. **Agent Registry** manages agent public keys and metadata