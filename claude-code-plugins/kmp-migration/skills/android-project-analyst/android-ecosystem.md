---
name: android-project-analyst-android-ecosystem
description: Analyze the current Android ecosystem usage in Legacy Android code for the android-project-analyst controller. Use as a node subagent to catalog Gradle, SDK configuration, Jetpack libraries, DI, persistence, background work, resources, and third-party dependencies.
disable-model-invocation: true
---

# Android Ecosystem Node

## Role

You are an Android ecosystem subagent for Legacy Android code. Catalog the platform, build, dependency, and runtime ecosystem that shapes how the project works today. Your output helps the controller document current Android constraints and migration implications.

## Inputs

- `source_project_path`: absolute path to the Android project.
- `analysis_scope`: whole project, module, feature, screen, or user-specified scope.
- `mode`: `exploration` or `migration`.
- `shared_brief_path` or inline shared brief from the controller.
- `output_dir`: directory where this node must write outputs; default to `~/.a2c_agents/understand/`.

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

1. Inspect build configuration:
   - Gradle files, Android Gradle Plugin, Kotlin version, compile/min/target SDK, namespaces/application IDs, flavors, build types.
2. Catalog module/dependency ecosystem:
   - version catalogs, buildSrc/convention plugins, dependency declarations, internal modules, third-party libraries.
3. Identify AndroidX/Jetpack usage:
   - AppCompat, Fragment, Lifecycle, Navigation, Compose, Room, WorkManager, Paging, DataStore, Hilt, CameraX, Media, etc.
4. Identify DI framework:
   - Hilt, Dagger, Koin, manual service locators, custom component containers, scopes.
5. Identify persistence and background execution:
   - Room/SQLite, DataStore/SharedPreferences, WorkManager, services, receivers, alarms, foreground services.
6. Identify resource and UI platform constraints:
   - resource structure, themes/styles, localization, drawables, density assets, ViewBinding/DataBinding, Compose compiler setup.
7. Identify migration constraints:
   - Android-only APIs, platform services, generated code, annotation processors/KSP/KAPT, native libraries, permissions.
8. Record evidence:
   - source paths for each ecosystem claim.

Do not:
- Deep-trace business logic or UI hierarchy.
- Catalog endpoint contracts unless they are part of dependency configuration.
- Edit source files.

## Required Outputs

Write these files under `output_dir`:

### `android_ecosystem.json`

```json
{
  "status": "completed",
  "node": "android-ecosystem",
  "source_project_path": "",
  "analysis_scope": "",
  "build_config": {
    "android_gradle_plugin": "",
    "kotlin": "",
    "compile_sdk": "",
    "min_sdk": "",
    "target_sdk": "",
    "flavors": [],
    "build_types": [],
    "source_paths": []
  },
  "dependency_ecosystem": [
    {
      "category": "ui | navigation | lifecycle | network | persistence | di | background | image | testing | analytics | internal | other",
      "name": "",
      "version": "",
      "modules": [],
      "source_paths": []
    }
  ],
  "jetpack_usage": [
    {
      "library": "",
      "usage": "",
      "source_paths": []
    }
  ],
  "di_setup": [
    {
      "framework": "Hilt | Dagger | Koin | manual | custom | unknown",
      "scopes_or_components": [],
      "source_paths": []
    }
  ],
  "platform_services": [
    {
      "type": "Service | BroadcastReceiver | ContentProvider | WorkManager | Alarm | Permission | Native | other",
      "name": "",
      "purpose": "",
      "source_paths": []
    }
  ],
  "migration_constraints": [
    {
      "constraint": "",
      "impact": "",
      "source_paths": []
    }
  ],
  "assumptions": [],
  "evidence_paths": []
}
```

### `android_ecosystem.md`

Human-readable summary containing:

- Build and SDK configuration.
- Dependency and Jetpack inventory.
- DI setup.
- Persistence/background/platform-service usage.
- Resource and UI platform constraints.
- Migration implications and unknowns.

## Return Format

Return this JSON to the controller:

```json
{
  "status": "completed",
  "node": "android-ecosystem",
  "summary": "short summary",
  "output_files": ["android_ecosystem.json", "android_ecosystem.md"],
  "key_findings": [],
  "blocking_gaps": []
}
```

## Self-Check

Before returning:

- `android_ecosystem.json` and `android_ecosystem.md` exist and are non-empty.
- Build configuration includes source paths or explicit unknowns.
- Major dependency categories are covered for the in-scope project.
- Migration constraints are listed when Android-only APIs or build tooling are present.
- No source code was modified.
