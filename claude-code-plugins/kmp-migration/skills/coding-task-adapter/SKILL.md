---
name: coding-task-adapter
description: |
  Front-door Swarm Skill that classifies Android/KMP migration requests, routes understand/migration/validation tasks (including partial migration scopes) to analyst, migrator, and validator workflows, and records stage gates plus asset ledgers before the final adapter report.
  Use when a controller must decide task intent and invoke the correct downstream workflow before detailed analysis, migration, or validation runs.
  Do NOT use for direct source lookup, single-file edits, generic KMP testing without migration context, or standalone implementation work.
version: "0.2"
kind: swarm-skill
disable-model-invocation: false
roles:
  - id: task-route-orchestrator
    kind: ai_agent
    purpose: Task route and orchestration — mode route (classify intent, paths, downstream sequence) or orchestrate (dispatch contracts, observed downstream outputs). No downstream role work.
    skills: [operating-instructions]
    tools: [rg, git]
  - id: adapter-workspace-state
    kind: ai_agent
    purpose: Workspace ledger — stage inspections, intermediate asset records, path compliance, freshness, reruns. No routing, orchestration, or final verdict.
    skills: [operating-instructions]
    tools: [git]
  - id: adapter-report
    kind: ai_agent
    purpose: Final adapter report from verified route, orchestration, workspace, stage, and downstream evidence. No new routing or workflow execution.
    skills: [operating-instructions]
    tools: [git]
---

# Migration Task Adapter Swarm Skill

Front-door adapter for the KMP Migration Toolkit. It does not replace `android-project-analyst`, `android-to-kmp-migrator`, or `kmp-test-validator`. It classifies the user task, invokes the right downstream workflow, enforces stage gates, records consumed artifacts, and produces a final adapter report.

**Canonical file recording system**: [output-contract.md](output-contract.md) defines every adapter output path, required content, write order, and **handoff package gates** (`A0`–`A6`). The Leader MUST read `output-contract.md` before the first dispatch and MUST NOT claim completion without updating `handoff_gates` in `adapter_workspace_state.json`.

**Baseline operating instructions**: [../operating-instructions/SKILL.md](../operating-instructions/SKILL.md) is the shared conduct layer for this skill and every dispatched adapter role. The Leader MUST read it before route/pre-flight work and include it in each role dispatch as baseline instructions; role files and output contracts add to it, not replace it.

## Task Routes

| Route | Downstream |
|---|---|
| `only_understand_ui` | `android-project-analyst` — UI/presentation focus |
| `only_understand_logic` | `android-project-analyst` — behavior/control-flow focus |
| `only_understand_architecture` | `android-project-analyst` — architecture/ecosystem focus |
| `only_understand_overview` | `android-project-analyst` — full representation + SPEC |
| `migration` | `android-project-analyst` ×2 (source understand subsystem + target understand subsystem) → `android-to-kmp-migrator` → **`kmp-test-validator` (required)**; defaults to full project, supports partial scope only when explicitly requested |
| `validation_handoff` | `kmp-test-validator` when migration evidence exists |

## Analysis Stage Modes (understand vs migrate)

The adapter front-door drives an analysis stage with two modes before any migrate/validate stage:

- **Understand mode** (`only_understand_*`): one `android-project-analyst` run on the source project. The adapter outputs the understand results and the file system only — no migrate or validate stage.
- **Migrate mode** (route `migration`): the analysis stage understands **both** projects by dispatching `android-project-analyst` once on the source and once on the target, into **two distinct understand folders** that use the current analyst file format:
  - **Source Project Subsystem** — analyst migration mode on `source_project_path` (`P6`).
  - **Target Project Subsystem** — analyst target-understanding on `target_project_path` (same output contract/format).

The migrate stage (`android-to-kmp-migrator`) fetches the comprehensive context from both understand subsystems, clarifies the migration task (partial or full), and transfers the required module from the source project into the target project. The validate stage (`kmp-test-validator`) is unchanged and remains required.

## Protocol Summary

0. **Pre-flight** — [dependencies.yaml](dependencies.yaml); lock adapter `output_root`.
1. **Route** — `task-route-orchestrator` mode `route` → `task_route.*`.
2. **Workspace init** — `adapter-workspace-state` → ledger, first stage inspection, asset records.
3. **Orchestrate** — `task-route-orchestrator` mode `orchestrate` → downstream dispatch contracts and observed outputs; for route `migration` dispatch the analysis stage as source-understand + target-understand analyst runs before the migrator; preserve `partial_migration` boundaries when scoped.
4. **Stage gates** — refresh `adapter-workspace-state` after each route and downstream boundary (`post_source_understand`, `post_target_understand`, `post_migrator`, `post_validator`).
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

See [output-contract.md](output-contract.md) for the full folder tree, filename invariants, path-accuracy validation, and handoff packages `A0`–`A6`. All paths converge on a single base `agents_root = <output_dir or ~/.a2c_agents>` (default `~/.a2c_agents`). Summary path variables:

```text
agents_root = <output_dir or ~/.a2c_agents>
output_root = <agents_root>/task-adapter/coding-task-adapter
downstream_index_dir = <output_root>/downstream-index
workspace_state_dir = <output_root>/workspace-state
route_orchestration_dir = <output_root>/route-orchestration
stage_inspection_dir = <output_root>/stage-inspections
intermediate_asset_dir = <output_root>/intermediate-assets
report_dir = <output_root>/report
```

Downstream roots are **derived from the same `agents_root`** (`<agents_root>/{understand,migration,validation}/<skill>`), owned by the downstream contracts, and only recorded by the adapter — their internal trees are excluded from the adapter's owned path tree.

Any adapter artifact written outside `output_root` is **invalid** — adapter roles MUST return `blocked` with `reason: out_of_path`; a downstream root that does not derive from `agents_root` is `blocked` with `reason: path_mismatch`.

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
- `only_understand_*` runs one analyst understand run on the source and outputs the understand results + file system only.
- Route `migration` runs the analysis stage as **two understand subsystems** — source understand + target understand — in two distinct analyst output roots before migrator dispatch. The migrator fetches both subsystems.
- Partial migration is route `migration` with `partial_migration.enabled: true` only when the user clearly asks for a module/feature/subset migration. Otherwise migrate the whole input project from `source_project_path`.
- When partial migration is enabled, scope must be preserved through both understand subsystems, migrator, validator, stage inspections, and final report.
- Every consumed durable artifact must appear in `intermediate_asset_records.*`.
- Downstream evidence is consumed by path and status only — never invented.
- Route `migration` MUST invoke `kmp-test-validator` after migrator handoff; adapter cannot claim migration completion without both understand subsystems, validator evidence, and `post_validator` stage pass.
- Final user-facing completion requires `adapter_report.*`.
