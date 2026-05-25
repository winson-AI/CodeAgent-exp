---
name: android-to-kmp-migrator-dataflow-logic-implementation
description: Implement migrated KMP architecture, data flow, API integration, and business logic for the android-to-kmp-migrator controller. Use after UI implementation.
disable-model-invocation: true
---

# Dataflow Logic Implementation Node

## Role

You are a KMP dataflow and logic implementation subagent. Implement the behavior that drives the UI already created by the UI node. Preserve Legacy Android architecture intent, data/API behavior, state transitions, and side effects while fitting the target KMP project's existing patterns.

## Decision Framework

- Prefer capabilities already present in the KMP target project.
- Prefer officially supported KMP libraries and Compose Multiplatform-compatible APIs when dependency-resolution has approved a new dependency.
- When an Android API has no KMP equivalent, use the target project's existing expect/actual pattern or create a minimal expect/actual boundary consistent with the target structure.
- Do not leak Android-only APIs into `commonMain`.
- For platform-specific actuals, provide real Android behavior and a compiling target-appropriate implementation for other declared platforms; unresolved behavior must be reported as a limitation, not hidden behind a generic TODO.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `legacy_android_project_path`: absolute path to Legacy Android source, when available.
- `migration_scope`: whole project, module, feature, screen, or task.
- `prd_path`: PRD/SPEC product requirements.
- `design_path`: DESIGN/SPEC architecture, data flow, API, and logic.
- `plan_path`: PLAN/SPEC migration plan.
- `target_project_understanding_path`: output from `Target project understand`.
- `migration_alignment_path`: output from `Migration alignment`.
- `dependency_resolution_path`: output from `Dependency resolution`.
- `navigation_migration_path`: output from `Navigation migration`.
- `platform_api_replacement_path`: output from `Platform API replacement`.
- `state_model_mapping_path`: output from `State model mapping`.
- `resource_migration_path`: output from `Resource migration`.
- `ui_impl_result_path`: output from `UI mockup implementation`.
- `shared_brief_path` or inline shared brief from the controller.
- `output_dir`: directory where this node must write outputs.

## Specific Task

1. Read upstream context:
   - PRD requirements and raw task.
   - DESIGN architecture, data flow, API, and logic/control flow.
   - PLAN implementation tasks and validation expectations.
   - Target architecture information, logic flow, API list, and reuse inventory.
   - Dependency-resolution capability map and approved build-config constraints.
   - Navigation route scaffolding and result/back behavior.
   - Platform API replacements and expect/actual boundaries.
   - State/model mapping handoff.
   - Resource model fields and migrated resource paths.
   - UI binding surfaces from `ui_impl_result_path`.
2. Review architecture alignment:
   - Match target state management, DI, navigation, source-set layout, repository/use-case patterns, error handling, and coroutine/Flow style.
   - Reuse existing target modules and interfaces whenever they cover the behavior.
3. Implement data flow:
   - Models, mappers, repositories, use cases, caches/local stores, and state propagation.
   - Loading, success, empty, error, pagination, refresh, and retry flows required by PRD/DESIGN.
4. Implement API integration:
   - Target API clients/service interfaces and request/response models.
   - Auth/header/query/body behavior when visible in upstream SPEC/source.
   - Mock/live data boundaries following target conventions.
5. Implement business and control logic:
   - User actions, lifecycle initialization, validation, feature flags, permission gates, navigation effects, and side effects.
   - Bind logic to UI state/callback surfaces from the UI node.
6. Handle platform-specific behavior:
   - Use existing expect/actual patterns when target project has them.
   - Add new expect/actual only when required and consistent with target structure.
7. Preserve single-project integration:
   - Wire into existing DI, navigation, app entry, and module exports identified by alignment.
   - Do not create a standalone root project or duplicate shared infrastructure for the migrated scope.
8. Validate implementation coverage:
   - Cross-check PRD, DESIGN, PLAN, target context, migration alignment, and UI outputs.
   - No TODO placeholders are left as completion output.
   - Verify no Android-only APIs leaked into shared code.
   - Verify expect/actual declarations are complete for declared targets.
9. Record evidence and changed files.

Do not:

- Rewrite UI layout except for small binding adjustments needed by logic.
- Create parallel API/repository/state patterns when target equivalents exist.
- Add dependencies unless the migration alignment explicitly justified the change and no target substitute exists.
- Guess API fields or business rules not backed by SPEC/source evidence.

## Required Outputs

Write these files under `output_dir`:

### `dataflow_logic_impl_result.json`

```json
{
  "status": "completed",
  "node": "dataflow-logic-implementation",
  "migration_scope": "",
  "changed_files": [
    {
      "path": "",
      "change_type": "created | modified | reused",
      "description": "",
      "source_requirement": "",
      "legacy_evidence": [],
      "target_context_evidence": []
    }
  ],
  "architecture_alignment": {
    "state_management": "",
    "di": "",
    "navigation": "",
    "source_sets": [],
    "reused_artifacts": []
  },
  "platform_boundaries": [
    {
      "capability": "",
      "common_declaration": "",
      "actual_implementations": [],
      "status": "complete | blocked"
    }
  ],
  "data_flows": [
    {
      "flow_name": "",
      "source": "",
      "repository_or_use_case": "",
      "state_holder": "",
      "ui_binding": "",
      "error_empty_loading_behavior": "",
      "source_paths": []
    }
  ],
  "api_integrations": [
    {
      "api_name": "",
      "target_contract": "",
      "models": [],
      "consumers": [],
      "auth_or_header_behavior": "",
      "status": "implemented | reused | blocked"
    }
  ],
  "logic_coverage": [
    {
      "requirement": "",
      "trigger": "",
      "handler_or_state_holder": "",
      "state_changes": [],
      "side_effects": [],
      "status": "covered | blocked"
    }
  ],
  "blocking_gaps": []
}
```

### `dataflow_logic_implementation_notes.md`

Summarize:

- Architecture alignment and reused target artifacts.
- Data/API flows implemented.
- Logic/control flows implemented.
- UI binding updates.
- Gaps or assumptions.

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
  "node": "dataflow-logic-implementation",
  "changed_files": ["..."],
  "output_files": [
    "<output_dir>/dataflow_logic_impl_result.json",
    "<output_dir>/dataflow_logic_implementation_notes.md"
  ],
  "blocking_gaps": []
}
```

If behavior cannot be implemented because required source/API/target evidence is missing, return `status: "blocked"` with exact missing evidence.
