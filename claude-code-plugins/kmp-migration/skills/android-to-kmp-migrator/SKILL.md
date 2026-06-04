---
name: android-to-kmp-migrator
description: |
  10-role reduced module-first Swarm Skill (C+B) that migrates Legacy Android into an existing KMP target project with strict output roots, migration-module inventory, per-module node results, module/global representations, review-fix modes, verification checks, and a validation-ready migration report.
  Use with the android-to-kmp-migrator controller to port Android UI, resources, navigation, state, data, platform behavior, and logic into one KMP project by migrating each module first, then synthesizing a global migration representation for kmp-test-validator.
  Do NOT use for Legacy Android analysis, KMP-only feature work, quick lookups, or non-migration refactors.
version: "0.4"
kind: swarm-skill
disable-model-invocation: true
roles:
  - id: migration-workspace-state
    kind: ai_agent
    purpose: State/progress ledger owner — per-module migration status, finish rates, plan-vs-code gaps, changed-file ownership, stale outputs, rerun hooks, blocker history, and next actions. No code analysis or edits.
    skills: []
    tools: [git]
  - id: migration-analysis-planning
    kind: ai_agent
    purpose: Analysis and planning owner — Legacy SPEC/raw-source deltas, target KMP understanding, reuse inventory, source-to-target map, integration scaffold, and ordered module tasks.
    skills: []
    tools: [rg]
  - id: dependency-platform-gate
    kind: ai_agent
    purpose: Dependency and platform owner — minimal-change dependency readiness plus Android-only API replacement strategy and expect/actual/platform-source-set plan.
    skills: []
    tools: [rg]
  - id: presentation-integration
    kind: ai_agent
    purpose: Presentation integration owner — theme/design tokens, resources, online media modeling, navigation routes, presentation gaps, and UI handoff.
    skills: []
    tools: [rg, curl]
  - id: state-data-prep
    kind: ai_agent
    purpose: State and data preparation owner — state holders, DTO/domain/UI models, mappers, API/data contract expectations, and logic handoff.
    skills: []
    tools: [rg]
  - id: ui-implementation
    kind: ai_agent
    purpose: UI implementation owner — migrated Compose UI layout/components/states/resources first, with binding surfaces and no business logic.
    skills: []
    tools: [rg]
  - id: logic-implementation
    kind: ai_agent
    purpose: Logic implementation owner — repositories/use cases/API integration/state propagation/business logic bound to approved UI surfaces.
    skills: []
    tools: [rg]
  - id: module-node-review-fix
    kind: ai_agent
    purpose: Review/fix owner with strict modes — read-only review or scoped fix for one module/node slice; fresh re-review required after every fix.
    skills: []
    tools: [rg, git]
  - id: migration-verification
    kind: ai_agent
    purpose: Verification owner — source-set, API contract, UI render/fidelity, and incremental build checks with stable check IDs and routed failures.
    skills: []
    tools: [rg, git]
  - id: completion-report
    kind: ai_agent
    purpose: Completion/report owner with strict modes — readiness/rerun/blocker decisions and final migration_report handoff after module/global representations exist.
    skills: []
    tools: [rg, git]
---

# Android To KMP Migrator Swarm Skill

This is the agent-facing registry and team definition for the `android-to-kmp-migrator` controller. It converts a completed Legacy Android SPEC plus an existing KMP target project into migrated, validation-ready KMP code through a module-first schedule.

The team is a **reduced specialization pipeline (C) with embedded parallel fan-outs (B)**. Role overlap has been collapsed into 10 role definitions; safety is preserved through explicit dispatch modes and strict path contracts. See [ROLE_REDUCTION.md](ROLE_REDUCTION.md) for the old-to-new mapping and merge rationale.

## Protocol Summary

0. **Pre-flight** — verify optional dependencies from [dependencies.yaml](dependencies.yaml).
1. **Trigger + output root** — lock `output_root = <output_dir or ~/.a2c_agents/migration>/android-to-kmp-migrator`; write `run_manifest.json`.
2. **Migration module inventory** — write `module-index/migration_module_inventory.json` and `.md`; write each module's `module_brief.json`.
3. **Workspace state** — initialize and refresh `migration-workspace-state` under `<output_root>/global/node-results/migration-workspace-state/` and module-scoped workspace-state dirs. It records per-module migration progress, finish rate, plan-vs-code gaps, stale outputs, rerun hooks, and next safe actions.
4. **Per-module planning** — run `migration-analysis-planning`.
5. **Per-module dependency/platform gate** — run `dependency-platform-gate`.
6. **Per-module prep fan-out** — run `presentation-integration` and `state-data-prep` when inputs allow.
7. **Review/fix loop** — run `module-node-review-fix` in `review` mode; if needed, run `fix` mode; then run a fresh `review`.
8. **UI then logic** — run `ui-implementation`, review/fix, then `logic-implementation`, review/fix.
9. **Verification** — run `migration-verification` with required `check_ids`: `source_set`, `api_contract`, `ui_render`, `incremental_build`.
10. **Completion/report** — run `completion-report` in `readiness` mode, write module/global representations, then run `completion-report` in `report` mode and hand off to `kmp-test-validator`.

## Roles

Each node is dispatched as a subagent that must read its role file (`skill_spec_path`), paste its `## Inline Persona for Teammate` into the dispatch prompt, and execute only that bounded slice.

| id | Purpose | When dispatched | Role file |
|---|---|---|---|
| `migration-workspace-state` | Migration progress ledger, finish rates, plan-vs-code gaps, stale outputs, and rerun hooks | Global and module refreshes after every major stage | [roles/migration-workspace-state.md](roles/migration-workspace-state.md) |
| `migration-analysis-planning` | SPEC deltas, target understanding, alignment | Per-module first stage | [roles/migration-analysis-planning.md](roles/migration-analysis-planning.md) |
| `dependency-platform-gate` | Dependency readiness and platform replacement | Before prep/implementation | [roles/dependency-platform-gate.md](roles/dependency-platform-gate.md) |
| `presentation-integration` | Theme, resources, navigation | Prep fan-out before UI | [roles/presentation-integration.md](roles/presentation-integration.md) |
| `state-data-prep` | State/model/API contract prep | Prep fan-out before logic | [roles/state-data-prep.md](roles/state-data-prep.md) |
| `ui-implementation` | UI-first migrated surface | After prep approval | [roles/ui-implementation.md](roles/ui-implementation.md) |
| `logic-implementation` | Data/API/business logic | After UI approval | [roles/logic-implementation.md](roles/logic-implementation.md) |
| `module-node-review-fix` | Read-only review or scoped fix by mode | After file-changing slices | [roles/module-node-review-fix.md](roles/module-node-review-fix.md) |
| `migration-verification` | Source-set/API/UI/build checks | After implementation approval | [roles/migration-verification.md](roles/migration-verification.md) |
| `completion-report` | Readiness and final report by mode | Module/global completion | [roles/completion-report.md](roles/completion-report.md) |

## Files

| File | What it contains |
|---|---|
| [ROLE_REDUCTION.md](ROLE_REDUCTION.md) | Reduced role analysis, old-to-new map, dispatch order, mode boundaries |
| [workflow.md](workflow.md) | Mermaid topology, staged protocol, gates, final report format |
| [bind.md](bind.md) | Resource limits, behavioral constraints, failure handling, path contract |
| [roles/](roles/) | Active reduced role specs |
| [dependencies.yaml](dependencies.yaml) | Optional CLI tools checked at startup |

## Strict Output Schedule

```text
output_root = <output_dir or ~/.a2c_agents/migration>/android-to-kmp-migrator
module_index_dir = <output_root>/module-index
module_root = <output_root>/modules/<migration_module_id>
node_result_dir = <module_root>/node-results/<node_id>
module_representation_dir = <module_root>/representation
global_dir = <output_root>/global
report_dir = <output_root>/report
```

Required artifacts:

- `<output_root>/run_manifest.json`
- `<module_index_dir>/migration_module_inventory.json`
- `<module_index_dir>/migration_module_inventory.md`
- `<global_dir>/node-results/migration-workspace-state/migration_workspace_state.json`
- `<global_dir>/node-results/migration-workspace-state/migration_workspace_state.md`
- `<module_root>/module_brief.json`
- `<module_root>/node-results/migration-workspace-state/migration_workspace_state.json`
- `<module_root>/node-results/migration-workspace-state/migration_workspace_state.md`
- `<node_result_dir>/<node-specific>.json`
- `<node_result_dir>/<node-specific>.md`
- `<module_representation_dir>/module_migration_representation.json`
- `<module_representation_dir>/module_migration_representation.md`
- `<global_dir>/global_migration_representation.json`
- `<global_dir>/global_migration_representation.md`
- `<report_dir>/migration_report.json`
- `<report_dir>/migration_report.md`

## Output Artifact Content Matrix

The controller verifies both artifact names and role-aligned content before a downstream stage consumes any file.

| Stage / owner | Output file(s) | Required content |
|---|---|---|
| Output root lock / Leader | `run_manifest.json` | Migration trigger, Android/SPEC inputs, KMP target path, migration scope, output root, allowed roots, dependency-preflight status, schedule version, timestamp. |
| Module inventory / Leader | `migration_module_inventory.json`, `migration_module_inventory.md` | Deterministic migration module list/order, `migration_module_id`, module scope, UI/logic/data/resource scope, target placement hints, allowed target files/source sets, module output roots, blockers. |
| Module brief / Leader | `module_brief.json` | One module's dispatch contract: module id/scope, source/SPEC evidence paths, target hints, allowed files/source sets, expected node schedule, representation path, assumptions. |
| Workspace progress / `migration-workspace-state` | `migration_workspace_state.json`, `migration_workspace_state.md` | Per-module migration status, finish rates, stage status, node status, changed-file ownership, plan-vs-code gaps, stale outputs, rerun hooks, blocker/rerun history, next safe actions. |
| Planning / `migration-analysis-planning` | `migration_analysis_planning.json`, `migration_analysis_planning.md` | SPEC/raw-source deltas, target KMP understanding, reuse inventory, source-to-target map, resource project map, integration scaffold, ordered implementation tasks, blockers. |
| Dependency/platform / `dependency-platform-gate` | `dependency_platform_gate.json`, `dependency_platform_gate.md` | Required capability map, minimal-change dependency decisions, build-config changes, platform capability boundaries, expect/actual/source-set plan, changed files, implementation constraints, blockers. |
| Presentation prep / `presentation-integration` | `presentation_integration.json`, `presentation_integration.md` | Theme/design-token mapping, target component/resource reuse, local/online media modeling, route/navigation mapping, UI handoff, changed files, presentation gaps, blockers. |
| State/data prep / `state-data-prep` | `state_data_prep.json`, `state_data_prep.md` | State holder mapping, UI state/events/effects, DTO/domain/UI model mapping, mappers, API/data contract expectations, logic handoff, changed files, blockers. |
| UI implementation / `ui-implementation` | `ui_implementation.json`, `ui_implementation.md` | Migrated visible UI surface, changed UI/resource files, UI coverage, fidelity notes, binding surfaces, diagnostics, blockers. |
| Logic implementation / `logic-implementation` | `logic_implementation.json`, `logic_implementation.md` | Implemented behavior/data/API/state propagation, architecture alignment, platform boundaries, data flows, API integrations, logic coverage, changed files, diagnostics, blockers. |
| Review mode / `module-node-review-fix` | `module_node_review.json`, `module_node_review.md` | Read-only review of one owning node slice: reviewed files, contract/scope/parity/source-set/dependency findings, approval or `needs_fix`, blockers. |
| Fix mode / `module-node-review-fix` | `module_node_fix.json`, `module_node_fix.md` | Scoped fix report for explicit findings: fixed/unfixed findings, changed files, `requires_re_review: true`, blockers. |
| Verification / `migration-verification` | `migration_verification.json`, `migration_verification.md`, optional log files | `source_set`, `api_contract`, `ui_render`, and `incremental_build` check results, evidence, failures, routed owner nodes, command/log paths, blockers. |
| Readiness / `completion-report` | `completion_readiness.json`, `completion_readiness.md` | Requirement coverage, migration invariants, review/verification completion, rerun requests, blockers, readiness for representation/report gates. |
| Module representation / Leader | `module_migration_representation.json`, `module_migration_representation.md` | Module synthesis from verified node outputs only: source-to-target mapping, changed files by role, UI/state/data/logic/platform coverage, verification evidence, gaps, readiness. |
| Global representation / Leader | `global_migration_representation.json`, `global_migration_representation.md` | Cross-module migration synthesis from module representations only: global target changes, shared files/ownership, coverage, unresolved blockers, validation handoff prerequisites. |
| Final report / `completion-report` | `migration_report.json`, `migration_report.md` | Validation-ready migration handoff: source/target paths, scope, module/global representation paths, changed files by role, source-to-target summary, coverage summary, validation inputs, limitations, manual steps, blockers. |

JSON artifacts are the machine-routable source of truth. Markdown artifacts are agent-readable handoffs that preserve exact paths, evidence, commands/logs where applicable, changed-file ownership, rerun context, blockers, and next-node routing. Node Markdown must not be a prose-only completion summary.

## Shared Return Shape

```json
{
  "status": "completed | passed | ready_for_implementation | ready_for_validation | needs_rerun | failed | blocked",
  "node": "<node-name>",
  "mode": "<mode when role has modes>",
  "migration_module_id": "<module id or global>",
  "module_scope": "<module/screen/feature/resource/API scope or global>",
  "output_dir": "<exact node_result_dir>",
  "output_files": ["<paths>"],
  "changed_files": ["<paths or empty>"],
  "stale_upstream_inputs": ["<paths or empty>"],
  "rerun_requests": [{ "node": "<responsible-node>", "reason": "", "required_inputs": [], "expected_output": "" }],
  "blocking_gaps": ["<gaps or empty>"]
}
```

Controller handling: missing/empty `output_files` -> rerun the same node; non-empty `stale_upstream_inputs` -> refresh upstream artifacts then rerun; non-empty `rerun_requests` or `migration-workspace-state.rerun_hooks` -> dispatch the responsible node first; unresolved `blocking_gaps` -> stop with a user-visible blocker. Downstream stages may consume a module only when the latest workspace-state progress record does not mark its required stage stale, blocked, failed, or missing review/verification.

## Shared Rules

- Each node must read its own role file before work and stay inside its responsibility boundary.
- Consolidated roles must respect `mode`; do not combine review and fix in one invocation.
- `migration-workspace-state` must be refreshed after inventory, planning, dependency/platform, prep fan-out, every review/fix loop, UI implementation, logic implementation, verification, readiness, module representation, global representation, and report. Its `module_progress`, `plan_code_gaps`, and `rerun_hooks` are routing inputs, not optional summaries.
- Every important claim must include evidence from source paths, SPEC sections, upstream node outputs, or module/global representations.
- The controller must not substitute itself for node implementation.
- Target conventions and reusable modules/components take priority over new abstractions.
- Target build config is read-only except through `dependency-platform-gate`.
- Migrated code stays inside one KMP target project; raw Legacy Android source wins when SPEC conflicts.
