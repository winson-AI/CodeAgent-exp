# KMP Migration Plugin

Specialized agents for migrating Android projects to Kotlin Multiplatform (KMP).

Version: `0.1.8`

## Agents

### `android-project-analyst`
Controller-only Android project analysis agent. It verifies the request, dispatches node subagents for UI, architecture, ecosystem, API, resource, data-flow, and logic understanding, then integrates verified outputs into SPEC documentation (`PRD`, `DESIGN`, `PLAN` when migration mode applies, plus `verification.md`).

### `android-to-kmp-migrator`
Controller-only Android-to-KMP migration agent. It verifies that the request is a migration scenario, requires Legacy Android SPEC context, dispatches workspace-state, SPEC-delta, target-understanding, resource/theme/navigation/platform/state, UI, dataflow/logic, module/node review-fix, guard/parity/fidelity/build-check, completion-check, and migration-report node subagents, and invokes KMP validation after the migration report is ready.

### `kmp-test-validator`
Controller-only post-migration validation agent. It verifies migration context, dispatches validation input, Android/KMP fidelity audit, validation planning, build/preview, test decomposition/execution, remediation, workspace-state, and reporting node subagents, then returns the final validation status.

### `memory-curator`
Audits and optimizes agent memory stores. Recommends which memories to retain, archive, or delete, and records resumable agent state for recovery.

### `skill-maintenance-advisor`
Reviews conversation context at regular turn intervals and recommends creating or updating reusable skills when useful patterns appear.

## Usage

After installation, the agents will be available in your Claude Code environment. You can trigger them by name or by describing the task (e.g., "Analyze this Android project for KMP migration").

## Skills

### `skills/android-project-analyst`
Node skill specs used by the `android-project-analyst` controller:

- `ui-understand.md`: screen inventory, UI technology mapping, navigation, and UI module boundaries.
- `architecture-pattern.md`: MVC/MVP/MVVM/MVI/Clean Architecture detection, module layering, and legacy hybrid risks.
- `android-ecosystem.md`: Gradle, SDK, Jetpack, DI, persistence, background work, resources, and dependency constraints.
- `api-list.md`: network API and data-source catalog with consumers, models, and unknowns.
- `resource-understand.md`: local and online image/icon/media resources, usage mapping, downloaded analysis copies, placeholders, and migration implications.
- `data-flow.md`: data sources, repositories, reactive streams, transformations, caches, and UI state propagation.
- `logic-understand.md`: business logic, control flow, state management, lifecycle behavior, user actions, and side effects.

### `skills/android-to-kmp-migrator`
Node skill specs used by the `android-to-kmp-migrator` controller:

- `target-project-understand.md`: relevant target sub-module detection plus current UI design, architecture, logic flow, API list, and reuse context.
- `legacy-spec-delta-review.md`: SPEC/raw-source coverage check with contradiction and blocker routing.
- `migration-alignment.md`: Legacy Android SPEC/raw understanding alignment with target project context and resource mapping.
- `dependency-resolution.md`: minimal-change dependency gate, baseline capability mapping, and justified build-config exceptions.
- `theme-design-system-mapping.md`: visual token and design-system mapping before UI implementation.
- `resource-migration.md`: local and online resource migration into KMP target conventions.
- `navigation-migration.md`: route, parameter, back behavior, deep link, and navigation scaffolding migration.
- `platform-api-replacement.md`: Android-only API replacement through target-safe abstractions or expect/actual.
- `state-model-mapping.md`: state holder and model mapping before dataflow/logic implementation.
- `ui-mockup-implementation.md`: UI layout, component, theme/resource, and binding surface implementation.
- `dataflow-logic-implementation.md`: architecture, data flow, API integration, navigation effects, lifecycle behavior, and business logic implementation.
- `module-node-migration-review.md`: per-module or per-node review for contract compliance, source parity, target conventions, scope, and handoff readiness.
- `module-node-migration-fix.md`: focused fixes from module/node review findings, followed by mandatory re-review.
- `migration-workspace-state.md`: node status, changed-file ownership, stale output, rerun history, and blocker ledger.
- `source-set-placement-guard.md`: KMP source-set placement and Android-only API boundary checks.
- `api-contract-parity.md`: migrated API contract comparison against Legacy Android API/data evidence.
- `ui-render-fidelity-check.md`: render path, visual-state, resource, and theme usage checks before final validation.
- `incremental-build-check.md`: smallest known target build/check gate with failure routing.
- `prd-completion-check.md`: PRD/raw task completion verification and re-dispatch gap reporting.
- `migration-report.md`: final migration report with mappings, changed files, coverage, limitations, manual steps, and validation inputs.

### `skills/kmp-test-validator`
Node skill specs used by the `kmp-test-validator` controller:

- `validation-workspace-state.md`: validation node status, changed-file ownership, stale input, rerun history, and blocker ledger.
- `validation-input-contract.md`: migration-validation trigger verification and normalized validation brief.
- `android-kmp-fidelity-audit.md`: Android/KMP comparison across UI, logic, data flow, and control flow.
- `kmp-validation-plan.md`: target KMP structure, source sets, test frameworks, and trusted command discovery.
- `build-preview-gate.md`: compile/build and Compose preview or renderability validation before behavioral tests.
- `test-case-decomposition.md`: atomic test/use-case inventory from user input, SPEC, and migration report validation inputs.
- `test-execution.md`: project-convention test execution and evidence capture.
- `validation-remediation.md`: focused KMP fixes for confirmed validation failures, followed by required reruns.
- `validation-report.md`: final fidelity, build, preview, test, remediation, blocker, and status report.

## Structure

- `agents/`: Subagent definitions.
- `commands/`: Reserved for future custom slash commands.
- `skills/`: Claude Code skills and controller node skill specs.
- `hooks/`: Reserved for future tool-layer enforcement.
- `templates/`: Reserved for future migration templates.
