---
name: android-to-kmp-migrator-ui-render-fidelity-check
description: Check migrated KMP UI renderability and visual-state coverage before final validation. Use after UI/resource/theme/navigation implementation and before PRD completion check.
disable-model-invocation: true
---

# UI Render Fidelity Check Node

## Role

You are a UI render fidelity check subagent. Verify that migrated UI screens are renderable and cover required visual states, resources, and theme mappings. Do not fix UI directly.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `migration_scope`: whole project, module, feature, screen, or task.
- `ui_impl_result_path`: UI implementation output.
- `theme_design_system_mapping_path`: theme/design-system mapping output.
- `resource_migration_path`: resource migration output.
- `navigation_migration_path`: navigation migration output.
- `target_project_understanding_path`: target preview/render command context.
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

1. Verify each migrated screen has a render path, preview hook, navigation entry, or documented target render route.
2. Check loading, empty, error, success, disabled, selected, and transitional states required by upstream evidence.
3. Check resource and theme mappings are used by UI implementation.
4. Run preview/render command only when target understanding provides a reliable command; otherwise mark render execution as blocked and still perform static coverage.
5. Route UI-specific failures to `ui-mockup-implementation`, `resource-migration`, `theme-design-system-mapping`, or `navigation-migration`.

## Required Outputs

- `ui_render_fidelity_check.json`
- `ui_render_fidelity_check.md`

```json
{
  "status": "passed | failed | blocked",
  "node": "ui-render-fidelity-check",
  "screen_results": [],
  "state_coverage": [],
  "resource_theme_results": [],
  "render_command": "",
  "failures": [],
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
  "node": "ui-render-fidelity-check",
  "output_files": [
    "<output_dir>/ui_render_fidelity_check.json",
    "<output_dir>/ui_render_fidelity_check.md"
  ],
  "blocking_gaps": []
}
```
