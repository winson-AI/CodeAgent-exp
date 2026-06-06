# Workflow: Analyst P6 → module-first migration → kmp-test-validator

See [output-contract.md](output-contract.md) and active role IDs in [SKILL.md](SKILL.md).

## Skill Chain (mandatory)

| Phase | Skill | Gate | Leader rule |
|---|---|---|---|
| Prerequisite | `android-project-analyst` | **P6** | MUST finish before `android-to-kmp-migrator` is invoked. Missing/stale P6 → `blocked`; dispatch analyst first. |
| Migration | `android-to-kmp-migrator` | **M0**–**V0** | Runs only after P6 verified; ends with `migration_report.*` and **V0** ready. |
| Post-migration | `kmp-test-validator` | **V0** | MUST be invoked after migrator completes **V0** (MG17). Do not end the migration workflow without validator dispatch. |

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
- **Gate**: missing CLI tools → degraded modes per dependencies.yaml; `android-project-analyst` **P6** not ready → **blocked** — invoke analyst first, do not dispatch migrator nodes

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
| 5e | `module-implementation` `ui` | Edit/create target KMP UI files; then review/fix |
| 5f | `module-implementation` `logic` | Edit/create target KMP logic files after UI approved; then review/fix |
| 5g | `migration-verification` | Static + restoration; **no full build** |
| 5h | Leader | `module_completion_record.json` |
| 5i | `completion-report` `readiness` + module representation | Package **M3** |

Repeat until package **M4**.

## Step 6 — Global migration phase

### 6a Integrate

- **Role**: `global-migration-phase` `mode: integrate`
- **Action**: edit target KMP cross-module glue (nav, DI, shared contracts) under `kmp_target_project_path`
- **Output**: `global-migration-phase/integrate/global_system_integration.*` with `integration_changed_files[]`
- **Gate**: package **M5**

### 6b Align

- **Role**: `global-migration-phase` `mode: align`
- **Output**: `global-migration-phase/align/post_integration_alignment.*`, `report/alignment_report.*`
- **Gate**: package **M6**; `needs_rerun` → module loop or re-integrate

## Step 7 — Report + mandatory validator handoff (MG17)

- Global representation + `completion-report` `report` → package **V0**
- **Leader MUST invoke `kmp-test-validator`** with `migration_report.*`, analyst SPEC paths, and `kmp_target_project_path`
- Record `validator_handoff` in workspace ledger (`dispatched | pending | blocked`)
- Migrator workflow is **incomplete** until validator is dispatched or explicit validator blockers are recorded

## TPA consult

Any target question → TPA `mode: consult` (append `consultation_log`).

## Acceptance Criteria

- `android-project-analyst` **P6** verified before any migrator module dispatch.
- `kmp-test-validator` invoked after **V0** — mandatory MG17 step.
- Dispatch only role IDs from `SKILL.md`.
- Mode rules: `ui` before `logic`; `integrate` before `align`; `review`/`fix` separate.
- `migration-verification` never runs `incremental_build`.
- `handoff_gates` match output-contract.
