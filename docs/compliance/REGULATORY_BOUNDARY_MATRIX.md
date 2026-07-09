# Regulatory Boundary Matrix

Status: compliance boundary scaffold, not legal advice  
Purpose: prevent PARRALAX product, token, trading, transfer, and fund claims from crossing into live regulated activity without explicit gates.

## 1. Core Rule

PARRALAX can build simulation, paper trading, proof receipts, wallet UI, local/test ledgers, and operator tooling before it can claim live fund, exchange, broker, custody, investment-advice, payment, or public token readiness.

Any movement from simulation/paper to live value requires a separate legal, compliance, custody, security, and operational gate.

## 2. Operating Modes

| Mode | Description | Allowed now | Prohibited until gated |
| --- | --- | --- | --- |
| `simulation` | Synthetic data, no user funds, no external execution. | Research, UI, benchmarks, receipts. | Real money movement or performance marketing. |
| `paper` | User-visible paper balances and paper orders. | Order lifecycle, risk gates, receipts. | Broker execution, deposits, withdrawals, fund claims. |
| `test-ledger` | Local/test ICRC or testnet chain ledgers. | Token/payment flow tests and entitlement receipts. | Public token launch or value claims. |
| `own-capital-live` | Trading or transfers with owner/company funds. | Only after internal approvals. | External capital, public fund claims, user-directed execution. |
| `external-user-live` | Users deposit/transfer/trade real assets. | Not enabled. | Requires money transmission/custody/payment/compliance review. |
| `fund` | Managed strategy, pooled capital, profit participation. | Not enabled. | Requires fund/securities/legal structure. |
| `exchange` | Marketplace for third-party trading. | Not enabled. | Requires exchange/ATS/broker/DEX analysis. |
| `asset-issuance` | Token/NFT issuance. | Test/access/receipt artifacts only. | Security/yield/fund-share token claims. |

## 3. Action Matrix

| Action | Simulation | Paper | Test ledger | Own-capital live | External-user live | Fund/exchange/token gate |
| --- | --- | --- | --- | --- | --- | --- |
| Display wallet balances | Yes, synthetic | Yes, paper | Yes, test | Yes, internal | Requires custody/payment review | Must state source/freshness. |
| Internal transfer | Synthetic only | Paper only | Test only | Internal treasury only | Requires money transmission review | Must be ledgered and idempotent. |
| ICP token payment | No value | No value | Local/test only | Internal only | Requires payment/custody review | Use ICRC standards. |
| Ethereum token payment | No value | No value | Testnet only | Internal only | Requires custody/compliance review | Do not custody user keys casually. |
| Paper order | Yes | Yes | N/A | N/A | N/A | Must be labeled paper. |
| Broker order | No | No | Sandbox only | Approval required | Not enabled | Broker/adviser/fund analysis. |
| Strategy performance display | Simulated | Paper only | N/A | Internal only | Restricted | Must disclose mode and evidence. |
| Token issuance | Design only | Design only | Test token only | Legal review | Legal review | Security/yield claims prohibited until cleared. |
| NFT receipt/access pass | Design only | Test only | Test only | Legal review | Legal review | Avoid investment language. |
| Public investor brief | Draft only | Draft only | Draft only | Legal review | Legal review | Claims ledger must approve wording. |

## 4. Token Boundary

| Token type | Boundary |
| --- | --- |
| Local/test utility token | Can be used to test wallet and ledger flows. No public value claim. |
| Access/credit token | May represent platform access only after terms and refund rules exist. |
| Receipt NFT | May represent proof/access/certificate, not profit or fund ownership. |
| Governance token | Needs legal analysis if transferable or tied to economic control. |
| Yield/fund/security token | Not enabled until legal structure, disclosures, custody, and compliance are complete. |

## 5. Wallet and Transfer Boundary

Wallet UI may be built before live rails, but it must label balances by source:

- synthetic;
- paper;
- test ledger;
- internal treasury;
- externally verified;
- stale/unverified.

No transfer button should submit live value until:

1. ledger journal is implemented;
2. idempotency is enforced;
3. risk/velocity limits exist;
4. receipt chain exists;
5. provider failure model exists;
6. compliance approval for that rail exists.

## 6. Trading Boundary

Paper trading may execute immediately as a product slice. Live trading requires:

- broker/exchange sandbox first;
- own-capital approval before any real execution;
- hard kill switch;
- pre-trade and post-trade risk receipts;
- audit logs;
- reconciliation;
- explicit prohibition on third-party capital until fund/compliance review is complete.

## 7. Required Public Wording Discipline

| Claim category | Allowed wording now | Avoid |
| --- | --- | --- |
| Product | "paper-first Control Tower" | "live hedge fund" |
| Token | "ICP ledger architecture" | "PARRALAX token deployed" |
| Trading | "paper trading and simulation" | "autonomous live HFT" |
| Wallet | "wallet and ledger app architecture" | "live money transfer app" |
| Proof | "receipt/proof design" | "audited production proof" |
| Compliance | "boundary matrix" | "regulatory compliant" without review |

## 8. Monitor Next

Before public launch language expands, update `docs/proof/CLAIMS_VERIFICATION_LEDGER.md` and ensure every README/product-paper claim maps to evidence, test, or future status.
