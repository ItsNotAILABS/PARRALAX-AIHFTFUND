# PARRALAX Financial Backend for Senda

PARTIAL SOURCE IMPLEMENTATION. Never treat as a connected exchange, bank or executing broker.

This service adds PARRALAX-owned v1 HTTP endpoints that match Senda's already-created `integrations/parralax` gateway contract:
- POST /v1/market/research — venue registry, explicit connection status
- POST /v1/risk/evaluate — deterministic fail-closed risk filter
- POST /v1/execution/plan — plan-only risk result
- POST /v1/execution/exit-plan — independently supplied quote comparison, **not** resting liquidity or guaranteed executable routing

All responses carry `schema: parralax.response.v1` and the requestId. Other Senda gateway routes remain unimplemented and return 404; do not fabricate receipts or clearing outputs.

Start:
```sh
export PARRALAX_SENDA_SERVICE_TOKEN="<32+ chars from secret manager>"
HOST=127.0.0.1 PORT=8790 node services/senda-finance/server.mjs
node --test services/senda-finance/core.test.mjs
```

Wire Senda gateway's `PARRALAX_UPSTREAM_URL` to a private HTTPS ingress for this service and its `PARRALAX_UPSTREAM_TOKEN` to the same shared server credential. This service's loopback listener should be exposed only behind private ingress with mTLS and authenticated tenant services. No browser or organism credentials.

**Financial invariants**:
- Senda's current wallet-signed Jupiter, Hyperliquid and Ostium paths remain unchanged.
- No organism may sign wallets, bypass venue eligibility, or execute trades here.
- A quoted exit is not a fill. Require fresh quote revalidation, venue-specific execution adapter, user-approved signed transaction, confirmation, and reconciliation.
- Existing Solana spot routes cannot be naively combined with perpetual margin venues; margin accounts and regulatory restrictions differ.
- A rug, halt, liquidity withdrawal or failed settlement may make exit impossible. No guarantee of saving capital.
- Credit balances, card numbers, insured deposits, fiat payment rails and bank obligations are NOT created by this service.

Next production gates: durable authenticated principal mapping, idempotency store, account-level budgets, per-venue live adapters and freshness checks, p95 latency, recovery, real order receipts, regulator/venue eligibility and external audit. External execution is intentionally disabled.
