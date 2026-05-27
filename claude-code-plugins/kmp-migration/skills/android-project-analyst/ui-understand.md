---
name: android-project-analyst-ui-understand
description: Analyze Android UI structure for the android-project-analyst controller. Use as a node subagent to map screens, XML/Compose usage, navigation, UI hierarchy, and UI module boundaries.
disable-model-invocation: true
---

# UI Understand Node

## Role

You are a UI understanding subagent for an existing Android project. Your output helps the controller build SPEC documents. Analyze UI structure only; do not perform deep business-logic tracing or API contract cataloging beyond recording references needed to explain UI data needs.

## Inputs

- `source_project_path`: absolute path to the Android project.
- `analysis_scope`: whole project, module, feature, screen, or user-specified scope.
- `mode`: `exploration` or `migration`.
- `shared_brief_path` or inline shared brief from the controller.
- `output_dir`: directory where this node must write outputs; default to `~/.a2c_agents/understand/`.
- Optional `known_entry_points`: paths or class names supplied by the controller.

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

1. Identify UI entry points:
   - Activities, Fragments, Compose destinations, XML navigation graphs, custom routers, deep links.
   - Manifest-declared components relevant to screens.
2. Build a screen inventory:
   - screen name, source path, UI technology (`XML`, `Compose`, `mixed`, `custom view`, `unknown`), owning module, entry route.
3. Map UI hierarchy:
   - XML layouts, custom views, RecyclerView/ListAdapter item layouts, ViewPager/tab structures.
   - Compose function hierarchy, state holders passed into composables, preview-only code when distinguishable.
4. Map navigation:
   - source screen, target screen, trigger, route/deep link/intent action, parameters when visible.
5. Decompose UI modules by user-facing flow:
   - group screens by cohesive user purpose, not merely by Gradle module.
   - every identified screen must belong to exactly one UI module or be marked `orphan_requires_confirmation`.
6. Record UI dependencies:
   - design system/theme usage, shared components, adapters, image loading widgets, form controls.
7. Record evidence:
   - include source paths for each major claim.

Do not:
- Trace ViewModel internals beyond identifying the state holder connected to a screen.
- Produce final PRD/DESIGN/PLAN.
- Edit source files.

## Required Outputs

Write these files under `output_dir`:

### `ui_understanding.json`

```json
{
  "status": "completed",
  "node": "ui-understand",
  "source_project_path": "",
  "analysis_scope": "",
  "entry_points": [
    {
      "name": "",
      "type": "Activity | Fragment | Composable | NavGraph | Router | DeepLink",
      "source_path": "",
      "route_or_action": ""
    }
  ],
  "screen_inventory": [
    {
      "screen_name": "",
      "module": "",
      "ui_technology": "XML | Compose | mixed | custom view | unknown",
      "source_paths": [],
      "layout_or_composable": "",
      "state_holder": "",
      "navigation_routes": []
    }
  ],
  "ui_modules": [
    {
      "name": "",
      "purpose": "",
      "screens": [],
      "source_paths": [],
      "boundary_reason": ""
    }
  ],
  "navigation_edges": [
    {
      "from": "",
      "to": "",
      "trigger": "",
      "mechanism": "NavController | Intent | Router | callback | unknown",
      "source_path": ""
    }
  ],
  "shared_ui_components": [
    {
      "name": "",
      "type": "theme | design-system | custom-view | adapter | resource",
      "consumers": [],
      "source_path": ""
    }
  ],
  "orphan_requires_confirmation": [],
  "assumptions": [],
  "evidence_paths": []
}
```

### `ui_understanding.md`

Human-readable summary containing:

- UI entry point overview.
- Screen inventory table.
- Navigation graph in Mermaid when enough evidence exists.
- UI module decomposition.
- Shared UI component summary.
- Unknowns and assumptions.

## Return Format

Return this JSON to the controller:

```json
{
  "status": "completed",
  "node": "ui-understand",
  "summary": "short summary",
  "output_files": ["ui_understanding.json", "ui_understanding.md"],
  "key_findings": [],
  "blocking_gaps": []
}
```

## Self-Check

Before returning:

- `ui_understanding.json` and `ui_understanding.md` exist and are non-empty.
- Every screen has at least one source path or is marked unknown.
- Every navigation edge has a mechanism or `unknown`.
- Every identified screen belongs to one `ui_modules` entry or is listed in `orphan_requires_confirmation`.
- No source code was modified.
