# Migration Task Adapter Notes

The `migration-task-adapter` is a control-plane skill. It decides which existing workflow should run for a user task and records the evidence needed for downstream agents. It does not replace the existing controller skills.

## Downstream Workflow Mapping

| Adapter route | Downstream workflow | Required handoff |
|---|---|---|
| `only_understand_ui` | `android-project-analyst` | Analyst output root, `presentation-resource` artifacts, module/global representation, SPEC verification |
| `only_understand_logic` | `android-project-analyst` | Analyst output root, verified Stage A artifacts, `behavior-logic` artifacts, module/global representation |
| `only_understand_architecture` | `android-project-analyst` | Analyst output root, `project-architecture` artifacts, module/global representation |
| `only_understand_overview` | `android-project-analyst` | Analyst output root, module inventory, module/global representation, SPEC package |
| `migration` | `android-project-analyst` then `android-to-kmp-migrator` | Fresh analyst SPEC before migrator; migration report before validation handoff |
| `validation_handoff` | `kmp-test-validator` | Migration report plus Android source/SPEC and KMP target evidence; validator output root is the parallel `validation` location |

## Required Adapter Records

Every adapter run must preserve:

- `task_understanding_router.*` for the route decision.
- `workflow_orchestration.*` for downstream contracts and observations.
- `workspace_state_discipline.*` for freshness, rerun, blocker, and path discipline.
- `stage_inspection.*` for every applicable stage boundary.
- `intermediate_asset_records.*` for every durable artifact consumed by a later stage.
- `task_adapter_report.*` for the final machine-routable result.

## Migration-Specific Gate

For migration tasks, the adapter must not invoke `android-to-kmp-migrator` until one of these is true:

- Fresh `android-project-analyst` SPEC artifacts are provided and recorded in intermediate asset records.
- The adapter first routes and observes an `android-project-analyst` migration-mode run that produces fresh SPEC artifacts.

If the migrator returns `ready_for_validation`, the adapter records the migration report and either routes `kmp-test-validator` or returns `ready_for_validation` with an explicit validation handoff requirement.

## Output Contract Refinement

The active adapter docs now distinguish output filenames from output content responsibilities. `SKILL.md` and `workflow.md` define the artifact schedule and content matrix, while each role file states the exact JSON/Markdown filenames and the evidence each artifact must contain.

Role ownership is explicit:

- `task_understanding_router.*` records the task interpretation, route, focus, inputs, artifact evidence, downstream sequence, and required inspections/assets.
- `workflow_orchestration.*` records downstream dispatch contracts, output roots, expected/observed artifacts, stage requests, asset updates, reruns, and blockers.
- `workspace_state_discipline.*` records adapter discipline state, artifact inventory, path/freshness checks, reruns, blockers, and next actions.
- `stage_inspection.*` records a single stage gate with checked inputs/outputs, compliance, freshness, asset coverage, reruns, blockers, and next stage.
- `intermediate_asset_records.*` records every consumed adapter/downstream artifact with producer, path, status, freshness, consumers, evidence, and gaps.
- `task_adapter_report.*` records the final verified adapter status, downstream summaries, stage/asset summaries, readiness, reruns, blockers, and next action.

The adapter must reject artifacts that have the correct filename but contain another role's work, generic downstream summaries without machine-routable evidence, or downstream validator paths written under the migration output root instead of the parallel `validation` output root.
