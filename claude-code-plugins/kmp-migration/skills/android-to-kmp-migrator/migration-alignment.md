---
name: android-to-kmp-migrator-migration-alignment
description: Align Legacy Android SPEC/raw understanding with target KMP project context for the android-to-kmp-migrator controller. Use after target project understanding and before implementation nodes.
disable-model-invocation: true
---

# Migration Alignment Node

## Role

You are a migration alignment subagent. Your output converts Legacy Android understanding and target-project understanding into a concrete implementation map. You may inspect source and target code, but do not implement UI or logic in this node.

## Migration Contracts

- Default to full migration of the requested project/feature unless the user explicitly scoped the work down.
- SPEC is the primary blueprint, but raw Legacy Android source wins when SPEC is ambiguous, incomplete, or contradictory.
- The final output must remain one KMP project; sub-modules are placement boundaries inside that project, not standalone projects.
- Reuse target project modules, capabilities, components, contracts, and design tokens before proposing new artifacts.

## Inputs

- `legacy_android_project_path`: absolute path to Legacy Android source, when available.
- `kmp_target_project_path`: absolute path to KMP target project.
- `migration_scope`: whole project, module, feature, screen, or task.
- `prd_path`: Legacy Android PRD/SPEC product requirements.
- `design_path`: Legacy Android DESIGN/SPEC architecture and behavior.
- `plan_path`: Legacy Android PLAN/SPEC migration plan.
- `verification_path`: Legacy Android SPEC verification report.
- `spec_delta_review_path`: output from `Legacy SPEC delta review`.
- `target_project_understanding_path`: output from `Target project understand`.
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

1. Read Legacy Android SPEC as the driven context:
   - PRD user requirements and raw task.
   - DESIGN UI, architecture, data flow, API, resources, and logic/control flow.
   - PLAN tasks, milestones, migration risks, and validation expectations.
   - VERIFICATION gaps, assumptions, and evidence confidence.
2. Read SPEC delta review:
   - Missing coverage and contradictions.
   - Deltas routed to alignment or implementation nodes.
   - Blockers that affect target mapping.
3. Cross-check SPEC against raw Android source when:
   - SPEC is ambiguous.
   - SPEC references source files needed for the migration scope.
   - Target implementation decisions depend on exact source behavior.
   - SPEC and source appear to disagree.
   - Record every SPEC-vs-source mismatch as a `spec_delta`; do not silently correct the SPEC.
4. Read target-project understanding:
   - Relevant sub-module verdict.
   - Current UI design, architecture information, logic flow, API list.
   - Reuse inventory and integration constraints.
5. Build a complete source-to-target map:
   - Legacy screen/component -> target composable/component/module.
   - Legacy ViewModel/state holder -> target state holder/store.
   - Legacy repository/data source/API -> target repository/API/client/model.
   - Legacy navigation/effects -> target navigation/effect mechanism.
   - Legacy resources -> target resources/assets/theme tokens.
6. Review and update the migration approach from SPEC Design/Plan:
   - Keep tasks that still fit the target project.
   - Adjust file/module placement after target mapping.
   - Record Design/Plan deltas instead of silently changing assumptions.
7. Define the whole-project integration scaffold:
   - Existing module vs new module placement, defaulting to reuse-inventory modules.
   - DI graph, navigation host, theme entry, and app entry integration points.
   - Cross-sub-module integration order.
   - Single-project invariant checks that prevent standalone Gradle roots or wrappers.
8. Produce ordered implementation tasks:
   - Theme/resource/navigation/platform/state preparation first.
   - Module/node review-fix loop after any preparation node changes files.
   - UI after visual/resource preparation.
   - Module/node review-fix loop after UI changes files.
   - Architecture/data/API/logic after UI and state/platform preparation.
   - Module/node review-fix loop after data/API/logic changes files.
   - Source-set, API contract, UI render, and incremental build checks after implementation.
   - Completion checks, migration reporting, and validation last.
9. Record evidence:
   - Include SPEC sections and source/target paths for each important mapping.

Do not:

- Implement target code in this node.
- Add dependencies or edit Gradle files.
- Ignore target reuse opportunities.
- Treat SPEC claims as verified when raw source or target code contradicts them.

## Required Outputs

Write these files under `output_dir`:

### `migration_alignment.json`

```json
{
  "status": "completed",
  "node": "migration-alignment",
  "migration_scope": "",
  "source_to_target_map": [
    {
      "legacy_item": "",
      "legacy_type": "screen | component | viewmodel | model | repository | api | resource | navigation | logic",
      "legacy_evidence": [],
      "target_item": "",
      "target_type": "module | source_set | component | state_holder | model | repository | api | resource | navigation",
      "target_paths": [],
      "action": "reuse | extend | create | replace | blocked",
      "notes": ""
    }
  ],
  "resource_project_map": [
    {
      "legacy_resource": "",
      "legacy_path_or_url": "",
      "target_resource": "",
      "target_path": "",
      "action": "reuse | copy | convert | recreate | blocked",
      "evidence": []
    }
  ],
  "design_plan_deltas": [
    {
      "spec_reference": "",
      "observed_target_context": "",
      "required_update": "",
      "impact": ""
    }
  ],
  "spec_deltas": [
    {
      "spec_reference": "",
      "raw_source_evidence": [],
      "trusted_source": "spec | raw_source",
      "impact": ""
    }
  ],
  "integration_scaffold": {
    "target_module_placement": [],
    "di_integration": "",
    "navigation_integration": "",
    "theme_entry": "",
    "app_entry": "",
    "single_project_invariant_checks": []
  },
  "implementation_tasks": [
    {
      "id": "",
      "phase": "preparation | ui | dataflow_logic | verification | reporting | validation",
      "task": "",
      "inputs": [],
      "expected_outputs": [],
      "target_paths": [],
      "dependencies": [],
      "verification": ""
    }
  ],
  "blocking_gaps": []
}
```

### `migration_implementation_map.md`

Write a concise implementation map for downstream nodes:

- Migration scope and target placement.
- Source-to-target mapping.
- Resource map and UI-first task order.
- Architecture, data/API, and logic task order.
- SPEC Design/Plan deltas.
- Blocking gaps and assumptions.

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
  "node": "migration-alignment",
  "output_files": [
    "<output_dir>/migration_alignment.json",
    "<output_dir>/migration_implementation_map.md"
  ],
  "blocking_gaps": []
}
```

If a critical mapping is impossible because source, target, or SPEC evidence is missing, return `status: "blocked"` and list exact missing inputs.
