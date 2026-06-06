---
name: android-to-kmp-migrator
description: |
  20-role pipeline Swarm Skill (C+B) that migrates Legacy Android into an existing KMP target project: analysis, dependency gate, parallel prep, UI-then-logic implementation, review→fix loops, verification, and a migration report.
  Use with the android-to-kmp-migrator controller to port Android UI, resources, navigation, state, and logic into one KMP project, then hand to kmp-test-validator.
  Do NOT use for Legacy Android analysis, KMP-only feature work, quick lookups, or non-migration refactors.
version: "0.2"
kind: swarm-skill
disable-model-invocation: false
roles:
  - id: migration-workspace-state
    kind: ai_agent
    purpose: State ledger — node status, changed-file ownership, stale outputs, rerun/blocker history, next actions. No code analysis or edits.
    skills: []
    tools: [git]
  - id: legacy-spec-delta-review
    kind: ai_agent
    purpose: Cross-check Legacy SPEC vs raw source for missing coverage and contradictions; classify and route deltas. Raw source wins.
    skills: []
    tools: [rg]
  - id: target-project-understand
    kind: ai_agent
    purpose: First migration node — verify KMP target, capture baseline env, detect relevant sub-module, build reuse inventory and constraints.
    skills: []
    tools: [rg]
  - id: migration-alignment
    kind: ai_agent
    purpose: Build source-to-target map, integration scaffold, and ordered implementation tasks; record SPEC/Design/Plan deltas. No implementation.
    skills: []
    tools: [rg]
  - id: dependency-resolution
    kind: ai_agent
    purpose: Minimal-change build gate — map capabilities to baseline/reuse, justify any build-config change. Returns dependency readiness.
    skills: []
    tools: [rg]
  - id: theme-design-system-mapping
    kind: ai_agent
    purpose: Map Legacy visual tokens to target design-system tokens/components, reuse-first; produce UI guidance and visual gaps.
    skills: []
    tools: [rg]
  - id: resource-migration
    kind: ai_agent
    purpose: Migrate or model local & online resources into target KMP conventions, preserving semantics; record resource gaps.
    skills: []
    tools: [rg, curl]
  - id: navigation-migration
    kind: ai_agent
    purpose: Migrate routes, parameters, back behavior, deep links, and result passing into target navigation; record route gaps.
    skills: []
    tools: [rg]
  - id: platform-api-replacement
    kind: ai_agent
    purpose: Replace Android-only APIs with target-safe abstractions or expect/actual; keep Android-only code out of commonMain.
    skills: []
    tools: [rg]
  - id: state-model-mapping
    kind: ai_agent
    purpose: Map state holders and DTO/domain/UI models to target structures, preserving state semantics; hand off to the logic node.
    skills: []
    tools: [rg]
  - id: ui-mockup-implementation
    kind: ai_agent
    purpose: Implement migrated UI layout/components/states/resources first in the target project; expose binding surfaces. No business logic.
    skills: []
    tools: [rg]
  - id: dataflow-logic-implementation
    kind: ai_agent
    purpose: Implement architecture, data flow, API integration, navigation effects, lifecycle, and business logic bound to UI surfaces.
    skills: []
    tools: [rg]
  - id: module-node-migration-review
    kind: ai_agent
    purpose: Read-only review of one migration slice for contract/scope/parity/conventions/handoff; classify and route must-fix findings.
    skills: []
    tools: [rg, git]
  - id: module-node-migration-fix
    kind: ai_agent
    purpose: Apply assigned must-fix findings inside allowed files only; preserve conventions; require mandatory re-review.
    skills: []
    tools: [rg, git]
  - id: source-set-placement-guard
    kind: ai_agent
    purpose: Verify KMP source-set placement; catch Android-only APIs in shared code and missing/duplicate actuals; route violations.
    skills: []
    tools: [rg, git]
  - id: api-contract-parity
    kind: ai_agent
    purpose: Diff migrated KMP API contracts vs Legacy API/data evidence; classify and route mismatches. No fixes.
    skills: []
    tools: [rg]
  - id: ui-render-fidelity-check
    kind: ai_agent
    purpose: Verify migrated screens render and cover visual states/resources/theme; route UI failures. Static coverage when no render command.
    skills: []
    tools: [rg]
  - id: incremental-build-check
    kind: ai_agent
    purpose: Run the smallest trustworthy target build/check; parse failures and route to responsible nodes. Early gate, not final validation.
    skills: []
    tools: [git]
  - id: prd-completion-check
    kind: ai_agent
    purpose: Judge readiness vs PRD/raw task/SPEC/node outputs and invariants; emit node-routed rerun requests or ready_for_validation.
    skills: []
    tools: [rg, git]
  - id: migration-report
    kind: ai_agent
    purpose: Synthesize final migration report and validation inputs for kmp-test-validator; ready_for_validation only when completion is ready.
    skills: []
    tools: [git]
---

# Android To KMP Migrator Swarm Skill

This is the agent-facing registry and team definition for the `android-to-kmp-migrator` controller (the same-name subagent in `kmp-migration/agents/`). It converts a Legacy Android SPEC plus an existing KMP target project into migrated, validation-ready KMP code.

The team is a **specialization pipeline (C) with embedded parallel fan-outs (B) and review→fix loops**: a serial analysis chain feeds a dependency gate, then a parallel prep stage, then UI-before-logic implementation, then parallel verification, completion check, and report. A single agent attempting the whole migration blurs the hard stage boundaries — it implements logic before the UI surface exists, skips the dependency minimal-change gate, lets Android-only APIs leak into `commonMain`, and self-approves its own work. Isolating each concern into an owned node with hard handoff gates and a mandatory review→fix→re-review loop keeps every change scoped, traceable, and reviewed before downstream nodes consume it. The controller (Leader) owns routing, contract enforcement, rerun handling, and the `kmp-test-validator` handoff; nodes own bounded target-understanding and implementation work.

## Workflow

The full playbook (Mermaid topology, per-step gates, review→fix loop, failure routing, Final Report format) is in [workflow.md](workflow.md). Protocol summary:

0. **Pre-flight: check dependencies** — read [dependencies.yaml](dependencies.yaml) and verify `rg` / `git` / `curl` (all `required: false`; the target Gradle wrapper drives builds). Report status; **user decides** whether to proceed.
1. **Trigger + shared brief + workspace state** — Leader confirms the migration trigger and Legacy SPEC context, builds the shared brief, and initializes `migration-workspace-state`. Default `output_dir` = `~/.a2c_agents/migration/`.
2. **Analysis chain (serial)** — `legacy-spec-delta-review` → `target-project-understand` (must confirm KMP, else `blocked`) → `migration-alignment`.
3. **Dependency gate** — `dependency-resolution` must return `ready_for_implementation` before any implementation node runs (minimal-change gate; see [bind.md](bind.md)).
4. **Stage Prep (parallel)** — `theme-design-system-mapping`, `resource-migration`, `navigation-migration`, `platform-api-replacement`, `state-model-mapping`.
5. **Review→fix loop** — after any file-changing node: `module-node-migration-review` → `module-node-migration-fix` (if `needs_fix`) → mandatory re-review, until `approved`.
6. **UI implementation** — `ui-mockup-implementation` (before logic), then the review→fix loop.
7. **Dataflow/logic implementation** — `dataflow-logic-implementation`, then the review→fix loop.
8. **Stage Verify (parallel)** — `source-set-placement-guard`, `api-contract-parity`, `ui-render-fidelity-check`, `incremental-build-check`; failures route back to the responsible node.
9. **Completion check** — `prd-completion-check` → `ready_for_validation`, `needs_rerun` (route to nodes), or `blocked`.
10. **Final: migration report** — `migration-report` returns `ready_for_validation` only when completion is ready; the Leader then invokes `kmp-test-validator`. Leader routes failures verbatim, never mediates.

## Roles

Each node is dispatched as a subagent that must read its role file (`skill_spec_path`), paste its `## Inline Persona for Teammate` into the dispatch prompt, and execute only that role's bounded slice. The dispatch order enforces upstream→downstream data availability and the review→fix gates.

| id | Purpose | When dispatched | Key dependencies | Role file |
|---|---|---|---|---|
| migration-workspace-state | State ledger / stale-output tracking | Step 1 + refreshed after major completions | git | [roles/migration-workspace-state.md](roles/migration-workspace-state.md) |
| legacy-spec-delta-review | SPEC-vs-source delta review | Step 2 (serial) | rg | [roles/legacy-spec-delta-review.md](roles/legacy-spec-delta-review.md) |
| target-project-understand | Target KMP understanding + reuse inventory | Step 2 (serial) | rg | [roles/target-project-understand.md](roles/target-project-understand.md) |
| migration-alignment | Source-to-target map + ordered tasks | Step 2 (serial) | rg | [roles/migration-alignment.md](roles/migration-alignment.md) |
| dependency-resolution | Minimal-change dependency gate | Step 3 (gate) | rg | [roles/dependency-resolution.md](roles/dependency-resolution.md) |
| theme-design-system-mapping | Visual token mapping | Step 4 (parallel prep) | rg | [roles/theme-design-system-mapping.md](roles/theme-design-system-mapping.md) |
| resource-migration | Local & online resource migration | Step 4 (parallel prep) | rg, curl | [roles/resource-migration.md](roles/resource-migration.md) |
| navigation-migration | Route/param/back/deep-link migration | Step 4 (parallel prep) | rg | [roles/navigation-migration.md](roles/navigation-migration.md) |
| platform-api-replacement | Android-only API → expect/actual | Step 4 (parallel prep) | rg | [roles/platform-api-replacement.md](roles/platform-api-replacement.md) |
| state-model-mapping | State holder & model mapping | Step 4 (parallel prep) | rg | [roles/state-model-mapping.md](roles/state-model-mapping.md) |
| ui-mockup-implementation | UI surface implementation (first) | Step 6 (after prep approved) | rg | [roles/ui-mockup-implementation.md](roles/ui-mockup-implementation.md) |
| dataflow-logic-implementation | Data/API/logic implementation | Step 7 (after UI approved) | rg | [roles/dataflow-logic-implementation.md](roles/dataflow-logic-implementation.md) |
| module-node-migration-review | Read-only per-slice review | Step 5 loop (after any file change) | rg, git | [roles/module-node-migration-review.md](roles/module-node-migration-review.md) |
| module-node-migration-fix | Scoped must-fix application | Step 5 loop (on needs_fix) | rg, git | [roles/module-node-migration-fix.md](roles/module-node-migration-fix.md) |
| source-set-placement-guard | KMP source-set boundary guard | Step 8 (parallel verify) | rg, git | [roles/source-set-placement-guard.md](roles/source-set-placement-guard.md) |
| api-contract-parity | Migrated vs Legacy API parity | Step 8 (parallel verify) | rg | [roles/api-contract-parity.md](roles/api-contract-parity.md) |
| ui-render-fidelity-check | Render + visual-state coverage | Step 8 (parallel verify) | rg | [roles/ui-render-fidelity-check.md](roles/ui-render-fidelity-check.md) |
| incremental-build-check | Smallest target build/check gate | Step 8 (parallel verify) | git | [roles/incremental-build-check.md](roles/incremental-build-check.md) |
| prd-completion-check | Readiness verdict + rerun routing | Step 9 | rg, git | [roles/prd-completion-check.md](roles/prd-completion-check.md) |
| migration-report | Final report + validation inputs | Step 10 | git | [roles/migration-report.md](roles/migration-report.md) |

> Before dispatching each teammate, read its role file and paste its `## Inline Persona for Teammate`
> section directly into the dispatch prompt — adopting agents do NOT auto-load role files. Fill the
> `{PLACEHOLDER}` inputs from the contract.

## Files

| File | What it contains | When to read |
|---|---|---|
| [workflow.md](workflow.md) | Mermaid C+B topology, staged protocol with gates, review→fix loop, failure routing, Final Report format | Before first dispatch — the complete playbook |
| [bind.md](bind.md) | Resource limits, team behavioral constraints, dependency-gate/single-project invariants, failure & degraded modes | When hitting limits, handling failures, or scoping a large migration |
| [roles/\*.md](roles/) | Per-node identity, success criteria, boundary, output schema, Inline Persona for Teammate | Before dispatching each teammate — extract Inline Persona |
| [dependencies.yaml](dependencies.yaml) | External CLI tools (`rg`, `git`, `curl`) checked at startup | Step 0 — verify deps, report missing items, user decides go/no-go |

## Shared Return Shape

Every node return payload includes, in addition to node-specific fields:

```json
{
  "status": "completed | passed | ready_for_implementation | ready_for_validation | needs_rerun | failed | blocked",
  "node": "<node-name>",
  "output_files": ["<paths>"],
  "changed_files": ["<paths or empty>"],
  "stale_upstream_inputs": ["<paths or empty>"],
  "rerun_requests": [ { "node": "<responsible-node>", "reason": "", "required_inputs": [], "expected_output": "" } ],
  "blocking_gaps": ["<gaps or empty>"]
}
```

Controller handling: missing/empty `output_files` → rerun the same node; non-empty `stale_upstream_inputs` → refresh those upstream artifacts then rerun; non-empty `rerun_requests` → dispatch the responsible node first; `blocking_gaps` with no resolving rerun → stop with a user-visible blocker.

## Optional Android Studio MCP Context

When the `jetbrains` MCP server is available, the controller may pass indexed IDE context to nodes: project structure/dependencies (`get_project_modules`, `get_project_dependencies`, `get_repositories`), code intelligence (`find_files_by_glob`, `search_in_files_by_regex`, `get_symbol_info`), diagnostics after code changes (`get_file_problems`), IDE build diagnostics (`build_project`), run configs (`get_run_configurations`, `execute_run_configuration`), and IDE-safe edits (`rename_refactoring`, `reformat_file`). Always pass `projectPath: <kmp_target_project_path>`. MCP is advisory — Gradle build/check gates, module review, completion check, and KMP validation remain required; record MCP gaps in the workspace ledger.

## Shared Rules

- Each node must read its own role file before work and stay inside its responsibility boundary.
- Every important claim must include evidence from source paths, SPEC sections, or upstream node outputs; unknowns are marked explicitly, never guessed.
- The controller must not substitute itself for node implementation; no migration leaves TODO placeholders as completion output.
- Target conventions and reusable modules/components take priority over new abstractions; target build config is read-only except via `dependency-resolution`.
- Migrated code stays inside one KMP target project; SPEC guides migration, but raw Legacy Android source wins when evidence conflicts.
