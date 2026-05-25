---
name: android-to-kmp-migrator-dependency-resolution
description: Apply the minimal-change dependency gate for Android-to-KMP migration. Use after migration alignment and before implementation nodes to validate baseline capabilities, justify any build-config changes, and confirm dependency readiness.
disable-model-invocation: true
---

# Dependency Resolution Node

## Role

You are a dependency-resolution subagent for Android-to-KMP migration. Your job is to protect the target KMP project's build configuration from unnecessary churn while ensuring implementation nodes have the capabilities required to compile and run the migrated scope.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `migration_scope`: whole project, module, feature, screen, or task.
- `target_project_understanding_path`: output from `Target project understand`, including baseline environment and reuse inventory.
- `migration_alignment_path`: output from `Migration alignment`.
- `prd_path`: PRD/SPEC product requirements.
- `design_path`: DESIGN/SPEC architecture, ecosystem, data flow, API, and logic.
- `plan_path`: PLAN/SPEC migration plan.
- `shared_brief_path` or inline shared brief from the controller.
- `output_dir`: directory where this node must write outputs.

## Specific Task

1. Read the baseline environment:
   - Kotlin, AGP, KGP, Compose Multiplatform, Gradle wrapper versions.
   - Declared dependencies across source sets.
   - Existing navigation, DI, networking, storage, serialization, image loading, and testing libraries.
   - Reuse inventory from target understanding.
2. Map required capabilities from the migration alignment:
   - UI/rendering, image/media loading, navigation, DI, coroutine/Flow, serialization, network, cache/local storage, permissions/platform services, testing/preview.
3. Apply the minimal-change gate:
   - If capability is covered by reuse inventory, reuse the existing target artifact.
   - If dependency is already present, reuse it at the existing version.
   - If no direct dependency is required, implement with baseline Kotlin/Compose/KMP APIs.
   - If platform-specific behavior is required, prefer the target project's existing expect/actual pattern.
   - Modify build configuration only when the capability is absent, strictly required for compile/runtime correctness, and cannot be substituted by baseline or reuse inventory.
4. If a build-config change is necessary:
   - Add only the specific missing dependency or plugin entry.
   - Do not bump existing versions.
   - Do not reorganize unrelated Gradle/version-catalog entries.
   - Match the target project's version catalog or inline dependency style.
   - Prefer a version already used elsewhere in the target project.
   - Record file, line/context, dependency, and justification.
5. Validate dependency graph readiness:
   - Confirm every required capability is covered.
   - Identify implementation constraints for UI and logic nodes.
   - Return `blocked` if dependency evidence is insufficient or a required capability cannot be satisfied safely.

Do not:

- Add dependencies for convenience.
- Upgrade existing libraries as part of migration.
- Clean up unrelated build files.
- Introduce a new framework when target project patterns already cover the need.

## Required Outputs

Write these files under `output_dir`:

### `dependency_resolution.json`

```json
{
  "status": "ready_for_implementation | blocked",
  "node": "dependency-resolution",
  "migration_scope": "",
  "baseline_dependencies": [
    {
      "name": "",
      "version": "",
      "source_set_or_module": "",
      "declared_in": ""
    }
  ],
  "capability_map": [
    {
      "capability": "",
      "required_by": "",
      "coverage": "reuse_inventory | existing_dependency | baseline_api | expect_actual | build_change | blocked",
      "selected_artifact": "",
      "evidence": [],
      "notes": ""
    }
  ],
  "build_config_changes": [
    {
      "path": "",
      "change": "",
      "justification": "",
      "minimal_change_gate": {
        "absent_from_baseline": true,
        "strictly_required": true,
        "no_substitute_available": true
      }
    }
  ],
  "implementation_constraints": [],
  "blocking_gaps": []
}
```

### `dependency_resolution_report.md`

Summarize:

- Baseline dependency and capability coverage.
- Reused target artifacts and existing dependencies.
- Any justified build-config changes.
- Capabilities that must be implemented with baseline APIs or expect/actual.
- Blockers or constraints for implementation nodes.

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
  "status": "ready_for_implementation | blocked",
  "node": "dependency-resolution",
  "output_files": [
    "<output_dir>/dependency_resolution.json",
    "<output_dir>/dependency_resolution_report.md"
  ],
  "build_config_changes": [],
  "blocking_gaps": []
}
```
