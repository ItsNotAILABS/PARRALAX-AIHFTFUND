# PARALLAX Wallet AOS

PARALLAX Wallet AOS is the money-routing, wallet, transfer, treasury, and agent-operating interface layer for PARALLAX.

This package is intentionally built as a proof-governed financial runtime, not a live money transmitter. It implements local ledger logic, wallet accounts, transfer proposals, approval gates, rail adapters, receipts, and ACYILA interfaces. Live rails must be connected only after licensing, partner onboarding, custody review, KYC/AML controls, sanctions screening, fraud controls, and operator approval are complete.

## Core promise

```text
intent -> wallet account -> policy gate -> transfer proposal -> approval -> receipt -> rail adapter
```

## Surfaces

- `src/ledger.js` — append-only hash-chained double-entry ledger.
- `src/wallet.js` — wallet accounts, balances, holds, proposal lifecycle.
- `src/policy.js` — policy checks, limits, KYC state, approval requirements.
- `src/rails.js` — sandbox-only rail adapters for internal ledger, bank, card, crypto, ICP.
- `src/aos.js` — PARALLAX Agent Operating System command router.
- `src/acyila.js` — ACYILA interface registry for UI/API/agent integrations.
- `src/server.js` — local HTTP JSON API.
- `src/cli.js` — local CLI demo and validation commands.

## Run

```bash
cd systems/parallax-wallet-aos
npm test
npm run demo
npm run server
```

## Safety boundary

The repository does not claim licensed money transmission, custody, brokerage, banking, card issuing, ACH origination, crypto exchange, investment advice, or live trade execution. The rail adapters are sandbox stubs until explicit legal, compliance, and partner approvals exist.
