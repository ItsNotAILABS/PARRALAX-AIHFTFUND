# Document Plan: PARRALAX Major Product Run

## Documents being created in this run

- `docs/packets/PARRALAX_ARTIFACT_PACKET_INDEX.md`
  - Type: packet index and document control map.
  - Required skill/instruction posture: repo-grounded artifact generation; document law; proof-chain continuity.
  - Validation: must classify existing and next documents by role, status, dependency, and release gate.

- `docs/product/WALLET_TRADING_TRANSFER_APP_ARCHITECTURE.md`
  - Type: product/runtime architecture.
  - Required skill/instruction posture: stack architecture, deployment surface planning, wallet/ledger/trading flow design.
  - Validation: must define app surfaces, backend contracts, money movement states, idempotency, and paper/live gates.

- `docs/architecture/ICP_TOKEN_LEDGER_ARCHITECTURE.md`
  - Type: ICP token and ledger architecture.
  - Required skill/instruction posture: Motoko backend authority, ICP ledger boundaries, token standards, deployment gating.
  - Validation: must avoid claiming deployed tokens; must separate local/test ledger from production token issuance.

- `docs/compliance/REGULATORY_BOUNDARY_MATRIX.md`
  - Type: compliance boundary matrix.
  - Required skill/instruction posture: compliance containment, product-mode boundaries, risk/overclaim prevention.
  - Validation: must distinguish simulation, paper, own-capital, external-capital, token, custody, and exchange modes.

- `docs/proof/CLAIMS_VERIFICATION_LEDGER.md`
  - Type: proof/claims ledger.
  - Required skill/instruction posture: proof-chain audit, release gating, production claim discipline.
  - Validation: every major product claim must have evidence status and allowed public wording.

## Aesthetic and structural validation

These are Markdown repository artifacts, not DOCX/PDF deliverables. They must be concise enough to maintain, structured enough to become governance tissue, and explicit about proof status.

## Requested/discovered revisions

- User asked for a major run across tests, real platform surface, tokens, wallet, multi-ledgers, trading app, money transfer app, research papers, charters, and documents.
- CI diagnosis found invalid workflow YAML, frontend typecheck drift, missing `quantitative` module, outdated webpack workflow, and actor hook contract drift.
- This run creates the controlling documents and compatibility patches while keeping live money/token deployment gated until real credentials, contracts, and legal/compliance checks exist.
