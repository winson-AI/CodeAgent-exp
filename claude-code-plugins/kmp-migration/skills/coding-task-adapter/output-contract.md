# Output Contract: Adapter File Recording, Downstream Roots, And Trigger Gates

This document is the **canonical path and content contract** for `coding-task-adapter`. Downstream controllers and human/agent orchestrators **MUST treat missing, empty, out-of-path, stale, or schema-invalid adapter artifacts as hard blockers** — they do not infer route, stage, or readiness from chat summaries.

The Leader and every node MUST read this file before writing artifacts. When `SKILL.md` or `workflow.md` diverge, **this file wins on paths, filenames, downstream root recording, and trigger gates**.

## Agents Root Resolution (single default base)

All paths in this toolkit converge on **one** base directory. Resolve it once, before any dispatch:

```text
agents_root = <output_dir or ~/.a2c_agents>
```

- `agents_root` is the only knob. When the user/caller supplies `output_dir`, use it verbatim as `agents_root`; otherwise **default to `~/.a2c_agents`**.
- `agents_root` MUST resolve to a single absolute path and is recorded once in `run_manifest.json` → `agents_root`.
- Every adapter and downstream path is derived from this base — no other default base may be introduced.

## Downstream Output Roots (resolved, not owned)

The adapter **does not own or define** the downstream workflow file trees — those are owned by each downstream skill's own `output-contract.md`. The adapter only **derives** each downstream `output_root` from the shared `agents_root` (so the whole pipeline stays consistent), passes it explicitly in the dispatch contract, and **records** the observed root. Downstream internal paths are therefore **excluded** from this contract's owned path tree and from the adapter's `out_of_path` check against `output_root`.

| Workflow | Understand subsystem | Derived `output_root` |
|---|---|---|
| `android-project-analyst` | source | `<agents_root>/understand/android-project-analyst/source` |
| `android-project-analyst` | target (migration only) | `<agents_root>/understand/android-project-analyst/target` |
| `android-to-kmp-migrator` | — | `<agents_root>/migration/android-to-kmp-migrator` |
| `kmp-test-validator` | — | `<agents_root>/validation/kmp-test-validator` |

For route `migration` the analysis stage produces **two** analyst understand subsystems in **distinct output roots** (`.../source` and `.../target`), both using the analyst output contract/file format. For `only_understand_*` routes only the source subsystem is produced. Validator artifacts MUST stay under the parallel `validation` root — never under the migration root.

**Fail closed**: adapter roles MUST NOT claim downstream pass without durable report artifacts and matching stage inspection support.

---

## Adapter Output Root Layout

Lock one `output_root` (derived from `agents_root`) before any dispatch:

```text
output_root = <agents_root>/task-adapter/coding-task-adapter

<output_root>/
├── run_manifest.json
├── downstream-index/
│   ├── downstream_workflow_index.json
│   └── downstream_workflow_index.md
├── workspace-state/
│   ├── adapter_workspace_state.json
│   └── adapter_workspace_state.md
├── route-orchestration/
│   ├── route/
│   │   ├── task_route.json
│   │   └── task_route.md
│   └── orchestrate/
│       ├── workflow_orchestration.json
│       └── workflow_orchestration.md
├── stage-inspections/
│   └── <stage_id>/
│       ├── stage_inspection.json
│       └── stage_inspection.md
├── intermediate-assets/
│   ├── intermediate_asset_records.json
│   └── intermediate_asset_records.md
└── report/
    ├── adapter_report.json
    └── adapter_report.md
```

### Path Variables (stable across runs)

| Variable | Resolved path |
|---|---|
| `agents_root` | `<output_dir or ~/.a2c_agents>` |
| `output_root` | `<agents_root>/task-adapter/coding-task-adapter` |
| `downstream_index_dir` | `<output_root>/downstream-index` |
| `workspace_state_dir` | `<output_root>/workspace-state` |
| `route_orchestration_dir` | `<output_root>/route-orchestration` |
| `route_dir` | `<route_orchestration_dir>/route` |
| `orchestrate_dir` | `<route_orchestration_dir>/orchestrate` |
| `stage_inspection_dir` | `<output_root>/stage-inspections` |
| `stage_dir` | `<stage_inspection_dir>/<stage_id>` |
| `intermediate_asset_dir` | `<output_root>/intermediate-assets` |
| `report_dir` | `<output_root>/report` |

### Filename Invariants (downstream parsers depend on these)

- JSON primary artifacts use **snake_case** basenames (`task_route.json`, `workflow_orchestration.json`, `adapter_workspace_state.json`).
- Route/orchestration subfolders use fixed names: `route/`, `orchestrate/`.
- Stage folders use **kebab-case** `stage_id` values listed below.
- No adapter artifact outside `<output_root>/` is valid for gates below.

### Path Accuracy Validation (mandatory)

Adapter roles MUST validate paths before consuming or recording them, and fail closed on any mismatch:

1. **Single base** — `agents_root` resolves to exactly one absolute path; if `output_dir` was supplied it is used verbatim, otherwise `~/.a2c_agents`. Reject relative paths, empty values, or a second base.
2. **Adapter containment** — every adapter artifact path MUST be under `output_root = <agents_root>/task-adapter/coding-task-adapter`. A path outside it is `out_of_path`.
3. **Downstream derivation** — every recorded downstream `output_root` MUST equal `<agents_root>/<stage>/<skill>[/<subsystem>]` for its workflow (`understand/android-project-analyst/{source,target}`, `migration/android-to-kmp-migrator`, `validation/kmp-test-validator`). A downstream root that does not derive from the same `agents_root`, or lands under the wrong stage folder, is `path_mismatch`.
4. **Subsystem distinctness** — for route `migration`, the source and target analyst roots MUST be distinct paths (`.../source` ≠ `.../target`); identical roots are `path_mismatch`.
5. **Cross-file consistency** — `agents_root`, `output_root`, and every `downstream_output_roots.*` value MUST be byte-identical across `run_manifest.json`, `downstream_workflow_index.json`, `adapter_workspace_state.json`, and `adapter_report.json`. Any divergence is `path_mismatch`.
6. **Existence + non-empty** — a path may only be marked `present`/`ready` when the file exists and is non-empty; otherwise `missing`/`empty`.

The `adapter-workspace-state` role records the outcome of checks 1–6 in `path_compliance[]`; a failure of any check blocks `pre_report`.

### Stage IDs (folder names under `stage-inspections/`)

| `stage_id` | When required |
|---|---|
| `route_decision` | After `task-route-orchestrator` mode `route` |
| `pre_downstream_dispatch` | Before downstream workflow invoke |
| `post_source_understand` | After the source-understand analyst run (covers the single analyst run for `only_understand_*`; the source subsystem for route `migration`) |
| `post_target_understand` | After the target-understand analyst run; **required** for route `migration` |
| `post_migrator` | After migrator workflow when route requires it |
| `post_validator` | After validator workflow; **required** for route `migration` |
| `pre_report` | Before `adapter-report` |
| `post_report` | After `adapter-report` |

---

## Write Order (Leader Schedule)

Artifacts MUST be produced in this order. Skipping a layer invalidates downstream trigger gates.

| Step | Gate id | Required artifacts before next step |
|---|---|---|
| 0 | `AG0` | `run_manifest.json` |
| 1 | `AG1` | `route-orchestration/route/task_route.*` |
| 2 | `AG2` | `workspace-state/adapter_workspace_state.*`, `stage-inspections/route_decision/*`, `intermediate-assets/intermediate_asset_records.*` |
| 3 | `AG3` | `route-orchestration/orchestrate/workflow_orchestration.*`, `downstream-index/downstream_workflow_index.*` |
| 4 | `AG4` | applicable `stage-inspections/<stage_id>/*` after each route/downstream boundary; route `migration` requires `post_source_understand`, `post_target_understand`, `post_migrator`, `post_validator` |
| 5 | `AG5` | `stage-inspections/pre_report/*` with `status: pass` |
| 6 | `AG6` | `report/adapter_report.*`, `stage-inspections/post_report/*` |

---

## Artifact Registry: Path, Owner, Content, Trigger Role

### Run identity

| Path | Owner | Required JSON / content keys | Downstream trigger role |
|---|---|---|---|
| `run_manifest.json` | Leader | `task_id`, `route`, `source_project_path`, `target_project_path`, `agents_root`, `output_root`, `downstream_output_roots`, `dependency_preflight`, `handoff_package`, `timestamp` | **All adapter roles** — resolves `agents_root` (single base) + roots and declares claimed gate package |

`handoff_package` MUST list absolute paths to the gate entry artifacts the run claims ready (see Handoff Packages below).

### Downstream index

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `downstream-index/downstream_workflow_index.json` | `task-route-orchestrator` mode `orchestrate` | `workflows[]` with `workflow_id`, `understand_subsystem`, `output_root`, `handoff_package`, `key_artifact_paths[]`, `status`, `scope`, `partial_migration` | **adapter-workspace-state**, **adapter-report** — machine lookup for consumed downstream evidence. Route `migration` MUST list **two** `android-project-analyst` entries: `understand_subsystem: source` and `understand_subsystem: target` |

### Workspace ledger

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `workspace-state/adapter_workspace_state.json` | `adapter-workspace-state` | `stage_status`, `partial_migration_status`, `artifact_inventory`, `path_compliance`, `freshness_checks`, `stale_upstream_inputs`, `rerun_history`, `blocking_gaps`, `handoff_gates`, `next_actions` | **All adapter roles** — refuse consumption when required artifacts are stale or `handoff_gates.*.ready` is false |

### Route and orchestration

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `route-orchestration/route/task_route.json` | `task-route-orchestrator` mode `route` | `route`, `task_kind`, `understand_focus`, `partial_migration`, `downstream_workflow_sequence`, `blocking_gaps` | **adapter-workspace-state**, **task-route-orchestrator** mode `orchestrate` |
| `route-orchestration/orchestrate/workflow_orchestration.json` | `task-route-orchestrator` mode `orchestrate` | `partial_migration`, `downstream_sequence`, `dispatch_contracts[]`, `observed_outputs[]`, `intermediate_asset_record_updates[]`, `rerun_requests`, `blocking_gaps` | **adapter-workspace-state**, **adapter-report** |

### Stage inspections and asset ledger

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `stage-inspections/<stage_id>/stage_inspection.json` | `adapter-workspace-state` | `stage_id`, `status` (`pass \| needs_rerun \| blocked`), `inspected_artifacts[]`, `blocking_gaps` | **adapter-report** — `pre_report` must be `pass` before final report |
| `intermediate-assets/intermediate_asset_records.json` | `adapter-workspace-state` | `records[]` with `artifact_id`, `producer`, `path`, `status`, `freshness`, `consumed_by` | **adapter-report** — every consumed durable artifact MUST have one record |

### Final report

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `report/adapter_report.json` | `adapter-report` | `status`, `route`, `downstream_workflows`, `verified_outputs[]`, `readiness`, `blocking_gaps`, `report_path` | **Human/agent consumers** — final adapter verdict |

---

## Handoff Package Gates

| Gate | Ready when |
|---|---|
| `A0` | `run_manifest.json` written; `output_root` locked |
| `A1` | `route-orchestration/route/task_route.json` — route known or explicit `blocked` with `blocking_gaps` |
| `A2` | `adapter_workspace_state.json`, `stage-inspections/route_decision/*`, route assets recorded in `intermediate_asset_records.json` |
| `A3` | `workflow_orchestration.json`, `downstream_workflow_index.json` — dispatch contracts and observed outputs recorded |
| `A4` | All applicable boundary stages (`pre_downstream_dispatch`, `post_source_understand`, `post_target_understand`, `post_migrator`, `post_validator`) are `pass` or explicitly `skipped` with evidence; route `migration` MUST NOT skip `post_target_understand` or `post_validator` |
| `A5` | `stage-inspections/pre_report/*` — `status: pass` |
| `A6` | `report/adapter_report.json` issued |

**Fail closed**: `adapter-report` MUST NOT run when `A5` is false. Final `completed` requires `A6` and verified downstream evidence for the route.

---

## Route-Specific Downstream Evidence Requirements

Record consumed paths in `intermediate_asset_records.json` and `downstream_workflow_index.json`. Gate on analyst `P*`, migrator `M*`/`V0`, validator `VG*` packages defined in their `output-contract.md` files.

| Route | Minimum downstream evidence before `A5` |
|---|---|
| `only_understand_ui` | analyst `P5` or focused `P2` with `presentation_resource.*` + SPEC |
| `only_understand_logic` | analyst `P5` or focused `P2` with `behavior_logic.*` + SPEC |
| `only_understand_architecture` | analyst `P5` or `P2` with `project_architecture.*` + SPEC |
| `only_understand_overview` | analyst `P5` |
| `migration` | source-understand analyst `P6` **and** target-understand analyst subsystem (`P5`+ on the target root), migrator `M6` + `migration_report.*`, **required** validator `VG5` + `kmp_validation_report.*`; when `partial_migration.enabled`, all evidence (both subsystems included) must match the declared partial scope/boundaries |
| `validation_handoff` | migrator `V0`, validator `VG5` + `kmp_validation_report.*` |

---

## Partial Migration Contract

Partial migration is represented as route `migration` with `partial_migration.enabled: true`; it is not a separate route and does not make validation optional.

**Trigger rule**: partial migration is enabled only when the user clearly asks to migrate a module, feature, screen flow, package, source root, file set, or other named subset. If the user provides only a source project path or gives no explicit partial requirement, route `migration` as whole-project migration from `source_project_path` with `partial_migration.enabled: false`.

### `partial_migration` minimum shape

```json
{
  "enabled": true,
  "scope_kind": "module | feature | screen_flow | package | file_set | mixed | unknown",
  "requested_scope": [],
  "requested_module_ids": [],
  "allowed_source_roots": [],
  "excluded_source_roots": [],
  "requires_module_resolution": false,
  "validation_scope": "",
  "boundary_notes": []
}
```

Rules:

- `enabled: false` means whole-project migration of the entire input project rooted at `source_project_path`.
- The default for route `migration` is `enabled: false`, `scope_kind: "full_project"`.
- Do NOT infer `enabled: true` from currently open files, recently viewed files, a path mentioned as context, or an adapter/controller narrowed view. Only explicit user wording such as "migrate module X", "only migrate feature Y", "partial migrate package Z", or "migrate these files" enables partial migration.
- If user wording explicitly requests partial migration but the subset cannot be resolved, keep `enabled: true` and block for clarification; do not silently fall back to full-project migration.
- When `enabled: true`, `task_route.json`, `workflow_orchestration.json`, `downstream_workflow_index.json`, `adapter_workspace_state.json`, and `adapter_report.json` MUST all carry the same scope object or a stricter resolved version.
- If `requires_module_resolution: true`, orchestration MUST run or consume `android-project-analyst` evidence before dispatching `android-to-kmp-migrator`; unresolved scope blocks `pre_downstream_dispatch`.
- Migrator dispatch contracts MUST include `migration_scope`, `migration_module_ids`, `allowed_source_roots`, and `partial_migration.enabled`.
- Validator dispatch contracts MUST include `validation_scope` matching the partial migration slice plus integration seams.
- Stage `post_migrator` passes for partial migration only when migrator artifacts prove the requested slice completed and record `partial_migration_boundaries` or equivalent scoped evidence. It MUST NOT require unrelated modules outside the partial scope to migrate.
- Stage `post_validator` remains required and passes only when validator evidence covers the partial slice and integration seams.
- Final `completed` for partial migration means "requested partial scope migrated and validated"; it must not claim full-project migration.

## Key Artifact Schemas

### `run_manifest.json`

```json
{
  "task_id": "",
  "route": "",
  "partial_migration": {
    "enabled": false,
    "scope_kind": "full_project | module | feature | screen_flow | package | file_set | mixed | unknown",
    "requested_scope": [],
    "requested_module_ids": [],
    "allowed_source_roots": [],
    "excluded_source_roots": [],
    "requires_module_resolution": false,
    "validation_scope": "",
    "boundary_notes": []
  },
  "source_project_path": "",
  "target_project_path": "",
  "agents_root": "<output_dir or ~/.a2c_agents>",
  "output_root": "<agents_root>/task-adapter/coding-task-adapter",
  "downstream_output_roots": {
    "android-project-analyst-source": "<agents_root>/understand/android-project-analyst/source",
    "android-project-analyst-target": "<agents_root>/understand/android-project-analyst/target",
    "android-to-kmp-migrator": "<agents_root>/migration/android-to-kmp-migrator",
    "kmp-test-validator": "<agents_root>/validation/kmp-test-validator"
  },
  "dependency_preflight": {},
  "handoff_package": "A0",
  "timestamp": ""
}
```

`agents_root` is the single resolved base. `output_root` and every `downstream_output_roots.*` MUST be derived from it; a target subsystem root is required only for route `migration`. The literal `<agents_root>` tokens above are placeholders — the manifest stores fully resolved absolute paths.

### `downstream_workflow_index.json`

```json
{
  "workflows": [
    {
      "workflow_id": "android-project-analyst | android-to-kmp-migrator | kmp-test-validator",
      "understand_subsystem": "source | target | none",
      "understand_target_path": "",
      "output_root": "",
      "handoff_package": "",
      "handoff_ready": true,
      "key_artifact_paths": [],
      "scope": "",
      "partial_migration": {},
      "status": "completed | needs_rerun | blocked | not_invoked"
    }
  ]
}
```

### `intermediate_asset_records.json` record shape

```json
{
  "artifact_id": "",
  "producer": "task-route-orchestrator | adapter-workspace-state | android-project-analyst | android-to-kmp-migrator | kmp-test-validator",
  "path": "",
  "status": "present | missing | stale | invalid",
  "freshness": "fresh | stale | unknown",
  "consumed_by": ["adapter-workspace-state", "adapter-report"]
}
```

### `adapter_report.json` status rules

- `completed` — understand route satisfied; inspections pass; assets recorded. Route `migration` additionally requires validator `VG5` and `kmp_validation_report.*`. If `partial_migration.enabled`, completion is scoped to the declared partial boundaries and the report must say so.
- `ready_for_validation` — migrator report ready but validator not yet complete; **invalid final status for route `migration`** — migration runs must trigger validator and resolve before `A6`.
- `needs_rerun` — concrete owner can resolve missing/stale evidence.
- `failed` — downstream workflow failed with verified evidence.
- `blocked` — missing path, evidence, or user decision.

---

## Leader Obligations For Downstream Triggers

Before claiming adapter completion, the Leader MUST:

0. Resolve `agents_root = <output_dir or ~/.a2c_agents>` once at pre-flight, derive `output_root` and every downstream root from it, and record them in `run_manifest.json`. Pass each derived downstream `output_root` explicitly in its dispatch contract — never let a downstream workflow fall back to its own default base.
1. Write `handoff_gates` into `adapter_workspace_state.json` with boolean `ready` flags for `A0`–`A6` and `missing_paths[]` per false gate.
2. Set `run_manifest.json` → `handoff_package` to the **highest package actually ready** (`A0`..`A6`) and list every artifact path in that package.
3. Refresh `adapter-workspace-state` after every route and downstream boundary.
4. Never invoke `adapter-report` before `A5` is true.
5. Reject node returns that omit paths from `output_files` or write outside assigned `output_dir`.
6. For route `migration`, dispatch the analysis stage as **two** analyst understand runs (source subsystem + target subsystem) into distinct understand output roots before the migrator; record both in `downstream_workflow_index.json`; do not mark `A4` ready without `post_source_understand` and `post_target_understand` pass.
7. For route `migration`, invoke `kmp-test-validator` after migrator handoff; record validator output root under parallel `validation` location; do not mark `A4`/`A6` ready without `post_validator` pass.
8. For partial migration, preserve the same `partial_migration` boundaries in route, both understand subsystems, downstream dispatches, stage inspections, asset records, and final report; never widen scope silently.

## Node Obligations

Every node MUST:

- Write only under the `output_dir` declared in its dispatch contract.
- Use exact filenames and subfolders from this contract.
- Mirror downstream paths in `intermediate_asset_record_updates` or asset records — never invent evidence.
- Return `blocked` when required upstream/downstream package gates are false.

## Invalid Artifact Handling (uniform rule)

| Condition | Handler action |
|---|---|
| Path missing | `blocked` — `blocking_gaps: [{ "artifact": "<path>", "reason": "missing" }]` |
| File empty | `blocked` — reason `empty` |
| Adapter artifact outside `output_root` | `blocked` — reason `out_of_path` |
| `agents_root` relative/empty or a second base introduced | `blocked` — reason `invalid_base` |
| Downstream root not derived from `agents_root` / wrong stage folder | `blocked` — reason `path_mismatch` |
| Source and target analyst roots identical (route `migration`) | `blocked` — reason `path_mismatch` |
| `agents_root`/`output_root`/`downstream_output_roots.*` diverge across manifest, index, ledger, report | `blocked` — reason `path_mismatch` |
| Stale per workspace ledger | `needs_rerun` — name owning role or downstream workflow |
| Schema/content invalid | `blocked` — reason `invalid_contract`; cite this file section |
| `pre_report` not `pass` | `blocked` — do not run `adapter-report` |

Downstream handlers MUST NOT parse chat text, controller summaries, or partial copies when gate artifacts are absent.
