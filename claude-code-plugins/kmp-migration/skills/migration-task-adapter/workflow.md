# Workflow: task → route → downstream workflow → adapter report

The adapter classifies intent, records contracts and stage gates, and emits a verified report. It does not perform analysis, migration, or validation itself.

**File recording system**: every adapter output path, content requirement, and trigger gate is defined in [output-contract.md](output-contract.md). Adapter roles MUST fail closed when handoff package artifacts are missing, empty, out-of-path, stale, or schema-invalid.

## Overview

```mermaid
graph TD
  L0[Pre-flight] --> ROOT[run_manifest.json]
  ROOT --> TRO_R[task-route-orchestrator route]
  TRO_R --> G0{Route ok?}
  G0 -- No --> STOP[blocked]
  G0 -- Yes --> WS0[adapter-workspace-state init]
  WS0 --> TRO_O[task-route-orchestrator orchestrate]
  TRO_O --> G1{Route}
  G1 --> APA[android-project-analyst variants]
  G1 --> MIG[migration: analyst then migrator]
  MIG --> KV[kmp-test-validator optional]
  APA --> WS1[adapter-workspace-state]
  KV --> WS1
  MIG --> WS1
  WS1 --> AR[adapter-report]
  AR --> WS2[adapter-workspace-state post_report]
```

## Output Paths

The canonical path tree, stage folder names, and handoff packages `A0`–`A6` are in [output-contract.md](output-contract.md). Summary:

```text
output_root = <output_dir or ~/.a2c_agents/task-adapter>/migration-task-adapter
downstream_index_dir = <output_root>/downstream-index
workspace_state_dir = <output_root>/workspace-state
route_orchestration_dir = <output_root>/route-orchestration
stage_inspection_dir = <output_root>/stage-inspections
intermediate_asset_dir = <output_root>/intermediate-assets
report_dir = <output_root>/report
```

Validator artifacts are recorded under the validator's parallel `validation` root, not the migration root.

## Route Matrix

| Route | Required inputs | Downstream | Key evidence |
|---|---|---|---|
| `only_understand_ui` | Android source, UI scope | analyst exploration, focus `ui` | `presentation_resource.*`, SPEC |
| `only_understand_logic` | Android source, logic scope | analyst exploration, focus `logic` | Stage A + `behavior_logic.*`, SPEC |
| `only_understand_architecture` | Android source | analyst exploration, focus `architecture` | `project_architecture.*`, SPEC |
| `only_understand_overview` | Android source | analyst exploration | module inventory, representations, SPEC |
| `migration` | source or SPEC, KMP target | analyst → migrator → validator optional | SPEC, `migration_report.*` |
| `validation_handoff` | KMP target, migration report | validator | `kmp_validation_report.*` |

## Steps

### Step 0 — Pre-flight

Lock `output_root`; write `run_manifest.json` with task id, paths, scope, dependency preflight.

### Step 1 — Route

- **Executor**: `task-route-orchestrator` mode `route`
- **Output**: `route-orchestration/route/task_route.*`
- **Gate**: route is known or `blocked` with `blocking_gaps`

### Step 2 — Workspace init

- **Executor**: `adapter-workspace-state`
- **Output**: `adapter_workspace_state.*`, first `stage_inspection.*`, `intermediate_asset_records.*`
- **Gate**: route artifacts recorded as assets before orchestrate

### Step 3 — Orchestrate

- **Executor**: `task-route-orchestrator` mode `orchestrate`
- **Output**: `route-orchestration/orchestrate/workflow_orchestration.*`
- **Gate**: downstream contracts and observed outputs recorded or blockers explicit

### Step 4 — Stage gates

- **Executor**: `adapter-workspace-state`
- **Stages**: `route_decision`, `pre_downstream_dispatch`, `post_analyst`, `post_migrator`, `post_validator`, `pre_report`, `post_report` (as applicable)
- **Gate**: `pre_report` must pass before adapter-report

### Step 5 — Adapter report

- **Executor**: `adapter-report`
- **Output**: `report/adapter_report.*`

## Final Report Shape

```json
{
  "status": "completed | ready_for_validation | failed | blocked",
  "task_id": "",
  "route": "",
  "understand_focus": "",
  "source_project_path": "",
  "target_project_path": "",
  "downstream_workflows": [],
  "stage_inspection_summary": [],
  "intermediate_asset_summary": {},
  "verified_outputs": [],
  "readiness": "",
  "blocking_gaps": [],
  "report_path": ""
}
```

## Acceptance Criteria

- Route classified before downstream invoke.
- Stage inspections at each applicable boundary.
- Every consumed artifact in `intermediate_asset_records.*` and downstream roots indexed in `downstream_workflow_index.*`.
- `handoff_gates` in `adapter_workspace_state.json` accurately reflect [output-contract.md](output-contract.md) package readiness (`A0`–`A6`).
- `adapter-report` runs only after fresh `pre_report` gate (`A5`).
- Final report cites verified paths; gaps listed, not filled in.
