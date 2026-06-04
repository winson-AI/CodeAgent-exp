---
name: kmp-test-validator
description: |
  6-role reduced pipeline Swarm Skill that validates Android-to-KMP migration output: workspace ledger, intake/fidelity trust gate, command/build-preview gate, Android-anchored test runner, scoped remediation, and final validation report.
  Use with the kmp-test-validator controller after android-to-kmp-migrator has produced a validation-ready migration report, or when given Android source/SPEC plus a KMP target for migrated behavior validation.
  Do NOT use for generic KMP testing, KMP-only feature work, isolated Gradle troubleshooting, Android analysis, or non-migration refactors.
version: "0.3"
kind: swarm-skill
disable-model-invocation: true
roles:
  - id: validation-workspace-state
    kind: ai_agent
    purpose: Validation ledger — node status, changed-file ownership, stale inputs, rerun/blocker history, next actions. No audit, build, test, fix, or verdict.
    skills: []
    tools: [git]
  - id: validation-intake-fidelity
    kind: ai_agent
    purpose: Intake and fidelity trust gate — verify migration scenario, normalize brief, compare Android source/SPEC vs KMP, and flag test-trust blockers.
    skills: []
    tools: [rg, git]
  - id: validation-plan-gate
    kind: ai_agent
    purpose: Command and build gate — resolve trusted build/preview/test commands, run build and preview/renderability before behavioral tests, route failures.
    skills: []
    tools: [rg, git]
  - id: validation-test-runner
    kind: ai_agent
    purpose: Test workflow — decompose validation requirements into atomic Android-anchored cases, execute them through project conventions, capture evidence.
    skills: []
    tools: [rg, git]
  - id: validation-remediation
    kind: ai_agent
    purpose: Scoped target fixes — fix confirmed target KMP failures inside allowed files and emit required reruns.
    skills: []
    tools: [rg, git]
  - id: validation-report
    kind: ai_agent
    purpose: Final verdict synthesis — passed/failed/blocked from verified fidelity, build, preview, test, and remediation evidence. No new tests or fixes.
    skills: []
    tools: [git]
---

# KMP Test Validator Swarm Skill

This is the agent-facing registry and team definition for the `kmp-test-validator` controller. It validates Android-to-KMP migration output against Android source and migration SPEC evidence.

The team is a **reduced serial pipeline with a remediation loop**. Role overlap has been collapsed from 9 role files to 6 role definitions. See [ROLE_REDUCTION.md](ROLE_REDUCTION.md) for the old-to-new map and merge rationale.

## Protocol Summary

0. **Pre-flight** — check optional dependencies from [dependencies.yaml](dependencies.yaml).
1. **Output root + workspace state** — lock validation output root parallel to migration, then initialize `validation-workspace-state`.
2. **Intake/fidelity trust gate** — run `validation-intake-fidelity`; block non-migration validation and test-trust blockers.
3. **Plan/build gate** — run `validation-plan-gate`; commands must be trusted, and build/preview must pass before behavioral tests.
4. **Test workflow** — run `validation-test-runner` when validation cases exist.
5. **Remediation loop** — run `validation-remediation` only for confirmed target KMP failures, then rerun affected gates/tests.
6. **Final report** — run `validation-report` to issue `passed | failed | blocked`.

## Roles

| id | Purpose | Role file |
|---|---|---|
| `validation-workspace-state` | Ledger and stale-input tracking | [roles/validation-workspace-state.md](roles/validation-workspace-state.md) |
| `validation-intake-fidelity` | Migration scenario gate and fidelity audit | [roles/validation-intake-fidelity.md](roles/validation-intake-fidelity.md) |
| `validation-plan-gate` | Command resolution plus build/preview gate | [roles/validation-plan-gate.md](roles/validation-plan-gate.md) |
| `validation-test-runner` | Test decomposition and execution | [roles/validation-test-runner.md](roles/validation-test-runner.md) |
| `validation-remediation` | Scoped target fixes and rerun requests | [roles/validation-remediation.md](roles/validation-remediation.md) |
| `validation-report` | Final verdict synthesis | [roles/validation-report.md](roles/validation-report.md) |

## Files

| File | What it contains |
|---|---|
| [ROLE_REDUCTION.md](ROLE_REDUCTION.md) | Reduced role analysis and old-to-new map |
| [workflow.md](workflow.md) | Reduced pipeline, gates, remediation loop, final report format |
| [bind.md](bind.md) | Guardrails, failure handling, resource constraints |
| [roles/](roles/) | Active reduced role specs |
| [dependencies.yaml](dependencies.yaml) | Optional CLI tools checked at startup |

## Strict Output Schedule

Validation artifacts must be written parallel to migration artifacts, under a `validation` base location. If the migration run uses a default base like `~/.a2c_agents/migration`, the validator uses the sibling base `~/.a2c_agents/validation`. If a `migration_output_root` is provided, derive the validation base by replacing the `migration` path segment with `validation` when possible; otherwise use `<output_dir or ~/.a2c_agents/validation>`.

```text
output_root = <output_dir or ~/.a2c_agents/validation>/kmp-test-validator
workspace_state_dir = <output_root>/workspace-state
intake_dir = <output_root>/intake-fidelity
plan_gate_dir = <output_root>/plan-gate
test_runner_dir = <output_root>/test-runner
remediation_dir = <output_root>/remediation
report_dir = <output_root>/report
logs_dir = <output_root>/logs
```

Required artifacts:

- `<output_root>/run_manifest.json`
- `<workspace_state_dir>/validation_workspace_state.json`
- `<workspace_state_dir>/validation_workspace_state.md`
- `<intake_dir>/validation_intake_fidelity.json`
- `<intake_dir>/validation_intake_fidelity.md`
- `<plan_gate_dir>/validation_plan_gate.json`
- `<plan_gate_dir>/validation_plan_gate.md`
- `<logs_dir>/plan-gate/*` when build/preview commands run
- `<test_runner_dir>/validation_test_runner.json`
- `<test_runner_dir>/validation_test_runner.md`
- `<logs_dir>/test-runner/*` when tests run
- `<remediation_dir>/<cycle_id>/validation_remediation.json` and `.md` when fixes run
- `<report_dir>/kmp_validation_report.json`
- `<report_dir>/kmp_validation_report.md`

No validator artifact may be written inside the migration output root. Migration artifacts are read-only inputs referenced by path.

## Output Artifact Content Matrix

The controller verifies both artifact names and role-aligned content before downstream stages consume any file.

| Stage / owner | Output file(s) | Required content |
|---|---|---|
| Output root lock / Leader | `run_manifest.json` | Validation scope, KMP target path, Android source/SPEC paths, migration report path, migration output root, validation output root, allowed roots, dependency-preflight status, timestamp. |
| Workspace ledger / `validation-workspace-state` | `validation_workspace_state.json`, `validation_workspace_state.md` | Validator node status, output files, changed-file ownership, stale upstream inputs, rerun history, blockers, and next safe action. |
| Intake/fidelity / `validation-intake-fidelity` | `validation_intake_fidelity.json`, `validation_intake_fidelity.md` | Migration trigger evidence, normalized validation brief, KMP evidence, Android/SPEC-vs-KMP fidelity gaps across UI/logic/data/control flow, test-trust blockers, rerun requests, blockers. |
| Plan/build gate / `validation-plan-gate` | `validation_plan_gate.json`, `validation_plan_gate.md`, plan-gate logs | Target structure, source sets, test frameworks, trusted command resolution, command sources, build/preview/renderability gate results, log paths, routed failures, blockers. |
| Test runner / `validation-test-runner` | `validation_test_runner.json`, `validation_test_runner.md`, test logs, optional changed test files | Android/SPEC-anchored test cases, expected vs actual results, commands, log paths, created/reused tests, failure routing, skipped/blocked reasons. |
| Remediation / `validation-remediation` | `validation_remediation.json`, `validation_remediation.md`, changed target files | Confirmed target KMP failures, Android/SPEC evidence for fixes, fixed/unfixed failures, changed files, diagnostics, required reruns, blockers. |
| Final verdict / `validation-report` | `kmp_validation_report.json`, `kmp_validation_report.md` | Final `passed | failed | blocked` verdict from verified evidence, fidelity summary, build/preview summary, test statistics, remediation summary, changed files, remaining failures, blockers, report path. |

JSON artifacts are the machine-routable source of truth. Markdown artifacts are agent-readable handoffs that preserve exact paths, commands/logs, changed-file ownership, rerun context, blockers, and downstream routing. Node Markdown must not be a prose-only completion summary.

## Shared Return Contract

```json
{
  "status": "completed | passed | failed | needs_rerun | blocked",
  "node": "node-name",
  "output_dir": "<exact validator node output dir under output_root>",
  "output_files": [],
  "changed_files": [],
  "stale_upstream_inputs": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```

Use `needs_rerun` when a previous role can resolve the gap, `failed` when validation evidence is complete and a behavior/build/test failure remains, and `blocked` when required evidence, command, environment, or user input is missing.

## Shared Rules

- Each role must read its role file before work and stay inside its responsibility boundary.
- Build/test/preview commands must come from user input, project scripts/docs/CI, or verified Gradle task discovery.
- A passing KMP test that contradicts Android source/SPEC behavior is a validation failure.
- Only `validation-remediation` edits target code.
- The controller must not substitute itself for a role's audit, command gate, test run, fix, or final verdict.
