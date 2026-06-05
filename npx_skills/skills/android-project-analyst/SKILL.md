---
name: android-project-analyst
description: |
  Module-first Swarm Skill that converts a Legacy Android project into module-indexed artifacts, per-module dimension folders, cross-module architecture/data-logic records, a workspace-state ledger, a global representation, and an integrated SPEC package (PRD/DESIGN/PLAN/verification) under strict output paths.
  Use when the android-project-analyst controller must understand, document, onboard, or migration-prep an existing Android project by dividing it into modules first, analyzing each module across presentation/architecture/data/behavior dimensions, recording inter-module assembly basis separately, then combining module representations into a full-project representation.
  Do NOT use for quick file/symbol lookup, non-Android codebases, or single-agent skill authoring.
version: "0.6"
kind: swarm-skill
disable-model-invocation: true
roles:
  - id: analysis-workspace-state
    kind: ai_agent
    purpose: Analysis ledger — module status, node output inventory, stale inputs, rerun/blocker history, artifact readiness, and next actions. No source analysis or SPEC writing.
    skills: []
    tools: [git]
  - id: presentation-resource
    kind: ai_agent
    purpose: Presentation and resource owner — screens, UI technologies, navigation, UI modules, local/remote image and media resources, safe downloads, and UI/resource migration implications.
    skills: []
    tools: [rg, curl]
  - id: project-architecture
    kind: ai_agent
    purpose: Project architecture owner — Gradle/module topology, architecture style, layer roles, dependency ecosystem, Jetpack/DI/platform services, generated tooling, and Android-only constraints.
    skills: []
    tools: [rg]
  - id: data-contract-flow
    kind: ai_agent
    purpose: Data contract and flow owner — network/local data contracts, models, consumers, repositories, streams, transformations, cache/error/pagination, write-back, and UI state propagation.
    skills: []
    tools: [rg]
  - id: behavior-logic
    kind: ai_agent
    purpose: Behavior and control-flow owner — user actions, lifecycle, state holders, business rules, side effects, state machines, navigation effects, gates, and cross-module interactions.
    skills: []
    tools: [rg]
---

# Android Project Analyst Swarm Skill

This is the agent-facing registry and team definition for the `android-project-analyst` controller (the same-name subagent in `kmp-migration/agents/`). It converts a Legacy Android source project into verified module artifacts, a global project representation, and SPEC artifacts for downstream onboarding, exploration, and migration agents.

**Canonical file recording system**: [output-contract.md](output-contract.md) defines every output path, required content, write order, and downstream **handoff package gates** (`P0`–`P6`). Downstream handlers (`migration-task-adapter`, `android-to-kmp-migrator`, `kmp-test-validator`) trigger only when the declared package artifacts exist, are non-empty, in-path, and not stale. The Leader MUST read `output-contract.md` before the first dispatch and MUST NOT claim completion without updating `handoff_gates` in the workspace ledger and `SPEC/verification.md`.

The team is **module-first Mixed B+C with a workspace-state ledger**: the Leader partitions the project into `analysis_modules`, writes index artifacts and one `modules/<module_id>/` folder per module, maintains `analysis-workspace-state` before downstream consumption, runs three foundation nodes in **parallel** (B) inside each module, then a final **gated specialization** node (C) synthesizes module behavior from verified upstream outputs. The Leader writes a module representation per module, records cross-module architecture and data/logic separately under `global/`, then combines everything into `global_representation.*` and SPEC. The controller owns routing, strict output-path enforcement, reconciliation, workspace-state refreshes, and SPEC integration; nodes own bounded module analysis only.

## Module Partitioning Model

Analysis follows a three-layer artifact model. Downstream migration agents (`android-to-kmp-migrator`) consume this layout to assemble modules in dependency order.

### Layer 1 — Module index and module ID folders

The Leader divides in-scope source into bounded `analysis_modules` and materializes:

- **Index**: `module-index/module_inventory.*` is the authoritative module schedule; `module-index/modules_index.json` is the machine-routable lookup from `module_id` to folder paths, dimension roots, and representation paths.
- **Per-module root**: every scheduled `module_id` gets `<output_root>/modules/<module_id>/` before node dispatch. No module analysis may run without its folder and `module_brief.json`.

Partitioning rules:

- Prefer Gradle modules and feature packages; split one Gradle module into multiple `analysis_modules` when independent features/routes/packages warrant it.
- Every in-scope source root belongs to exactly one scheduled module or `out_of_scope`.
- `module_id` is a stable slug reused across inventory, folder names, node outputs, representations, global cross-module records, and migration handoff.

### Layer 2 — Multi-dimensional understanding inside each module folder

Each module is understood from four analysis dimensions. Dimension outputs live under the same `module_id` folder and are indexed by `dimension_index.json`:

| Dimension | Node | Storage path under `modules/<module_id>/` |
|---|---|---|
| `presentation-resource` | `presentation-resource` | `node-results/presentation-resource/` |
| `project-architecture` | `project-architecture` | `node-results/project-architecture/` |
| `data-contract-flow` | `data-contract-flow` | `node-results/data-contract-flow/` |
| `behavior-logic` | `behavior-logic` | `node-results/behavior-logic/` |

The Leader writes `dimension_index.json` after all four node outputs verify. `representation/module_representation.*` synthesizes only from verified dimension artifacts for that `module_id`. Nodes must not write outside their assigned dimension directory.

### Layer 3 — Cross-module architecture and data/logic (migration assembly basis)

Inter-module relationships are **not** folded only into per-module representations. After every scheduled module has a representation, the Leader writes dedicated global artifacts before `global_representation.*`:

- `global/cross_module_architecture.*` — Gradle/topology glue, layer boundaries, navigation integration, shared platform services, DI scope bridges, and architectural dependency graph across `module_id`s.
- `global/cross_module_data_logic.*` — shared APIs/models/stores, cross-module data flows, event/callback/bus links, and cross-module control interactions.
- `global/migration_assembly_basis.*` — ordered module assembly sequence, integration checkpoints, shared contracts each module must preserve, and blockers for partial migration.

`global_representation.*` synthesizes from module representations plus the three cross-module artifacts above. SPEC `design.md` and migration-mode `plan.md` must cite these global cross-module artifacts when describing integration or assembly order.

## Workflow

The full playbook (Mermaid topology, per-step gates, integration rules, Final Report format) is in [workflow.md](workflow.md). Protocol summary:

0. **Pre-flight: check dependencies** — read [dependencies.yaml](dependencies.yaml): `tools[]` (`rg`, `curl`, `git`), `optional_mcp.jetbrains`, and migration-mode `downstream_handoff` **P6** requirements. Report `dependency_preflight` in `run_manifest.json`; **user decides** whether to proceed.
1. **Trigger + output root lock** — Leader verifies Android evidence and scope, selects `exploration` or `migration`, locks `output_root = <output_dir or ~/.a2c_agents/understand>/android-project-analyst`, and writes `run_manifest.json`.
2. **Workspace state** — dispatch `analysis-workspace-state` under `<output_root>/workspace-state/`; refresh it after module inventory, each module node group, each module representation, cross-module global records, global representation, and SPEC.
3. **Module inventory + index** — Leader writes `module-index/module_inventory.json` and `.md`, plus `module-index/modules_index.json`, dividing the project into deterministic `analysis_modules` and creating each `modules/<module_id>/` folder with scopes and output roots.
4. **Per-module Stage A (parallel, B-pattern)** — for each `module_id`, dispatch `presentation-resource`, `project-architecture`, and `data-contract-flow` under `<output_root>/modules/<module_id>/node-results/<dimension>/`.
5. **Per-module Stage B (gated behavior stage, C-pattern)** — after that module's Stage A verifies and workspace-state marks upstream outputs fresh, dispatch `behavior-logic` under the same module root.
6. **Module dimension index + representation** — Leader writes `dimension_index.json`, then `representation/module_representation.json` and `.md`, synthesizing all four dimensions for that `module_id` before moving to the next module.
7. **Cross-module global records** — Leader aggregates verified module outputs into `global/cross_module_architecture.*`, `global/cross_module_data_logic.*`, and `global/migration_assembly_basis.*`.
8. **Global representation + SPEC** — Leader combines module representations and cross-module global records into `global/global_representation.json` and `.md`, then writes SPEC under `<output_root>/SPEC`.

## Roles

Each node is dispatched as a subagent that must read its role file (`skill_spec_path`) and execute only that role's bounded slice. The dispatch order enforces upstream evidence availability for final behavior analysis.

| id | Purpose | When dispatched | Input | Key dependencies | Role file |
|---|---|---|---|---|---|
| analysis-workspace-state | Analysis ledger: module status, node output inventory, stale inputs, rerun/blocker history, artifact readiness, next actions | After output root lock and refreshed after each major group | output root, module inventory/statuses, node outputs, representations, SPEC outputs | git | [roles/analysis-workspace-state.md](roles/analysis-workspace-state.md) |
| presentation-resource | Presentation/resources: screens, navigation, UI modules, local/remote resources, safe downloads, usage map | Per-module Stage A (parallel) | source path, `module_id`, module scope, module brief | rg, curl | [roles/presentation-resource.md](roles/presentation-resource.md) |
| project-architecture | Project architecture/ecosystem: topology, architecture style, dependencies, Jetpack/DI/platform constraints | Per-module Stage A (parallel) | source path, `module_id`, module scope, module brief | rg | [roles/project-architecture.md](roles/project-architecture.md) |
| data-contract-flow | Data contracts/flow: APIs, local data sources, models, repositories, streams, transformations, UI state | Per-module Stage A (parallel) | source path, `module_id`, module scope, module brief, optional presentation hints | rg | [roles/data-contract-flow.md](roles/data-contract-flow.md) |
| behavior-logic | Behavior/control flow: actions, lifecycle, state holders, rules, side effects, state machines | Per-module Stage B (after A) | `module_id`, module scope, all Stage A outputs | rg | [roles/behavior-logic.md](roles/behavior-logic.md) |

> Before dispatching each teammate, read the corresponding role file and paste its
> `## Inline Persona for Teammate` section directly into the dispatch prompt — adopting
> agents do NOT auto-load role files. Fill the `{PLACEHOLDER}` inputs from the contract.

## Files

| File | What it contains | When to read |
|---|---|---|
| [output-contract.md](output-contract.md) | Canonical path tree, artifact registry, JSON schemas, handoff packages `P0`–`P6`, downstream trigger rules | **Before first dispatch and before claiming handoff** — downstream handlers gate on this file |
| [workflow.md](workflow.md) | Mermaid B+C topology, step-by-step protocol with gates, integration rules, Final Report format | Before first dispatch — the complete playbook |
| [bind.md](bind.md) | Resource limits, team behavioral constraints, contract enforcement, failure & degraded modes | When hitting limits, handling failures, or scoping a large project |
| [roles/\*.md](roles/) | Per-node identity, success criteria, boundary, output schema, Inline Persona for Teammate | Before dispatching each teammate — extract Inline Persona |
| [dependencies.yaml](dependencies.yaml) | CLI tools, optional `jetbrains` MCP, migration **P6** downstream handoff | Step 0 — verify deps, record `dependency_preflight`, user decides go/no-go |

## SPEC Output Contract

The Leader integrates verified module representations and the global representation into a SPEC package under `<output_root>/SPEC`:

| Artifact | Goal | Required in |
|---|---|---|
| `prd.md` | What the legacy app/feature does: scope, features, journeys, data needs, business rules, assumptions. | Exploration and migration |
| `design.md` | How the legacy project is built: architecture, UI/navigation, ecosystem, resources, APIs, data flow, logic, risks. | Exploration and migration |
| `plan.md` | How to migrate/refactor: milestones, ordered tasks, source-to-target mapping, resource migration, validation, risks. | Migration only |
| `verification.md` | Coverage matrix, evidence/traceability index, consistency checks, readiness verdict (`ready` / `ready_with_assumptions` / `blocked`). | Exploration and migration |

SPEC documents must synthesize, not paste node summaries. Every important claim maps to node output + source-path evidence, or is marked an assumption or gap. Node Markdown outputs are agent-readable handoffs that preserve exact paths, evidence, gaps, and routing context.

## Strict Output Schedule And Handoff Gates

The Leader MUST follow the write-order gates `G0`–`G9` and handoff packages `P0`–`P6` in [output-contract.md](output-contract.md). Summary:

| Gate | Artifacts | Unlocks |
|---|---|---|
| `G0`–`G2` | `run_manifest.json`, workspace ledger, `module_inventory.*`, `modules_index.json` | Module dispatch (`P1`) |
| `G3`–`G5` | per-module `module_brief.json` + four dimension JSON/MD pairs | Dimension completeness (`P2`) |
| `G6` | per-module `dimension_index.json`, `module_representation.*` | Module handoff (`P3`) |
| `G7` | `cross_module_architecture.*`, `cross_module_data_logic.*`, `migration_assembly_basis.*` | Migrator scheduling (`P4`) |
| `G8`–`G9` | `global_representation.*`, `SPEC/*` | Exploration (`P5`) or migration (`P6`) pipeline entry |

Any artifact written outside the path tree in `output-contract.md` is **invalid** — downstream handlers MUST return `blocked` with `reason: out_of_path`.

Before final completion, the Leader MUST set `handoff_gates` in `analysis_workspace_state.json` and mirror them in `SPEC/verification.md` → `## Handoff Gates`. Set `run_manifest.json` → `handoff_package` to the highest ready package (`P0`..`P6`).

JSON artifacts are the machine-routable source of truth. Markdown artifacts are agent-readable handoffs. Full per-file content requirements live in [output-contract.md](output-contract.md) § Artifact Registry.

## Optional Android Studio MCP Context

When the `jetbrains` MCP server is available, the controller may pass indexed Android Studio context into the shared brief: project modules/dependencies/VCS roots (`get_project_modules`, `get_project_dependencies`, `get_repositories`), file/symbol discovery (`find_files_by_glob`, `search_in_files_by_regex`, `get_symbol_info`), and diagnostics (`get_file_problems`). Always pass `projectPath: <source_project_path>`. Treat MCP output as supporting evidence — major claims still need source paths and confidence labels; record any MCP gap in `verification.md`.

## Shared Rules

- Each node must read its own role file before analysis and stay inside its responsibility boundary.
- `analysis-workspace-state` must be refreshed before downstream roles consume prior artifacts when source, module, node, representation, or SPEC inputs changed.
- Each node output must include source-path evidence for important claims; unknowns are marked explicitly, never guessed.
- Node outputs are intermediate artifacts for SPEC generation, not final user-facing documentation.
- No node or the Leader modifies the analyzed source project.
- Downstream handlers gate on file artifacts only — never on chat summaries. Missing package artifacts MUST yield `blocked`, not best-effort continuation.
