<p align="center">
  <img src="./assets/banner.svg" alt="PARRALAX AI HFT FUND" width="100%"/>
</p>

# PARRALAX

**Sovereign AI-native financial execution infrastructure built around risk gates, machine-checkable state, compute receipts and auditable coordination.**

PARRALAX is the financial execution plane of the wider POCKET/NEXUS ecosystem. It combines market research, strategy/risk evaluation, paper/sandbox execution, wallet/ledger infrastructure, execution receipts and clearing handoffs behind explicit policy and approval boundaries.

```text
market data / strategy / user intent
              │
              ▼
           PARRALAX
              │
              ├── signal / research
              ├── portfolio + risk state
              ├── execution planning
              ├── policy / approvals
              ├── paper or configured execution adapter
              ├── wallet / internal ledger
              ├── execution receipts
              └── clearing handoff
              │
              ▼
PARALLAX Clearinghouse / audit / operator surfaces
```

## Core product lanes

### Market intelligence

- signals and strategy inputs;
- multi-asset portfolio state;
- risk limits and scenario analysis;
- research/backtest artifacts;
- strategy-pack evidence.

### Execution control

- explicit order/execution plans;
- risk gates before action;
- idempotent operations;
- approvals for privileged/irreversible actions;
- provider/broker adapter boundary;
- execution acknowledgements and receipts.

### Wallet AOS

The repository includes an internal wallet/account operating layer with:

```text
double-entry ledger
wallet/account balances
sandbox credits
holds / releases
transfer proposals
policy / approval lifecycle
persistence and reconciliation lanes
statements / audit hashes
```

### Clearing integration

PARRALAX can hand validated execution/netting inputs to [PARALLAX Exchange Clearinghouse](https://github.com/ItsNotAILABS/PARALLAX-Exchange-Clearinghouse) through machine-readable contracts rather than merging clearing logic into the strategy runtime.

## NEXUS federation

Declaration: [`ecosystem.surface.json`](ecosystem.surface.json).

Primary ecosystem capabilities include:

```text
market.research
risk.evaluate
execution.plan
execution.simulate
receipt.verify
clearing.handoff
```

Shared operating contracts include:

```text
nexus.task.v1
nexus.policy-decision.v1
nexus.approval.v1
nexus.idempotency.v1
nexus.budget.v1
nexus.artifact.v1
nexus.execution-receipt.v1
nexus.audit-event.v1
nexus.handoff.v1
```

## Verifiable execution model

PARRALAX treats execution as an evidence chain:

```text
intent
 -> normalized market/account inputs
 -> risk decision
 -> execution plan
 -> approval state
 -> adapter request
 -> external/internal acknowledgement
 -> resulting position/ledger mutation
 -> receipt
 -> reconciliation
```

For sandbox/paper lanes, the same chain can be exercised without an external broker so strategy, governance and reconciliation code can be developed independently from a live venue integration.

## Machine-checkable netting

Orders, fills, internal wallet entries and clearing handoffs should use stable identifiers and deterministic accounting fields so a downstream clearing system can verify:

```text
instrument
side
quantity
price / valuation source
time
account / strategy
execution ID
fees
position impact
cash impact
counterparty / venue reference when present
receipt hash
```

## Public/API positioning

PARRALAX is designed around:

- verifiable execution;
- machine-checkable netting;
- compute and execution receipts;
- synchronization/coordination layers;
- auditability;
- governance/compliance integration boundaries;
- provider-neutral adapters.

That lets the platform mature market by market without making the core ledger/risk/receipt architecture dependent on one broker, exchange or asset class.

## Development

The repository contains multiple runtime languages and product surfaces. Use the local package/workspace commands for the component you are changing and keep cross-language contracts versioned.

For the financial runtime and wallet lanes, prioritize deterministic tests around:

```text
double-entry invariants
idempotent transfer/order IDs
risk denial
approval quorum
balance/position reconciliation
receipt hashes
ledger persistence
recovery from partial execution
```

## NEXUS validation

After changing the ecosystem contract:

```bash
# from ItsNotAILABS/nexus
python tools/validate_ecosystem_protocols.py
python tools/validate_ecosystem_registry.py
python tools/production_gate.py
```

## Production topology

```text
Client / strategy
       │
       ▼
POCKET identity + tenant
       │
       ▼
PARRALAX risk / execution gateway
       │
       ├── market-data adapters
       ├── model/signal workers
       ├── wallet/ledger
       ├── execution adapter
       └── receipt/audit store
       │
       ▼
PARALLAX Clearinghouse
       │
       ▼
reconciliation / statements / audit
```

## Operator checklist

```text
[ ] account/strategy IDs are explicit
[ ] market data source is named
[ ] risk limits are loaded
[ ] idempotency key is present for mutating requests
[ ] execution mode/adapter is explicit
[ ] privileged actions have approval state
[ ] execution response is persisted
[ ] ledger mutation balances
[ ] receipt digest is produced
[ ] clearing/reconciliation handoff is correlated
[ ] circuit/retry policy exists for provider failure
```

## Ecosystem

- [NEXUS](https://github.com/ItsNotAILABS/nexus) — protocols and routing
- [POCKET](https://github.com/ItsNotAILABS/pocket) — identity, tenancy, product host
- [POCKET Agent](https://github.com/ItsNotAILABS/pocket-agent) — long-running strategy/operations work
- [AURO](https://github.com/ItsNotAILABS/AURO) — model/runtime intelligence
- [PARALLAX Exchange Clearinghouse](https://github.com/ItsNotAILABS/PARALLAX-Exchange-Clearinghouse) — netting and clearing

PARRALAX is built to make financial automation **inspectable from intent through risk, execution, ledger impact, reconciliation and receipt.**
