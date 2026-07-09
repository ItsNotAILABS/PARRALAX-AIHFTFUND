# Wallet, Multi-Ledger, Trading, and Transfer App Architecture

Status: product/runtime architecture scaffold  
Target surface: PARRALAX Control Tower money runtime  
Execution mode: paper/simulation first; live money movement gated.

## 1. Product Goal

Build one operator-grade app surface that combines:

- wallet balances;
- internal double-entry ledger;
- external ledger references;
- paper trading order flow;
- money transfer intent flow;
- risk checks;
- receipts and audit trail.

The app must never let the frontend invent money truth. Backend/canister state owns truth; the UI presents reconciled states and receipts.

## 2. Operator Surfaces

### Dashboard

- Net worth by asset and mode.
- Available, reserved, pending, and settled balances.
- Active orders and pending transfers.
- Recent receipts.
- Ledger health badges: synced, delayed, degraded.
- Risk exposure snapshot.

### Wallet

- Account selector: fiat, stablecoin, ICP, ckBTC, ckETH, strategy vault, paper account.
- Balance cards: available, reserved, pending, settled.
- Actions: deposit, withdraw, transfer, convert.
- Funding rails: internal transfer, ICP ledger, EVM address, bank rail placeholder.
- Transaction drawer with journal id, external reference, risk result, and receipt hash.

### Ledgers

- Multi-ledger timeline.
- Filters: internal, ICP, EVM, exchange, bank, settlement.
- Reconciliation status.
- Journal entry viewer: debit, credit, idempotency key, source ledger, status.
- Exception queue: stale balance, unmatched deposit, failed withdrawal, delayed provider callback.

### Trading

- Market selector.
- Paper order ticket: buy/sell, limit/market, quantity, notional.
- Pre-trade checks: available funds, max size, slippage, pair status, system mode.
- Order timeline: created, reserved, routed, partially filled, filled, canceled, failed.
- Positions and PnL, clearly marked paper/simulation until live gate is complete.

### Transfer

- Recipient selector.
- Rail selector: internal, ICP, EVM, bank placeholder.
- Quote preview: amount, fee, settlement estimate, risk result.
- Confirmation screen with idempotency key.
- Transfer receipt with status and ledger impact.

## 3. Backend Domain Modules

| Module | Role |
| --- | --- |
| `IdentityService` | User, principal, role, account, KYC status pointer, consent. |
| `WalletService` | Account containers, addresses, payment methods, display balances. |
| `LedgerService` | Double-entry journal, immutable entries, account balances, reservations. |
| `TransferService` | Transfer intents, quotes, approvals, execution, settlement. |
| `TradingService` | Order intents, reservations, lifecycle, fills, positions, PnL. |
| `RiskService` | Pre-trade checks, transfer limits, velocity limits, exposure limits. |
| `ReconciliationService` | Internal ledger versus external ledger/provider records. |
| `AuditService` | Append-only event/receipt trail for every money-moving action. |
| `NotificationService` | Balance, order, transfer, and exception updates. |

## 4. Money State Model

| State | Meaning | UI behavior |
| --- | --- | --- |
| `available` | Spendable/tradable now. | Can be used for new orders/transfers. |
| `reserved` | Held for pending order or transfer. | Show as locked; cannot double-spend. |
| `pending` | Provider/chain/bank settlement not final. | Show pending timeline and risk warning. |
| `settled` | Final in internal ledger and external confirmation where applicable. | Count in confirmed balance. |
| `failed` | Action failed and reservation should release or reverse. | Show failure receipt and remediation. |
| `reconciled` | Internal and external sources agree. | Show healthy ledger state. |
| `exception` | Reconciliation mismatch or ambiguous provider state. | Route to admin exception console. |

## 5. API Contract Shape

All money-moving POST commands require an idempotency key.

```ts
export interface MoneyCommandBase {
  idempotencyKey: string;
  clientTimestamp: string;
  sourceAccountId: string;
  amount: string;
  asset: string;
}

export interface CommandReceipt {
  status: "pending" | "reserved" | "settled" | "failed" | "canceled";
  journalId: string;
  receiptId: string;
  externalReference?: string;
  balanceImpact: {
    availableDelta: string;
    reservedDelta: string;
    pendingDelta: string;
    settledDelta: string;
  };
  nextAction: "none" | "approve" | "wait" | "retry" | "contact_support";
}
```

Minimum endpoint or canister-method families:

```text
wallet.summary
wallet.accounts
wallet.account_transactions

transfers.quote
transfers.create
transfers.get

ledgers.account
ledgers.journal
ledgers.reconciliation_status

trading.markets
trading.quote_order
trading.place_order
trading.get_order
trading.positions

risk.limits
risk.check
receipts.list
receipts.get
```

## 6. First Vertical Slice

Build first:

**Internal Wallet Transfer With Ledger Proof**

Flow:

1. User logs in.
2. Wallet dashboard shows one USD paper account and one strategy/paper account.
3. User opens Transfer.
4. User selects internal recipient or second owned account.
5. Backend/canister returns quote with fee `0` or fixed test fee.
6. User confirms.
7. Backend creates transfer intent.
8. Ledger reserves funds.
9. Ledger writes double-entry journal.
10. Transfer settles internally.
11. UI updates available/reserved/settled balances.
12. Transaction detail shows journal id, debit entry, credit entry, receipt id, timestamp, and status.

This slice comes before trading because it proves the hardest invariant: no money action exists without idempotency, ledger entries, balance impact, and a receipt.

## 7. Trading Slice After Transfer

Second slice:

**Paper Order With Ledger Reservation**

Flow:

1. User creates paper order.
2. Risk checks order size, pair status, system mode, and available balance.
3. Ledger reserves quote/base asset.
4. Order enters paper order book.
5. Fill writes settlement journal and fill receipt.
6. Cancel releases reservation and emits receipt.

## 8. Reconciliation and Exception Console

Reconciliation jobs compare:

- internal ledger balances;
- ICP/ICRC block records;
- EVM transaction receipts;
- exchange/broker statements;
- bank/fiat provider events.

Exception types:

- unmatched deposit;
- delayed confirmation;
- provider timeout;
- duplicate callback;
- balance mismatch;
- failed withdrawal after reservation;
- fill after cancel request.

## 9. Test Matrix

| Area | Required test |
| --- | --- |
| Idempotency | Same key returns same receipt; different key with same payload is flagged if suspicious. |
| Ledger | Debit and credit entries always balance. |
| Reservation | Available balance decreases before external execution. |
| Transfer | Failed transfer releases or reverses reservation with receipt. |
| Trading | Fill after cancel has deterministic handling. |
| Reconciliation | Mismatched external balance produces exception. |
| UI | Refresh during pending transfer does not double-submit. |
| Risk | Velocity, size, and mode limits block actions. |
| Audit | Every command produces exactly one receipt chain. |

## 10. Deployment Posture

| Stage | Enabled | Disabled |
| --- | --- | --- |
| v0 local | Internal paper transfer, paper balances, receipts. | External money movement. |
| v1 test | ICRC test ledger payments and access receipts. | Public token claims. |
| v2 alpha | Paper trading with ledger reservations. | Live broker execution. |
| v3 sandbox | Broker sandbox and chain testnet transfers. | Third-party capital. |
| v4 restricted | Limited live rails after legal/compliance/security review. | Ungated fund/exchange operation. |

## 11. Monitor Next

Implement `LedgerService`/ledger canister semantics before adding real external rails. The first code milestone should prove:

`UI intent -> idempotency record -> ledger journal -> balance update -> audit receipt -> frontend receipt view`.
