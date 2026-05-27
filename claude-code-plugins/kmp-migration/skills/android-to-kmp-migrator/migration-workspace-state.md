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
