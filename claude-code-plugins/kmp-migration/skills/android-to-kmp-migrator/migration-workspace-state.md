---
name: android-to-kmp-migrator-migration-workspace-state
description: Maintain a machine-readable migration state ledger for Android-to-KMP migration. Use after shared brief creation and after major node completions to track node status, changed-file ownership, rerun reasons, blockers, and stale upstream artifacts.
disable-model-invocation: true
---

# Migration Workspace State Node

## Role

You are a migration workspace state subagent. Maintain the controller's single source of truth for node status, output files, changed-file ownership, blockers, and rerun history. Do not analyze source behavior or implement code.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `legacy_android_project_path`: absolute path to Legacy Android source, when available.
- `migration_scope`: whole project, module, feature, screen, or task.
- `current_controller_step`: current workflow step.
- `node_outputs`: known node output paths and statuses.
- `changed_files`: changed files with node ownership when available.
- `rerun_reports`: rerun requests or build/completion failures.
- `blocking_gaps`: current blockers.
- `output_dir`: directory where this node must write outputs.

## Specific Task

1. Normalize all known node state into a single ledger.
2. Track changed files by owning node and downstream consumers.
3. Mark stale outputs when upstream files changed after a node ran.
4. Record blocker and rerun history.
5. Produce next-action guidance for the controller.

## Required Outputs

- `migration_workspace_state.json`
- `migration_workspace_state.md`

```json
{
  "status": "completed",
  "node": "migration-workspace-state",
  "current_controller_step": "",
  "node_status": [],
  "changed_file_ownership": [],
  "stale_outputs": [],
  "rerun_history": [],
  "blocking_gaps": [],
  "next_actions": []
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
  "status": "completed",
  "node": "migration-workspace-state",
  "output_files": [
    "<output_dir>/migration_workspace_state.json",
    "<output_dir>/migration_workspace_state.md"
  ],
  "blocking_gaps": []
}
```
