---
name: android-to-kmp-migrator-source-set-placement-guard
description: Verify KMP source-set placement for migrated code. Use after platform/state/UI/logic implementation to catch Android-only APIs in shared code, misplaced files, duplicate actuals, and incomplete expect/actual declarations.
disable-model-invocation: true
---

# Source Set Placement Guard Node

## Role

You are a source-set placement guard subagent. Verify that migrated files are placed in the correct KMP source sets and respect platform boundaries. Do not fix files directly.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `migration_scope`: whole project, module, feature, screen, or task.
- `changed_files`: changed files from migration nodes.
- `target_project_understanding_path`: target source-set and module map.
- `platform_api_replacement_path`: platform API replacement output.
- `state_model_mapping_path`: state/model mapping output.
- `dependency_resolution_path`: dependency-resolution output.
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

1. Verify changed files are in valid target modules/source sets.
2. Detect Android-only imports or APIs in shared source sets.
3. Verify expect/actual declarations and actual implementations for declared targets.
4. Detect duplicate or conflicting platform implementations.
5. Route findings to the responsible implementation node.

## Required Outputs

- `source_set_placement_guard.json`
- `source_set_placement_guard.md`

```json
{
  "status": "passed | failed | blocked",
  "node": "source-set-placement-guard",
  "checked_files": [],
  "violations": [
    {
      "path": "",
      "type": "wrong_source_set | android_api_in_common | missing_actual | duplicate_actual | unknown",
      "message": "",
      "route_to_node": "",
      "evidence": []
    }
  ],
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
  "status": "passed | failed | blocked",
  "node": "source-set-placement-guard",
  "output_files": [
    "<output_dir>/source_set_placement_guard.json",
    "<output_dir>/source_set_placement_guard.md"
  ],
  "blocking_gaps": []
}
```
