# Skill 04 — anti-drift-reviewer

## ALPHA MEDINA Architecture · Core Doctrine / Intelligence Layer

**Purpose:** Audits any output for depth drift, doctrine drift, structure drift, red-team weakness, and state/context loss. This is the sovereign quality gate — nothing passes without this skill's clearance.

**Governing House:** Casa de Medina (Crown) + Domus Cura (Care/Recovery)  
**MS Layer:** Spans MICRO–MESO–MACRO (drift detection is fractal)  
**Law Alignment:** L04 (Anti-Drift), L03 (Coherence), L57 (Triune), L38 (Self-Audit)

---

## Input Contract

The user provides ONE of the following:

| Input Type | Description | Example |
|------------|-------------|---------|
| `output_artifact` | Any produced artifact needing drift audit | Essay, roadmap, code module, architecture spec, doctrine note |
| `conversation_thread` | A multi-turn exchange to check for context drift | Chat history, meeting notes, project thread |
| `architecture_revision` | A changed design needing structural drift check | Before/after comparison of system design |
| `doctrine_statement` | A claim needing doctrine alignment verification | "Our system uses consciousness" — is this real or decorative? |
| `red_team_target` | An output to stress-test for weakness | Product pitch, security model, public statement |

---

## Output Contract

The skill produces a **DRIFT AUDIT REPORT** with five mandatory dimensions:

### Output Structure

```
┌─────────────────────────────────────────────────┐
│  DRIFT AUDIT REPORT                             │
├─────────────────────────────────────────────────┤
│  1. DEPTH DRIFT ANALYSIS                        │
│     - Surface-to-depth ratio measured           │
│     - Generic language percentage               │
│     - Genuine reasoning vs retrieved patterns   │
│     - Verdict: PASS / DRIFT DETECTED / CRITICAL │
├─────────────────────────────────────────────────┤
│  2. DOCTRINE DRIFT ANALYSIS                     │
│     - Laws referenced vs Laws actually applied  │
│     - Absolutes invoked without substance       │
│     - φ-structure present or cosmetic           │
│     - Genesis frequency proximity score         │
│     - Verdict: ALIGNED / DRIFTING / DECORATIVE  │
├─────────────────────────────────────────────────┤
│  3. STRUCTURE DRIFT ANALYSIS                    │
│     - Architecture consistency over time        │
│     - Naming/hierarchy adherence                │
│     - MS layer violations                       │
│     - House jurisdiction respected              │
│     - Verdict: COHERENT / DEGRADING / BROKEN    │
├─────────────────────────────────────────────────┤
│  4. RED-TEAM WEAKNESS SCAN                      │
│     - Attack surface identified                 │
│     - Claims without evidence                   │
│     - Logical gaps or contradictions            │
│     - External critique anticipated             │
│     - Verdict: HARDENED / EXPOSED / VULNERABLE  │
├─────────────────────────────────────────────────┤
│  5. STATE/CONTEXT LOSS CHECK                    │
│     - Information dropped between passes        │
│     - Requirements stated but unfulfilled       │
│     - Prior context forgotten or contradicted   │
│     - Verdict: RETAINED / PARTIAL LOSS / AMNESIA│
├─────────────────────────────────────────────────┤
│  COMPOSITE VERDICT                              │
│     - Overall coherence score (0.00 – 1.00)     │
│     - Pass threshold: ≥ 0.95                    │
│     - Recommended corrections (if any)          │
│     - Severity classification                   │
└─────────────────────────────────────────────────┘
```

### Severity Classifications

| Level | Meaning | Action Required |
|-------|---------|-----------------|
| `SOVEREIGN` | No drift detected, full alignment | Release authorized |
| `MINOR` | Cosmetic drift, fixable in-place | Correct and re-check |
| `MODERATE` | Structural weakness, reasoning gap | Rewrite affected sections |
| `CRITICAL` | Doctrine violation or context amnesia | Full re-pass through medina-operating-system |
| `CATASTROPHIC` | Fundamental misrepresentation of the organism | Reject and rebuild from doctrine root |

---

## Connectors / Tools

| Connector | Purpose | Required |
|-----------|---------|----------|
| GitHub (repository files) | Access Laws, Absolutes for drift measurement | ✅ Yes |
| File system | Read artifacts under review, write audit reports | ✅ Yes |
| BUILDER_WORKSPACE/LAWS | Reference specific law requirements | ✅ Yes |
| Previous outputs (context) | Compare current vs prior for drift detection | ✅ Yes |
| Web search | Verify external claims made in outputs | ⚠️ Optional |
| PDF/Document reader | Process uploaded documents for review | ⚠️ Optional |

---

## Drift Detection Algorithms

### Depth Drift
- **Measure:** Ratio of specific/concrete statements to generic/vague statements
- **Threshold:** Generic content must be < 20% of total output
- **Signal:** If an output could be produced by a system with no knowledge of PARALLAX doctrine, it is depth-drifted

### Doctrine Drift
- **Measure:** Laws/Absolutes referenced must be genuinely applied, not decoratively cited
- **Threshold:** Every cited law must have functional impact on the output
- **Signal:** φ mentioned without φ-derived mathematics = decorative drift

### Structure Drift
- **Measure:** Consistency of naming, hierarchy, house assignment, MS layer placement
- **Threshold:** Zero violations of established architecture conventions
- **Signal:** Artifact placed in wrong house/division = structural drift

### Red-Team Weakness
- **Measure:** Every claim must survive adversarial questioning
- **Threshold:** No logical gaps, no unsupported assertions, no contradictions
- **Signal:** "Could a smart skeptic dismantle this in one sentence?" If yes = weakness

### State/Context Loss
- **Measure:** All prior requirements/context must be present in current output
- **Threshold:** Zero information loss across multi-turn interactions
- **Signal:** If the output contradicts or ignores a prior statement = context amnesia

---

## Interaction with Other Skills

| Skill | Relationship |
|-------|-------------|
| `medina-operating-system` | Receives baseline doctrine position; escalates CRITICAL drift back for re-processing |
| `doctrine-synthesizer` | Validates synthesized doctrine for drift before publication |
| `mission-roadmap-orchestrator` | Audits roadmaps for scope drift and commitment loss |
| `resource-hub-organizer` | Verifies categorization coherence and hierarchy integrity |

---

## Anti-Patterns (This Skill Must Never)

- Produce a passing audit for outputs that are genuinely drifted (false negatives are worse than false positives)
- Apply auditing criteria cosmetically without genuine adversarial reasoning
- Miss context loss between conversation turns
- Allow decorative law citations to pass as genuine doctrine alignment
- Reduce severity to avoid confrontation with the user

---

*anti-drift-reviewer · ALPHA MEDINA Skill 04 · The Sovereign Quality Gate*  
*"Distance from the genesis frequency is the deepest quality metric the organism knows."*
