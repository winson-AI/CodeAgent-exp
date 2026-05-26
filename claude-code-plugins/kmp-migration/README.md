# KMP Migration Plugin

Specialized agents for migrating Android projects to Kotlin Multiplatform (KMP).

Version: `0.1.15`

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

After installation, the agents are available in your Claude Code environment. You can trigger them by name or by describing the task.

Default artifact roots:

- Understand/explore artifacts: `~/.d2c_agents/understand/`
- Migration artifacts: `~/.d2c_agents/migration/`
- Validation artifacts: `~/.d2c_agents/validation/`

SPEC documents are written under `<output_dir>/SPEC`.

### Explore Mode Prompt Template

Use `android-project-analyst` when you want structured understanding of an existing Android project before migration or refactoring.

```text
Use the android-project-analyst agent in exploration mode.

source_project_path: <absolute path to Android project>
analysis_scope: <whole project | module | feature | screen>
mode: exploration
output_dir: <optional artifact root; default ~/.d2c_agents/understand/>
language: English

Goal:
- Understand the Android project structure, UI, architecture, APIs, resources, data flow, and logic/control flow.
- Generate SPEC artifacts under <output_dir>/SPEC: prd.md, design.md, verification.md.
```

Example:

```text
Use android-project-analyst in exploration mode.

source_project_path: /Users/me/projects/legacy-android
analysis_scope: checkout feature
mode: exploration
output_dir: ~/.d2c_agents/understand/checkout
language: English

Please analyze the checkout feature and produce evidence-backed SPEC docs.
```

Natural-language example:

```text
Analyze this Android project with android-project-analyst in exploration mode:
/Users/me/projects/legacy-android

Focus on the checkout feature and write SPEC docs under ~/.d2c_agents/understand/checkout/SPEC.
```

### Legacy Android Understand Command

Use `/legacy-android-understand` as a slash-command entry point for `android-project-analyst` exploration mode. It accepts a whole project, module/feature/screen scope, a question to answer after analysis, or target code paths to trace.

```text
/legacy-android-understand

source_project_path: <absolute path to Legacy Android project>
analysis_scope: <whole project | module | feature | screen | target code>
question: <optional question to answer after analysis>
module: <optional Gradle module, package, or module name>
feature: <optional feature or user flow>
screen: <optional Activity, Fragment, or Compose screen>
target_code:
- <optional file/class/package path to analyze>
output_dir: <optional artifact root; default ~/.d2c_agents/understand/>
language: English
```

The command forces `mode: exploration`, dispatches `android-project-analyst`, writes `prd.md`, `design.md`, and `verification.md` under `<output_dir>/SPEC`, then returns the answer or scoped code understanding backed by generated evidence.

### Migration Mode Prompt Template

Use `android-to-kmp-migrator` when you want to migrate Android behavior into a KMP or Compose Multiplatform target. If Legacy Android SPEC artifacts are missing or incomplete, the migrator will invoke `android-project-analyst` in migration mode first.

```text
Use the android-to-kmp-migrator agent.

legacy_android_project_path: <absolute path to Android project>
kmp_target_project_path: <absolute path to KMP target project>
migration_scope: <whole project | module | feature | screen | task>
spec_dir: <optional path to existing SPEC directory>
output_dir: <optional artifact root; default ~/.d2c_agents/migration/>
validation_requirements: <optional build targets, use cases, preview expectations, acceptance criteria>
language: English

Goal:
- Migrate the requested Android behavior into the KMP target project.
- Preserve UI, resources, navigation, data flow, API contracts, state, and business logic.
- Produce a migration report under <output_dir> and invoke KMP validation when ready.
```

Example:

```text
Use android-to-kmp-migrator.

legacy_android_project_path: /Users/me/projects/legacy-android
kmp_target_project_path: /Users/me/projects/app-kmp
migration_scope: checkout feature
spec_dir: ~/.d2c_agents/understand/checkout/SPEC
output_dir: ~/.d2c_agents/migration/checkout
validation_requirements:
- Run the smallest available KMP build/check task.
- Verify checkout happy path, empty cart, payment error, and retry behavior.
- Check Compose renderability for migrated checkout screens.
language: English
```

Natural-language example:

```text
Migrate the checkout feature from /Users/me/projects/legacy-android into
/Users/me/projects/app-kmp using android-to-kmp-migrator.

Use existing SPEC from ~/.d2c_agents/understand/checkout/SPEC, write migration
artifacts to ~/.d2c_agents/migration/checkout, and validate build,
renderability, and checkout use cases after migration.
```

### Validation Prompt Template

Use `kmp-test-validator` when a migrated KMP target is ready to validate against Android source, SPEC, or a migration report.

```text
Use the kmp-test-validator agent.

kmp_target_project_path: <absolute path to migrated KMP project>
legacy_android_project_path: <absolute path to Android project>
migration_scope: <whole project | module | feature | screen | task>
spec_dir: <path to SPEC directory>
migration_report_path: <path to migration_report.md or migration_report.json>
output_dir: <optional artifact root; default ~/.d2c_agents/validation/>
validation_requirements: <build targets, use cases, preview expectations, acceptance criteria>
language: English
```

### Fix Issue Command

Use `/fix-issue-kmp` when a KMP/CMP target has a known compile failure or a migrated use-case failure that needs a focused fix plus rerun evidence.

```text
/fix-issue-kmp

kmp_target_project_path: <absolute path to KMP target project>
issue_type: <compile | use_case>
issue_summary: <known compiler, build, test, preview, or use-case failure>
failing_command: <optional exact command that currently fails>
failure_log_path: <optional path to full failure log>
legacy_android_project_path: <optional path when use-case behavior needs Android evidence>
spec_dir: <optional path to SPEC directory>
migration_report_path: <optional path to migration report>
allowed_files:
- <optional file path this fix may edit>
user_provided_commands:
  build: <optional build command>
  test: <optional use-case or regression command>
  renderability: <optional Compose preview/renderability command>
output_dir: optional artifact root; default ~/.d2c_agents/fix-issue-kmp/TIMESTAMP/
language: English
```

The command writes `fix_issue_kmp_report.md` and `fix_issue_kmp_report.json`, captures command logs, classifies failures, applies only targeted target-code fixes, and reruns the smallest failing command before broader build/check or use-case gates.

## Hooks and Guardrails

### `.env` Edit Protection

The plugin ships a `PreToolUse` command hook that blocks write/edit tools from modifying `.env` and `.env.*` files.

- Hook config: `hooks/hooks.json`
- Hook script: `scripts/pre-edit-protect.sh`
- Matched tools: `Write`, `Edit`, `MultiEdit`, and `NotebookEdit`
- Behavior: returns exit code `2` when the target path is a protected `.env` file.

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
- `commands/`: Slash commands, including `/legacy-android-understand` for Android exploration and `/fix-issue-kmp` for targeted KMP compile or migrated use-case fixes.
- `skills/`: Claude Code skills and controller node skill specs.
- `hooks/`: Tool-layer enforcement, including a `PreToolUse` guard that blocks edits to `.env` files.
- `scripts/`: Hook and utility scripts, including `pre-edit-protect.sh`.
- `monitors/`: Plugin monitor configuration.
- `templates/`: Reserved for future migration templates.
- `.mcp.json`: Plugin MCP configuration.
- `.lsp.json`: Plugin LSP configuration.
- `settings.json`: Plugin settings.
