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
| `validation_handoff` | `kmp-test-validator` | Migration report plus Android source/SPEC and KMP target evidence |

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
