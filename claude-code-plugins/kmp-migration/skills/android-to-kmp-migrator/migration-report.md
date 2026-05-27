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
- `output_dir`: directory where this node must write outputs; default to `~/.d2c_agents/migration/`.

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
