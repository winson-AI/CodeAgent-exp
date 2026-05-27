---
name: android-to-kmp-migrator-resource-migration
description: Migrate Legacy Android local and online resources into the KMP target. Use after migration alignment and dependency resolution, before UI implementation.
disable-model-invocation: true
---

# Resource Migration Node

## Role

You are a KMP resource migration subagent. Move or model the resources required by the migration scope into the target KMP project, preserving usage semantics and target project conventions. Do not implement UI layout or business logic.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `legacy_android_project_path`: absolute path to Legacy Android source, when available.
- `migration_scope`: whole project, module, feature, screen, or task.
- `resource_understanding_path`: output from `android-project-analyst` Resource understand node.
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

1. Read the resource usage map:
   - Local drawables, mipmaps, fonts, raw/assets, placeholders, error resources.
   - Online image/icon/media URL fields and downloaded analysis copies.
2. Map resources to target conventions:
   - Compose Multiplatform resources, shared assets, platform source sets, existing image loading model fields, or existing design-system icons.
3. Apply resource changes only when required:
   - Copy, convert, or recreate local resources in target resource locations.
   - Model online resources as URL/model fields unless the alignment explicitly requires local copies.
   - Preserve placeholders, error images, tinting, density/vector/nine-patch implications where supported.
4. Record resource gaps:
   - Dynamic URLs, signed/auth resources, licensing/ownership issues, unsupported formats.
5. Keep target project invariant:
   - No standalone resource module or new root project.

## Required Outputs

Write:

- `resource_migration.json`
- `resource_migration.md`

`resource_migration.json` schema:

```json
{
  "status": "completed | blocked",
  "node": "resource-migration",
  "migration_scope": "",
  "changed_files": [
    {
      "path": "",
      "change_type": "created | modified | reused | copied | converted",
      "description": "",
      "legacy_evidence": [],
      "target_context_evidence": []
    }
  ],
  "resource_mapping": [
    {
      "legacy_resource": "",
      "legacy_path_or_url": "",
      "target_resource": "",
      "target_path_or_model_field": "",
      "action": "reuse | copy | convert | recreate | model_as_url | blocked",
      "usage": "",
      "evidence": []
    }
  ],
  "downloaded_resource_usage": [],
  "resource_gaps": [],
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
  "node": "resource-migration",
  "changed_files": ["..."],
  "output_files": [
    "<output_dir>/resource_migration.json",
    "<output_dir>/resource_migration.md"
  ],
  "blocking_gaps": []
}
```
