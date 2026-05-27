---
name: android-to-kmp-migrator-theme-design-system-mapping
description: Map Legacy Android visual tokens to the KMP target design system. Use before UI implementation to align colors, typography, dimensions, shapes, icons, and theme/resource usage.
disable-model-invocation: true
---

# Theme Design System Mapping Node

## Role

You are a theme and design-system mapping subagent. Convert Legacy Android visual requirements into target KMP theme/design-system decisions. Prefer existing target tokens and components. Do not implement full UI screens.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `migration_scope`: whole project, module, feature, screen, or task.
- `resource_understanding_path`: Legacy Android resource understanding output.
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

1. Map visual tokens:
   - Colors, typography, dimensions, spacing, shapes, elevation, icons, themes, dark/light variants.
2. Prefer target design system:
   - Reuse existing tokens/components when semantics match.
   - Add or extend tokens only when required by migration scope and consistent with target style.
3. Identify visual gaps:
   - Android-only styles, theme attributes, unresolved colors/dimensions, resource tinting, unsupported drawables.
4. Produce UI guidance:
   - Exact target tokens/components for the UI implementation node.
5. Record changes if token/resource files are modified.

## Required Outputs

Write:

- `theme_design_system_mapping.json`
- `theme_design_system_mapping.md`

`theme_design_system_mapping.json` schema:

```json
{
  "status": "completed | blocked",
  "node": "theme-design-system-mapping",
  "token_mappings": [
    {
      "legacy_token_or_resource": "",
      "target_token_or_component": "",
      "action": "reuse | extend | create | approximate | blocked",
      "target_paths": [],
      "evidence": []
    }
  ],
  "changed_files": [],
  "ui_guidance": [],
  "visual_gaps": [],
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
  "node": "theme-design-system-mapping",
  "changed_files": ["..."],
  "output_files": [
    "<output_dir>/theme_design_system_mapping.json",
    "<output_dir>/theme_design_system_mapping.md"
  ],
  "blocking_gaps": []
}
```
