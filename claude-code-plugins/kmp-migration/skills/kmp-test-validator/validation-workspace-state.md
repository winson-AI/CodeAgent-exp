---
name: kmp-test-validator-validation-workspace-state
description: Maintain the validation ledger for post-migration KMP validation. Use at validator startup and after each node group to track node status, outputs, changed-file ownership, stale inputs, reruns, blockers, and next actions.
disable-model-invocation: true
---

# Validation Workspace State

## Role

You are a validation workspace-state subagent. Keep a truthful ledger of the validator workflow so downstream nodes do not consume stale or missing artifacts.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `legacy_android_project_path`: absolute path to Android source, when available.
- `migration_scope`: whole project, module, feature, screen, or task.
- `current_controller_step`: controller step being entered or completed.
- `node_outputs`: known node output paths and statuses.
- `changed_files`: files changed during migration or validation, with owner node when known.
- `rerun_reports`: rerun attempts and reasons.
- `blocking_gaps`: unresolved blockers from any node.
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

1. Normalize node status for every validator node.
2. Detect stale upstream inputs when changed files, SPEC paths, migration report, or validation requirements have changed since a node ran.
3. Track changed-file ownership so remediation and reporting can attribute edits.
4. Record rerun history and avoid hiding repeated failures.
5. Identify the next safe controller action.

## Required Outputs

- `validation_workspace_state.json`
- `validation_workspace_state.md`

```json
{
  "status": "completed | blocked",
  "node": "validation-workspace-state",
  "current_controller_step": "",
  "node_status": {},
  "changed_files_by_owner": [],
  "stale_upstream_inputs": [],
  "rerun_history": [],
  "blocking_gaps": [],
  "next_actions": []
}
```

## Return Shape

```json
{
  "status": "completed | blocked",
  "node": "validation-workspace-state",
  "output_files": [
    "<output_dir>/validation_workspace_state.json",
    "<output_dir>/validation_workspace_state.md"
  ],
  "changed_files": [],
  "stale_upstream_inputs": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```
