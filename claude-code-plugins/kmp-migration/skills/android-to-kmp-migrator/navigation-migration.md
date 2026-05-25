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
- `output_dir`: directory where this node must write outputs; default to `~/.d2c_agents/migration/`.

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
