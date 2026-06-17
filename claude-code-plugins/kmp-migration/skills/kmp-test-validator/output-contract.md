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
│   ├── fix/
│   │   └── <cycle_id>/
│   │       ├── validation_code_fix.json
│   │       └── validation_code_fix.md
│   └── knowledge/
│       ├── compile_error_knowledge.json
│       ├── compile_error_knowledge.md
│       └── entries/
│           └── <entry_id>/
│               ├── bug_fix_experience.json
│               └── bug_fix_experience.md
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
| `code_gate_knowledge_dir` | `<code_gate_dir>/knowledge` |
| `knowledge_entries_dir` | `<code_gate_knowledge_dir>/entries` |
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
4. `validation-code-gate` mode `build` → `VG2`; on failure → mode `fix` (lookup `compile_error_knowledge.*` and optional `error_knowledge_path`) → rerun `build` (max 3 fix cycles); on `VG2` pass after a fix cycle, persist verified bug-fix experiences under `code-gate/knowledge/entries/`.
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
| `VG3` | `fidelity-gate/restoreability/validation_restoreability_audit.json` — `restoreability_verdict: passed`; when `analytics_reporting_required`, `analytics_reporting_summary.verdict: passed | not_applicable` |
| `VG4` | `business-testing/validation_business_testing.json` — submodule outcomes or explicit `skipped`; `analytics_reporting` MUST run when migrator requires it |
| `VG5` | `report/kmp_validation_report.json` issued |

**Fail closed**: `passed` requires `VG2` + `VG3`; enabled `VG4` submodules must have no unresolved failures.

---

## Key Artifact Schemas

### `validation_fidelity_trust.json` (mode `trust`)

Migration trigger evidence, `fidelity_gaps`, `test_trust_blockers`, normalized validation brief. Replaces legacy `validation_intake_fidelity.json`.

### `validation_code_build.json` (mode `build`)

`compile_resolution_scenario`: `user_specified` → `global_tool_search` → `default_gradle_kmp`. Build/preview status, log paths, failures routed to `validation-code-gate:fix`.

### `validation_code_fix.json` (mode `fix`)

`kmp_target_project_path`, `fix_knowledge_source`: `prior_experience | error_database | model_inference`, `knowledge_lookup`, `referenced_entry_ids[]`, `knowledge_candidates[]`, `target_edit_summary`, `changed_files[]` listing every target KMP path created or modified to resolve build/preview failures, `restoreability_impact` per change. `required_reruns`: `["validation-code-gate:build", ...]`. Fix mode is the **only** validator role that edits target production code.

**Forbidden fix patterns**: delete/stub migrated behavior solely to pass compile; route missing modules to migrator supplement.

### Compile error knowledge store (`code-gate/knowledge/`)

The validator maintains a durable bug-fix experience ledger for compile/preview failures. Reuse it before inventing new fixes.

| Path | Owner | When written | Purpose |
|---|---|---|---|
| `compile_error_knowledge.json` | `validation-code-gate` | init empty; update after verified fix | Machine index: fingerprints → `entry_id`, hit counts, last match |
| `compile_error_knowledge.md` | `validation-code-gate` | with index updates | Agent-readable lookup table |
| `entries/<entry_id>/bug_fix_experience.json` | `validation-code-gate` | after `VG2` pass confirms fix cycle | Verified error signature + solution steps + changed files |
| `entries/<entry_id>/bug_fix_experience.md` | `validation-code-gate` | with entry JSON | Agent-readable bug-fix experience card |

**Lookup order (fix mode, before editing target code)**:

1. `code-gate/knowledge/compile_error_knowledge.json` — match `message_fingerprint`, `error_code`, `file_pattern`, `symbol_pattern`.
2. Optional external `error_knowledge_path` — same signature matching when configured.
3. `model_inference` — only when no prior experience matches.

**Persist rule**: write or update `entries/<entry_id>/` only after the fix cycle is **verified** by a subsequent code-gate `build` pass (`VG2`). Unverified fixes stay in `validation_code_fix.json` → `knowledge_candidates[]` only.

#### `compile_error_knowledge.json` index shape

```json
{
  "knowledge_root": "",
  "external_error_knowledge_path": "",
  "entry_count": 0,
  "entries": [
    {
      "entry_id": "ce-<slug>",
      "message_fingerprint": "",
      "error_code": "",
      "compiler": "kotlin | gradle | compose",
      "verified": true,
      "hit_count": 0,
      "last_matched_at": "",
      "entry_path": "entries/<entry_id>/bug_fix_experience.json"
    }
  ]
}
```

#### `bug_fix_experience.json` entry shape

```json
{
  "entry_id": "ce-<slug>",
  "error_signature": {
    "compiler": "kotlin | gradle | compose",
    "error_code": "",
    "normalized_message": "",
    "message_fingerprint": "",
    "file_pattern": "",
    "symbol_pattern": ""
  },
  "root_error_excerpt": "",
  "build_log_ref": "",
  "failure_id": "",
  "fix_summary": "",
  "solution_steps": [],
  "target_files_changed": [],
  "changed_files_snapshot": [],
  "fix_knowledge_source": "prior_experience | error_database | model_inference",
  "referenced_entry_ids": [],
  "verified_by": "validation-code-gate:build",
  "verification_cycle_id": "",
  "fix_cycle_id": "",
  "created_at": "",
  "hit_count": 0,
  "last_matched_at": ""
}
```

**Same-error reuse**: when a routed failure matches an existing fingerprint, fix mode MUST set `fix_knowledge_source: prior_experience`, populate `referenced_entry_ids`, apply the recorded `solution_steps` when still valid, and increment `hit_count` in the index after successful verification.

### `validation_restoreability_audit.json` (mode `restoreability`)

`migrator_supplement_request` when new migration work required. When `migration_report.validation_inputs.analytics_reporting_required`, MUST include `analytics_reporting_results[]` and `analytics_reporting_summary` — failed analytics reporting blocks `restoreability_verdict: passed`. Controller invokes `android-to-kmp-migrator` — not code-gate `fix`.

### `validation_business_testing.json`

```json
{
  "submodules": {
    "behavioral": { "enabled": false, "status": "passed | failed | skipped | blocked" },
    "ui_comparison": { "enabled": false, "status": "passed | failed | skipped | blocked" },
    "analytics_reporting": { "enabled": false, "status": "passed | failed | skipped | blocked" }
  }
}
```

`analytics_reporting` is **enabled** when migrator `validation_inputs.analytics_reporting_required` is true — not optional skip when legacy scope had 埋点.

---

## Leader Obligations

1. Dispatch only role IDs listed in [SKILL.md](SKILL.md).
2. Run fidelity-gate `trust` before code-gate `build`; `restoreability` only after `VG2`.
3. Route compile failures to code-gate `fix`; route missing modules to migrator supplement.
4. Initialize `code-gate/knowledge/compile_error_knowledge.json` when missing; persist verified bug-fix experiences after `VG2` pass.
5. Enable business-testing submodules only with user prerequisites.
6. Maintain `handoff_gates` in workspace ledger and final report.

## Invalid Artifact Handling

| Condition | Action |
|---|---|
| Unknown or invalid role ID in return payload | Reject; re-dispatch with role + mode from `SKILL.md` |
| `restoreability` before `VG2` | `blocked` |
| Fix mode delete/stub violation | `failed`; rerun fix with constraint recorded |
| Business submodule without user input | `skipped`, not pass-by-omission |
