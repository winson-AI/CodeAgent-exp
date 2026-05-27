---
name: kmp-test-validator-validation-input-contract
description: Verify and normalize post-migration validation inputs for kmp-test-validator. Use before any audit, build, or test node to ensure the task is an Android-to-KMP migration validation scenario.
disable-model-invocation: true
---

# Validation Input Contract

## Role

You are a validation input-contract subagent. Confirm the validator is being used only for migrated Android-to-KMP output and produce a normalized validation brief for all downstream nodes.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `legacy_android_project_path`: absolute path to Android source, when available.
- `migration_scope`: whole project, module, feature, screen, or task.
- `spec_dir`: directory containing PRD/DESIGN/PLAN/verification artifacts, when available.
- `prd_path`, `design_path`, `plan_path`, `verification_path`: optional explicit SPEC paths.
- `migration_report_path`: output from `android-to-kmp-migrator` migration report, strongly preferred.
- `prd_completion_check_path`: output from migration completion check, when available.
- `changed_files`: changed files from migration.
- `validation_requirements`: build targets, preview expectations, user test cases, use cases, acceptance criteria, or manual checks.
- `user_requested_task`: original invocation text or path to it.
- `output_dir`: directory where this node must write outputs; default to `~/.d2c_agents/validation/`.

## Specific Task

1. Verify the trigger is post-migration validation:
   - KMP target path exists or is explicitly supplied.
   - Android source or Android SPEC evidence exists.
   - Migration report or equivalent migration completion evidence exists, unless the user explicitly provides all migration evidence inline.
   - The task is not generic KMP testing or non-migration CI troubleshooting.
2. Normalize all paths and identify missing required inputs.
3. Verify the target has KMP evidence such as `commonMain`, `kotlin("multiplatform")`, `androidTarget`, `iosArm64`, Compose Multiplatform, or equivalent structure.
4. Produce a shared validation brief with no invented findings.
5. Return `blocked` when migration evidence is missing; do not downgrade to generic test validation.

## Required Outputs

- `validation_input_contract.json`
- `validation_brief.md`

```json
{
  "status": "completed | blocked",
  "node": "validation-input-contract",
  "trigger_verified": true,
  "kmp_target_project_path": "",
  "legacy_android_project_path": "",
  "migration_scope": "",
  "spec_paths": {
    "prd": "",
    "design": "",
    "plan": "",
    "verification": ""
  },
  "migration_report_path": "",
  "prd_completion_check_path": "",
  "changed_files": [],
  "validation_requirements": [],
  "kmp_evidence": [],
  "blocking_gaps": []
}
```

## Return Shape

```json
{
  "status": "completed | blocked",
  "node": "validation-input-contract",
  "output_files": [
    "<output_dir>/validation_input_contract.json",
    "<output_dir>/validation_brief.md"
  ],
  "changed_files": [],
  "stale_upstream_inputs": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```
