# Workflow: migrated KMP target → verified validation verdict

Serial pipeline with mode-based fidelity and code gates. See [output-contract.md](output-contract.md) and [SKILL.md](SKILL.md).

## Overview

```mermaid
graph TD
  L0[Leader: V0 + output_root] --> WS[validation-workspace-state]
  WS --> FG1[validation-fidelity-gate<br/>mode: trust]
  FG1 -->|VG1| CG1[validation-code-gate<br/>mode: build]
  CG1 -->|compile failed| CG2[validation-code-gate<br/>mode: fix]
  CG2 --> CG1
  CG1 -->|VG2| FG2[validation-fidelity-gate<br/>mode: restoreability]
  FG2 -->|needs supplement| MIG[android-to-kmp-migrator<br/>max 3]
  MIG --> FG1
  MIG --> CG1
  FG2 -->|VG3| BT[validation-business-testing<br/>optional]
  BT -->|failures| CG2
  CG2 --> BT
  BT --> VR[validation-report]
  FG2 -->|no business inputs| VR
  VR --> OUT[passed / failed / blocked]
```

## Steps

### Step 0 — Pre-flight

Verify migrator `V0`; write `upstream_migration_index.json`; lock `output_root` (`VG0`).

### Step 1 — Workspace State

Initialize ledger with `handoff_gates` VG0–VG5; track `fix_cycles` and `migrator_supplement_cycles`.

### Step 2 — Fidelity Gate `trust`

- **Executor**: `validation-fidelity-gate` mode `trust`
- **Output**: `fidelity-gate/trust/validation_fidelity_trust.*`
- **Gate**: `VG1`

### Step 3 — Code Gate `build`

- **Executor**: `validation-code-gate` mode `build`
- **Compile scenarios**: `user_specified` → `global_tool_search` → `default_gradle_kmp`
- **Output**: `code-gate/build/validation_code_build.*`, `logs/code-gate/*`
- **On failure**: dispatch code-gate mode `fix` — lookup `code-gate/knowledge/compile_error_knowledge.json` and optional `error_knowledge_path` for matching bug-fix experiences, then edit target KMP files → rerun `build` (max 3 fix cycles)
- **On `VG2` pass after fix**: persist verified `knowledge_candidates` to `code-gate/knowledge/entries/<entry_id>/bug_fix_experience.*` and update the knowledge index
- **Gate**: `VG2`

### Step 4 — Fidelity Gate `restoreability`

- **Executor**: `validation-fidelity-gate` mode `restoreability`
- **Prerequisite**: `VG2`
- **Output**: `fidelity-gate/restoreability/validation_restoreability_audit.*` (incl. `analytics_reporting_results[]` when migrator requires analytics reporting)
- **On gaps**: migrator supplement loop (max 3) → refresh upstream → rerun trust/build as scoped
- **Gate**: `VG3`

### Step 5 — Business Testing (optional)

- **Executor**: `validation-business-testing`
- **Prerequisite**: `VG3`
- **Submodules**: `behavioral` (user test cases), `ui_comparison` (Figma refs), `analytics_reporting` (migrator `analytics_reporting_required` — verify 埋点 reporting on key flows)
- **Output**: `business-testing/validation_business_testing.*`
- **Gate**: `VG4` or explicit skip

### Step 6 — Final Report

- **Executor**: `validation-report`
- **Gate**: `VG5`

## Controller Loops

| Loop | Max | Trigger |
|---|---|---|
| Code fix | 3 | `validation-code-gate` build failed or business-testing failures |
| Migrator supplement | 3 | fidelity-gate `restoreability` → `migrator_supplement_request.required` |

## Acceptance Criteria

- Dispatch only role IDs from `SKILL.md`.
- Fidelity-gate `trust` before code-gate `build`; `restoreability` after `VG2`.
- Only code-gate mode `fix` edits production code.
- Compile errors with verified solutions are stored as bug-fix experiences; same fingerprints reuse prior entries before `model_inference`.
- Business testing skipped (not passed) when no user inputs.
- Final verdict evidence-backed from verified artifacts.
