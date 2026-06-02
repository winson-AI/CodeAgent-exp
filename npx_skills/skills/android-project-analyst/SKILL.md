---
name: android-project-analyst
description: |
  7-role parallel-then-pipeline (B+C) Swarm Skill that converts a Legacy Android project into verified, source-traceable node artifacts and an integrated SPEC package (PRD/DESIGN/PLAN/verification).
  Use when the android-project-analyst controller must understand, document, onboard, or migration-prep an existing Android project across UI, architecture, ecosystem, API, resource, data-flow, and logic.
  Do NOT use for quick file/symbol lookup, non-Android codebases, or single-agent skill authoring.
version: "0.2"
kind: swarm-skill
disable-model-invocation: true
roles:
  - id: ui-understand
    kind: ai_agent
    purpose: UI surface owner — entry points, screen inventory, XML/Compose hierarchy, navigation edges, shared components, UI module boundaries.
    skills: []
    tools: [rg]
  - id: architecture-pattern
    kind: ai_agent
    purpose: Architecture owner — Gradle/package topology, architecture style, layer roles, dependency direction, boundary violations, legacy hybrids.
    skills: []
    tools: [rg]
  - id: android-ecosystem
    kind: ai_agent
    purpose: Ecosystem owner — Gradle/SDK/build config, Jetpack & third-party deps, DI, persistence, background work, platform services, Android-only constraints.
    skills: []
    tools: [rg]
  - id: api-list
    kind: ai_agent
    purpose: API/data-source owner — network stack, service declarations, request/response models, consumers, local sources, cache/error/pagination, unknown APIs.
    skills: []
    tools: [rg]
  - id: resource-understand
    kind: ai_agent
    purpose: Resource owner — local & online image/media resources, safe downloaded copies, usage map, placeholder/error/theme links, migration implications.
    skills: []
    tools: [rg, curl]
  - id: data-flow
    kind: ai_agent
    purpose: Data-flow owner — sources through repositories, mappers, reactive streams, caches, write-back paths, and UI state propagation.
    skills: []
    tools: [rg]
  - id: logic-understand
    kind: ai_agent
    purpose: Logic/control-flow owner — user actions, lifecycle, state holders, business rules, side effects, state machines, cross-module interactions.
    skills: []
    tools: [rg]
---

# Android Project Analyst Swarm Skill

This is the agent-facing registry and team definition for the `android-project-analyst` controller (the same-name subagent in `kmp-migration/agents/`). It converts a Legacy Android source project into verified analysis artifacts for downstream onboarding, exploration, and migration agents.

The team is **Mixed B+C**: four foundation nodes run in **parallel** (B) over disjoint slices, then a **gated pipeline** (C) runs resource + data-flow, then logic. A single agent role-playing all seven slices systematically under-delivers — it converges on whichever slice it started with, blurs ownership boundaries, and silently rebuilds the same catalog three times. Isolating each slice into an owned node with a hard handoff gate keeps every claim traceable to source and prevents the controller from inventing un-evidenced architecture. The controller (Leader) owns routing, contract enforcement, reconciliation, and SPEC integration; nodes own bounded analysis only.

## Workflow

The full playbook (Mermaid topology, per-step gates, integration rules, Final Report format) is in [workflow.md](workflow.md). Protocol summary:

0. **Pre-flight: check dependencies** — read [dependencies.yaml](dependencies.yaml) and verify `rg` / `curl`. Both are `required: false`; built-in Grep/Read substitute for `rg`, and missing `curl` degrades resource downloads to `download_gaps`. Report status; **user decides** whether to proceed.
1. **Trigger + mode + shared brief** — Leader verifies Android evidence and scope, selects `exploration` or `migration`, and builds a minimal shared brief. Default `output_dir` = `~/.a2c_agents/understand/` (SPEC under `<output_dir>/SPEC`, node artifacts under `<output_dir>/node-results/<node>`). See [bind.md](bind.md) for over-scale degradation.
2. **Stage A (parallel, B-pattern)** — dispatch `ui-understand`, `architecture-pattern`, `android-ecosystem`, `api-list`. Gate: each return is `completed` with verified non-empty `output_files`, else re-dispatch with the failure reason.
3. **Stage B (gated handoff, C-pattern)** — after Stage A verifies, dispatch `resource-understand` and `data-flow` with upstream output paths.
4. **Stage C (final stage)** — after Stage B verifies, dispatch `logic-understand` with all upstream paths.
5. **Integrate** — reconcile verified outputs into a coverage matrix + evidence index; conflicts affecting architecture/data-flow/ecosystem/migration become `Needs confirmation`.
6. **Final: write SPEC + verdict** — Leader writes `prd.md`, `design.md`, `verification.md` (+ `plan.md` for migration) under `<output_dir>/SPEC`, then emits the completion report. Leader surfaces conflicts verbatim, never mediates.

## Roles

Each node is dispatched as a subagent that must read its role file (`skill_spec_path`) and execute only that role's bounded slice. The dispatch order enforces upstream→downstream data availability.

| id | Purpose | When dispatched | Input | Key dependencies | Role file |
|---|---|---|---|---|---|
| ui-understand | UI surface: screens, navigation, UI modules | Stage A (parallel) | source path, scope, brief | rg | [roles/ui-understand.md](roles/ui-understand.md) |
| architecture-pattern | Architecture style, layering, boundaries | Stage A (parallel) | source path, scope, brief | rg | [roles/architecture-pattern.md](roles/architecture-pattern.md) |
| android-ecosystem | Build/SDK/Jetpack/DI/platform constraints | Stage A (parallel) | source path, scope, brief | rg | [roles/android-ecosystem.md](roles/android-ecosystem.md) |
| api-list | APIs, models, local data sources | Stage A (parallel) | source path, scope, brief, optional UI entry points | rg | [roles/api-list.md](roles/api-list.md) |
| resource-understand | Local + online resources, downloads, usage map | Stage B (after A) | UI/API/ecosystem outputs | rg, curl | [roles/resource-understand.md](roles/resource-understand.md) |
| data-flow | Sources→repos→streams→UI state | Stage B (after A) | required api_list, optional arch/ecosystem/UI | rg | [roles/data-flow.md](roles/data-flow.md) |
| logic-understand | User/lifecycle control flow, business rules | Stage C (after B) | all upstream node outputs | rg | [roles/logic-understand.md](roles/logic-understand.md) |

> Before dispatching each teammate, read the corresponding role file and paste its
> `## Inline Persona for Teammate` section directly into the dispatch prompt — adopting
> agents do NOT auto-load role files. Fill the `{PLACEHOLDER}` inputs from the contract.

## Files

| File | What it contains | When to read |
|---|---|---|
| [workflow.md](workflow.md) | Mermaid B+C topology, step-by-step protocol with gates, integration rules, Final Report format | Before first dispatch — the complete playbook |
| [bind.md](bind.md) | Resource limits, team behavioral constraints, contract enforcement, failure & degraded modes | When hitting limits, handling failures, or scoping a large project |
| [roles/\*.md](roles/) | Per-node identity, success criteria, boundary, output schema, Inline Persona for Teammate | Before dispatching each teammate — extract Inline Persona |
| [dependencies.yaml](dependencies.yaml) | External CLI tools (`rg`, `curl`) checked at startup | Step 0 — verify deps, report missing items, user decides go/no-go |

## Converted SPEC Output Contract

The Leader integrates verified node outputs into a SPEC package under `<output_dir>/SPEC`:

| Artifact | Goal | Required in |
|---|---|---|
| `prd.md` | What the legacy app/feature does: scope, features, journeys, data needs, business rules, assumptions. | Exploration and migration |
| `design.md` | How the legacy project is built: architecture, UI/navigation, ecosystem, resources, APIs, data flow, logic, risks. | Exploration and migration |
| `plan.md` | How to migrate/refactor: milestones, ordered tasks, source-to-target mapping, resource migration, validation, risks. | Migration only |
| `verification.md` | Coverage matrix, evidence/traceability index, consistency checks, readiness verdict (`ready` / `ready_with_assumptions` / `blocked`). | Exploration and migration |

SPEC documents must synthesize, not paste node summaries. Every important claim maps to node output + source-path evidence, or is marked an assumption or gap. Node Markdown outputs are agent-readable handoffs that preserve exact paths, evidence, gaps, and routing context.

## Optional Android Studio MCP Context

When the `jetbrains` MCP server is available, the controller may pass indexed Android Studio context into the shared brief: project modules/dependencies/VCS roots (`get_project_modules`, `get_project_dependencies`, `get_repositories`), file/symbol discovery (`find_files_by_glob`, `search_in_files_by_regex`, `get_symbol_info`), and diagnostics (`get_file_problems`). Always pass `projectPath: <source_project_path>`. Treat MCP output as supporting evidence — major claims still need source paths and confidence labels; record any MCP gap in `verification.md`.

## Shared Rules

- Each node must read its own role file before analysis and stay inside its responsibility boundary.
- Each node output must include source-path evidence for important claims; unknowns are marked explicitly, never guessed.
- Node outputs are intermediate artifacts for SPEC generation, not final user-facing documentation.
- No node or the Leader modifies the analyzed source project.
