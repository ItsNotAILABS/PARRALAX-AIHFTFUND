# PARRALAX Artifact Packet Index

Status: active packet-control document  
Owner surface: PARRALAX Control Tower / proof and governance stack  
Purpose: organize research papers, charters, compliance boundaries, proof packs, and product documents into one release-governed artifact system.

## 1. Operating Rule

PARRALAX documents are not passive notes. They are governance tissue, proof boundaries, and release gates. A market-facing claim should not leave the repo until it is mapped to evidence, tests, receipts, or an explicit future/unverified status.

## 2. Current Canonical Sources

| Source | Role | Current status | Required next action |
| --- | --- | --- | --- |
| `README.md` | Public system narrative | Broad, high-claim | Align wording with claims ledger before major public push. |
| `docs/PRODUCT_ARCHITECTURE.md` | Control Tower architecture | Canonical first product slice | Use as trunk for paper exchange and receipt flow. |
| `ARCHITECTURE.md` | System architecture source | Source material | Map claims into proof ledger. |
| `GOVERNANCE.md` | Governance source | Source material | Expand into operating charter. |
| `AGENT_AUTHORITY_CHARTER.md` | Agent authority source | Source material | Convert to promotion/demotion standard. |
| `COMPLIANCE_BOUNDARY.md` | Compliance source | Source material | Convert to regulatory boundary matrix. |
| `RISK.md` | Risk source | Source material | Convert to risk gate specification. |
| `SECURITY.md` | Security source | Source material | Convert to secrets/key custody boundary. |
| `EXECUTION_PROTOCOL.md` | Execution source | Source material | Convert to execution lifecycle proof pack. |
| `COMPUTE_RECEIPT_PROTOCOL.md` | Receipt proof source | Source material | Convert to verifier-oriented proof pack. |
| `RESEARCH_PAPERS.md` | Research source index | Source material | Split into focused papers after proof boundary is set. |

## 3. Artifact Families

| Family | Purpose | Release gate |
| --- | --- | --- |
| Product papers | Define what the app is and what users can actually do. | Must match implemented app flows or be marked roadmap. |
| Charters | Define governance, roles, authority, and prohibited actions. | Must define enforcement and amendment process. |
| Compliance boundaries | Distinguish simulation, paper, own-capital, third-party capital, tokens, custody, and exchange activity. | Must be reviewed before public launch language expands. |
| Proof packs | Tie claims to receipts, tests, hashes, logs, and verification procedures. | Must include a failure and replay model. |
| Research papers | Explain technical thesis and market reasoning. | Must cite product boundaries and avoid live-readiness claims without evidence. |
| Benchmark packs | Define hard-to-game performance and safety tests. | Must run before certification or production-grade claims. |

## 4. First Document Sprint

| Order | Artifact | Why first |
| --- | --- | --- |
| 1 | `docs/packets/PARRALAX_ARTIFACT_PACKET_INDEX.md` | Controls the document civilization and prevents scatter. |
| 2 | `docs/compliance/REGULATORY_BOUNDARY_MATRIX.md` | Prevents token/trading/fund claims from outrunning legal/product posture. |
| 3 | `docs/proof/CLAIMS_VERIFICATION_LEDGER.md` | Maps claims to evidence and allowed wording. |
| 4 | `docs/architecture/ICP_TOKEN_LEDGER_ARCHITECTURE.md` | Defines how ICP tokens and ledgers become real without fake deployment claims. |
| 5 | `docs/product/WALLET_TRADING_TRANSFER_APP_ARCHITECTURE.md` | Defines the combined wallet, trading, multi-ledger, and money transfer product. |

## 5. Full Packet Backlog

| Priority | Filename | Type | Purpose |
| --- | --- | --- | --- |
| P0 | `docs/compliance/REGULATORY_BOUNDARY_MATRIX.md` | Compliance matrix | Map actions to operating modes and compliance gates. |
| P0 | `docs/proof/CLAIMS_VERIFICATION_LEDGER.md` | Proof ledger | Track major product claims, evidence, tests, and allowed wording. |
| P0 | `docs/architecture/ICP_TOKEN_LEDGER_ARCHITECTURE.md` | Runtime architecture | Define ICRC ledgers, canister boundaries, and token deployment gates. |
| P0 | `docs/product/WALLET_TRADING_TRANSFER_APP_ARCHITECTURE.md` | Product architecture | Define wallet, ledger, trading, transfer, and operator flows. |
| P1 | `docs/product/PARRALAX_CONTROL_TOWER_PRODUCT_PAPER.md` | Product paper | External-facing product paper after claims are controlled. |
| P1 | `docs/governance/GOVERNANCE_OPERATING_CHARTER.md` | Charter | Decision rights, emergency powers, review cadence, amendments. |
| P1 | `docs/governance/AGENT_AUTHORITY_AND_PROMOTION_STANDARD.md` | Governance standard | Promotion/demotion evidence, authority ceilings, kill-switch triggers. |
| P1 | `docs/risk/RISK_GATE_SPECIFICATION.md` | Risk spec | Enforceable thresholds, receipt outputs, failure handling. |
| P1 | `docs/security/SECURITY_AND_SECRETS_BOUNDARY.md` | Security boundary | API secrets, signing, key custody, incident escalation. |
| P1 | `docs/proof/COMPUTE_RECEIPT_PROOF_PACK.md` | Proof pack | Receipt verification, replay checks, chain continuity. |
| P1 | `docs/proof/EXECUTION_LIFECYCLE_PROOF_PACK.md` | Proof pack | Signal to settlement lifecycle proof. |
| P2 | `docs/research/MARKET_MICROSTRUCTURE_RESEARCH_PAPER.md` | Research paper | Market microstructure and execution research. |
| P2 | `docs/research/AI_AGENT_GOVERNANCE_RESEARCH_PAPER.md` | Research paper | Agent authority, alignment, and governance paper. |
| P2 | `docs/research/COMPUTE_RECEIPTS_AND_AUDITABLE_AI_EXECUTION.md` | Research/proof paper | Thesis for auditable agentic finance. |
| P2 | `docs/charters/FUND_OPERATOR_CHARTER.md` | Charter | Operator role, capital boundaries, launch gates. |
| P2 | `docs/charters/ASSET_ISSUANCE_AND_TOKEN_BOUNDARY_CHARTER.md` | Charter | Token/NFT issuance boundaries and prohibited claims. |
| P2 | `docs/compliance/DATA_RETENTION_AND_AUDIT_POLICY.md` | Compliance policy | Record retention, audit exports, privacy boundaries. |
| P2 | `docs/benchmarks/BENCHMARK_AND_CHAOS_TEST_PLAN.md` | Benchmark pack | Latency, risk, receipt, permission, replay, stress benchmarks. |
| P3 | `docs/proof/RELEASE_READINESS_PROOF_PACKET.md` | Release proof pack | Final deploy/readiness gate tying docs, tests, claims, and known gaps. |
| P3 | `docs/product/INVESTOR_AND_OPERATOR_BRIEF.md` | Market brief | External narrative after evidence gates are satisfied. |

## 6. Release Gates

| Gate | Meaning | Required evidence |
| --- | --- | --- |
| `source` | Source doctrine exists. | File exists and is linked from packet index. |
| `draft` | Artifact drafted but not verified. | Owner, purpose, assumptions, and gaps stated. |
| `proof-mapped` | Claims tied to repo/test/receipt evidence. | Claims ledger rows complete. |
| `implementation-linked` | Artifact references concrete files or API contracts. | File paths, methods, schemas, or workflow names included. |
| `release-candidate` | Ready for external or operator use. | Tests/benchmarks linked and unresolved risks listed. |
| `public` | Safe for public narrative. | Compliance boundary and claims ledger permit wording. |

## 7. Monitor Next

The next control action is to keep `REGULATORY_BOUNDARY_MATRIX.md` and `CLAIMS_VERIFICATION_LEDGER.md` updated before any README, token, fund, live trading, or investor-facing language is expanded.
