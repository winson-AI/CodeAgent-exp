# Output Contract: Validation File Recording, Upstream Inputs, And Trigger Gates

This document is the **canonical path and content contract** for `kmp-test-validator`. Downstream handlers and cross-controller loops **MUST treat missing, empty, out-of-path, stale, or schema-invalid artifacts as hard blockers**.

When `SKILL.md` or `workflow.md` diverge, **this file wins on paths, filenames, upstream inputs, and trigger gates**.

## Upstream Input Contract (android-to-kmp-migrator)

Validation starts only when migrator handoff package **`V0`** is ready. Required upstream paths (read-only):

| Upstream artifact | Purpose |
|---|---|
| `migration_output_root/run_manifest.json` | KMP target, analyst SPEC paths, `handoff_gates.V0`, partial migration / mock data preflight when present |
| `migration_output_root/report/migration_report.json` | Scope, changed files, module completion, partial migration, mock-data usage summary |
| `migration_output_root/global/global_migration_representation.json` | Restoreability baseline |
| `migration_output_root/global/node-results/global-migration-phase/align/post_integration_alignment.json` | Alignment baseline; `entry_point_alignment_results[]` |
| `migration_output_root/global/node-results/global-migration-phase/integrate/global_system_integration.json` | Entry point wiring baseline; `entry_point_wiring[]` |
| `migration_output_root/module-index/modules_migration_index.json` | Module lookup |
| Analyst `SPEC/prd.md`, `design.md`, `plan.md`, `verification.md` | Ground truth |

Record resolved paths in `run_manifest.json` → `upstream_migration_artifacts`.

**Fail closed**: migrator `V0` false → `blocked`.

When upstream migration is partial, the validator MUST preserve the same scoped module/feature boundary. Out-of-scope modules are dependency context only unless `migration_report.partial_migration.integration_seams_verified[]` explicitly requires validation.

### Partial Migration Mock Machine Contract

For partial migration only, the validator may use a controlled **mock machine** to pass the current module check when real runtime dependencies are unavailable. A mock machine is a temporary validation harness such as a fake backend, local service, DI override, fixture source set, emulator/device profile, test app shell, or static-only launch substitute that lets the scoped module compile/launch/restoreability-check without validating the entire product environment.

```json
{
  "mock_machine_preflight": {
    "allowed": false,
    "source": "user_input | migrator_mock_data_preflight | validator_dependency_gap | none",
    "scope": "none | current_module | screen_flow | entry_point | analytics_reporting | local_service | static_only",
    "current_module_ids": [],
    "reason": "",
    "must_not_ship": true,
    "expiry_condition": "",
    "approval_evidence": []
  }
}
```

Rules:

- `mock_machine_preflight.allowed: true` is valid only for `partial_migration.enabled: true` and only for the current scoped module/feature check.
- Mock machine evidence may satisfy `current_module_check` / scoped build, launch, restoreability, or analytics reachability when the real dependency is outside migration scope or unavailable.
- Mock machine evidence MUST NOT certify full-project behavior, replace missing migrated logic, hide API contract mismatch, or count as release-ready validation.
- Every use MUST be recorded in `validation_code_build.json`, `validation_restoreability_audit.json`, `validation_business_testing.json`, workspace state, and final report as applicable.

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
│   ├── validation_business_testing.md
│   └── entry-point-launch/
│       ├── validation_entry_point_launch.json
│       └── validation_entry_point_launch.md
├── report/
│   ├── kmp_validation_report.json
│   └── kmp_validation_report.md
└── logs/
    ├── code-gate/
    ├── business-testing/
    ├── entry-point-launch/
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
| `entry_point_launch_dir` | `<business_testing_dir>/entry-point-launch` |

### Role Ownership (mandatory)

| Duty | Owner |
|---|---|
| Pre-build fidelity trust | `validation-fidelity-gate` mode `trust` |
| Compile/build/preview execution | `validation-code-gate` mode `build` |
| Compile/test fixes | `validation-code-gate` mode `fix` (only production-code editor) |
| Post-build restoreability | `validation-fidelity-gate` mode `restoreability` |
| Optional business tests / Figma UI / entry launch | `validation-business-testing` |
| Missing modules → migrator supplement | Leader loop (not code-gate fix) |

---

## Write Order (Leader Schedule)

1. Verify `V0`; write `run_manifest.json`, `upstream_migration_index.json`, including `partial_migration` and `mock_machine_preflight` when applicable.
2. `validation-workspace-state` — initialize `pipeline_steps[]` and `validation_todo_list[]`; refresh after each group and sync todo/step status.
3. `validation-fidelity-gate` mode `trust` → `VG1`.
4. `validation-code-gate` mode `build` → `VG2`; on failure → mode `fix` (lookup `compile_error_knowledge.*` and optional `error_knowledge_path`) → rerun `build` (max 3 fix cycles); on `VG2` pass after a fix cycle, persist verified bug-fix experiences under `code-gate/knowledge/entries/`.
4.5. `validation-business-testing` submodule `entry_point_launch` after `VG2` — mandatory for migration `V0`; on failure → code-gate mode `fix` → rerun `build` and entry point launch.
5. `validation-fidelity-gate` mode `restoreability` → `VG3`; on `needs_migrator_supplement` → migrator supplement (max 3) → refresh upstream → rerun affected stages.
6. `validation-business-testing` optional submodules when user inputs exist → `VG4` or explicit skip.
7. On business failures → code-gate mode `fix` → rerun `build` and/or business-testing.
8. `validation-report` → `VG5`.

---

## Handoff Package Gates

| Gate | Ready when |
|---|---|
| `VG0` | Migrator `V0` verified; `upstream_migration_index.json` written |
| `VG1` | `fidelity-gate/trust/validation_fidelity_trust.json` — no unresolved `test_trust_blockers` |
| `VG2` | `code-gate/build/validation_code_build.json` — `build.status: passed`; preview passed or justified `skipped`; for partial current-module mock machine runs, `current_module_check.status: passed` and `mock_machine_summary.status: approved_used | not_used` |
| `VG3` | `fidelity-gate/restoreability/validation_restoreability_audit.json` — `restoreability_verdict: passed`; when `analytics_reporting_required`, `analytics_reporting_summary.verdict: passed | not_applicable`; mock-machine-assisted passes require approved `mock_machine_restoreability[]` evidence |
| `VG4` | `business-testing/validation_business_testing.json` — `submodules.entry_point_launch.status: passed` for migration `V0`; optional submodule outcomes or explicit `skipped`; `analytics_reporting` MUST run when migrator requires it |
| `VG5` | `report/kmp_validation_report.json` issued |

**Fail closed**: `passed` requires `VG2` + `VG3` + `entry_point_launch` passed for migration `V0`; enabled optional `VG4` submodules must have no unresolved failures.

---

## Key Artifact Schemas

### `validation_workspace_state.json` (state monitor)

Owner: `validation-workspace-state`. Path: `workspace-state/validation_workspace_state.json`. Refreshed after each validator node group.

| Key | Purpose |
|---|---|
| `validation_todo_list[]` | Checks still to run — seeded from `migration_report`, SPEC, `validation_requirements`, `figma_refs`, mandatory `entry_point_launch`, optional business/analytics submodules |
| `pipeline_steps[]` | Schedule `VG0`–`VG5` with synced step `status` (incl. fix/supplement loop rows) |
| `validation_status.todo_summary` | Todo counts by status |
| `validation_status.pipeline_summary` | Step counts + `current_step_id` |
| `handoff_gates` | `VG0`–`VG5` readiness |
| `fix_cycles`, `migrator_supplement_cycles` | Active remediation loop counters |
| `partial_migration` | Scoped validation boundary inherited from migrator |
| `mock_machine_tracking` | Approved/used mock machine evidence and replacement blockers |

`validation_workspace_state.md` MUST include **Validation Todo List** and **Pipeline Progress** tables.

### `validation_fidelity_trust.json` (mode `trust`)

Migration trigger evidence, `fidelity_gaps`, `test_trust_blockers`, normalized validation brief. Replaces legacy `validation_intake_fidelity.json`.

### `validation_code_build.json` (mode `build`)

`compile_resolution_scenario`: `user_specified` → `global_tool_search` → `default_gradle_kmp`. Build/preview status, log paths, failures routed to `validation-code-gate:fix`.

For partial migration with approved mock machine, `validation_code_build.json` MUST include:

```json
{
  "current_module_check": {
    "enabled": false,
    "migration_module_ids": [],
    "status": "passed | failed | blocked | not_applicable",
    "commands": [],
    "evidence": [],
    "dependency_gaps_masked": []
  },
  "mock_machine_summary": {
    "used": false,
    "status": "approved_used | unapproved_used | not_used | blocked",
    "items": [],
    "must_not_ship": true,
    "replacement_follow_ups": []
  }
}
```

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

`migrator_supplement_request` when new migration work required. Post-build **entry point static re-verification**: for each row in migrator `post_integration_alignment.json` → `entry_point_alignment_results[]`, confirm built target evidence still resolves the KMP shell path/symbol and `global_alignment_results.entry_points.verdict` remains `passed | passed_with_assumptions`; record `entry_point_verification_results[]` with `post_build_status`. Failed entry point static verification blocks `restoreability_verdict: passed`. When `migration_report.validation_inputs.analytics_reporting_required`, MUST include `analytics_reporting_results[]` and `analytics_reporting_summary` — failed analytics reporting blocks `restoreability_verdict: passed`. Controller invokes `android-to-kmp-migrator` — not code-gate `fix`.

For approved partial mock-machine runs, restoreability may include:

```json
{
  "mock_machine_restoreability": [
    {
      "mock_machine_id": "",
      "migration_module_id": "",
      "validated_surface": "current_module | screen_flow | entry_point | analytics_reporting",
      "real_dependency_replaced": "",
      "evidence_paths": [],
      "status": "passed | failed | blocked",
      "release_blocker": true,
      "replacement_follow_up": ""
    }
  ]
}
```

### `validation_entry_point_launch.json` (submodule `entry_point_launch`)

Mandatory after `VG2` for migration `V0`. Anchors Legacy Android launcher/Application/root-nav/deep-link evidence to KMP post-build launch behavior.

```json
{
  "status": "passed | failed | blocked",
  "node": "validation-business-testing",
  "submodule": "entry_point_launch",
  "legacy_android_project_path": "",
  "kmp_target_project_path": "",
  "alignment_baseline_path": "",
  "entry_point_wiring_path": "",
  "launch_environment": {
    "available": true,
    "method": "adb | gradle_install | jetbrains_run | static_only",
    "device_or_emulator": "",
    "reason_if_unavailable": ""
  },
  "entry_point_launch_results": [
    {
      "legacy_entry_id": "",
      "legacy_name": "",
      "legacy_type": "Activity | Application | NavGraph | DeepLink | Composable",
      "legacy_source_path": "",
      "target_path": "",
      "target_symbol": "",
      "launch_flow_match": true,
      "start_destination_match": true,
      "startup_hook_match": true,
      "deep_link_match": true,
      "first_screen_match": true,
      "status": "passed | failed | blocked",
      "evidence_paths": [],
      "launch_log_ref": "",
      "gap": ""
    }
  ],
  "entry_point_launch_summary": {
    "total_entries": 0,
    "passed_count": 0,
    "failed_count": 0,
    "verdict": "passed | failed | blocked"
  },
  "rerun_requests": [],
  "blocking_gaps": []
}
```

**Launch verification rules**:

1. Resolve each Legacy Android entry from manifest `MAIN`/`LAUNCHER`, analyst `presentation_resource` `entry_points[]`, and migrator `entry_point_alignment_results[]`.
2. Install/launch KMP Android shell using trusted commands (`user_specified` → `gradle :androidApp:installDebug` / project-equivalent → jetbrains run when available).
3. Compare launch order, start destination/route, Application/startup hooks, deep-link handlers, and first visible screen against Android evidence.
4. Mismatch → `failed`; route shell/glue fixable issues to code-gate `fix`; missing migration wiring → `needs_migrator_supplement` via restoreability, not delete/stub fixes.
5. When launch environment unavailable: `blocked` unless post-build static evidence plus migrator `global_alignment_results.entry_points.verdict: passed` is re-verified on disk — never auto-pass without launch or documented static fallback.

### `validation_business_testing.json`

```json
{
  "submodules": {
    "entry_point_launch": { "enabled": true, "status": "passed | failed | skipped | blocked" },
    "behavioral": { "enabled": false, "status": "passed | failed | skipped | blocked" },
    "ui_comparison": { "enabled": false, "status": "passed | failed | skipped | blocked" },
    "analytics_reporting": { "enabled": false, "status": "passed | failed | skipped | blocked" }
  }
}
```

`entry_point_launch` is **enabled** for every migration `V0` handoff — mandatory, not optional skip. `analytics_reporting` is **enabled** when migrator `validation_inputs.analytics_reporting_required` is true — not optional skip when legacy scope had 埋点.

---

## Leader Obligations

1. Dispatch only role IDs listed in [SKILL.md](SKILL.md).
2. Run fidelity-gate `trust` before code-gate `build`; `entry_point_launch` after `VG2`; `restoreability` only after `entry_point_launch` completes (pass or documented `blocked`).
3. Route compile failures to code-gate `fix`; route missing modules to migrator supplement.
4. Initialize `code-gate/knowledge/compile_error_knowledge.json` when missing; persist verified bug-fix experiences after `VG2` pass.
5. Enable business-testing submodules only with user prerequisites.
6. Maintain `handoff_gates` in workspace ledger and final report.
7. Refresh `validation-workspace-state` so `validation_todo_list` and `pipeline_steps` reflect status before issuing `VG5` verdict.
8. For partial migration mock-machine checks, ensure every mock-machine item is approved, scoped to the current module, and carried into final report limitations/replacement follow-ups.

## Invalid Artifact Handling

| Condition | Action |
|---|---|
| Unknown or invalid role ID in return payload | Reject; re-dispatch with role + mode from `SKILL.md` |
| `restoreability` before `VG2` or before `entry_point_launch` completes | `blocked` |
| Fix mode delete/stub violation | `failed`; rerun fix with constraint recorded |
| Business optional submodule without user input | `skipped`, not pass-by-omission |
| `entry_point_launch` skipped for migration `V0` | `failed` |
| Mock machine used without `mock_machine_preflight.allowed` | `blocked` |
| Mock machine used for full-project validation | `failed` — rerun without mock or narrow to partial current-module scope |
| Mock machine hides missing migrated logic/API mismatch | `failed`; route to migrator supplement or code-gate fix |
