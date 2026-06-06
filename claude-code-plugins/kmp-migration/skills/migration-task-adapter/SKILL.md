---
name: migration-task-adapter
description: |
  Front-door Swarm Skill that classifies Android/KMP migration requests, routes understand/migration/validation tasks to analyst, migrator, and validator workflows, and records stage gates plus asset ledgers before the final adapter report.
  Use when a controller must decide task intent and invoke the correct downstream workflow before detailed analysis, migration, or validation runs.
  Do NOT use for direct source lookup, single-file edits, generic KMP testing without migration context, or standalone implementation work.
version: "0.2"
kind: swarm-skill
disable-model-invocation: false
roles:
  - id: task-route-orchestrator
    kind: ai_agent
    purpose: Task route and orchestration — mode route (classify intent, paths, downstream sequence) or orchestrate (dispatch contracts, observed downstream outputs). No downstream role work.
    skills: []
    tools: [rg, git]
  - id: adapter-workspace-state
    kind: ai_agent
    purpose: Workspace ledger — stage inspections, intermediate asset records, path compliance, freshness, reruns. No routing, orchestration, or final verdict.
    skills: []
    tools: [git]
  - id: adapter-report
    kind: ai_agent
    purpose: Final adapter report from verified route, orchestration, workspace, stage, and downstream evidence. No new routing or workflow execution.
    skills: []
    tools: [git]
---

# Migration Task Adapter Swarm Skill

Front-door adapter for the KMP Migration Toolkit. It does not replace `android-project-analyst`, `android-to-kmp-migrator`, or `kmp-test-validator`. It classifies the user task, invokes the right downstream workflow, enforces stage gates, records consumed artifacts, and produces a final adapter report.

**Canonical file recording system**: [output-contract.md](output-contract.md) defines every adapter output path, required content, write order, and **handoff package gates** (`A0`–`A6`). The Leader MUST read `output-contract.md` before the first dispatch and MUST NOT claim completion without updating `handoff_gates` in `adapter_workspace_state.json`.

## Task Routes

| Route | Downstream |
|---|---|
| `only_understand_ui` | `android-project-analyst` — UI/presentation focus |
| `only_understand_logic` | `android-project-analyst` — behavior/control-flow focus |
| `only_understand_architecture` | `android-project-analyst` — architecture/ecosystem focus |
| `only_understand_overview` | `android-project-analyst` — full representation + SPEC |
| `migration` | analyst (if SPEC stale) → `android-to-kmp-migrator` → **`kmp-test-validator` (required)** |
| `validation_handoff` | `kmp-test-validator` when migration evidence exists |

## Protocol Summary

0. **Pre-flight** — [dependencies.yaml](dependencies.yaml); lock adapter `output_root`.
1. **Route** — `task-route-orchestrator` mode `route` → `task_route.*`.
2. **Workspace init** — `adapter-workspace-state` → ledger, first stage inspection, asset records.
3. **Orchestrate** — `task-route-orchestrator` mode `orchestrate` → downstream dispatch contracts and observed outputs.
4. **Stage gates** — refresh `adapter-workspace-state` after each route and downstream boundary.
5. **Report** — `adapter-report` when `pre_report` stage passes and assets are complete.

## Roles

| id | Modes | Role file |
|---|---|---|
| `task-route-orchestrator` | `route \| orchestrate` | [roles/task-route-orchestrator.md](roles/task-route-orchestrator.md) |
| `adapter-workspace-state` | — | [roles/adapter-workspace-state.md](roles/adapter-workspace-state.md) |
| `adapter-report` | — | [roles/adapter-report.md](roles/adapter-report.md) |

## Files

| File | Contents |
|---|---|
| [output-contract.md](output-contract.md) | Canonical path tree, artifact registry, gates `A0`–`A6`, downstream root recording |
| [workflow.md](workflow.md) | Topology, route matrix, stage gates, report shape |
| [bind.md](bind.md) | Guardrails, path contract, failure handling |
| [dependencies.yaml](dependencies.yaml) | Downstream skills and optional tools |
| [roles/](roles/) | Role specs |

## Output Layout

See [output-contract.md](output-contract.md) for the full folder tree, filename invariants, and handoff packages `A0`–`A6`. Summary path variables:

```text
output_root = <output_dir or ~/.a2c_agents/task-adapter>/migration-task-adapter
downstream_index_dir = <output_root>/downstream-index
workspace_state_dir = <output_root>/workspace-state
route_orchestration_dir = <output_root>/route-orchestration
stage_inspection_dir = <output_root>/stage-inspections
intermediate_asset_dir = <output_root>/intermediate-assets
report_dir = <output_root>/report
```

Downstream workflows write only to their own output roots; the adapter records paths in `downstream-index/` and `intermediate-assets/`.

Any artifact written outside the path tree in `output-contract.md` is **invalid** — adapter roles MUST return `blocked` with `reason: out_of_path`.

## Artifact Owners

| Owner | Artifacts |
|---|---|
| Leader | `run_manifest.json` |
| `task-route-orchestrator` | `task_route.*`, `workflow_orchestration.*`, `downstream_workflow_index.*` |
| `adapter-workspace-state` | `adapter_workspace_state.*`, `stage_inspection.*`, `intermediate_asset_records.*` |
| `adapter-report` | `adapter_report.*` |

## Shared Return Contract

```json
{
  "status": "completed | routed | passed | ready_for_report | needs_rerun | failed | blocked",
  "node": "node-id",
  "mode": "route | orchestrate",
  "task_id": "",
  "route": "",
  "output_dir": "",
  "output_files": [],
  "changed_files": [],
  "stale_upstream_inputs": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```

## Shared Rules

- Adapter roles orchestrate only — no Android analysis, migration implementation, validation testing, or code fixes.
- Route classification happens before downstream workflow selection.
- Every consumed durable artifact must appear in `intermediate_asset_records.*`.
- Downstream evidence is consumed by path and status only — never invented.
- Route `migration` MUST invoke `kmp-test-validator` after migrator handoff; adapter cannot claim migration completion without validator evidence and `post_validator` stage pass.
- Final user-facing completion requires `adapter_report.*`.
