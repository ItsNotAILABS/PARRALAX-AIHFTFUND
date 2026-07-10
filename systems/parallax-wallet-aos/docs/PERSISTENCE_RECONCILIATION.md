# PARALLAX Wallet AOS v0.2 — Persistence, Reconciliation, Roles, Statements

This layer upgrades the v0.1 sandbox wallet core into an operating financial core.

## Added in v0.2

- Persistent JSON vault with snapshot hash verification.
- Storage receipts for every saved state envelope.
- Reconciliation reports comparing internal ledger totals to imported external balances.
- Account and wallet statements with statement hashes.
- Treasury role assignments and approval quorum checks.
- Operator dashboard contract for UI/API builders.
- Deterministic v0.2 tests covering persistence, reconciliation, statements, roles, and dashboard surfaces.

## Persistence model

The vault writes an atomic state envelope:

```text
snapshot -> snapshotHash -> state.json.tmp -> state.json -> storage_receipt
```

The loader verifies the snapshot hash before returning state. A mismatch fails closed.

## Reconciliation model

The reconciliation engine calculates internal ledger totals by currency and compares them to provided external balances.

Exception types:

- `external_balance_mismatch`
- `available_plus_held_mismatch`
- `ledger_hash_chain_failed`

## Statement model

Statements are generated from ledger entries touching a wallet settlement account. Each statement includes a deterministic statement hash.

## Treasury roles

Roles:

- `viewer`
- `proposer`
- `approver`
- `settler`
- `admin`

The quorum engine supports approval counts and distinct-approver checks.

## Boundary

This remains sandbox-only. Persistence and reconciliation do not activate live rails, custody, card issuing, ACH origination, bank wires, crypto signing, brokerage, money transmission, or live trading.
