---
name: android-project-analyst
description: |
  5-role module-first Swarm Skill that converts a Legacy Android project into module-scoped artifacts, a workspace-state ledger, a global representation, and an integrated SPEC package (PRD/DESIGN/PLAN/verification) under strict output paths.
  Use when the android-project-analyst controller must understand, document, onboard, or migration-prep an existing Android project by dividing it into modules first, including UI and logic coverage, then combining module representations into a full-project representation.
  Do NOT use for quick file/symbol lookup, non-Android codebases, or single-agent skill authoring.
version: "0.4"
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

The team is **module-first Mixed B+C with a workspace-state ledger**: the Leader partitions the project into `analysis_modules`, maintains `analysis-workspace-state` before downstream consumption, runs three foundation nodes in **parallel** (B) inside each module, then a final **gated specialization** node (C) synthesizes module behavior from verified upstream outputs. The Leader writes a module representation per module before combining them into `global_representation.*` and SPEC. The controller owns routing, strict output-path enforcement, reconciliation, workspace-state refreshes, and SPEC integration; nodes own bounded module analysis only.

## Workflow

The full playbook (Mermaid topology, per-step gates, integration rules, Final Report format) is in [workflow.md](workflow.md). Protocol summary:

0. **Pre-flight: check dependencies** — read [dependencies.yaml](dependencies.yaml) and verify `rg` / `curl` / `git`. All are `required: false`; built-in Grep/Read substitute for `rg`, missing `curl` degrades presentation/resource downloads to `download_gaps`, and missing `git` degrades stale-input detection. Report status; **user decides** whether to proceed.
1. **Trigger + output root lock** — Leader verifies Android evidence and scope, selects `exploration` or `migration`, locks `output_root = <output_dir or ~/.a2c_agents/understand>/android-project-analyst`, and writes `run_manifest.json`.
2. **Workspace state** — dispatch `analysis-workspace-state` under `<output_root>/workspace-state/`; refresh it after module inventory, each module node group, each module representation, global representation, and SPEC.
3. **Module inventory** — Leader writes `module-index/module_inventory.json` and `.md`, dividing the project into deterministic `analysis_modules` with UI, logic, data, resource, and dependency scopes.
4. **Per-module Stage A (parallel, B-pattern)** — for each `module_id`, dispatch `presentation-resource`, `project-architecture`, and `data-contract-flow` under `<output_root>/modules/<module_id>/node-results/<node_id>/`.
5. **Per-module Stage B (gated behavior stage, C-pattern)** — after that module's Stage A verifies and workspace-state marks upstream outputs fresh, dispatch `behavior-logic` under the same module root.
6. **Module representation** — Leader writes `<output_root>/modules/<module_id>/representation/module_representation.json` and `.md` before moving to the next module.
7. **Global representation + SPEC** — Leader combines module representations into `<output_root>/global/global_representation.json` and `.md`, then writes SPEC under `<output_root>/SPEC`.

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
| [workflow.md](workflow.md) | Mermaid B+C topology, step-by-step protocol with gates, integration rules, Final Report format | Before first dispatch — the complete playbook |
| [bind.md](bind.md) | Resource limits, team behavioral constraints, contract enforcement, failure & degraded modes | When hitting limits, handling failures, or scoping a large project |
| [ROLE_CLUSTERING.md](ROLE_CLUSTERING.md) | Function/duty analysis, old-to-new role mapping, and clustering rationale | When auditing role ownership or updating personas |
| [roles/\*.md](roles/) | Per-node identity, success criteria, boundary, output schema, Inline Persona for Teammate | Before dispatching each teammate — extract Inline Persona |
| [dependencies.yaml](dependencies.yaml) | External CLI tools (`rg`, `curl`, `git`) checked at startup | Step 0 — verify deps, report missing items, user decides go/no-go |

## Converted SPEC Output Contract

The Leader integrates verified module representations and the global representation into a SPEC package under `<output_root>/SPEC`:

| Artifact | Goal | Required in |
|---|---|---|
| `prd.md` | What the legacy app/feature does: scope, features, journeys, data needs, business rules, assumptions. | Exploration and migration |
| `design.md` | How the legacy project is built: architecture, UI/navigation, ecosystem, resources, APIs, data flow, logic, risks. | Exploration and migration |
| `plan.md` | How to migrate/refactor: milestones, ordered tasks, source-to-target mapping, resource migration, validation, risks. | Migration only |
| `verification.md` | Coverage matrix, evidence/traceability index, consistency checks, readiness verdict (`ready` / `ready_with_assumptions` / `blocked`). | Exploration and migration |

SPEC documents must synthesize, not paste node summaries. Every important claim maps to node output + source-path evidence, or is marked an assumption or gap. Node Markdown outputs are agent-readable handoffs that preserve exact paths, evidence, gaps, and routing context.

## Strict Output Schedule

The Leader MUST write artifacts in this order and MUST NOT skip directly from raw source to global SPEC:

1. `<output_root>/run_manifest.json`
2. `<output_root>/workspace-state/analysis_workspace_state.json` and `.md` (initialized and refreshed after each major group)
3. `<output_root>/module-index/module_inventory.json` and `.md`
4. For each `module_id` in deterministic `module_order`:
   - `<output_root>/modules/<module_id>/module_brief.json`
   - `<output_root>/modules/<module_id>/node-results/presentation-resource/presentation_resource.json` and `.md`
   - `<output_root>/modules/<module_id>/node-results/project-architecture/project_architecture.json` and `.md`
   - `<output_root>/modules/<module_id>/node-results/data-contract-flow/data_contract_flow.json` and `.md`
   - `<output_root>/modules/<module_id>/node-results/behavior-logic/behavior_logic.json` and `.md`
   - `<output_root>/modules/<module_id>/representation/module_representation.json` and `.md`
5. `<output_root>/global/global_representation.json` and `.md`
6. `<output_root>/SPEC/prd.md`, `design.md`, `verification.md`, and migration-only `plan.md`

Any artifact written outside these paths is invalid for downstream gates.

## Optional Android Studio MCP Context

When the `jetbrains` MCP server is available, the controller may pass indexed Android Studio context into the shared brief: project modules/dependencies/VCS roots (`get_project_modules`, `get_project_dependencies`, `get_repositories`), file/symbol discovery (`find_files_by_glob`, `search_in_files_by_regex`, `get_symbol_info`), and diagnostics (`get_file_problems`). Always pass `projectPath: <source_project_path>`. Treat MCP output as supporting evidence — major claims still need source paths and confidence labels; record any MCP gap in `verification.md`.

## Shared Rules

- Each node must read its own role file before analysis and stay inside its responsibility boundary.
- `analysis-workspace-state` must be refreshed before downstream roles consume prior artifacts when source, module, node, representation, or SPEC inputs changed.
- Each node output must include source-path evidence for important claims; unknowns are marked explicitly, never guessed.
- Node outputs are intermediate artifacts for SPEC generation, not final user-facing documentation.
- No node or the Leader modifies the analyzed source project.
