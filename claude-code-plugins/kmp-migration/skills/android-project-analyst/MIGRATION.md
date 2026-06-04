# Conversion Note: `android-project-analyst` → clustered Swarm Skill

This file records the role-shape history for the `android-project-analyst` skill folder. It is not an active dispatch contract; active node contracts live in [SKILL.md](SKILL.md), [workflow.md](workflow.md), and the files under [roles](roles/).

## Phase 1 — Controller support skill to Swarm Skill

The skill was first converted from a single controller-support skill (a flat `SKILL.md` registry plus seven sibling node-spec files) into a compliant **Swarm Skill** using `swarmskill-creator` convert mode.

### Source structure before Phase 1

- `SKILL.md` — controller registry describing convert mode, node contracts, dispatch order, and the SPEC output contract.
- Seven flat node specs at the skill root: `ui-understand.md`, `architecture-pattern.md`, `android-ecosystem.md`, `api-list.md`, `resource-understand.md`, `data-flow.md`, `logic-understand.md`. Each contained Role / Inputs / Mandatory Input Validation & Output Storage / Specific Task / Required Outputs / Return Format / Self-Check.

### What Phase 1 added

The registry already separated controller from nodes, but it did not encode the team as a first-class artifact: there were no per-role anti-convergence mottos, no `Forbidden`/`Mandatory` boundary blocks the validator could check, no pasteable `Inline Persona` (so each dispatch re-derived the contract by hand), no Mermaid topology making the parallel-then-pipeline shape explicit, and no resource/behavioral guardrails (`max_parallel_teammates`, token/wall-clock budgets, degraded modes). The handoff gates between stages lived only in prose.

The seven-role Swarm Skill preserved the source contracts while adding explicit topology, per-role boundaries, self-contained pasteable personas, budgets, and degraded modes.

## Phase 2 — Seven roles to four clustered roles

The second pass analyzed each role's function and duty, found repeated cataloging across adjacent personas, and reduced active dispatch from seven roles to four clustered personas. The full analysis is in [ROLE_CLUSTERING.md](ROLE_CLUSTERING.md).

## Phase 3 — Add workspace-state ledger role

The third pass adds `analysis-workspace-state`, following the ledger pattern used by `android-to-kmp-migrator` and `kmp-test-validator`. This role does not change the four clustered analysis personas. It tracks module/node artifact status, stale upstream inputs, rerun/blocker history, and next safe controller actions so global representations and SPEC files are not built from stale evidence.

## Old-to-new role map

| Old role(s) | New clustered role | Reason |
|---|---|---|
| `ui-understand` + `resource-understand` | `presentation-resource` | Resource usage and migration risk are meaningful only when tied to screens, components, navigation, and UI technology. |
| `architecture-pattern` + `android-ecosystem` | `project-architecture` | Module topology, architecture style, dependency ecosystem, DI scopes, generated tooling, and Android-only constraints form one project-structure reality check. |
| `api-list` + `data-flow` | `data-contract-flow` | APIs, local data sources, models, repositories, streams, cache/error behavior, transformations, and write-back paths are one data path. |
| `logic-understand` | `behavior-logic` | Behavior remains last because user/lifecycle/control-flow analysis requires verified upstream presentation, project, and data evidence. |
| none (new ledger role) | `analysis-workspace-state` | Workspace-state tracking is cross-cutting and read-only; it prevents stale module/node artifacts from being consumed downstream. |

## Current decomposition

- **Pattern: Workspace-state + Mixed B + C.** `analysis-workspace-state` is initialized after output-root lock and refreshed after each major artifact group. Stage A (`presentation-resource`, `project-architecture`, `data-contract-flow`) is parallel decomposition (B) over clustered slices. Stage B (`behavior-logic`) is a gated specialization step (C) that consumes verified, non-stale upstream outputs and must not rebuild them.
- **Boundary check: PASS.** Clustered roles remove the most common duplicate cataloging while preserving distinct ownership: workspace ledger vs. presentation/resource evidence vs. project architecture/ecosystem evidence vs. data contract/flow evidence vs. behavior/control evidence.

## Current content port map

| Contract content | Current location |
|---|---|
| Active role registry | `SKILL.md` frontmatter |
| Staged dispatch order + verification | `workflow.md` |
| Mandatory contract enforcement + agent-only rules | `bind.md` § Behavioral Constraints |
| Node failure / rerun handling | `bind.md` § Failure Handling |
| Function/duty analysis and old-to-new map | `ROLE_CLUSTERING.md` |
| Per-role identity, boundary, schema, and teammate persona | `roles/<clustered-role>.md` |
| SPEC output contract + MCP context | `SKILL.md` body |

## Output Contract Refinement

The active skill docs now distinguish output file names from output content responsibilities. `SKILL.md` and `workflow.md` define the full artifact schedule and content matrix, while each role file states the exact JSON/Markdown filenames and the evidence each artifact must contain.

This refinement keeps role ownership explicit:

- `analysis-workspace-state.*` records ledger state only.
- `presentation_resource.*` records screens, checked UI trees, navigation, presentation modules, and resources.
- `project_architecture.*` records build/module topology, architecture patterns, dependencies, platform services, and migration constraints.
- `data_contract_flow.*` records APIs, models, data sources, mappings, streams, and end-to-end data flows.
- `behavior_logic.*` records user actions, lifecycle behavior, state holders, rules, side effects, state machines, and upstream alignment.

The Leader must reject artifacts that have the correct filename but contain another role's work or prose-only summaries without machine-routable evidence.
