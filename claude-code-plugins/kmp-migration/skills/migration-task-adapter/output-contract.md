# Output Contract: Adapter File Recording, Downstream Roots, And Trigger Gates

This document is the **canonical path and content contract** for `migration-task-adapter`. Downstream controllers and human/agent orchestrators **MUST treat missing, empty, out-of-path, stale, or schema-invalid adapter artifacts as hard blockers** — they do not infer route, stage, or readiness from chat summaries.

The Leader and every node MUST read this file before writing artifacts. When `SKILL.md` or `workflow.md` diverge, **this file wins on paths, filenames, downstream root recording, and trigger gates**.

## Downstream Output Roots (read-only consumption)

The adapter records but does not write into downstream workflow roots:

| Workflow | Default `output_root` |
|---|---|
| `android-project-analyst` | `<output_dir or ~/.a2c_agents/understand>/android-project-analyst` |
| `android-to-kmp-migrator` | `<output_dir or ~/.a2c_agents/migration>/android-to-kmp-migrator` |
| `kmp-test-validator` | `<output_dir or ~/.a2c_agents/validation>/kmp-test-validator` |

Validator artifacts MUST stay under the parallel `validation` root — never under the migration root.

**Fail closed**: adapter roles MUST NOT claim downstream pass without durable report artifacts and matching stage inspection support.

---

## Adapter Output Root Layout

Lock one `output_root` before any dispatch:

```text
output_root = <output_dir or ~/.a2c_agents/task-adapter>/migration-task-adapter

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
| `output_root` | `<output_dir or ~/.a2c_agents/task-adapter>/migration-task-adapter` |
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

### Stage IDs (folder names under `stage-inspections/`)

| `stage_id` | When required |
|---|---|
| `route_decision` | After `task-route-orchestrator` mode `route` |
| `pre_downstream_dispatch` | Before downstream workflow invoke |
| `post_analyst` | After analyst workflow when route requires it |
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
| 4 | `AG4` | applicable `stage-inspections/<stage_id>/*` after each route/downstream boundary |
| 5 | `AG5` | `stage-inspections/pre_report/*` with `status: pass` |
| 6 | `AG6` | `report/adapter_report.*`, `stage-inspections/post_report/*` |

---

## Artifact Registry: Path, Owner, Content, Trigger Role

### Run identity

| Path | Owner | Required JSON / content keys | Downstream trigger role |
|---|---|---|---|
| `run_manifest.json` | Leader | `task_id`, `route`, `source_project_path`, `target_project_path`, `output_root`, `downstream_output_roots`, `dependency_preflight`, `handoff_package`, `timestamp` | **All adapter roles** — resolves roots and declares claimed gate package |

`handoff_package` MUST list absolute paths to the gate entry artifacts the run claims ready (see Handoff Packages below).

### Downstream index

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `downstream-index/downstream_workflow_index.json` | `task-route-orchestrator` mode `orchestrate` | `workflows[]` with `workflow_id`, `output_root`, `handoff_package`, `key_artifact_paths[]`, `status` | **adapter-workspace-state**, **adapter-report** — machine lookup for consumed downstream evidence |

### Workspace ledger

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `workspace-state/adapter_workspace_state.json` | `adapter-workspace-state` | `stage_status`, `artifact_inventory`, `path_compliance`, `freshness_checks`, `stale_upstream_inputs`, `rerun_history`, `blocking_gaps`, `handoff_gates`, `next_actions` | **All adapter roles** — refuse consumption when required artifacts are stale or `handoff_gates.*.ready` is false |

### Route and orchestration

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `route-orchestration/route/task_route.json` | `task-route-orchestrator` mode `route` | `route`, `task_kind`, `understand_focus`, `downstream_workflow_sequence`, `blocking_gaps` | **adapter-workspace-state**, **task-route-orchestrator** mode `orchestrate` |
| `route-orchestration/orchestrate/workflow_orchestration.json` | `task-route-orchestrator` mode `orchestrate` | `downstream_sequence`, `dispatch_contracts[]`, `observed_outputs[]`, `intermediate_asset_record_updates[]`, `rerun_requests`, `blocking_gaps` | **adapter-workspace-state**, **adapter-report** |

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
| `A4` | All applicable boundary stages (`pre_downstream_dispatch`, `post_analyst`, `post_migrator`, `post_validator`) are `pass` or explicitly `skipped` with evidence; route `migration` MUST NOT skip `post_validator` |
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
| `migration` | analyst `P6` when required, migrator `M6` + `migration_report.*`, **required** validator `VG5` + `kmp_validation_report.*` |
| `validation_handoff` | migrator `V0`, validator `VG5` + `kmp_validation_report.*` |

---

## Key Artifact Schemas

### `run_manifest.json`

```json
{
  "task_id": "",
  "route": "",
  "source_project_path": "",
  "target_project_path": "",
  "output_root": "",
  "downstream_output_roots": {
    "android-project-analyst": "",
    "android-to-kmp-migrator": "",
    "kmp-test-validator": ""
  },
  "dependency_preflight": {},
  "handoff_package": "A0",
  "timestamp": ""
}
```

### `downstream_workflow_index.json`

```json
{
  "workflows": [
    {
      "workflow_id": "android-project-analyst | android-to-kmp-migrator | kmp-test-validator",
      "output_root": "",
      "handoff_package": "",
      "handoff_ready": true,
      "key_artifact_paths": [],
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

- `completed` — understand route satisfied; inspections pass; assets recorded. Route `migration` additionally requires validator `VG5` and `kmp_validation_report.*`.
- `ready_for_validation` — migrator report ready but validator not yet complete; **invalid final status for route `migration`** — migration runs must trigger validator and resolve before `A6`.
- `needs_rerun` — concrete owner can resolve missing/stale evidence.
- `failed` — downstream workflow failed with verified evidence.
- `blocked` — missing path, evidence, or user decision.

---

## Leader Obligations For Downstream Triggers

Before claiming adapter completion, the Leader MUST:

1. Write `handoff_gates` into `adapter_workspace_state.json` with boolean `ready` flags for `A0`–`A6` and `missing_paths[]` per false gate.
2. Set `run_manifest.json` → `handoff_package` to the **highest package actually ready** (`A0`..`A6`) and list every artifact path in that package.
3. Refresh `adapter-workspace-state` after every route and downstream boundary.
4. Never invoke `adapter-report` before `A5` is true.
5. Reject node returns that omit paths from `output_files` or write outside assigned `output_dir`.
6. For route `migration`, invoke `kmp-test-validator` after migrator handoff; record validator output root under parallel `validation` location; do not mark `A4`/`A6` ready without `post_validator` pass.

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
| Path outside `output_root` | `blocked` — reason `out_of_path` |
| Stale per workspace ledger | `needs_rerun` — name owning role or downstream workflow |
| Schema/content invalid | `blocked` — reason `invalid_contract`; cite this file section |
| `pre_report` not `pass` | `blocked` — do not run `adapter-report` |

Downstream handlers MUST NOT parse chat text, controller summaries, or partial copies when gate artifacts are absent.
