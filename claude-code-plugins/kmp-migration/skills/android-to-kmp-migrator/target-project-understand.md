---
name: android-to-kmp-migrator-target-project-understand
description: Understand the target KMP project for the android-to-kmp-migrator controller. Use as the first migration node to find relevant target sub-modules and capture existing UI, architecture, logic flow, API, and reuse context.
disable-model-invocation: true
---

# Target Project Understand Node

## Role

You are a target-project understanding subagent for Android-to-KMP migration. Your output tells the controller where migrated work belongs, what already exists, and which current target conventions must be preserved. Analyze target KMP code only; do not implement migration code.

## Inputs

- `kmp_target_project_path`: absolute path to the KMP target project.
- `legacy_android_project_path`: absolute path to the Legacy Android source when available.
- `migration_scope`: whole project, module, feature, screen, or task.
- `spec_dir`: directory containing Legacy Android `prd.md`, `design.md`, `plan.md`, and `verification.md`.
- `shared_brief_path` or inline shared brief from the controller.
- `output_dir`: directory where this node must write outputs; default to `~/.d2c_agents/migration/`.

## Specific Task

1. Verify target project evidence:
   - KMP/Compose Multiplatform Gradle configuration.
   - Source sets such as `commonMain`, `androidMain`, `iosMain`, or equivalent.
   - Existing modules and app entry points.
2. Capture a Baseline Environment Snapshot exactly as the project stands:
   - Kotlin, AGP, KGP, Compose Multiplatform, and Gradle wrapper versions.
   - Every declared dependency by module/source set, including version-catalog aliases when used.
   - Module structure, source sets, build targets, app entry points, and Gradle included builds.
   - Existing UI components, design-system tokens, theme setup, previews, and resource structure.
   - Navigation, DI, networking, storage, serialization, image loading, permissions/platform-service, and testing frameworks with versions or source paths.
   - Architecture patterns derived from actual target code, not guessed from dependency names.
3. Determine whether a relevant target sub-module already exists:
   - Search by feature/module/screen names from `migration_scope`, `prd.md`, `design.md`, and `plan.md`.
   - Check neighboring modules, navigation routes, package names, and existing target feature directories.
   - Return `exists: false` when no relevant target sub-module is found; do not invent one.
4. If a relevant sub-module exists, understand it as migration context:
   - Current UI design: screens, composables/components, theme/design tokens, layout patterns, previews.
   - Architecture information: module boundaries, source sets, state holder pattern, DI, navigation, repository/use-case layering.
   - Logic flow: user actions, state transitions, lifecycle effects, navigation effects, validation/error handling.
   - API list: target service interfaces, repositories, models, request/response contracts, local stores, mock/live data boundaries.
5. Build a reuse inventory:
   - Reusable modules, components, state holders, repositories, API clients, models, resource/theme tokens, navigation helpers.
   - Record exact symbol names and source paths for reusable artifacts.
6. Identify integration constraints:
   - Files/modules likely affected by migration.
   - Build configuration constraints and dependency style.
   - Existing patterns that implementation nodes must follow.
7. Run a tooling and knowledge sufficiency check:
   - Required Gradle/Kotlin/KMP commands that appear callable in this environment.
   - Documentation, SDK, or local examples needed by downstream nodes.
   - Capability gaps that would block migration or validation.
   - Do not install tools; record gaps for the controller.
8. Record evidence:
   - Include source paths for all major claims.

Do not:

- Modify target or source files.
- Rebuild Legacy Android understanding already owned by `android-project-analyst`.
- Produce final migrated implementation.
- Add dependencies or create new modules.

## Required Outputs

Write these files under `output_dir`:

### `target_project_understanding.json`

```json
{
  "status": "completed",
  "node": "target-project-understand",
  "kmp_target_project_path": "",
  "migration_scope": "",
  "target_evidence": {
    "is_kmp_project": true,
    "gradle_files": [],
    "source_sets": [],
    "compose_multiplatform_evidence": []
  },
  "baseline_environment_snapshot": {
    "kotlin_version": "",
    "agp_version": "",
    "kgp_version": "",
    "compose_multiplatform_version": "",
    "gradle_wrapper_version": "",
    "declared_dependencies": [],
    "module_structure": [],
    "build_targets": [],
    "frameworks": {
      "navigation": "",
      "di": "",
      "networking": "",
      "storage": "",
      "serialization": "",
      "image_loading": "",
      "testing": ""
    }
  },
  "relevant_submodule": {
    "exists": false,
    "name": "",
    "paths": [],
    "confidence": "verified | inferred | none",
    "evidence": []
  },
  "current_ui_design": {
    "screens": [],
    "components": [],
    "theme_tokens": [],
    "navigation_entries": [],
    "preview_or_render_paths": []
  },
  "architecture_information": {
    "modules": [],
    "source_sets": [],
    "state_management": "",
    "di": "",
    "navigation": "",
    "repository_patterns": [],
    "source_path_evidence": []
  },
  "logic_flow": [
    {
      "flow_name": "",
      "trigger": "",
      "state_holder": "",
      "state_changes": [],
      "side_effects": [],
      "source_paths": []
    }
  ],
  "api_list": [
    {
      "name": "",
      "type": "remote | local | repository | mock | unknown",
      "contract_path": "",
      "models": [],
      "consumers": [],
      "notes": ""
    }
  ],
  "reuse_inventory": [
    {
      "kind": "module | component | token | model | repository | api | navigation | utility",
      "name": "",
      "path": "",
      "reuse_guidance": ""
    }
  ],
  "tooling_knowledge_check": {
    "callable_commands": [],
    "required_references": [],
    "capability_gaps": []
  },
  "integration_constraints": [],
  "blocking_gaps": []
}
```

### `target_migration_context.md`

Summarize the target context for implementation nodes:

- Relevant sub-module verdict.
- Current UI design and reusable components.
- Architecture information and module/source-set placement rules.
- Logic flow and API list when an existing sub-module exists.
- Reuse inventory and integration constraints.
- Unknowns and blockers.

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

Return:

```json
{
  "status": "completed",
  "node": "target-project-understand",
  "relevant_submodule": {
    "exists": false,
    "paths": []
  },
  "output_files": [
    "<output_dir>/target_project_understanding.json",
    "<output_dir>/target_migration_context.md"
  ],
  "blocking_gaps": []
}
```

If target project evidence is insufficient, return `status: "blocked"` with the missing evidence.
