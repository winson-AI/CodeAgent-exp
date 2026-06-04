---
name: migration-task-adapter
description: |
  4-role task adapter Swarm Skill that classifies an incoming Android/KMP migration request, routes only-understand tasks for UI, logic, architecture, or overview to android-project-analyst, routes migration tasks through android-project-analyst and android-to-kmp-migrator, and records stage inspections plus intermediate asset records before final reporting.
  Use when a controller must decide whether the user is asking for focused understanding, overview analysis, migration, or post-migration validation handoff before invoking analyst/migrator/validator workflows.
  Do NOT use for direct source lookup, single-file edits, generic KMP testing without migration context, or standalone implementation work.
version: "0.1"
kind: swarm-skill
disable-model-invocation: true
roles:
  - id: task-understanding-router
    kind: ai_agent
    purpose: Task intake and route decision owner - normalize the user request, classify only-understand vs migration, choose UI/logic/architecture/overview focus, identify required source/target paths, and emit route contracts.
    skills: []
    tools: [rg]
  - id: workflow-orchestrator
    kind: ai_agent
    purpose: Workflow orchestration owner - consume the route decision, build downstream analyst/migrator/validator dispatch contracts, record observed workflow results, and request reruns without doing downstream role work.
    skills: []
    tools: [rg, git]
  - id: workspace-state-discipline-inspector
    kind: ai_agent
    purpose: Discipline inspector - verify workspace-state freshness, stage inspection records, intermediate asset records, output path compliance, stale inputs, and rerun/blocker routing.
    skills: []
    tools: [git]
  - id: task-reporter
    kind: ai_agent
    purpose: Final task report owner - synthesize verified adapter and downstream workflow evidence into a machine-routable task report without new analysis, migration, validation, or fixes.
    skills: []
    tools: [git]
---

# Migration Task Adapter Swarm Skill

This is the agent-facing registry and team definition for a front-door adapter in the KMP Migration Toolkit. It does not replace `android-project-analyst`, `android-to-kmp-migrator`, or `kmp-test-validator`. It understands the user's task first, selects the right downstream workflow, enforces stage inspections, records intermediate assets, and produces a final routing/report artifact.

Supported task targets:

- `only_understand_ui`: focused UI/presentation/resource understanding through `android-project-analyst`, with emphasis on `presentation-resource` outputs.
- `only_understand_logic`: focused behavior/control-flow understanding through `android-project-analyst`, with emphasis on `behavior-logic` outputs and verified Stage A inputs.
- `only_understand_architecture`: focused project architecture/ecosystem understanding through `android-project-analyst`, with emphasis on `project-architecture` outputs.
- `only_understand_overview`: overview understanding through the full analyst representation and SPEC verification path.
- `migration`: Android-to-KMP migration through analyst completion, migrator execution, and validator handoff when migration output is ready.
- `validation_handoff`: post-migration validation through `kmp-test-validator` only when migration evidence exists.

## Protocol Summary

0. **Pre-flight** - read [dependencies.yaml](dependencies.yaml), report missing optional tools, and lock adapter output root.
1. **Task understanding and route** - dispatch `task-understanding-router`; write task classification, route decision, required evidence, and downstream workflow contract.
2. **Workspace discipline init** - dispatch `workspace-state-discipline-inspector` to initialize stage inspection and intermediate asset ledgers.
3. **Workflow orchestration** - dispatch `workflow-orchestrator` to prepare and record downstream workflow execution:
   - only-understand routes to `android-project-analyst`.
   - migration routes to `android-project-analyst` first when SPEC evidence is missing or stale, then `android-to-kmp-migrator`, then validation handoff when ready.
   - validation handoff routes to `kmp-test-validator` only after migration report evidence exists.
4. **Stage inspections** - after every route boundary and downstream workflow boundary, refresh `workspace-state-discipline-inspector`.
5. **Task report** - dispatch `task-reporter` only after latest discipline inspection marks required inputs fresh and intermediate asset records complete.

## Roles

Each role is dispatched as a subagent that must read its role file (`skill_spec_path`) and execute only that bounded slice.

| id | Purpose | When dispatched | Role file |
|---|---|---|---|
| `task-understanding-router` | Classify request, normalize paths/scope, select route and downstream workflow contracts | First stage after output root lock | [roles/task-understanding-router.md](roles/task-understanding-router.md) |
| `workflow-orchestrator` | Build dispatch contracts, track downstream workflow observations, route reruns/blockers | After route decision and before/after downstream workflow execution | [roles/workflow-orchestrator.md](roles/workflow-orchestrator.md) |
| `workspace-state-discipline-inspector` | Inspect stage records, intermediate assets, output paths, workspace freshness, reruns | Initialized early and refreshed after every stage boundary | [roles/workspace-state-discipline-inspector.md](roles/workspace-state-discipline-inspector.md) |
| `task-reporter` | Final machine-routable report from verified adapter/downstream artifacts | Last stage only | [roles/task-reporter.md](roles/task-reporter.md) |

## Files

| File | What it contains |
|---|---|
| [workflow.md](workflow.md) | Adapter topology, route matrix, stage inspection gates, intermediate asset records, final report contract |
| [bind.md](bind.md) | Guardrails, failure handling, path discipline, stage inspection requirements |
| [dependencies.yaml](dependencies.yaml) | Optional CLI tools checked at startup |
| [roles/](roles/) | Active role specs |

## Strict Output Schedule

```text
output_root = <output_dir or ~/.a2c_agents/task-adapter>/migration-task-adapter
task_dir = <output_root>/task
workspace_state_dir = <output_root>/workspace-state
orchestration_dir = <output_root>/orchestration
stage_inspection_dir = <output_root>/stage-inspections
intermediate_asset_dir = <output_root>/intermediate-assets
report_dir = <output_root>/report
```

Required artifacts:

- `<output_root>/run_manifest.json`
- `<task_dir>/task_understanding_router.json`
- `<task_dir>/task_understanding_router.md`
- `<workspace_state_dir>/workspace_state_discipline.json`
- `<workspace_state_dir>/workspace_state_discipline.md`
- `<stage_inspection_dir>/<stage_id>/stage_inspection.json`
- `<stage_inspection_dir>/<stage_id>/stage_inspection.md`
- `<intermediate_asset_dir>/intermediate_asset_records.json`
- `<intermediate_asset_dir>/intermediate_asset_records.md`
- `<orchestration_dir>/workflow_orchestration.json`
- `<orchestration_dir>/workflow_orchestration.md`
- `<report_dir>/task_adapter_report.json`
- `<report_dir>/task_adapter_report.md`

## Output Artifact Content Matrix

The adapter verifies both artifact names and role-aligned content before any downstream stage consumes an artifact.

| Stage / owner | Output file(s) | Required content |
|---|---|---|
| Output root lock / Leader | `run_manifest.json` | Task id, raw task summary, requested scope, source/target paths when provided, adapter output root, allowed roots, downstream workflow candidates, dependency-preflight status, schedule version, timestamp. |
| Task route / `task-understanding-router` | `task_understanding_router.json`, `task_understanding_router.md` | Normalized task, route, task kind, understand focus, source/target/scope fields, existing artifact evidence, required/missing inputs, downstream workflow sequence, stage inspection requirements, intermediate asset requirements, blockers. |
| Orchestration / `workflow-orchestrator` | `workflow_orchestration.json`, `workflow_orchestration.md` | Downstream workflow sequence, dispatch contracts, expected output roots/artifacts, route constraints, stage inspection requests, observed downstream outputs, intermediate asset updates, rerun requests, blockers. |
| Workspace discipline / `workspace-state-discipline-inspector` | `workspace_state_discipline.json`, `workspace_state_discipline.md` | Adapter artifact inventory, stage status, path compliance, freshness checks, intermediate asset coverage, rerun history, blockers, next safe actions. No task routing or downstream analysis. |
| Stage inspections / `workspace-state-discipline-inspector` | `<stage_inspection_dir>/<stage_id>/stage_inspection.json`, `.md` | Checked inputs/outputs, path compliance, freshness checks, intermediate asset coverage, downstream contract checks, stage status, rerun requests, blockers, next allowed stage. |
| Intermediate assets / `workspace-state-discipline-inspector` | `intermediate_asset_records.json`, `intermediate_asset_records.md` | Stable records for every consumed adapter/downstream artifact: asset id/type, producer, path, status, freshness basis, consumers, source evidence, coverage gaps, blockers. |
| Final task report / `task-reporter` | `task_adapter_report.json`, `task_adapter_report.md` | Final route/status/readiness, source/target paths, downstream workflow summaries, stage inspection summary, intermediate asset summary, verified outputs, rerun requests, blockers, report path. |

Downstream output roots are external asset paths. The adapter records them but does not write into them: `android-project-analyst` writes to its understand output root, `android-to-kmp-migrator` writes to its migration output root, and `kmp-test-validator` writes to its parallel validation output root.

JSON artifacts are the machine-routable source of truth. Markdown artifacts are agent-readable handoffs that preserve exact paths, route decisions, stage evidence, asset records, rerun context, blockers, and downstream routing. Adapter Markdown must not be prose-only summaries.

## Shared Return Contract

```json
{
  "status": "completed | routed | passed | ready_for_report | needs_rerun | failed | blocked",
  "node": "<node-id>",
  "task_id": "<stable task id>",
  "route": "<only_understand_ui | only_understand_logic | only_understand_architecture | only_understand_overview | migration | validation_handoff | unknown>",
  "output_dir": "<exact role output dir>",
  "output_files": ["<paths>"],
  "changed_files": [],
  "stale_upstream_inputs": [],
  "rerun_requests": [
    { "node": "<adapter or downstream node/workflow>", "reason": "", "required_inputs": [], "expected_output": "" }
  ],
  "blocking_gaps": []
}
```

Controller handling: missing or empty output files cause rerun of the same role. Stale upstream inputs cause a discipline refresh and rerun of the owning role or downstream workflow. Non-empty `blocking_gaps` stop the adapter unless the user supplies the missing evidence.

## Shared Rules

- The adapter is an orchestrator only. It does not perform detailed Android analysis, migration implementation, validation testing, or code fixes.
- Task classification must happen before selecting any downstream workflow.
- Stage inspections are required after route decision, before downstream dispatch, after every downstream workflow boundary, before final report, and after final report.
- Every durable artifact consumed by another stage must be recorded in `intermediate_asset_records.*`.
- Downstream workflow outputs are consumed by path and status only; the adapter never invents missing downstream evidence.
- User-facing completion happens only after `task-reporter` writes verified report artifacts.
