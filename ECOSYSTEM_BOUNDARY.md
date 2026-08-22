# PARRALAX Ecosystem Boundary

PARRALAX participates in the NEXUS ecosystem as **verifiable market research, risk evaluation, execution planning, simulation, and receipt infrastructure**.

## Default mode

Ecosystem-routed actions are **paper/simulation by default**. A plan, signal, backtest, portfolio calculation, or execution simulation is not evidence that money was moved or an order reached a broker/exchange.

## Live execution gate

A live financial action requires all of the following outside the generic ecosystem contract:

1. an authenticated, operator-owned broker/exchange connection;
2. tenant/account authorization;
3. explicit risk-policy approval;
4. order parameters and notional limits;
5. an irreversible-action confirmation where required;
6. broker/exchange acknowledgement evidence;
7. transaction/order identifiers;
8. a `nexus.execution-receipt.v1` that references the external evidence.

Without those artifacts, release/UI/API language must describe the result as **planned, simulated, paper, backtested, or unverified** as applicable.

## Public language

Preferred public framing:

- verifiable execution infrastructure
- machine-checkable risk/netting inputs
- compute and execution receipts
- synchronization/coordination layer
- auditability and governance boundaries

Do not infer financial returns, production trading status, sub-millisecond live execution, AUM, broker connectivity, or regulatory approval from source code alone.

## NEXUS boundary

NEXUS may route and govern PARRALAX tasks. It does not grant brokerage authority. POCKET may provide identity/tenant policy. It does not supply financial authorization by itself.

## Safety and reversibility

Research, simulation, and paper execution can be automated within budgets. External funds movement and live market orders are separate irreversible/high-impact boundaries and require the live execution gate above.
