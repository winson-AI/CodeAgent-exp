---
name: android-project-analyst
description: Controller support skill for Legacy Android project analysis. Use with the android-project-analyst agent to locate node skill specs for UI understanding, architecture pattern analysis, Android ecosystem analysis, API listing, resource understanding, data-flow tracing, and logic understanding.
disable-model-invocation: true
---

# Android Project Analyst Node Skill Registry

This directory stores the node skill specs used by the `android-project-analyst` controller. The controller owns routing, output verification, SPEC integration, and final readiness judgment. Node subagents own deep analysis of Legacy Android code.

## Default Output Directory

Unless the user or controller provides an explicit `output_dir`, use `~/.d2c_agents/understand/` as the artifact root. Write SPEC artifacts under `<output_dir>/SPEC` and node artifacts under `<output_dir>/node-results`.

## Node Skills

| Node | Skill spec | Responsibility |
|---|---|---|
| `UI understand` | [ui-understand.md](ui-understand.md) | Screen inventory, UI technology mapping, navigation, UI hierarchy, and UI module boundaries. |
| `Architecture pattern` | [architecture-pattern.md](architecture-pattern.md) | MVC/MVP/MVVM/MVI/Clean Architecture detection, module layering, dependency boundaries, and legacy hybrid risks. |
| `Android ecosystem` | [android-ecosystem.md](android-ecosystem.md) | Gradle, SDK, Jetpack, DI, persistence, background work, resources, generated-code tooling, and third-party dependency constraints. |
| `API list` | [api-list.md](api-list.md) | Network API and data-source catalog, service contracts, models, consumers, and gaps. |
| `Resource understand` | [resource-understand.md](resource-understand.md) | Local and online image/icon/media resources, usage locations, downloaded analysis copies, placeholders, resource paths, and migration implications. |
| `Data flow` | [data-flow.md](data-flow.md) | Data sources, repositories, reactive streams, transformations, caches, write-back paths, and UI state propagation. |
| `Logic understand` | [logic-understand.md](logic-understand.md) | Business logic, control flow, state management, lifecycle behavior, user actions, side effects, and cross-module behavior. |

## Recommended Dispatch Order

1. Run `UI understand`, `Architecture pattern`, `Android ecosystem`, and `API list` as foundation nodes.
2. Run `Resource understand` after UI, API, and ecosystem outputs are available.
3. Run `Data flow` after API and architecture outputs are available.
4. Run `Logic understand` last, using all upstream outputs.

## SPEC Output Contract

The controller must integrate verified node outputs into a SPEC package under `<output_dir>/SPEC`:

| Artifact | Goal | Required in |
|---|---|---|
| `prd.md` | Explain what the legacy app/feature does: scope, features, journeys, data needs, business rules, assumptions. | Exploration and migration |
| `design.md` | Explain how the legacy project is built: architecture patterns, UI/navigation, Android ecosystem, resources, APIs/data sources, data flow, logic/control flow, risks. | Exploration and migration |
| `plan.md` | Explain how to migrate/refactor: milestones, ordered tasks, source-to-target mapping, resource migration, validation, risks. | Migration only |
| `verification.md` | Prove coverage and traceability: node outputs, artifact inventory, coverage matrix, claim evidence, consistency checks, readiness verdict. | Exploration and migration |

SPEC documents must not be a raw paste of node summaries. They must synthesize nodes into a coherent product + architecture + verification package. Every important claim must map to node output and source-path evidence, or be marked as an assumption or gap.

## Verification Expectations

Before the controller returns:

- All required node outputs exist and are non-empty.
- All required SPEC artifacts for the selected mode exist and are non-empty.
- `verification.md` includes a readiness verdict: `ready`, `ready_with_assumptions`, or `blocked`.
- Screens from `UI understand` are represented in `design.md` or explicitly out of scope.
- Architecture patterns and legacy hybrid risks are represented in `design.md`.
- Android ecosystem constraints are represented in `design.md` and, for migration mode, reflected in `plan.md`.
- APIs used by data or logic flows appear in `api-list` output or are marked unknown.
- Local and online resources used by UI/data/logic appear in `resource-understand` output or are marked unknown.
- Data-flow and logic-flow names align across `design.md`, `plan.md`, and `verification.md`.
- Unknown dynamic code paths are not presented as verified facts.

## Shared Rules

- Each node subagent must read its own skill spec before analysis.
- Each node must stay inside its responsibility boundary.
- Each node output must include source path evidence for important claims.
- Node outputs are intermediate artifacts for SPEC generation, not final user-facing documentation.
- Unknowns must be marked explicitly instead of guessed.
- Do not modify source code in any node skill.
