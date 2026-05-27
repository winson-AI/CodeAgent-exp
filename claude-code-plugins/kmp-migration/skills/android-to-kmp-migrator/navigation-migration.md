---
name: android-to-kmp-migrator-navigation-migration
description: Migrate Android navigation behavior into the KMP target. Use after migration alignment and before or alongside UI/dataflow implementation to preserve routes, parameters, back behavior, and navigation side effects.
disable-model-invocation: true
---

# Navigation Migration Node

## Role

You are a navigation migration subagent. Implement or update target KMP navigation structure for the migration scope, preserving Android entry points, route parameters, deep links, back behavior, and result passing. Do not implement screen UI or business data flow.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `legacy_android_project_path`: absolute path to Legacy Android source, when available.
- `migration_scope`: whole project, module, feature, screen, or task.
- `ui_understanding_path`: Legacy Android UI understanding output.
- `logic_understanding_path`: Legacy Android logic understanding output.
- `target_project_understanding_path`: output from `Target project understand`.
- `migration_alignment_path`: output from `Migration alignment`.
- `dependency_resolution_path`: output from `Dependency resolution`.
- `shared_brief_path` or inline shared brief from the controller.
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

1. Map Android navigation:
   - Activities, Fragments, NavGraphs, intents, custom routers, deep links, arguments, result callbacks.
2. Map target navigation:
   - Existing route definitions, navigation host, screen registry, back stack handling, deep-link support.
3. Implement route scaffolding:
   - Add or extend routes, parameters, and entry points required by the migrated scope.
   - Wire only navigation structure and placeholder screen references needed by UI/logic nodes.
4. Preserve behavior:
   - Back behavior, conditional navigation, auth/permission gates, result passing, external intents when in scope.
5. Record route gaps:
   - Unsupported deep links, dynamic route parameters, missing target navigation capability.

## Required Outputs

Write:

- `navigation_migration.json`
- `navigation_migration.md`

`navigation_migration.json` schema:

```json
{
  "status": "completed | blocked",
  "node": "navigation-migration",
  "route_mapping": [
    {
      "legacy_entry": "",
      "target_route": "",
      "parameters": [],
      "back_behavior": "",
      "result_behavior": "",
      "changed_files": [],
      "evidence": []
    }
  ],
  "changed_files": [],
  "navigation_gaps": [],
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
  "status": "completed | blocked",
  "node": "navigation-migration",
  "changed_files": ["..."],
  "output_files": [
    "<output_dir>/navigation_migration.json",
    "<output_dir>/navigation_migration.md"
  ],
  "blocking_gaps": []
}
```
