# Output Contract: Validation File Recording, Upstream Inputs, And Trigger Gates

This document is the **canonical path and content contract** for `kmp-test-validator`. Downstream handlers and cross-controller loops **MUST treat missing, empty, out-of-path, stale, or schema-invalid artifacts as hard blockers**.

When `SKILL.md` or `workflow.md` diverge, **this file wins on paths, filenames, upstream inputs, and trigger gates**.

## Upstream Input Contract (android-to-kmp-migrator)

Validation starts only when migrator handoff package **`V0`** is ready. Required upstream paths (read-only):

| Upstream artifact | Purpose |
|---|---|
| `migration_output_root/run_manifest.json` | KMP target, analyst SPEC paths, `handoff_gates.V0` |
| `migration_output_root/report/migration_report.json` | Scope, changed files, module completion |
| `migration_output_root/global/global_migration_representation.json` | Restoreability baseline |
| `migration_output_root/global/node-results/global-migration-phase/align/post_integration_alignment.json` | Alignment baseline |
| `migration_output_root/module-index/modules_migration_index.json` | Module lookup |
| Analyst `SPEC/prd.md`, `design.md`, `plan.md`, `verification.md` | Ground truth |

Record resolved paths in `run_manifest.json` → `upstream_migration_artifacts`.

**Fail closed**: migrator `V0` false → `blocked`.

---

## Validation Output Root Layout

```text
output_root = <output_dir or ~/.a2c_agents/validation>/kmp-test-validator

<output_root>/
├── run_manifest.json
├── upstream-index/
│   └── upstream_migration_index.json
├── workspace-state/
│   ├── validation_workspace_state.json
│   └── validation_workspace_state.md
├── fidelity-gate/
│   ├── trust/
│   │   ├── validation_fidelity_trust.json
│   │   └── validation_fidelity_trust.md
│   └── restoreability/
│       ├── validation_restoreability_audit.json
│       └── validation_restoreability_audit.md
├── code-gate/
│   ├── build/
│   │   ├── validation_code_build.json
│   │   └── validation_code_build.md
│   └── fix/
│       └── <cycle_id>/
│           ├── validation_code_fix.json
│           └── validation_code_fix.md
├── business-testing/
│   ├── validation_business_testing.json
│   └── validation_business_testing.md
├── report/
│   ├── kmp_validation_report.json
│   └── kmp_validation_report.md
└── logs/
    ├── code-gate/
    ├── business-testing/
    └── ui-comparison/
```

### Path Variables

| Variable | Path |
|---|---|
| `fidelity_gate_dir` | `<output_root>/fidelity-gate` |
| `fidelity_trust_dir` | `<fidelity_gate_dir>/trust` |
| `fidelity_restoreability_dir` | `<fidelity_gate_dir>/restoreability` |
| `code_gate_dir` | `<output_root>/code-gate` |
| `code_build_dir` | `<code_gate_dir>/build` |
| `code_fix_dir` | `<code_gate_dir>/fix` |
| `business_testing_dir` | `<output_root>/business-testing` |

### Role Ownership (mandatory)

| Duty | Owner |
|---|---|
| Pre-build fidelity trust | `validation-fidelity-gate` mode `trust` |
| Compile/build/preview execution | `validation-code-gate` mode `build` |
| Compile/test fixes | `validation-code-gate` mode `fix` (only production-code editor) |
| Post-build restoreability | `validation-fidelity-gate` mode `restoreability` |
| Optional business tests / Figma UI | `validation-business-testing` |
| Missing modules → migrator supplement | Leader loop (not code-gate fix) |

---

## Write Order (Leader Schedule)

1. Verify `V0`; write `run_manifest.json`, `upstream_migration_index.json`.
2. `validation-workspace-state` — initialize; refresh after each group.
3. `validation-fidelity-gate` mode `trust` → `VG1`.
4. `validation-code-gate` mode `build` → `VG2`; on failure → mode `fix` → rerun `build` (max 3 fix cycles).
5. `validation-fidelity-gate` mode `restoreability` → `VG3`; on `needs_migrator_supplement` → migrator supplement (max 3) → refresh upstream → rerun affected stages.
6. `validation-business-testing` when user inputs exist → `VG4` or explicit skip.
7. On business failures → code-gate mode `fix` → rerun `build` and/or business-testing.
8. `validation-report` → `VG5`.

---

## Handoff Package Gates

| Gate | Ready when |
|---|---|
| `VG0` | Migrator `V0` verified; `upstream_migration_index.json` written |
| `VG1` | `fidelity-gate/trust/validation_fidelity_trust.json` — no unresolved `test_trust_blockers` |
| `VG2` | `code-gate/build/validation_code_build.json` — `build.status: passed`; preview passed or justified `skipped` |
| `VG3` | `fidelity-gate/restoreability/validation_restoreability_audit.json` — `restoreability_verdict: passed` |
| `VG4` | `business-testing/validation_business_testing.json` — submodule outcomes or explicit `skipped` |
| `VG5` | `report/kmp_validation_report.json` issued |

**Fail closed**: `passed` requires `VG2` + `VG3`; enabled `VG4` submodules must have no unresolved failures.

---

## Key Artifact Schemas

### `validation_fidelity_trust.json` (mode `trust`)

Migration trigger evidence, `fidelity_gaps`, `test_trust_blockers`, normalized validation brief. Replaces legacy `validation_intake_fidelity.json`.

### `validation_code_build.json` (mode `build`)

`compile_resolution_scenario`: `user_specified` → `global_tool_search` → `default_gradle_kmp`. Build/preview status, log paths, failures routed to `validation-code-gate:fix`.

### `validation_code_fix.json` (mode `fix`)

`fix_knowledge_source`: `error_database | model_inference`. `restoreability_impact` per changed file. `required_reruns`: `["validation-code-gate:build", ...]`.

**Forbidden fix patterns**: delete/stub migrated behavior solely to pass compile; route missing modules to migrator supplement.

### `validation_restoreability_audit.json` (mode `restoreability`)

`migrator_supplement_request` when new migration work required. Controller invokes `android-to-kmp-migrator` — not code-gate `fix`.

### `validation_business_testing.json`

```json
{
  "submodules": {
    "behavioral": { "enabled": false, "status": "passed | failed | skipped | blocked" },
    "ui_comparison": { "enabled": false, "status": "passed | failed | skipped | blocked" }
  }
}
```

---

## Leader Obligations

1. Dispatch only role IDs listed in [SKILL.md](SKILL.md).
2. Run fidelity-gate `trust` before code-gate `build`; `restoreability` only after `VG2`.
3. Route compile failures to code-gate `fix`; route missing modules to migrator supplement.
4. Enable business-testing submodules only with user prerequisites.
5. Maintain `handoff_gates` in workspace ledger and final report.

## Invalid Artifact Handling

| Condition | Action |
|---|---|
| Unknown or invalid role ID in return payload | Reject; re-dispatch with role + mode from `SKILL.md` |
| `restoreability` before `VG2` | `blocked` |
| Fix mode delete/stub violation | `failed`; rerun fix with constraint recorded |
| Business submodule without user input | `skipped`, not pass-by-omission |
