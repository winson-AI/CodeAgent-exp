# Workflow: migrated KMP target + Android source/SPEC -> verified validation verdict

This reduced workflow validates Android-to-KMP migration output through 6 active roles. The fidelity trust gate still runs before tests are trusted, and the build/preview gate still runs before behavioral tests.

## Overview

```mermaid
graph TD
  L0[Leader pre-flight] --> WS[validation-workspace-state]
  WS --> IF[validation-intake-fidelity]
  IF -->|blocked| STOP[Stop: not trusted migration validation]
  IF -->|trusted| PG[validation-plan-gate]
  PG -->|build/preview failed| REM[validation-remediation]
  PG -->|passed| TR[validation-test-runner]
  TR -->|failures| REM
  REM -->|required_reruns| PG
  REM -->|required_reruns| TR
  REM -->|blocked| STOP2[Route blocker]
  TR -->|passed or no cases| VR[validation-report]
  PG -->|no cases| VR
  VR --> OUT[passed / failed / blocked]
  WS -. refreshed after each group .-> VR
```

## Detailed Steps

### Step 0 — Pre-flight

- **Executor**: Leader
- **Input**: [dependencies.yaml](dependencies.yaml)
- **Action**: verify optional tools; target Gradle wrapper drives build/test.
- **Gate**: missing optional tools are recorded as degraded behavior.

### Step 1 — Workspace State

- **Executor**: `validation-workspace-state`
- **Action**: initialize ledger and refresh after each major group.
- **Output**: `validation_workspace_state.json`, `validation_workspace_state.md`
- **Gate**: no role consumes stale required inputs.

### Step 2 — Intake And Fidelity Trust Gate

- **Executor**: `validation-intake-fidelity`
- **Action**:
  - verify post-migration validation trigger.
  - normalize validation brief.
  - verify KMP evidence and migration evidence.
  - compare Android source/SPEC vs migrated KMP across UI, logic, data flow, and control flow.
  - flag `test_trust_blockers`.
- **Output**: `validation_intake_fidelity.json`, `validation_intake_fidelity.md`
- **Gate**: missing migration evidence or blocking fidelity gaps stop trusted tests and route to user/migration/remediation.

### Step 3 — Validation Plan And Build/Preview Gate

- **Executor**: `validation-plan-gate`
- **Action**:
  - discover target modules/source sets/test frameworks.
  - resolve commands from user input, project scripts/docs/CI, or verified Gradle tasks.
  - run resolved build command.
  - run preview/renderability gate when UI is in scope.
  - classify failures and route by owner.
- **Output**: `validation_plan_gate.json`, `validation_plan_gate.md`, log files
- **Gate**: behavioral tests do not run unless required build/preview gates pass.

### Step 4 — Test Runner

- **Executor**: `validation-test-runner`
- **Action**:
  - decompose validation requirements and migration report inputs into atomic Android-anchored cases.
  - reuse existing tests when possible.
  - create minimal project-convention tests only when needed.
  - execute through trusted commands/channels.
  - record pass/fail/skip/blocker evidence.
- **Output**: `validation_test_runner.json`, `validation_test_runner.md`, logs, changed test files when created
- **Gate**: a KMP pass that contradicts Android evidence is a failure.

### Step 5 — Remediation Loop

- **Executor**: `validation-remediation`
- **Input**: failed plan/build gate or test runner outputs, `allowed_files`, failure IDs, fidelity evidence
- **Action**: fix only confirmed target KMP failures inside allowed files.
- **Output**: `validation_remediation.json`, `validation_remediation.md`
- **Gate**: every remediation emits `required_reruns`; the controller reruns `validation-plan-gate` and/or `validation-test-runner` until pass or blocked.

### Step 6 — Final Report

- **Executor**: `validation-report`
- **Input**: workspace state, intake/fidelity, plan/gate, test runner, remediation, migration report
- **Action**: synthesize the final validation verdict.
- **Output**: `kmp_validation_report.json`, `kmp_validation_report.md`
- **Gate**: report runs only when latest workspace state shows no stale required inputs.

## Final Report Format

```json
{
  "status": "passed | failed | blocked",
  "migration_scope": "",
  "kmp_target_project_path": "",
  "fidelity_summary": { "ui": "", "logic": "", "data_flow": "", "control_flow": "" },
  "build_summary": {},
  "preview_or_renderability_summary": {},
  "test_statistics": { "total": 0, "passed": 0, "failed": 0, "skipped": 0, "blocked": 0 },
  "remediation_summary": [],
  "remaining_failures": [],
  "blocking_gaps": [],
  "report_path": ""
}
```

## Acceptance Criteria

- Active dispatch uses only the 6 reduced role IDs.
- Intake/fidelity trust gate completes before build/test results are trusted.
- Build/preview gate passes before behavioral tests run.
- Commands are trusted and never invented.
- Test cases are Android/SPEC anchored; contradictory KMP passes are failures.
- Every remediation fix is followed by required reruns.
- `validation-report` decides `passed | failed | blocked` only from verified outputs.
