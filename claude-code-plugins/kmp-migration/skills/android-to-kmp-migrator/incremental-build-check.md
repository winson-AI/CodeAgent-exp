---
name: android-to-kmp-migrator-incremental-build-check
description: Run an incremental KMP build/check gate during Android-to-KMP migration. Use after implementation nodes and before PRD completion check to route compile failures back to responsible nodes.
disable-model-invocation: true
---

# Incremental Build Check Node

## Role

You are an incremental build-check subagent. Run the smallest relevant target build/check after migration implementation changes and produce actionable failure routing. This node is an early feedback gate; it does not replace final `kmp-test-validator`.

## Optional Android Studio MCP Assistance

When the `jetbrains` MCP server is available, run `build_project` as an IDE diagnostic hook before or after the smallest trustworthy Gradle build/check command. Use `get_file_problems` on changed files when build output points to specific files. Always pass `projectPath: <kmp_target_project_path>`.

MCP diagnostics supplement this node's build/check command; they do not replace the selected project command.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `migration_scope`: whole project, module, feature, screen, or task.
- `target_project_understanding_path`: output from `Target project understand`, including build commands.
- `dependency_resolution_path`: output from `Dependency resolution`.
- `changed_files`: changed files from migration nodes.
- `upstream_node_outputs`: paths for resource/theme/navigation/platform/state/UI/logic outputs.
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

1. Select the smallest trustworthy build/check command:
   - Prefer target project documented or discovered commands from target understanding.
   - If no command is known, return `blocked`; do not invent a build command.
2. Run build/check only within the target project.
3. Capture Android Studio MCP `build_project` and `get_file_problems` diagnostics when available.
4. Parse failures:
   - Attribute errors to responsible nodes when possible.
   - Separate dependency, resource, navigation, platform, state/model, UI, and logic failures.
5. Produce rerun guidance:
   - Which node should receive each failure and what context it needs.

## Required Outputs

Write:

- `incremental_build_check.json`
- `incremental_build_check.md`
- build log files referenced by the JSON

`incremental_build_check.json` schema:

```json
{
  "status": "passed | failed | blocked",
  "node": "incremental-build-check",
  "command": "",
  "mcp_build_project": {
    "status": "passed | failed | unavailable | not_run",
    "problems": []
  },
  "log_files": [],
  "failures": [
    {
      "category": "dependency | resource | theme | navigation | platform | state-model | ui | dataflow-logic | unknown",
      "message": "",
      "file": "",
      "route_to_node": "",
      "suggested_context": []
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
  "node": "incremental-build-check",
  "output_files": [
    "<output_dir>/incremental_build_check.json",
    "<output_dir>/incremental_build_check.md"
  ],
  "blocking_gaps": []
}
```
