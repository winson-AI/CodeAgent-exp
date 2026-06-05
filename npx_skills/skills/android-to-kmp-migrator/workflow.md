# Workflow: Analyst P6 → module-first migration → kmp-test-validator

See [output-contract.md](output-contract.md) and active role IDs in [SKILL.md](SKILL.md).

## Overview

```mermaid
graph TD
  L0[Pre-flight deps] --> UP[Verify analyst P6]
  UP --> INV[migration inventory]
  INV --> WS[migration-workspace-state]
  WS --> TPA0[target-project-assistant global_baseline]
  TPA0 --> LOOP[For each migration_module_id]

  subgraph MOD[Per-module pipeline]
    TPA1[target-project-assistant module_anchors]
    TPA1 --> PG[migration-planning-gate]
    PG --> PREP[migration-prep]
    PREP --> RF1[review/fix]
    RF1 --> UI[module-implementation mode ui]
    UI --> RF2[review/fix]
    RF2 --> LOGIC[module-implementation mode logic]
    LOGIC --> RF3[review/fix]
    RF3 --> VER[migration-verification]
    VER --> MCR[module_completion_record]
    MCR --> READY[completion-report readiness]
    READY --> MODREP[module_migration_representation]
  end

  LOOP --> MOD
  MOD --> M4{Package M4?}
  M4 -- No --> LOOP
  M4 -- Yes --> GMP1[global-migration-phase mode integrate]
  GMP1 --> GMP2[global-migration-phase mode align]
  GMP2 -->|needs_rerun| LOOP
  GMP2 -->|passed| GLOB[global_migration_representation]
  GLOB --> REPORT[completion-report report]
  REPORT --> KV[kmp-test-validator V0]
```

## Step 0 — Pre-flight

- **Executor**: Leader
- **Input**: [dependencies.yaml](dependencies.yaml) — `tools[]` (`rg`, `git`, `curl`), `optional_mcp.jetbrains`, `upstream_inputs` analyst **P6**
- **Output**: `run_manifest.json` → `dependency_preflight` (CLI status, MCP availability, P6 readiness pointer)
- **Gate**: missing CLI tools → degraded modes per dependencies.yaml; analyst P6 not ready → **blocked** before module dispatch

## Step 1 — Upstream + output root

- Verify analyst package **P6**; write `upstream_analyst_index.json`.

## Step 2 — Migration inventory

- `migration_module_inventory.*`, `modules_migration_index.json`, per-module `module_brief.json`.

## Step 3 — Workspace state

- Init ledger; track handoff gates **M0**–**V0**.

## Step 4 — Target project assistant (global)

- `mode: global_baseline` → `target_alignment_revision.*`

## Step 5 — Per-module pipeline

| Step | Role | Notes |
|---|---|---|
| 5a | TPA `module_anchors` | Package **M2** per module |
| 5b | `migration-planning-gate` | Planning + dep/platform in one pass |
| 5c | `migration-prep` | Presentation + state/data in one pass |
| 5d | `module-node-review-fix` | After prep if file-changing |
| 5e | `module-implementation` `ui` | Then review/fix |
| 5f | `module-implementation` `logic` | After UI approved; then review/fix |
| 5g | `migration-verification` | Static + restoration; **no full build** |
| 5h | Leader | `module_completion_record.json` |
| 5i | `completion-report` `readiness` + module representation | Package **M3** |

Repeat until package **M4**.

## Step 6 — Global migration phase

### 6a Integrate

- **Role**: `global-migration-phase` `mode: integrate`
- **Output**: `global-migration-phase/integrate/global_system_integration.*`
- **Gate**: package **M5**

### 6b Align

- **Role**: `global-migration-phase` `mode: align`
- **Output**: `global-migration-phase/align/post_integration_alignment.*`, `report/alignment_report.*`
- **Gate**: package **M6**; `needs_rerun` → module loop or re-integrate

## Step 7 — Report + validator

- Global representation + `completion-report` `report` → package **V0** → `kmp-test-validator`

## TPA consult

Any target question → TPA `mode: consult` (append `consultation_log`).

## Acceptance Criteria

- Dispatch only role IDs from `SKILL.md`.
- Mode rules: `ui` before `logic`; `integrate` before `align`; `review`/`fix` separate.
- `migration-verification` never runs `incremental_build`.
- `handoff_gates` match output-contract.
