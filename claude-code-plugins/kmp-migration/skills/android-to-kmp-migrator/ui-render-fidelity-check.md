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
- `output_dir`: directory where this node must write outputs.

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
