---
name: android-to-kmp-migrator-prd-completion-check
description: Check migrated KMP implementation against PRD, raw user task, SPEC, and upstream node outputs for the android-to-kmp-migrator controller. Use after UI/dataflow implementation and guard/parity/fidelity/build checks, before migration-report generation.
disable-model-invocation: true
---

# PRD Completion Check Node

## Role

You are a migration completion-check subagent. Verify that the target implementation satisfies the PRD, raw user task, Legacy Android SPEC, target context, and migration node outputs. Your primary output is a readiness verdict and actionable gap report for controller re-dispatch.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `legacy_android_project_path`: absolute path to Legacy Android source, when available.
- `migration_scope`: whole project, module, feature, screen, or task.
- `raw_user_task`: original user request or path to it.
- `prd_path`: PRD/SPEC product requirements.
- `design_path`: DESIGN/SPEC architecture, UI, resources, data flow, API, and logic.
- `plan_path`: PLAN/SPEC migration plan.
- `verification_path`: SPEC verification report.
- `target_project_understanding_path`: output from `Target project understand`.
- `migration_alignment_path`: output from `Migration alignment`.
- `dependency_resolution_path`: output from `Dependency resolution`.
- `theme_design_system_mapping_path`: output from `Theme design-system mapping`.
- `resource_migration_path`: output from `Resource migration`.
- `navigation_migration_path`: output from `Navigation migration`.
- `platform_api_replacement_path`: output from `Platform API replacement`.
- `state_model_mapping_path`: output from `State model mapping`.
- `ui_impl_result_path`: output from `UI mockup implementation`.
- `dataflow_logic_impl_result_path`: output from `Dataflow logic implementation`.
- `module_node_review_paths`: outputs from `Module/node migration review`.
- `module_node_fix_paths`: outputs from `Module/node migration fix`, when fixes were needed.
- `source_set_placement_guard_path`: output from `Source set placement guard`.
- `api_contract_parity_path`: output from `API contract parity`.
- `ui_render_fidelity_check_path`: output from `UI render fidelity check`.
- `incremental_build_check_path`: output from `Incremental build check`.
- `changed_files`: changed files from implementation nodes.
- `output_dir`: directory where this node must write outputs.

## Specific Task

1. Build a requirement checklist:
   - PRD user-facing requirements.
   - Raw user task requirements.
   - DESIGN UI/resource/architecture/data/API/logic obligations.
   - PLAN implementation and validation tasks.
2. Verify UI completion:
   - Required screens, components, layout states, resources, navigation surfaces, and visible interactions.
   - Referenced Legacy Android resources are implemented, reused, modeled, or explicitly blocked.
3. Verify architecture and target integration:
   - File/module/source-set placement.
   - Reuse of existing target sub-module/components/interfaces when available.
   - DI, navigation, state holder, repository/API patterns align with target conventions.
4. Verify data/API behavior:
   - Models, repositories, APIs, local stores, loading/empty/error behavior, cache/pagination/refresh behavior.
   - API names and data contracts match upstream evidence or are marked as gaps.
5. Verify logic/control flow:
   - User actions, lifecycle flows, validation, feature flags, permissions, navigation effects, and side effects.
6. Inspect changed files for incomplete implementation markers:
   - `TODO`, `FIXME`, placeholder stubs, sample-only data in production paths, unimplemented branches.
7. Verify module/node review-fix readiness:
   - Every changed preparation, UI, dataflow/logic, or module slice has an approved latest review.
   - Every fix output was followed by a re-review for the same module or node scope.
   - Any unresolved review finding is routed to the responsible node.
8. Verify migration invariants:
   - No Android-only APIs leaked into shared source sets.
   - expect/actual declarations are complete for declared targets.
   - Dependency changes, if any, match dependency-resolution approvals.
   - No migrated sub-module became a standalone project with its own root Gradle/settings/wrapper.
   - Cross-sub-module integration is wired through existing DI, navigation, theme, and app entry points.
9. Verify guard/parity/fidelity/build reports:
   - Source-set placement guard has passed or clear rerun requests exist.
   - API contract parity has passed or clear rerun requests exist.
   - UI render fidelity has passed or clear rerun requests exist.
   - Incremental build check has passed or clear rerun requests exist.
10. Produce actionable gaps:
   - For each gap, identify the responsible node to re-run: `migration-alignment`, `dependency-resolution`, `theme-design-system-mapping`, `resource-migration`, `navigation-migration`, `platform-api-replacement`, `state-model-mapping`, `ui-mockup-implementation`, `dataflow-logic-implementation`, `module-node-migration-review`, `module-node-migration-fix`, `source-set-placement-guard`, `api-contract-parity`, `ui-render-fidelity-check`, or `incremental-build-check`.
   - Include exact expected input/context for the re-run.
11. Decide readiness:
   - `ready_for_validation`: all required migration obligations are satisfied enough for `kmp-test-validator`.
   - `needs_rerun`: gaps are clear and should be routed back to implementation nodes.
   - `blocked`: required source/target/SPEC evidence is missing or contradictory.

Do not:

- Mark completion based only on changed-file presence.
- Ignore raw user task requirements that are not repeated in PRD.
- Fix broad implementation gaps directly; return a node re-dispatch report.
- Declare validation passed; validation belongs to `kmp-test-validator`.

## Required Outputs

Write these files under `output_dir`:

### `prd_completion_check.json`

```json
{
  "status": "ready_for_validation | needs_rerun | blocked",
  "node": "prd-completion-check",
  "migration_scope": "",
  "requirement_coverage": [
    {
      "requirement_id": "",
      "source": "raw_user_task | prd | design | plan",
      "requirement": "",
      "evidence": [],
      "status": "covered | gap | blocked"
    }
  ],
  "ui_completion": {
    "status": "covered | gap | blocked",
    "evidence": [],
    "gaps": []
  },
  "resource_completion": {
    "status": "covered | gap | blocked",
    "evidence": [],
    "gaps": []
  },
  "architecture_completion": {
    "status": "covered | gap | blocked",
    "evidence": [],
    "gaps": []
  },
  "data_api_completion": {
    "status": "covered | gap | blocked",
    "evidence": [],
    "gaps": []
  },
  "logic_completion": {
    "status": "covered | gap | blocked",
    "evidence": [],
    "gaps": []
  },
  "migration_invariants": {
    "no_android_only_api_in_common": "pass | gap | blocked",
    "expect_actual_complete": "pass | gap | blocked",
    "dependency_gate_respected": "pass | gap | blocked",
    "single_project_invariant": "pass | gap | blocked",
    "cross_module_integration": "pass | gap | blocked"
  },
  "module_node_review_status": [],
  "incomplete_markers": [
    {
      "path": "",
      "marker": "",
      "line_or_context": "",
      "severity": "blocker | warning"
    }
  ],
  "rerun_requests": [
    {
      "node": "migration-alignment | dependency-resolution | theme-design-system-mapping | resource-migration | navigation-migration | platform-api-replacement | state-model-mapping | ui-mockup-implementation | dataflow-logic-implementation | module-node-migration-review | module-node-migration-fix | source-set-placement-guard | api-contract-parity | ui-render-fidelity-check | incremental-build-check",
      "reason": "",
      "required_inputs": [],
      "expected_output": ""
    }
  ],
  "blocking_gaps": []
}
```

### `prd_completion_report.md`

Summarize:

- Readiness verdict.
- Requirement coverage matrix.
- UI/resource/architecture/data/API/logic completion.
- Incomplete markers found.
- Module/node review-fix status.
- Migration invariant results.
- Guard/parity/fidelity/build-check results.
- Re-run requests or blockers.
- Readiness signal for the dedicated `migration-report` node.

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
  "status": "ready_for_validation | needs_rerun | blocked",
  "node": "prd-completion-check",
  "output_files": [
    "<output_dir>/prd_completion_check.json",
    "<output_dir>/prd_completion_report.md"
  ],
  "rerun_requests": [],
  "blocking_gaps": []
}
```
