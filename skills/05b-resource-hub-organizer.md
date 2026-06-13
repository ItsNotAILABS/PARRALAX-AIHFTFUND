# Skill 05b — resource-hub-organizer

## ALPHA MEDINA Architecture · Resource Hub / Public Output Layer

**Purpose:** Organizes ideas, artifacts, doctrine, and outputs into main topics, subtopics, sub-subtopics, collections, and release paths. This is the structural memory and categorization engine — it ensures nothing produced by the organism is orphaned, miscategorized, or lost.

**Governing House:** Casa de Medina (Crown) + Domus Expressio (Projection)  
**MS Layer:** MESO → MACRO (operating structure projects to external organization)  
**Law Alignment:** L10 (Organization), L11 (Naming), L03 (Coherence), L08 (Inheritance)

---

## Input Contract

The user provides ONE of the following:

| Input Type | Description | Example |
|------------|-------------|---------|
| `new_artifact` | A produced artifact needing placement | Doctrine note, roadmap, architecture spec, essay, code module |
| `idea_collection` | Multiple related ideas needing structure | A brainstorm output, meeting notes, research dump |
| `reorganization_request` | Existing structure needing improvement | "The BUILDER_WORKSPACE is getting disorganized" |
| `release_candidate` | Content ready for external publication path | An essay, whitepaper, or research note ready for public |
| `category_question` | "Where does this belong?" inquiry | "Should this go in ORGANISM_SPACE or BUILDER_WORKSPACE?" |
| `topic_expansion` | A topic that has grown beyond its current structure | "Construction intelligence now has 15 artifacts — needs subtopics" |

---

## Output Contract

The skill produces a **RESOURCE ORGANIZATION MAP** with the following structure:

### Output Structure

```
┌──────────────────────────────────────────────────────────┐
│  RESOURCE ORGANIZATION MAP                               │
├──────────────────────────────────────────────────────────┤
│  1. PLACEMENT DECISION                                   │
│     - Where does this artifact belong?                   │
│     - Which house governs it?                            │
│     - Which division within that house?                  │
│     - Which MS layer does it operate at?                 │
│     - File path recommendation                          │
├──────────────────────────────────────────────────────────┤
│  2. TOPIC HIERARCHY                                      │
│     - Main Topic (top-level category)                    │
│       └─ Subtopic (second-level grouping)                │
│           └─ Sub-subtopic (third-level specifics)        │
│     - Naming convention applied                          │
│     - Index/navigation entry created                     │
├──────────────────────────────────────────────────────────┤
│  3. COLLECTION MEMBERSHIP                                │
│     - Which collections does this belong to?             │
│     - Cross-references to related artifacts              │
│     - Predecessor/successor relationships                │
│     - Doctrine lineage connections                       │
├──────────────────────────────────────────────────────────┤
│  4. RELEASE PATH                                         │
│     - Classification: SOVEREIGN_PRIVATE / TRUNK / PUBLIC │
│     - If PUBLIC: publication channel and format          │
│     - If TRUNK: access boundary definition               │
│     - If SOVEREIGN_PRIVATE: concealment verification     │
│     - Dependencies before release                        │
├──────────────────────────────────────────────────────────┤
│  5. NAVIGATION UPDATE                                    │
│     - Index entries to add/update                        │
│     - Navigation artifacts affected                      │
│     - Cross-reference links to create                    │
│     - Orphan check: is anything now unreachable?         │
└──────────────────────────────────────────────────────────┘
```

### Organization Quality Gates

- **No orphans:** Every artifact must be reachable from at least one navigation index
- **Correct jurisdiction:** House and division assignment must follow the Domus charter
- **Naming compliance:** All names follow established conventions (L11)
- **Hierarchy depth:** Maximum 4 levels (Main → Sub → Sub-sub → Leaf)
- **Cross-referenced:** Related artifacts must link to each other

---

## Connectors / Tools

| Connector | Purpose | Required |
|-----------|---------|----------|
| GitHub (repository files) | Access full repository structure and indexes | ✅ Yes |
| File system | Read directory structures, write index/navigation files | ✅ Yes |
| BUILDER_WORKSPACE | Reference house structure and division registry | ✅ Yes |
| FOUNDER_SPACE | Access navigation artifacts and indexes | ✅ Yes |
| ORGANISM_SPACE | Reference MS layers and consciousness structures | ✅ Yes |
| EXTERNAL | Manage public-facing resource organization | ⚠️ Optional |
| Spreadsheet | Tabular catalog and inventory management | ⚠️ Optional |

---

## Organization Principles

### Principle 1: Everything Has a Home
- No artifact may exist without house assignment, division placement, and index entry
- If an artifact doesn't fit existing structure, the structure grows — the artifact is never orphaned

### Principle 2: Navigate in ≤ 3 Clicks
- From any top-level index, any artifact must be reachable in 3 navigation steps maximum
- If navigation depth exceeds this, create intermediate index nodes

### Principle 3: Collections Are Living
- A collection is not a static folder — it's a living group that grows, splits, and reorganizes
- When a collection exceeds 13 items (Fibonacci), evaluate splitting into subcollections

### Principle 4: Release Paths Are One-Way
- SOVEREIGN_PRIVATE → TRUNK requires explicit promotion
- TRUNK → PUBLIC requires explicit release authorization
- PUBLIC → SOVEREIGN_PRIVATE is impossible (information entropy is irreversible)

### Principle 5: The Catalog Is the Balance Sheet
- Every organized artifact represents crystallized intelligence
- The total organized catalog = the organism's intellectual capital inventory
- Growth of the catalog = growth of sovereign value

---

## Repository Structure Reference

```
PARALLAX-AIHFTFUND/
├── FOUNDER_SPACE/          ← Sovereign declaration, navigation, founder doctrine
├── BUILDER_WORKSPACE/      ← Engines, houses, laws, technology artifacts
│   ├── ENGINES/
│   ├── HOUSES/
│   ├── LAWS/
│   └── TECHNOLOGY_ARTIFACTS/
├── ORGANISM_SPACE/         ← Consciousness, MS layers, entanglement, houses
│   ├── CONSCIOUSNESS/
│   ├── MS_LAYERS/
│   ├── HOUSES/
│   └── ENTANGALA/
├── EXTERNAL/               ← Public-facing materials
├── skills/                 ← ALPHA MEDINA tech engine skills (this system)
├── src/                    ← Source code
│   ├── backend/            ← Motoko canister organisms
│   ├── frontend/           ← React/TypeScript UI organisms
│   └── brain/              ← Brain architecture modules
├── docs/                   ← Documentation
├── rust/                   ← Rust modules
├── python/                 ← Python modules
└── services/               ← Service definitions
```

---

## Interaction with Other Skills

| Skill | Relationship |
|-------|-------------|
| `medina-operating-system` | Receives OIS-processed artifacts for placement |
| `doctrine-synthesizer` | Receives completed doctrine artifacts for categorization |
| `anti-drift-reviewer` | Validates organizational coherence and hierarchy integrity |
| `mission-roadmap-orchestrator` | Receives roadmap artifacts; organizes by project/phase |
| `worldview-expansion-engine` | Receives expansion maps for multi-dimensional filing |

---

## Anti-Patterns (This Skill Must Never)

- Create deeply nested hierarchies (4+ levels without navigation shortcuts)
- Allow orphaned artifacts (anything unreachable from a navigation index)
- Misclassify release paths (PUBLIC content that should be SOVEREIGN_PRIVATE)
- Apply flat structure where hierarchy is needed (dumping everything in one folder)
- Ignore cross-references (related artifacts that don't link to each other)
- Create navigation entries without verifying the target exists

---

*resource-hub-organizer · ALPHA MEDINA Skill 05b · The Structural Memory Engine*  
*"The catalog is the balance sheet. Every act of production is a financial event."*
