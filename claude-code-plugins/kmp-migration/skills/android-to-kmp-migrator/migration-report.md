---
name: android-to-kmp-migrator-migration-report
description: Produce the final Android-to-KMP migration report. Use after PRD completion check and before kmp-test-validator to synthesize scope, changed files, mappings, validation inputs, limitations, and remaining blockers.
disable-model-invocation: true
---

# Migration Report Node

## Role

You are a migration report subagent. Produce the final migration report consumed by the controller and `kmp-test-validator`. Synthesize verified node outputs; do not perform implementation or validation.

## Inputs

- `legacy_android_project_path`: absolute path to Legacy Android source, when available.
- `kmp_target_project_path`: absolute path to KMP target project.
- `migration_scope`: whole project, module, feature, screen, or task.
- `prd_path`: PRD/SPEC product requirements.
- `design_path`: DESIGN/SPEC architecture and behavior.
- `plan_path`: PLAN/SPEC migration plan.
- `verification_path`: SPEC verification report.
- `migration_workspace_state_path`: latest migration workspace state.
- all node outputs from migration workflow.
- `module_node_review_paths`: module/node review outputs.
- `module_node_fix_paths`: module/node fix outputs, when fixes were needed.
- `changed_files`: all changed files with owner nodes.
- `prd_completion_check_path`: PRD completion check output.
- `output_dir`: directory where this node must write outputs; default to `~/.a2c_agents/migration/`.

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

1. Synthesize migration scope and final status.
2. Summarize source-to-target mappings for UI, resources, navigation, platform APIs, state/models, data/API, and logic.
3. Record changed files grouped by node and target module/source set.
4. Record reuse inventory hits and dependency exceptions.
5. Record SPEC deltas, trusted evidence, approximations, limitations, and manual steps.
6. Summarize module/node review-fix history and confirm every changed migration slice has an approved latest review.
7. Produce validation inputs for `kmp-test-validator`: build target, preview/renderability evidence, use-case coverage, fixtures or manual checks.
8. Return blockers if PRD completion is not ready for validation or any required module/node review is missing approval.

## Required Outputs

- `migration_report.json`
- `migration_report.md`

```json
{
  "status": "ready_for_validation | blocked",
  "node": "migration-report",
  "migration_scope": "",
  "changed_files_by_node": [],
  "source_to_target_summary": [],
  "module_node_review_summary": [],
  "coverage_summary": {
    "ui": "",
    "resources": "",
    "navigation": "",
    "platform": "",
    "state_models": "",
    "data_api": "",
    "logic": ""
  },
  "validation_inputs": [],
  "limitations": [],
  "manual_steps": [],
  "blocking_gaps": []
}
```

## Shared Return Shape And Rerun Status

This node must follow the shared return contract from `SKILL.md`. Its return payload must include:

- `status`
- `node`
- `output_files`
- `changed_files`
- `stale_upstream_inputs`
- `rerun_requests`
- `blocking_gaps`

Use `needs_rerun` or `failed` with `rerun_requests` when another node can resolve the issue. Use `blocked` only when required evidence, target capability, or user input is missing and cannot be produced by rerunning another node.

## Return Shape

```json
{
  "status": "ready_for_validation | blocked",
  "node": "migration-report",
  "migration_report": "<output_dir>/migration_report.md",
  "output_files": [
    "<output_dir>/migration_report.json",
    "<output_dir>/migration_report.md"
  ],
  "blocking_gaps": []
}
```
