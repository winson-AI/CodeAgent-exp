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
  G1 -- only_understand_* --> APA[android-project-analyst: source understand only]
  G1 -- migration --> AST[Analysis stage: dual understand]
  AST --> AS[android-project-analyst: source understand subsystem]
  AST --> AT[android-project-analyst: target understand subsystem]
  AS --> MIG[android-to-kmp-migrator: fetch source+target understand, transfer module]
  AT --> MIG
  MIG --> KV[kmp-test-validator required]
  APA --> WS1[adapter-workspace-state]
  KV --> WS1
  MIG --> WS1
  WS1 --> AR[adapter-report]
  AR --> WS2[adapter-workspace-state post_report]
```

## Analysis Stage Modes

The adapter drives an analysis stage with two modes, then a migrate stage and a validate stage.

| Mode | Trigger | Analysis stage behavior | Understand subsystems |
|---|---|---|---|
| **Understand** | `only_understand_*` | One `android-project-analyst` run on the source project. Output the understand results and file system only. No migrate/validate stage. | `source` only |
| **Migrate** | route `migration` | The analysis stage understands **both** the source and the target project by running `android-project-analyst` once per project, into **two distinct understand folders** using the current analyst file format. | `source` + `target` |

In migrate mode the two understand subsystems feed the migrate stage:

- **Source Project Subsystem** — `android-project-analyst` (migration mode) on `source_project_path`, full analyst handoff (`P6`).
- **Target Project Subsystem** — `android-project-analyst` (target-understanding) on `target_project_path`, same analyst output contract/file format.

The migrate stage (`android-to-kmp-migrator`) fetches the comprehensive context from **both** subsystems, clarifies the migration task (partial or full), and transfers the required module from the source project into the target project. The validate stage (`kmp-test-validator`) is unchanged and remains required.

## Output Paths

The canonical path tree, stage folder names, and handoff packages `A0`–`A6` are in [output-contract.md](output-contract.md). Summary:

```text
output_root = <output_dir or ~/.a2c_agents/task-adapter>/coding-task-adapter
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
| `migration` | Android source, KMP target; explicit partial scope optional | analyst (source understand) + analyst (target understand) → migrator → **validator required** | source + target understand subsystems, `migration_report.*`, `kmp_validation_report.*`; partial scope evidence only when explicitly requested |
| `validation_handoff` | KMP target, migration report | validator | `kmp_validation_report.*` |

## Partial Migration

Partial migration is route `migration` with scoped metadata, not a separate route. Trigger it **only** when the user clearly asks to migrate a module, feature, screen flow, package, source root, file set, or other named subset.

Default behavior: if the user asks to migrate a project/app/source path without an explicit partial requirement, migrate the whole input project from `source_project_path` (`partial_migration.enabled: false`, `scope_kind: full_project`).

Required behavior:

- Route step records `partial_migration.enabled`, `scope_kind`, requested scope, allowed/excluded roots, and whether analyst module resolution is required. It must not infer partial scope from open files or contextual paths.
- Orchestrate step passes the same scope to analyst, migrator, and validator dispatch contracts.
- Stage gates validate that downstream evidence matches the requested partial scope.
- Validator remains required after migrator handoff.
- Final adapter report says the completed status is for the requested partial scope only.

## Steps

### Step 0 — Pre-flight

Lock `output_root`; write `run_manifest.json` with task id, paths, scope, dependency preflight.

### Step 1 — Route

- **Executor**: `task-route-orchestrator` mode `route`
- **Output**: `route-orchestration/route/task_route.*`
- **Gate**: route is known or `blocked` with `blocking_gaps`; partial migration is enabled only by explicit partial user input, otherwise migration scope is full project from `source_project_path`

### Step 2 — Workspace init

- **Executor**: `adapter-workspace-state`
- **Output**: `adapter_workspace_state.*`, first `stage_inspection.*`, `intermediate_asset_records.*`
- **Gate**: route artifacts recorded as assets before orchestrate

### Step 3 — Orchestrate

- **Executor**: `task-route-orchestrator` mode `orchestrate`
- **Output**: `route-orchestration/orchestrate/workflow_orchestration.*`
- **Action**: route `migration` MUST dispatch the analysis stage as **two understand runs** — `android-project-analyst` on the source (Source Project Subsystem) and `android-project-analyst` on the target (Target Project Subsystem) into two distinct understand output roots — then `android-to-kmp-migrator` (which fetches both subsystems), then `kmp-test-validator`; partial migration MUST preserve the same scope in both analyst runs, migrator, and validator contracts; record validator output root under parallel `validation` location
- **Gate**: downstream contracts and observed outputs recorded or blockers explicit; migration route incomplete without both understand subsystems and validator dispatch/evidence

### Step 4 — Stage gates

- **Executor**: `adapter-workspace-state`
- **Stages**: `route_decision`, `pre_downstream_dispatch`, `post_source_understand`, `post_target_understand`, `post_migrator`, `post_validator`, `pre_report`, `post_report` (as applicable)
- **Gate**: `pre_report` must pass before adapter-report. For route `migration`, both `post_source_understand` and `post_target_understand` must pass before `post_migrator`. For `only_understand_*` routes, only `post_source_understand` applies (it covers the single analyst understand run).

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
  "understand_subsystems": {
    "source": { "analyst_output_root": "", "handoff_package": "", "ready": false },
    "target": { "analyst_output_root": "", "handoff_package": "", "ready": false }
  },
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
- `only_understand_*` runs one analyst understand run on the source and outputs the understand results + file system only (no migrate/validate stage).
- Route `migration` runs the analysis stage as two understand runs — source understand subsystem and target understand subsystem — in two distinct understand output roots using the analyst file format, before migrator dispatch.
- Partial migration scope is preserved in route, orchestration, both understand subsystems, downstream index, stage inspections, and report.
- Stage inspections at each applicable boundary.
- Every consumed artifact in `intermediate_asset_records.*` and downstream roots indexed in `downstream_workflow_index.*`.
- `handoff_gates` in `adapter_workspace_state.json` accurately reflect [output-contract.md](output-contract.md) package readiness (`A0`–`A6`).
- `adapter-report` runs only after fresh `pre_report` gate (`A5`).
- Route `migration` always dispatches `kmp-test-validator` after migrator; `post_source_understand`, `post_target_understand`, and `post_validator` stages required before `pre_report`, including partial migration.
- Final report cites verified paths for both understand subsystems; gaps listed, not filled in.
