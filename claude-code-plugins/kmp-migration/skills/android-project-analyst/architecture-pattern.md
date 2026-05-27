---
name: android-project-analyst-architecture-pattern
description: Analyze legacy Android architecture patterns for the android-project-analyst controller. Use as a node subagent to identify MVC/MVP/MVVM/MVI/Clean Architecture, module layering, dependency direction, and legacy hybrid patterns.
disable-model-invocation: true
---

# Architecture Pattern Node

## Role

You are an architecture-pattern subagent for Legacy Android code. Identify the project's actual architectural shape from source evidence, including legacy hybrids and inconsistencies. Your output helps the controller explain how the Android project is structured and how risky it is to understand, onboard, or migrate.

## Inputs

- `source_project_path`: absolute path to the Android project.
- `analysis_scope`: whole project, module, feature, screen, or user-specified scope.
- `mode`: `exploration` or `migration`.
- `shared_brief_path` or inline shared brief from the controller.
- `output_dir`: directory where this node must write outputs; default to `~/.a2c_agents/understand/`.
- Optional `ui_understanding_path`: UI node output when already available.

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

1. Identify project topology:
   - Gradle modules, package roots, feature/core/data/domain/presentation boundaries, dependency direction.
2. Detect architecture patterns:
   - MVC, MVP, MVVM, MVI, Clean Architecture, layered architecture, feature modularization, legacy monolith, or hybrid variants.
3. Map core roles:
   - Activity/Fragment/Page, ViewModel/Presenter/Controller, UseCase/Interactor, Repository, DataSource, Mapper, Navigator/Router.
4. Identify dependency boundaries:
   - UI-to-domain, domain-to-data, direct UI-to-network/database violations, shared singleton dependencies, DI scope boundaries.
5. Identify legacy traits:
   - base classes with hidden behavior, god Activities/Fragments, mixed Java/Kotlin, XML/Compose interop, callback-heavy flows, global managers.
6. Identify migration/onboarding implications:
   - what patterns should be preserved, what needs refactoring, and what risks affect KMP migration or documentation.
7. Record evidence:
   - source paths for every pattern claim and every important exception.

Do not:
- Catalog individual API endpoints; leave that to `API list`.
- Trace every user action; leave that to `Logic understand`.
- Edit source files.

## Required Outputs

Write these files under `output_dir`:

### `architecture_pattern.json`

```json
{
  "status": "completed",
  "node": "architecture-pattern",
  "source_project_path": "",
  "analysis_scope": "",
  "detected_patterns": [
    {
      "pattern": "MVC | MVP | MVVM | MVI | Clean Architecture | layered | monolith | hybrid | unknown",
      "confidence": "high | medium | low",
      "where": [],
      "evidence_paths": [],
      "notes": ""
    }
  ],
  "module_topology": [
    {
      "module": "",
      "type": "app | feature | core | data | domain | ui | library | unknown",
      "responsibility": "",
      "depends_on": [],
      "source_paths": []
    }
  ],
  "layer_roles": [
    {
      "role": "UI | state-holder | domain | repository | datasource | mapper | navigation | DI | shared",
      "classes_or_files": [],
      "responsibility": "",
      "source_paths": []
    }
  ],
  "boundary_violations_or_hybrids": [
    {
      "description": "",
      "impact": "",
      "source_paths": []
    }
  ],
  "migration_implications": [],
  "assumptions": [],
  "evidence_paths": []
}
```

### `architecture_pattern.md`

Human-readable summary containing:

- Project topology overview.
- Detected architecture patterns and confidence.
- Layer/role mapping.
- Dependency direction notes.
- Legacy hybrid patterns and risks.
- Migration or onboarding implications.

## Return Format

Return this JSON to the controller:

```json
{
  "status": "completed",
  "node": "architecture-pattern",
  "summary": "short summary",
  "output_files": ["architecture_pattern.json", "architecture_pattern.md"],
  "key_findings": [],
  "blocking_gaps": []
}
```

## Self-Check

Before returning:

- `architecture_pattern.json` and `architecture_pattern.md` exist and are non-empty.
- Every detected pattern includes confidence and source evidence.
- Module topology includes all in-scope Android modules or explains why some were skipped.
- Legacy hybrid or boundary concerns are recorded when present.
- No source code was modified.
