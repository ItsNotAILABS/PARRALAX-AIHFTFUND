# PARRALAX Institutional Agent Risk Plane

Status: **SOURCE IMPLEMENTED / NOT DEPLOYED / NOT AN AUTONOMOUS BROKER**.

## Responsibilities

PARRALAX independently owns policy, market-evidence verification, portfolio limits, proposal evaluation and receipt reconciliation. Senda owns the wallet-native financial UX and its existing verified execution integrations. This package never receives a user's secret key, submits swaps, or claims trading alpha.

Eight bounded agent domains are declared in `pretrade.mjs`: market-data QA, liquidity scouting, volatility regime, transaction-cost analysis, portfolio risk, funding/basis, treasury policy and order proposals. No agent has permission to submit, sign, withdraw or transfer.

The `evaluatePretrade` function denies missing/invalid inputs, ineligible venues or instruments, leverage or per-order caps, spreads/price impact/slippage, stale oracle/quote data, thin markets, exposure limits, daily P&L stops, drawdown, open orders and turnover.

The server in `server.mjs` offers `POST /v1/agents/pretrade` with service bearer authentication. **It requires an externally supplied `loadTrustedContext` resolver** that retrieves tenant policy, portfolio, oracle, quote provenance and eligibility from trusted stores. It discards any order-supplied portfolio/policy fields. No generic demo resolver is provided; service cannot start without real trusted adapters.

### Request body

```json
{"schema":"senda.pretrade.request.v1","quoteId":"quote-123","order":{"requestId":"req-123","tenantId":"tenant-1","agentId":"agent-1","venue":"jupiter","mint":"So11111111111111111111111111111111111111112","side":"buy","notionalUsd":10,"leverage":1,"priceImpactBps":10,"slippageBps":30}}
```

The client must authenticate its Senda user/tenant first and derive `x-service-principal` server-side. The trusted resolver must independently retrieve the market data and policy, not trust caller-supplied flags. A decision of `APPROVAL_REQUIRED` is **not** permission to sign or send.

## Production evidence requirements

1. JWT/mTLS between Senda and PARRALAX; per-tenant policy/permissions; no public gateway or private token in browser bundles.
2. Durable, revisioned policy store and atomic idempotency/budget reservations.
3. Independently validated quote source and oracle state; venue-health checks and explicit halt handling.
4. Position and account ledger reconciliation, funding/liquidation risk for perps, and transaction simulator.
5. Hardware-isolated or audited program-scoped signer with owner controls, revocation, on-chain caps and key rotation.
6. Fill confirmation independent of quote; compare net-of-costs P&L, fee/funding, implementation shortfall, drawdown and venue outages. No claims of profitability until out-of-sample results.
7. Human-approved execution until signed program grants and security reviews are complete. No keys in agent prompts or browser localStorage.

## Security incidents

As of November 25, 2026, public reporting says Velocity (a fork of Drift V2) paused transactions during a bug investigation; treat both the archived/paused Drift program and Velocity as **disabled** for new Senda execution adapters until independently verified. A venue pause may prevent exits; no guarantee otherwise.

## Unit tests

```sh
node --test services/agent-trading/pretrade.test.mjs
```

This command is to be run in PARRALAX CI. No passed test, actual order, receipt or deployment is asserted here. Source-based risk checks are not a substitute for execution-proof and security audits.
