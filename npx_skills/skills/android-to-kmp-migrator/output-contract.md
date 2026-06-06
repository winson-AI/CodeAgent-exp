# Output Contract: File Recording System, Upstream Inputs, And Downstream Trigger Gates

This document is the **canonical path and content contract** for `android-to-kmp-migrator`. Downstream handlers (`kmp-test-validator`, `migration-task-adapter`) **MUST treat missing, empty, out-of-path, stale, or schema-invalid artifacts as hard blockers** — they do not infer from chat summaries.

The Leader and every node MUST read this file before writing artifacts. When `SKILL.md` or `workflow.md` diverge, **this file wins on paths, filenames, upstream inputs, and trigger gates**.

## Upstream Input Contract (android-project-analyst)

Migration starts only when analyst handoff package **`P6`** (see `android-project-analyst/output-contract.md`) is ready. Required upstream paths (read-only inputs):

| Upstream artifact | Purpose for migrator |
|---|---|
| `analyst_output_root/run_manifest.json` | Source path, mode, analyst `handoff_package` |
| `analyst_output_root/module-index/modules_index.json` | Legacy `module_id` → folder/dimension paths |
| `analyst_output_root/module-index/module_inventory.json` | Module schedule, scopes, `depends_on` |
| `analyst_output_root/global/migration_assembly_basis.json` | Module assembly order, integration checkpoints |
| `analyst_output_root/global/cross_module_architecture.json` | Inter-module topology for global integration |
| `analyst_output_root/global/cross_module_data_logic.json` | Cross-module data/control links |
| `analyst_output_root/global/global_representation.json` | Full-project legacy synthesis |
| `analyst_output_root/SPEC/prd.md`, `design.md`, `plan.md`, `verification.md` | Product/design/plan baseline |

Per legacy `module_id`, migrator may consume:

- `modules/<module_id>/representation/module_representation.json`
- `modules/<module_id>/dimension_index.json`
- dimension JSON artifacts under `node-results/<dimension>/`

Record all resolved upstream paths in `run_manifest.json` → `upstream_analyst_artifacts`.

**Fail closed**: if analyst `handoff_gates.P6.ready` is false or paths are missing, migrator returns `blocked` — do not start module dispatch. Dispatch or re-run `android-project-analyst` until **P6** is ready.

## Skill Chain (mandatory)

```text
android-project-analyst (P6) → android-to-kmp-migrator (M0–V0) → kmp-test-validator (V0)
```

| Skill | When | Rule |
|---|---|---|
| `android-project-analyst` | **Before** migrator | MUST finish; package **P6** required. Migrator MUST NOT be invoked until P6 is ready. |
| `android-to-kmp-migrator` | Migration body | Consumes P6 artifacts only; produces **V0** via `migration_report.*`. |
| `kmp-test-validator` | **After** migrator | MUST be invoked when **V0** is true (MG17). Migration is incomplete without validator dispatch. |

---

## Migration Output Root Layout

```text
output_root = <output_dir or ~/.a2c_agents/migration>/android-to-kmp-migrator

<output_root>/
├── run_manifest.json
├── upstream-index/
│   └── upstream_analyst_index.json              # resolved analyst paths + P6 gate snapshot
├── module-index/
│   ├── migration_module_inventory.json
│   ├── migration_module_inventory.md
│   └── modules_migration_index.json           # migration_module_id → paths + legacy module_id map
├── global/
│   ├── node-results/
│   │   ├── migration-workspace-state/
│   │   │   ├── migration_workspace_state.json
│   │   │   └── migration_workspace_state.md
│   │   ├── target-project-assistant/
│   │   │   ├── target_project_assistant.json
│   │   │   ├── target_project_assistant.md
│   │   │   ├── target_alignment_revision.json
│   │   │   └── target_alignment_revision.md
│   │   └── global-migration-phase/
│   │       ├── integrate/
│   │       │   ├── global_system_integration.json
│   │       │   └── global_system_integration.md
│   │       └── align/
│   │           ├── post_integration_alignment.json
│   │           └── post_integration_alignment.md
│   ├── global_migration_representation.json
│   └── global_migration_representation.md
├── modules/
│   └── <migration_module_id>/
│       ├── module_brief.json
│       ├── node-results/
│       │   ├── migration-workspace-state/       # per-module ledger slice
│       │   ├── target-project-assistant/        # per-module anchors (mode module_anchors)
│       │   ├── migration-planning-gate/
│       │   │   ├── migration_planning_gate.json
│       │   │   └── migration_planning_gate.md
│       │   ├── migration-prep/
│       │   │   ├── migration_prep.json
│       │   │   └── migration_prep.md
│       │   ├── module-implementation/
│       │   │   ├── ui/
│       │   │   │   ├── module_implementation_ui.json
│       │   │   │   └── module_implementation_ui.md
│       │   │   └── logic/
│       │   │       ├── module_implementation_logic.json
│       │   │       └── module_implementation_logic.md
│       │   ├── module-node-review-fix/
│       │   ├── migration-verification/
│       │   └── completion-report/
│       └── representation/
│           ├── module_migration_representation.json
│           ├── module_migration_representation.md
│           └── module_completion_record.json
└── report/
    ├── alignment_report.json
    ├── alignment_report.md
    ├── migration_report.json
    └── migration_report.md
```

### Path Variables

| Variable | Resolved path |
|---|---|
| `output_root` | `<output_dir or ~/.a2c_agents/migration>/android-to-kmp-migrator` |
| `upstream_index_dir` | `<output_root>/upstream-index` |
| `module_index_dir` | `<output_root>/module-index` |
| `module_root` | `<output_root>/modules/<migration_module_id>` |
| `node_result_dir` | `<module_root>/node-results/<node_id>` |
| `module_representation_dir` | `<module_root>/representation` |
| `global_dir` | `<output_root>/global` |
| `report_dir` | `<output_root>/report` |

### Build Boundary (mandatory)

- **Migrator verification** runs **syntax/code structure checks** and **UI/logic restoration checks** against upstream analyst evidence. It does **NOT** compile or build the entire KMP project.
- **`incremental_build` is forbidden** in `migration-verification` during migrator runs.
- **Full compile/build/preview/behavioral tests** are delegated to **`kmp-test-validator`** after `migration_report.*` handoff package **`V0`** is ready.

---

## Write Order (Leader Schedule)

| Step | Gate | Required artifacts before next step |
|---|---|---|
| `MG0` | Run lock | `run_manifest.json`, `upstream-index/upstream_analyst_index.json` |
| `MG1` | Workspace init | global `migration_workspace_state.*` |
| `MG2` | Migration index | `migration_module_inventory.*`, `modules_migration_index.json`, per-module `module_brief.json` |
| `MG3` | Target baseline | global `target-project-assistant/*` (`mode: global_baseline`) + `target_alignment_revision.*` |
| `MG4` | Per-module anchors | per-module `target-project-assistant/target_module_anchors.json` |
| `MG5` | Per-module plan+gate | `migration-planning-gate/migration_planning_gate.*` |
| `MG6`–`MG10` | Per-module impl | prep → review/fix → module-implementation `ui` → review/fix → `logic` → review/fix |
| `MG11` | Module verify | `migration_verification.*` (no full build) + `module_completion_record.json` |
| `MG12` | Module rep | `module_migration_representation.*` |
| `MG13` | All modules done | every scheduled module passes `MG11`–`MG12` |
| `MG14` | Global integrate | `global-migration-phase/integrate/global_system_integration.*` |
| `MG15` | Global align | `global-migration-phase/align/post_integration_alignment.*`, `report/alignment_report.*` (read-only) |
| `MG16` | Global rep + report | `global_migration_representation.*`, `migration_report.*` |
| `MG17` | Validator handoff | invoke `kmp-test-validator` |

---

## Handoff Packages (Downstream Trigger Conditions)

### Package `M0` — Migration run identity

| Required paths |
|---|
| `run_manifest.json` |
| `upstream-index/upstream_analyst_index.json` |
| global `migration_workspace_state.json` |

### Package `M1` — Migration module routing

| Required paths |
|---|
| `migration_module_inventory.json` |
| `modules_migration_index.json` |

### Package `M2` — Target alignment ready

| Required paths |
|---|
| Package `M1` |
| `global/node-results/target-project-assistant/target_alignment_revision.json` |
| per scheduled module: `node-results/target-project-assistant/target_module_anchors.json` |

### Package `M3` — Module implementation complete (per `migration_module_id`)

| Required paths |
|---|
| Package `M2` for this module |
| `migration-planning-gate/migration_planning_gate.json` |
| `migration-prep/migration_prep.json` |
| `module-implementation/ui/module_implementation_ui.json`, `module-implementation/logic/module_implementation_logic.json` + approved reviews |
| `migration_verification.json` with all required `check_ids` passed |
| `module_completion_record.json` with `ui_restoration` and `logic_restoration` passed |

### Package `M4` — All modules migrated

| Required paths |
|---|
| Package `M3` for every `migration_module_id` in `assembly_order` |
| all `module_migration_representation.json` files |

### Package `M5` — Global system integrated

| Required paths |
|---|
| Package `M4` |
| `global/node-results/global-migration-phase/integrate/global_system_integration.json` |
| `global_migration_representation.json` |

### Package `M6` — Post-integration alignment passed

| Required paths |
|---|
| Package `M5` |
| `global/node-results/global-migration-phase/align/post_integration_alignment.json` with `alignment_verdict: passed \| passed_with_assumptions` |
| `report/alignment_report.json` |

### Package `V0` — kmp-test-validator entry (downstream)

| Required paths |
|---|
| Package `M6` |
| `report/migration_report.json` |
| `global_migration_representation.json` |
| analyst `SPEC/*` paths recorded in `run_manifest.json` |

**Fail closed**: `kmp-test-validator` MUST NOT start when `V0` is false. It owns full project build, preview, and behavioral tests.

**Mandatory downstream**: when `V0` is true, the migrator Leader MUST invoke `kmp-test-validator` before treating the migration workflow as complete. Record `validator_handoff.status` in the workspace ledger (`pending | dispatched | blocked`).

---

## Key Artifact Content Requirements

### `upstream_analyst_index.json`

```json
{
  "analyst_output_root": "",
  "analyst_handoff_package": "P6",
  "analyst_handoff_ready": true,
  "modules_index_path": "",
  "migration_assembly_basis_path": "",
  "cross_module_architecture_path": "",
  "cross_module_data_logic_path": "",
  "global_representation_path": "",
  "spec_paths": {},
  "legacy_module_map": [{ "legacy_module_id": "", "migration_module_id": "" }]
}
```

### `modules_migration_index.json`

Machine lookup: `migration_module_id` → `legacy_module_id`, `module_output_root`, `upstream_module_representation_path`, `target_anchor_paths`, `completion_status`.

### `target_alignment_revision.json` (Target-Project-Assistant)

`target_project_layout`, `reusable_components[]`, `anchor_points[]` (legacy scope → target path), `revised_alignment[]`, `integration_constraints[]`, `consultation_log[]`.

### `target_module_anchors.json` (per module)

`migration_module_id`, `legacy_module_id`, `target_paths[]`, `anchor_points[]`, `reuse_decisions[]`, `alignment_revision_refs[]`.

### `module_completion_record.json`

```json
{
  "migration_module_id": "",
  "legacy_module_id": "",
  "completion_status": "completed | needs_rerun | blocked",
  "verification_ref": "",
  "ui_restoration": { "status": "passed | failed", "gaps": [] },
  "logic_restoration": { "status": "passed | failed", "gaps": [] },
  "upstream_match": { "module_representation_path": "", "matched_claims": [], "missing_claims": [] },
  "rerun_required": false,
  "evidence_paths": []
}
```

### `migration_verification.json` — required `check_ids` (migrator only)

- `source_set` — files in allowed source sets
- `syntax_check` — Kotlin/syntax validity on changed files (static; no full project compile)
- `api_contract` — API/model shape vs planning + analyst data contracts
- `ui_render` — static UI surface check (Compose structure/resources; no full render pipeline build)
- `ui_restoration` — migrated UI coverage vs upstream `presentation_resource` + module representation
- `logic_restoration` — migrated logic coverage vs upstream `behavior_logic` + module representation

**Forbidden**: `incremental_build`, `full_project_compile`, `gradle_assemble`.

### `global_system_integration.json`

`kmp_target_project_path`, `target_edit_summary`, `assembly_order`, `ui_transition_edges[]`, `control_logic_handoffs[]`, `data_call_edges[]`, `shared_contracts_applied[]`, `integration_changed_files[]` (target glue paths only), evidence paths from analyst cross-module globals. Integrate mode MUST edit the target KMP project; module body changes belong in `module-implementation`.

### `post_integration_alignment.json` (analysis only — no target edits)

`alignment_verdict`, `module_alignment_results[]`, `global_alignment_results`, `omissions[]`, `poor_restoration[]`, `rerun_modules[]`, `comparison_evidence[]` (analyst path vs target path pairs).

### `migration_planning_gate.json`

Combined `planning` (spec deltas, source-to-target map, tasks) and `dependency_platform` (capability map, platform boundaries) sections. Status `ready_for_implementation` when both complete.

### `migration_prep.json`

Combined `presentation` (tokens, resources, routes) and `state_data` (state/models/API expectations) sections.

### `module_implementation_ui.json` / `module_implementation_logic.json`

UI mode and logic mode outputs under `module-implementation/ui/` and `module-implementation/logic/` respectively. Each MUST record `kmp_target_project_path`, `target_edit_summary`, and `changed_files[]` listing every target KMP path created or modified in that invocation. Legacy Android paths are evidence only — implementation edits occur under `kmp_target_project_path`.

### `alignment_report.json`

Human/agent-readable synthesis of align mode; routes reruns to `migration_module_id` or `global-migration-phase integrate`.

---

## Leader Obligations

1. Verify analyst package `P6` before `MG0` completes.
2. Dispatch `target-project-assistant` for all target-project questions; other roles MUST reference TPA artifacts instead of re-analyzing target ad hoc.
3. Write `module_completion_record.json` after each module passes `migration-verification`.
4. Run `global-migration-phase` `integrate` only after package `M4`.
5. Run `global-migration-phase` `align` only after integrate; **no code changes** in align mode.
6. Dispatch only role IDs listed in [SKILL.md](SKILL.md).
7. Set `handoff_gates` (`M0`–`M6`, `V0`) in workspace ledger and `migration_report.json`.
8. **MUST** invoke `kmp-test-validator` when `V0` is true (MG17). Do not end the migration workflow without validator dispatch or explicit validator blockers in `migration_report.json`.

## Invalid Artifact Handling

| Condition | Action |
|---|---|
| Missing path | `blocked`, `reason: missing` |
| Empty file | `blocked`, `reason: empty` |
| Out of `output_root` | `blocked`, `reason: out_of_path` |
| Stale per workspace ledger | `needs_rerun`, name owner |
| `module_completion_record` failed | Re-enter module loop from routed node |
| `post_integration_alignment` omissions | Rerun listed modules or `global-migration-phase integrate` |
| Full build requested during migrator | Reject — route to `kmp-test-validator` |
