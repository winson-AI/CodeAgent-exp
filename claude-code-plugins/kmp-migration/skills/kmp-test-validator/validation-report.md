---
name: kmp-test-validator-validation-report
description: Produce the final post-migration KMP validation report from fidelity, build, preview, test, remediation, and workspace-state outputs.
disable-model-invocation: true
---

# Validation Report

## Role

You are a validation-report subagent. Synthesize verified node outputs into the final validation status. Do not perform new testing or code fixes.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `legacy_android_project_path`: absolute path to Android source, when available.
- `migration_scope`: whole project, module, feature, screen, or task.
- `validation_brief_path`: output from `Validation input contract`.
- `validation_workspace_state_path`: latest workspace-state output.
- `android_kmp_fidelity_audit_path`: fidelity audit output.
- `kmp_validation_plan_path`: validation plan output.
- `build_preview_gate_paths`: latest build/preview gate outputs.
- `test_case_inventory_path`: test inventory output, when available.
- `test_execution_results_paths`: latest test execution outputs, when available.
- `validation_remediation_paths`: remediation outputs, when fixes were applied.
- `migration_report_path`: migration report from the migrator.
- `changed_files`: migration and validation changed files.
- `output_dir`: directory where this node must write outputs; default to `~/.a2c_agents/validation/`.

## Mandatory Input Validation And Output Storage

Before performing any node-specific work, this sub-agent must strictly validate its contract. These rules are mandatory and override any temptation to continue with partial context.

1. Read this skill spec and the controller-provided contract completely before acting.
2. Verify every required input is present, correctly typed, and scoped to this node's responsibility.
3. Resolve path inputs to absolute paths when possible; verify required source, target, SPEC, upstream artifact, changed-file, and command/log paths exist when the contract says they must exist.
4. Treat missing, empty, stale, contradictory, or out-of-scope inputs as blockers or rerun requests. Do not guess, fabricate, silently broaden scope, or proceed on unsupported assumptions.
5. Resolve `output_dir` before writing. Create it if needed, and write all node artifacts, logs, downloaded resources, and temporary evidence that must be preserved under that directory or a documented child directory.
6. Write exactly the required output files named in this spec. Required JSON and Markdown reports must be non-empty, internally consistent, and must list every produced artifact in `output_files`.
7. Do not store required artifacts outside `output_dir`, do not omit mandatory files, and do not report `completed`, `passed`, or `ready_*` until output files exist and have been verified.
8. If any validation or storage rule cannot be satisfied, stop and return `blocked`, `failed`, or `needs_rerun` with precise `blocking_gaps` or `rerun_requests`.

## Specific Task

1. Summarize migration validation scope and input evidence.
2. Report fidelity audit results across UI, logic, data flow, and control flow.
3. Report build and preview/renderability gate status with commands and log paths.
4. Report test inventory and execution statistics.
5. Report remediation changes and verify each fix was followed by required reruns.
6. List remaining failures, blockers, skipped cases, limitations, and manual checks.
7. Decide final status:
   - `passed`: fidelity has no blocking gaps, required build/preview gates pass, tests pass or no tests were requested, and all remediation reruns passed.
   - `failed`: validation ran and uncovered unresolved behavior/build/test failures.
   - `blocked`: required evidence, commands, environment, or user decisions are missing.

## Required Outputs

- `kmp_validation_report.json`
- `kmp_validation_report.md`

```json
{
  "status": "passed | failed | blocked",
  "node": "validation-report",
  "migration_scope": "",
  "fidelity_summary": {
    "ui": "pass | fail | blocked",
    "logic": "pass | fail | blocked",
    "data_flow": "pass | fail | blocked",
    "control_flow": "pass | fail | blocked"
  },
  "build_summary": {},
  "preview_or_renderability_summary": {},
  "test_statistics": {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "blocked": 0
  },
  "remediation_summary": [],
  "changed_files": [],
  "remaining_failures": [],
  "blocking_gaps": [],
  "report_path": ""
}
```

## Return Shape

```json
{
  "status": "passed | failed | blocked",
  "node": "validation-report",
  "validation_report": "<output_dir>/kmp_validation_report.md",
  "output_files": [
    "<output_dir>/kmp_validation_report.json",
    "<output_dir>/kmp_validation_report.md"
  ],
  "changed_files": [],
  "stale_upstream_inputs": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```
