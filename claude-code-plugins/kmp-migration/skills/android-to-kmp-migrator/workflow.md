# Workflow: Analyst P6 → module-first migration → kmp-test-validator

See [output-contract.md](output-contract.md) and active role IDs in [SKILL.md](SKILL.md).

## Skill Chain (mandatory)

| Phase | Skill | Gate | Leader rule |
|---|---|---|---|
| Prerequisite | `android-project-analyst` ×2 | source **P6** + target subsystem | Both understand subsystems MUST finish before `android-to-kmp-migrator` is invoked. Missing/stale source P6 or (route `migration`) target subsystem → `blocked`; dispatch the missing analyst run first. |
| Migration | `android-to-kmp-migrator` | **M0**–**V0** | Runs only after P6 verified; ends with `migration_report.*` and **V0** ready. |
| Post-migration | `kmp-test-validator` | **V0** | MUST be invoked after migrator completes **V0** (MG17). Do not end the migration workflow without validator dispatch. |

## Target KMP Edit Flow

After analyst **P6** understanding (read-only), the migrator **edits** `kmp_target_project_path`:

1. **Per module**: `migration-prep` (optional scaffold) → `module-implementation` `ui` → `logic` (required target edits) → review/fix remediation as needed.
2. **Global**: `global-migration-phase` `integrate` edits cross-module glue and entry-point wiring.
3. **Align** is read-only verification — reruns integrate or module implementation when target edits are missing or wrong.

Planning and TPA artifacts route edits; they do not replace implementation.

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
    MODREP --> WSR[Refresh workspace-state sync todos + steps]
  end

  LOOP --> MOD
  MOD --> WSR
  WSR --> M4{Package M4?}
  M4 -- No --> LOOP
  M4 -- Yes --> GMP1[global-migration-phase mode integrate]
  GMP1 --> GMP2[global-migration-phase mode align]
  GMP2 -->|needs_rerun| LOOP
  GMP2 -->|passed| GLOB[global_migration_representation]
  GLOB --> REPORT[completion-report report]
  REPORT --> WSF[Refresh workspace-state final sync]
  WSF --> KV[kmp-test-validator V0]
```

## Step 0 — Pre-flight

- **Executor**: Leader
- **Input**: [dependencies.yaml](dependencies.yaml) — `tools[]` (`rg`, `git`, `curl`), `optional_mcp.jetbrains`, `upstream_inputs` **source understand subsystem `P6`** and **target understand subsystem** (route `migration`); the **user input / migration request**; optional adapter `partial_migration`
- **Output**: `run_manifest.json` → `dependency_preflight` (CLI status, MCP availability, source `P6` + target subsystem readiness pointers), `design_mode` (architecture pattern decision), `raw_user_task`, `user_task_constraints`, `partial_migration`, and `mock_data_preflight`
- **Gate**: missing CLI tools → degraded modes per dependencies.yaml; source subsystem **P6** not ready, or target understand subsystem missing for route `migration` → **blocked** — invoke `android-project-analyst` for the missing subsystem first, do not dispatch migrator nodes

### Step 0a — Identify design mode (default MVI)

- Scan the **user input** for an explicit or implied presentation architecture:
  - **`mvvm`** signals: "MVVM", shared `ViewModel`, `StateFlow` / `uiState`, `viewModelScope`, `collectAsStateWithLifecycle`, KMP-ObservableViewModel, SKIE → `references/kmp-mvvm.md`
  - **`mvi`** signals: "MVI", FlowRedux, state machine, reducer, intent, unidirectional, sealed `State`/`Action`, `dispatch`, `inState`, `onEnter` → `references/kmp-mvi-flowredux.md`
- **No clear signal → default `mvi`.**
- Record `design_mode: { value: "mvi | mvvm", source: "user_input | default", signals: [], architecture_reference_path: "" }` in `run_manifest.json`.
- Freeze `design_mode` for the run; pass `design_mode` + `architecture_reference_path` into every architecture-producing dispatch (planning-gate, prep, module-implementation, module-node-review-fix, global-migration-phase) and to TPA for target-pattern detection.

### Step 0b — Resolve user task, partial scope, and mock-data preflight

- Record the exact user request in `raw_user_task` and normalize actionable constraints into `user_task_constraints`.
- If adapter/user input declares partial migration, resolve `partial_migration.migration_module_ids`, `allowed_source_roots`, and `validation_scope` from analyst P6 indexes and `focused_analysis`. If the requested scope cannot be resolved, block instead of broadening to full-project migration.
- If no explicit partial migration request exists, set `partial_migration.enabled: false` and migrate the whole analyst assembly scope.
- Allow mock data only when a dependency gap blocks local migration wiring and the user/task permits it. Record `mock_data_preflight.allowed`, reason, scope, allowed modules, expiry condition, and tracking ids. Mock data is temporary migration scaffolding, not production completion.

## Step 1 — Upstream + output root (fetch comprehensive context)

- Resolve the shared base `agents_root = <output_dir or ~/.a2c_agents>` (use the upstream-supplied base/`output_root` verbatim), lock `output_root = <agents_root>/migration/android-to-kmp-migrator`, and confirm both understand subsystem roots resolve under the same `agents_root` (`.../understand/android-project-analyst/{source,target}`).
- Fetch the comprehensive context from **both** understand subsystems: verify the source subsystem package **P6** and (for route `migration`) the target subsystem; write `upstream_analyst_index.json` with `source_subsystem` and `target_subsystem` blocks, including the source `focused_analysis` snapshot when present.
- **Clarify the migration task** here: confirm whether the request is **full** or **partial** migration from `partial_migration` / `raw_user_task`, and resolve which source module(s) transfer into the target. Partial migration stays bounded to the requested module/feature/subset; full migration covers the source assembly scope.
- For partial migration, the source P6 must either already be focused to the requested module/feature or contain enough module-index evidence to restrict migrator inventory without inspecting out-of-scope modules; the target subsystem provides the anchor candidates for the requested slice.

## Step 2 — Migration inventory

- `migration_module_inventory.*`, `modules_migration_index.json`, per-module `module_brief.json`.
- For partial migration, inventory only requested modules plus explicitly required integration seams. Out-of-scope modules are dependency pointers, not scheduled implementation work.

## Step 3 — Workspace state

- Init ledger with `pipeline_steps[]` (all schedule rows `not_started`) and empty `migration_todo_list[]`; track handoff gates **M0**–**V0**
- **Refresh after**: module inventory, each module node group (sync todos + steps), each module representation, global integrate/align, global report
- Each refresh MUST update `migration_todo_list[].status` and `pipeline_steps[].status` from verified artifacts — do not advance the controller on stale ledger

## Step 4 — Target project assistant (global)

- `mode: global_baseline` → `target_alignment_revision.*`, consuming the **Target Project Subsystem** understand artifacts (`target_analyst_output_root`) as primary evidence; TPA maps legacy scopes to target anchors rather than re-analyzing the target from scratch.

## Step 5 — Per-module pipeline

| Step | Role | Notes |
|---|---|---|
| 5a | TPA `module_anchors` | Package **M2** per module |
| 5b | `migration-planning-gate` | Planning + dep/platform in one pass; preserve user constraints, partial boundary, and `mock_data_plan` |
| 5c | `migration-prep` | Presentation + state/data + `analytics_expectations[]`; prepare permitted mock fixtures only when preflight allows |
| 5d | `module-node-review-fix` | After prep if file-changing |
| 5e | `module-implementation` `ui` | Edit/create focused target KMP UI files only; then review/fix |
| 5f | `module-implementation` `logic` | Edit/create focused target KMP logic + **埋点** restoration; mock only preflight-approved gaps; then review/fix |
| 5g | `migration-verification` | Static + restoration incl. **analytics_restoration** (埋点 parity) and mock-data usage; **no full build** |
| 5h | Leader | `module_completion_record.json` |
| 5i | `completion-report` `readiness` + module representation | Package **M3** |

Repeat until package **M4**.

## Step 6 — Global migration phase

### 6a Integrate

- **Role**: `global-migration-phase` `mode: integrate`
- **Action**: edit target KMP cross-module glue (nav, DI, shared contracts), **wire app-shell entry points** (launcher, Application/startup, root NavHost start destination, deep links), and **analytics SDK/init/facade** when legacy uses analytics, under `kmp_target_project_path`, using TPA `entry_point_anchors[]` and analyst `presentation_resource` `entry_points[]`. In partial migration, integrate only scoped routes/entry paths and explicit seams needed for the requested feature/module.
- **Output**: `global-migration-phase/integrate/global_system_integration.*` with `integration_changed_files[]`, `entry_point_wiring[]`, and `analytics_sdk_wiring[]`
- **Gate**: package **M5**

### 6b Align

- **Role**: `global-migration-phase` `mode: align`
- **Action**: read-only comparison including **entry point alignment** and **analytics alignment** — verify each Android entry resolves to the correct KMP shell path; verify legacy 埋点 inventory matches migrated track/report calls and global analytics SDK wiring
- **Output**: `global-migration-phase/align/post_integration_alignment.*` with `entry_point_alignment_results[]`, `analytics_alignment_results[]`, `global_alignment_results.entry_points`, `global_alignment_results.analytics`, plus `report/alignment_report.*`
- **Gate**: package **M6**; entry point, analytics SDK, or cross-module mismatch → `rerun_global_integration` or module loop

## Step 7 — Report + mandatory validator handoff (MG17)

- Global representation + `completion-report` `report` → package **V0**; report must include `partial_migration` and `mock_data_usage_summary` when applicable.
- **Leader MUST invoke `kmp-test-validator`** with `migration_report.*`, analyst SPEC paths, and `kmp_target_project_path`
- Record `validator_handoff` in workspace ledger (`dispatched | pending | blocked`)
- Migrator workflow is **incomplete** until validator is dispatched or explicit validator blockers are recorded

## TPA consult

Any target question → TPA `mode: consult` (append `consultation_log`).

## Acceptance Criteria

- Source understand subsystem **P6** **and** (for route `migration`) the target understand subsystem verified before any migrator module dispatch; both recorded in `upstream_analyst_index.json`.
- Migration task clarified as full or partial at Step 1, with the requested source module(s) resolved for transfer into the target.
- `design_mode` identified from user input at Step 0 (default `mvi`) and recorded in `run_manifest.json`; architecture-producing dispatches carry `design_mode` + `architecture_reference_path`.
- `raw_user_task`, `user_task_constraints`, `partial_migration`, and `mock_data_preflight` recorded at Step 0 and passed through planning/prep/implementation/verification/report dispatches.
- Partial migration never broadens to whole-project implementation; unresolved focused scope blocks instead of guessing.
- Mock data is used only when preflight-approved and appears in planning, implementation, verification, and final report follow-ups.
- Target KMP files created or updated under `kmp_target_project_path` for every module requiring implementation; `target_changed_files[]` aggregated in `migration_report.json`.
- `kmp-test-validator` invoked after **V0** — mandatory MG17 step.
- Dispatch only role IDs from `SKILL.md`.
- Mode rules: `ui` before `logic`; `integrate` before `align`; `review`/`fix` separate.
- `migration-verification` never runs `incremental_build`.
- Per-module and global **analytics_restoration** (埋点) parity verified before **M3** / **M6**; runtime analytics **reporting** deferred to `kmp-test-validator`.
- `handoff_gates` match output-contract.
