---
name: android-to-kmp-migrator
description: Controller support skill registry for Android-to-KMP migration. Use with the android-to-kmp-migrator agent to locate node skill specs for workspace state, SPEC delta review, target project understanding, migration alignment, dependency resolution, theme/resource/navigation/platform/state preparation, UI mockup implementation, dataflow/logic implementation, module/node review-fix loops, guard/parity/fidelity/build checks, PRD completion checking, and migration report output.
disable-model-invocation: true
---

# Android To KMP Migrator Node Skill Registry

This directory stores node skill specs used by the `android-to-kmp-migrator` controller. The controller owns trigger verification, routing, output validation, re-dispatch, and final migration readiness. Node subagents own target-project understanding and migration implementation work.

## Default Output Directory

Unless the user or controller provides an explicit `output_dir`, write migration and node artifacts under `~/.d2c_agents/migration/`.

## Node Skills

| Node | Skill spec | Responsibility |
|---|---|---|
| `Migration workspace state` | [migration-workspace-state.md](migration-workspace-state.md) | Maintain node status, changed-file ownership, stale outputs, rerun history, blockers, and next actions. |
| `Legacy SPEC delta review` | [legacy-spec-delta-review.md](legacy-spec-delta-review.md) | Cross-check Legacy Android SPEC against raw source for missing coverage, contradictions, and migration blockers. |
| `Target project understand` | [target-project-understand.md](target-project-understand.md) | Determine whether a relevant sub-module already exists in the target KMP project; if it exists, capture current UI design, architecture, logic flow, API list, reuse inventory, and migration context. |
| `Migration alignment` | [migration-alignment.md](migration-alignment.md) | Align Legacy Android SPEC/raw understanding with the target-project context, review SPEC Design/Plan, map resources, and produce ordered implementation tasks. |
| `Dependency resolution` | [dependency-resolution.md](dependency-resolution.md) | Apply the minimal-change dependency gate, map required capabilities to baseline/reuse inventory, justify any build-config changes, and validate dependency readiness. |
| `Theme design-system mapping` | [theme-design-system-mapping.md](theme-design-system-mapping.md) | Map Legacy Android visual tokens to target design-system tokens/components and provide UI implementation guidance. |
| `Resource migration` | [resource-migration.md](resource-migration.md) | Migrate local and online resources into target KMP resource conventions before UI implementation. |
| `Navigation migration` | [navigation-migration.md](navigation-migration.md) | Migrate routes, parameters, back behavior, deep links, and navigation scaffolding into the target project. |
| `Platform API replacement` | [platform-api-replacement.md](platform-api-replacement.md) | Replace Android-only APIs with target-safe KMP abstractions or expect/actual boundaries. |
| `State model mapping` | [state-model-mapping.md](state-model-mapping.md) | Map and implement state holders, DTO/domain/UI models, and state semantics before logic implementation. |
| `UI mockup implementation` | [ui-mockup-implementation.md](ui-mockup-implementation.md) | Implement required UI layouts, components, theme/resource references, and legacy resources first. |
| `Dataflow logic implementation` | [dataflow-logic-implementation.md](dataflow-logic-implementation.md) | Implement architecture, data flow, API integration, navigation effects, lifecycle behavior, and business logic in the target project. |
| `Module/node migration review` | [module-node-migration-review.md](module-node-migration-review.md) | Review each module or node migration slice for contract compliance, source parity, target conventions, changed-file scope, and handoff readiness. |
| `Module/node migration fix` | [module-node-migration-fix.md](module-node-migration-fix.md) | Apply focused fixes from module/node review findings and require re-review before downstream gates consume the slice. |
| `Source set placement guard` | [source-set-placement-guard.md](source-set-placement-guard.md) | Verify changed files are in correct KMP source sets and Android-only APIs do not leak into shared code. |
| `API contract parity` | [api-contract-parity.md](api-contract-parity.md) | Compare migrated KMP API contracts against Legacy Android API/data evidence. |
| `UI render fidelity check` | [ui-render-fidelity-check.md](ui-render-fidelity-check.md) | Check migrated UI render paths, visual states, resources, and theme usage before final validation. |
| `Incremental build check` | [incremental-build-check.md](incremental-build-check.md) | Run the smallest known target build/check and route compile failures to responsible nodes before final validation. |
| `PRD completion check` | [prd-completion-check.md](prd-completion-check.md) | Verify PRD/raw task completion across UI, resources, architecture, data/API, logic, and target integration; return actionable gaps for re-dispatch. |
| `Migration report` | [migration-report.md](migration-report.md) | Produce the final migration report consumed by validation, including mappings, changed files, coverage, limitations, and validation inputs. |

## Required Dispatch Order

1. Initialize and refresh `Migration workspace state`.
2. Run `Legacy SPEC delta review`.
3. Run `Target project understand`.
4. Run `Migration alignment` after target understanding, SPEC delta review, and Legacy Android SPEC are available.
5. Run `Dependency resolution` before implementation nodes.
6. Run `Theme design-system mapping`, `Resource migration`, `Navigation migration`, `Platform API replacement`, and `State model mapping`.
7. Run `Module/node migration review` for changed preparation slices; run `Module/node migration fix` and re-review when needed.
8. Run `UI mockup implementation` before logic implementation, then run the review/fix loop for UI slices.
9. Run `Dataflow logic implementation` after UI implementation and state/platform/navigation preparation, then run the review/fix loop for logic/data/API slices.
10. Run `Source set placement guard`, `API contract parity`, `UI render fidelity check`, and `Incremental build check`; re-run responsible nodes when failures are routed.
11. Run `PRD completion check`; re-run earlier nodes when gaps are found.
12. Run `Migration report` when completion check returns `ready_for_validation`.
13. The controller invokes `kmp-test-validator` only after migration report returns `ready_for_validation`.

## Subagent Contracts

The controller must pass each node a complete contract. Each node must return the declared artifacts, or the controller re-runs that node with the missing-output reason.

All `output_dir` fields in the node contracts below inherit the migration stage default `~/.d2c_agents/migration/` unless the user or controller provides a node-specific directory.

### `Migration workspace state`

Specific task:

- Normalize node statuses, output files, changed-file ownership, rerun history, stale outputs, blockers, and next actions.
- Prevent downstream nodes from consuming stale upstream artifacts.

Input:

```yaml
kmp_target_project_path: <absolute path>
legacy_android_project_path: <absolute path or null>
migration_scope: <scope>
current_controller_step: <step name>
node_outputs: <known node output paths/statuses>
changed_files: <paths with owner nodes>
rerun_reports: <reports>
blocking_gaps: <gaps>
output_dir: <node output directory>
```

Output:

- `migration_workspace_state.json`
- `migration_workspace_state.md`

### `Legacy SPEC delta review`

Specific task:

- Check PRD/DESIGN/PLAN/verification coverage against migration scope.
- Cross-check raw Android source for missing or contradictory behavior.
- Classify deltas and route them to downstream nodes.

Input:

```yaml
legacy_android_project_path: <absolute path or null>
migration_scope: <scope>
prd_path: <path>
design_path: <path>
plan_path: <path>
verification_path: <path>
shared_brief_path: <path or inline brief>
output_dir: <node output directory>
```

Output:

- `spec_delta_review.json`
- `spec_delta_review.md`

### `Target project understand`

Specific task:

- Verify the target is a KMP project.
- Detect whether a relevant target sub-module already exists.
- Capture the baseline environment snapshot, current UI design, architecture information, logic flow, API list, reuse inventory, integration constraints, and tooling gaps.

Input:

```yaml
kmp_target_project_path: <absolute path>
legacy_android_project_path: <absolute path or null>
migration_scope: <whole project | module | feature | screen | task>
spec_dir: <directory containing prd.md/design.md/plan.md/verification.md>
shared_brief_path: <path or inline brief>
output_dir: <node output directory>
```

Output:

- `target_project_understanding.json`
- `target_migration_context.md`

### `Migration alignment`

Specific task:

- Read Legacy Android SPEC as the driven context.
- Cross-check SPEC against raw Android source where implementation depends on exact behavior.
- Map legacy screens, state holders, APIs, resources, navigation, and logic to target modules/components.
- Record SPEC deltas, whole-project integration scaffold, and ordered implementation tasks.

Input:

```yaml
legacy_android_project_path: <absolute path or null>
kmp_target_project_path: <absolute path>
migration_scope: <scope>
prd_path: <path>
design_path: <path>
plan_path: <path>
verification_path: <path>
spec_delta_review_path: <path>
target_project_understanding_path: <path>
shared_brief_path: <path or inline brief>
output_dir: <node output directory>
```

Output:

- `migration_alignment.json`
- `migration_implementation_map.md`

### `Dependency resolution`

Specific task:

- Map required migration capabilities to the target baseline and reuse inventory.
- Enforce the minimal-change gate for build configuration.
- Justify any build-config change as absent from baseline, strictly required, and not replaceable by existing target capability.
- Return dependency readiness before implementation nodes run.

Input:

```yaml
kmp_target_project_path: <absolute path>
migration_scope: <scope>
target_project_understanding_path: <path>
migration_alignment_path: <path>
prd_path: <path>
design_path: <path>
plan_path: <path>
shared_brief_path: <path or inline brief>
output_dir: <node output directory>
```

Output:

- `dependency_resolution.json`
- `dependency_resolution_report.md`

### `Theme design-system mapping`

Specific task:

- Map Legacy Android colors, typography, dimensions, shapes, icons, and themes to target design-system tokens/components.
- Reuse target tokens first; add or extend only when required.
- Produce UI implementation guidance and visual gaps.

Input:

```yaml
kmp_target_project_path: <absolute path>
migration_scope: <scope>
resource_understanding_path: <path>
target_project_understanding_path: <path>
migration_alignment_path: <path>
dependency_resolution_path: <path>
theme_design_system_mapping_path: <path>
resource_migration_path: <path>
navigation_migration_path: <path>
shared_brief_path: <path or inline brief>
output_dir: <node output directory>
```

Output:

- `theme_design_system_mapping.json`
- `theme_design_system_mapping.md`
- changed theme/resource files when needed

### `Resource migration`

Specific task:

- Migrate or model local and online Legacy Android resources in the target KMP project.
- Preserve placeholders, error images, density/vector/tinting constraints, and target naming conventions.
- Record resource gaps instead of inventing missing assets.

Input:

```yaml
kmp_target_project_path: <absolute path>
legacy_android_project_path: <absolute path or null>
migration_scope: <scope>
resource_understanding_path: <path>
target_project_understanding_path: <path>
migration_alignment_path: <path>
dependency_resolution_path: <path>
shared_brief_path: <path or inline brief>
output_dir: <node output directory>
```

Output:

- `resource_migration.json`
- `resource_migration.md`
- changed target resource files

### `Navigation migration`

Specific task:

- Map Android Activities/Fragments/NavGraphs/intents/deep links to target KMP routes.
- Implement route scaffolding, parameters, back behavior, and result passing.
- Return navigation gaps for unsupported dynamic routes or target capability gaps.

Input:

```yaml
kmp_target_project_path: <absolute path>
legacy_android_project_path: <absolute path or null>
migration_scope: <scope>
ui_understanding_path: <path>
logic_understanding_path: <path>
target_project_understanding_path: <path>
migration_alignment_path: <path>
dependency_resolution_path: <path>
shared_brief_path: <path or inline brief>
output_dir: <node output directory>
```

Output:

- `navigation_migration.json`
- `navigation_migration.md`
- changed navigation files

### `Platform API replacement`

Specific task:

- Identify Android-only APIs and platform services in scope.
- Reuse target abstractions or implement expect/actual/platform-source-set replacements.
- Keep Android-only APIs out of shared source sets.

Input:

```yaml
kmp_target_project_path: <absolute path>
legacy_android_project_path: <absolute path or null>
migration_scope: <scope>
android_ecosystem_path: <path>
logic_understanding_path: <path>
data_flow_path: <path>
target_project_understanding_path: <path>
migration_alignment_path: <path>
dependency_resolution_path: <path>
shared_brief_path: <path or inline brief>
output_dir: <node output directory>
```

Output:

- `platform_api_replacement.json`
- `platform_api_replacement.md`
- changed platform abstraction files

### `State model mapping`

Specific task:

- Map Legacy Android state holders, events/effects, DTOs, domain models, and UI models to target KMP structures.
- Preserve loading/error/empty/pagination/refresh state semantics.
- Produce handoff context for dataflow/logic implementation.

Input:

```yaml
kmp_target_project_path: <absolute path>
migration_scope: <scope>
architecture_pattern_path: <path>
data_flow_path: <path>
logic_understanding_path: <path>
api_list_path: <path>
target_project_understanding_path: <path>
migration_alignment_path: <path>
dependency_resolution_path: <path>
ui_impl_result_path: <path or null>
shared_brief_path: <path or inline brief>
output_dir: <node output directory>
```

Output:

- `state_model_mapping.json`
- `state_model_mapping.md`
- changed model/state files

### `UI mockup implementation`

Specific task:

- Implement UI layout, components, visual states, theme/resource usage, and referenced Legacy Android resources first.
- Reuse target components and design tokens when semantics match.
- Keep migrated UI inside the existing target KMP project.
- Expose binding surfaces for the logic node.

Input:

```yaml
kmp_target_project_path: <absolute path>
legacy_android_project_path: <absolute path or null>
migration_scope: <scope>
prd_path: <path>
design_path: <path>
plan_path: <path>
target_project_understanding_path: <path>
migration_alignment_path: <path>
dependency_resolution_path: <path>
shared_brief_path: <path or inline brief>
output_dir: <node output directory>
```

Output:

- `ui_impl_result.json`
- `ui_implementation_notes.md`
- changed target UI/resource files

### `Dataflow logic implementation`

Specific task:

- Implement state holders, models, mappers, repositories/use cases, API integration, navigation effects, lifecycle behavior, and business logic.
- Bind logic to UI surfaces from the UI node.
- Preserve target architecture patterns and platform boundaries.
- Ensure no Android-only APIs leak into shared source sets.

Input:

```yaml
kmp_target_project_path: <absolute path>
legacy_android_project_path: <absolute path or null>
migration_scope: <scope>
prd_path: <path>
design_path: <path>
plan_path: <path>
target_project_understanding_path: <path>
migration_alignment_path: <path>
dependency_resolution_path: <path>
resource_migration_path: <path>
navigation_migration_path: <path>
platform_api_replacement_path: <path>
state_model_mapping_path: <path>
ui_impl_result_path: <path>
shared_brief_path: <path or inline brief>
output_dir: <node output directory>
```

Output:

- `dataflow_logic_impl_result.json`
- `dataflow_logic_implementation_notes.md`
- changed target logic/data/API files

### `Module/node migration review`

Specific task:

- Review one module or node migration slice after a preparation, implementation, or fix node changes files.
- Check owning-node contract compliance, source parity, target conventions, changed-file scope, and downstream handoff readiness.
- Return findings with exact routing to fix, owning node, verification node, controller, or user.

Input:

```yaml
kmp_target_project_path: <absolute path>
legacy_android_project_path: <absolute path or null>
migration_scope: <scope>
module_or_node_scope: <module | screen | feature | resource group | route | state holder | API group | node output>
owning_node: <node name>
owning_node_skill_path: <path>
owning_node_output_path: <path>
changed_files: <paths>
upstream_evidence_paths: <paths>
migration_workspace_state_path: <path>
previous_review_path: <path or null>
output_dir: <node output directory>
```

Output:

- `module_node_migration_review.json`
- `module_node_migration_review.md`

### `Module/node migration fix`

Specific task:

- Apply only actionable `must_fix` findings assigned by module/node migration review.
- Keep edits inside allowed files and the declared module/node scope.
- Preserve source-set placement, target conventions, dependency decisions, and single-project invariant.
- Return changed files for mandatory re-review.

Input:

```yaml
kmp_target_project_path: <absolute path>
legacy_android_project_path: <absolute path or null>
migration_scope: <scope>
module_or_node_scope: <module | screen | feature | resource group | route | state holder | API group | node output>
owning_node: <node name>
owning_node_skill_path: <path>
owning_node_output_path: <path>
review_report_path: <path>
allowed_files: <paths>
upstream_evidence_paths: <paths>
migration_workspace_state_path: <path>
output_dir: <node output directory>
```

Output:

- `module_node_migration_fix.json`
- `module_node_migration_fix.md`
- changed target files

### `Source set placement guard`

Specific task:

- Verify changed files are in the correct KMP source sets.
- Detect Android-only APIs in shared code and incomplete expect/actual declarations.
- Route violations to the responsible implementation node.

Input:

```yaml
kmp_target_project_path: <absolute path>
migration_scope: <scope>
changed_files: <paths>
target_project_understanding_path: <path>
platform_api_replacement_path: <path>
state_model_mapping_path: <path>
dependency_resolution_path: <path>
output_dir: <node output directory>
```

Output:

- `source_set_placement_guard.json`
- `source_set_placement_guard.md`

### `API contract parity`

Specific task:

- Compare migrated KMP API contracts with Legacy Android API/data evidence.
- Check endpoints, params, headers, request/response models, errors, pagination, auth, and cache-relevant behavior.
- Route mismatches to state/model, dependency, or dataflow/logic nodes.

Input:

```yaml
kmp_target_project_path: <absolute path>
migration_scope: <scope>
api_list_path: <path>
data_flow_path: <path>
dataflow_logic_impl_result_path: <path>
changed_files: <paths>
output_dir: <node output directory>
```

Output:

- `api_contract_parity.json`
- `api_contract_parity.md`

### `UI render fidelity check`

Specific task:

- Verify migrated screens have render paths, previews, navigation entries, or documented render routes.
- Check visual-state coverage and resource/theme usage.
- Route UI failures to UI, resource, theme, or navigation nodes.

Input:

```yaml
kmp_target_project_path: <absolute path>
migration_scope: <scope>
ui_impl_result_path: <path>
theme_design_system_mapping_path: <path>
resource_migration_path: <path>
navigation_migration_path: <path>
target_project_understanding_path: <path>
output_dir: <node output directory>
```

Output:

- `ui_render_fidelity_check.json`
- `ui_render_fidelity_check.md`

### `Incremental build check`

Specific task:

- Run the smallest known target build/check command from target understanding.
- Parse failures and route them to responsible nodes.
- Provide an early compile gate without replacing final `kmp-test-validator`.

Input:

```yaml
kmp_target_project_path: <absolute path>
migration_scope: <scope>
target_project_understanding_path: <path>
dependency_resolution_path: <path>
changed_files: <paths>
upstream_node_outputs: <paths>
output_dir: <node output directory>
```

Output:

- `incremental_build_check.json`
- `incremental_build_check.md`
- build log files referenced by the JSON

### `PRD completion check`

Specific task:

- Verify raw user task, PRD, DESIGN, PLAN, upstream node outputs, and changed files.
- Check UI, resources, architecture, data/API, logic, incomplete markers, platform boundaries, dependency gate, and single-project invariant.
- Produce rerun requests for the responsible node, or mark ready for validation.

Input:

```yaml
kmp_target_project_path: <absolute path>
legacy_android_project_path: <absolute path or null>
migration_scope: <scope>
raw_user_task: <text or path>
prd_path: <path>
design_path: <path>
plan_path: <path>
verification_path: <path>
target_project_understanding_path: <path>
migration_alignment_path: <path>
dependency_resolution_path: <path>
theme_design_system_mapping_path: <path>
resource_migration_path: <path>
navigation_migration_path: <path>
platform_api_replacement_path: <path>
state_model_mapping_path: <path>
ui_impl_result_path: <path>
dataflow_logic_impl_result_path: <path>
module_node_review_paths: <paths>
module_node_fix_paths: <paths>
incremental_build_check_path: <path>
source_set_placement_guard_path: <path>
api_contract_parity_path: <path>
ui_render_fidelity_check_path: <path>
changed_files: <paths>
output_dir: <node output directory>
```

Output:

- `prd_completion_check.json`
- `prd_completion_report.md`

### `Migration report`

Specific task:

- Synthesize all verified node outputs and changed files into the final migration report.
- Record source-to-target mapping, coverage summary, limitations, manual steps, and validation inputs.
- Return `ready_for_validation` only when PRD completion is ready.

Input:

```yaml
legacy_android_project_path: <absolute path or null>
kmp_target_project_path: <absolute path>
migration_scope: <scope>
prd_path: <path>
design_path: <path>
plan_path: <path>
verification_path: <path>
migration_workspace_state_path: <path>
all_node_outputs: <paths>
changed_files: <paths>
module_node_review_paths: <paths>
module_node_fix_paths: <paths>
prd_completion_check_path: <path>
output_dir: <node output directory>
```

Output:

- `migration_report.json`
- `migration_report.md`

## Shared Input Contract

Every node receives:

```yaml
legacy_android_project_path: <absolute path or null>
kmp_target_project_path: <absolute path>
migration_scope: <whole project | module | feature | screen | task>
spec_dir: <directory containing prd.md/design.md/plan.md/verification.md>
output_dir: <node-specific output directory>
shared_brief_path: <path or inline brief>
```

Implementation nodes also receive upstream node output paths and changed-file lists from previous implementation nodes.

## Shared Return Shape And Rerun Status

Every node return payload must include these fields, in addition to any node-specific fields:

```json
{
  "status": "completed | passed | ready_for_implementation | ready_for_validation | needs_rerun | failed | blocked",
  "node": "<node-name>",
  "output_files": ["<paths>"],
  "changed_files": ["<paths or empty>"],
  "stale_upstream_inputs": ["<paths or empty>"],
  "rerun_requests": [
    {
      "node": "<responsible-node>",
      "reason": "<why rerun is required>",
      "required_inputs": ["<paths or facts needed>"],
      "expected_output": "<artifact or behavior expected>"
    }
  ],
  "blocking_gaps": ["<gaps or empty>"]
}
```

Status semantics:

- `completed`: analysis, implementation, review, fix, or report artifact was produced successfully.
- `passed`: verification node passed with no required rerun.
- `ready_for_implementation`: dependency/capability gate passed and implementation nodes may run.
- `ready_for_validation`: completion/report gate passed and the controller may invoke `kmp-test-validator`.
- `needs_rerun`: node found fixable gaps and populated `rerun_requests`.
- `failed`: verification or build check failed and populated `rerun_requests`.
- `blocked`: required evidence, target capability, or user input is missing and cannot be resolved by rerunning another node.

Controller handling:

- If `output_files` are missing or empty, rerun the same node.
- If `stale_upstream_inputs` is non-empty, rerun the node after refreshing those upstream artifacts.
- If `rerun_requests` is non-empty, dispatch the responsible node with the request context before continuing.
- If `blocking_gaps` is non-empty and no rerun request can resolve it, stop with a user-visible blocker.

## Shared Rules

- Each node subagent must read its own skill spec before work.
- Each node must stay inside its responsibility boundary.
- Every important claim must include evidence from source paths, SPEC sections, or upstream node outputs.
- Unknowns must be marked explicitly instead of guessed.
- The controller must not substitute itself for node implementation.
- No migration implementation may leave TODO placeholders as completion output.
- Target project conventions and reusable modules/components take priority over new abstractions.
- Target build configuration is read-only by default; only the dependency-resolution node may justify build changes.
- Migrated code must stay inside one KMP target project; no migrated sub-module may become a standalone project.
- SPEC guides migration, but raw Legacy Android source wins when evidence conflicts.
