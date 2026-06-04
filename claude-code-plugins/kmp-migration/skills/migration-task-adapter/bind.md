# Execution Guardrails

## Resource Constraints

| Item | Limit | Reason |
|---|---|---|
| `max_parallel_teammates` | 1 | The adapter is a control plane. Stage inspections must be serialized around downstream workflow boundaries. |
| `total_wall_clock_budget` | 20 min adapter overhead | Downstream analyst/migrator/validator workflows keep their own budgets. |
| `total_token_budget` | 300k adapter overhead | The adapter records contracts, inspections, and asset ledgers; it must not duplicate downstream analysis. |
| `per_node_token_budget` | 80k | Roles are narrow and should cite downstream artifacts by path rather than paste large outputs. |
| `max_route_retries` | 2 | Repeated route ambiguity should be surfaced to the user as a blocker. |
| `max_stage_inspection_repairs` | 2 per stage | Missing or malformed inspection records are repaired by rerunning the discipline inspector, not by bypassing the gate. |

## Behavioral Constraints

- **Adapter-as-orchestrator only**: the Leader and adapter roles classify, route, inspect, record, and report. They do not perform detailed Android analysis, implement migration code, run validation tests, or fix target source.
- **Task-first routing**: `task-understanding-router` must complete before any downstream workflow is selected. A guessed route is invalid.
- **Strict output root**: the Leader must lock `output_root = <output_dir or ~/.a2c_agents/task-adapter>/migration-task-adapter` before role dispatch. Adapter roles write only under this root.
- **Downstream boundary**: analyst, migrator, and validator artifacts stay under their own declared output roots. The adapter records their paths and statuses in intermediate asset records.
- **Stage inspection discipline**: every route boundary and downstream workflow boundary must have a `stage_inspection.json` and `.md`. A stage inspection must say whether the next stage is `pass`, `needs_rerun`, or `blocked`.
- **Intermediate asset discipline**: every durable artifact consumed by another stage must have one asset record with producer, path, status, freshness basis, consumers, and gaps.
- **Workspace-state freshness**: the adapter must refresh `workspace-state-discipline-inspector` after task routing, after downstream workflow completion, before report, and after report.
- **No hidden fallbacks**: if analyst/migrator/validator evidence is missing or stale, route a rerun request to that workflow. Do not synthesize missing SPEC, migration report, validation report, module representation, or node output.
- **Only-understand focus is a route constraint, not a license to skip evidence gates**: focused UI, logic, architecture, and overview understanding still require analyst artifacts and verification. The focus determines priority and reporting emphasis.
- **Migration readiness**: migration may not start from raw source alone when the migrator requires analyst completion. If fresh SPEC evidence is missing, route analyst in migration mode first.
- **Report-only finalization**: only `task-reporter` issues the adapter final task status, and only from verified adapter and downstream artifacts.

## Stage Inspection Contract

Each stage inspection artifact must include:

```json
{
  "stage_id": "",
  "status": "pass | needs_rerun | blocked",
  "checked_inputs": [],
  "checked_outputs": [],
  "path_compliance": [],
  "freshness_checks": [],
  "intermediate_asset_coverage": [],
  "downstream_contract_checks": [],
  "rerun_requests": [],
  "blocking_gaps": [],
  "next_allowed_stage": ""
}
```

Inspection rules:

- `pass` requires all required inputs and outputs to exist, be non-empty, be under allowed roots, and be recorded in intermediate assets when consumed.
- `needs_rerun` requires a concrete owner and expected output.
- `blocked` requires a user/actionable gap or unavailable environment/tool/evidence.

## Intermediate Asset Record Contract

Every asset record must be stable and machine-routable:

```json
{
  "asset_id": "",
  "asset_type": "run_manifest | route_decision | stage_inspection | workspace_state | downstream_output | representation | spec | migration_report | validation_report | final_report | log | other",
  "producer": "",
  "path": "",
  "status": "exists | missing | stale | blocked | not_applicable",
  "created_or_observed_at": "",
  "freshness_basis": "",
  "consumers": [],
  "source_evidence": [],
  "blocking_gaps": []
}
```

No downstream stage may consume a durable artifact whose record is `missing`, `stale`, or `blocked`.

## Failure Handling

### Teammate failure

| Failure mode | Response |
|---|---|
| Node timeout | Retry once with the same contract. On second timeout, record `[ROLE MISSING - node timed out]` in workspace discipline and block any stage that hard-requires it. |
| Malformed output or missing JSON/MD artifacts | Rerun the same role once with the expected schema and output paths inlined. On second failure, record `[ROLE MISSING - malformed output]` and block downstream consumption. |
| Route is ambiguous | Rerun `task-understanding-router` with the ambiguity. If still ambiguous, ask the user for source path, target path, task target, or scope. |
| Stage inspection missing or malformed | Rerun `workspace-state-discipline-inspector` for that `stage_id`. Do not proceed past the stage. |
| Intermediate asset record missing for consumed artifact | Rerun `workspace-state-discipline-inspector` to repair the asset ledger before downstream consumption. |
| Downstream workflow output missing/empty | Route rerun to the owning downstream workflow or role; do not create adapter-side replacement artifacts. |
| Downstream output stale | Refresh the owning downstream workspace-state workflow if available, then rerun the owning workflow/role before consumption. |
| Downstream workflow returns blocked | Preserve its blocker in adapter stage inspection and final report. Do not downgrade to a partial pass. |

### Input over-scale degradation

| Trigger condition | Degraded mode |
|---|---|
| User asks for whole-project overview without a scope on a very large Android project | Route to `only_understand_overview` with a scope-narrowing blocker or ask for feature/module priority. |
| User asks for migration without a KMP target path | Route classification may complete, but orchestration blocks before migrator dispatch. |
| User asks for validation without migration report/SPEC evidence | Route to `validation_handoff` only as blocked, listing required migration evidence. |
| Existing downstream artifacts are too large to inspect inline | Record paths and status only; require downstream report/verification artifacts instead of pasting node contents. |

## Required Path Contract

```json
{
  "output_root": "<output_dir or ~/.a2c_agents/task-adapter>/migration-task-adapter",
  "task_dir": "<output_root>/task",
  "workspace_state_dir": "<output_root>/workspace-state",
  "orchestration_dir": "<output_root>/orchestration",
  "stage_inspection_dir": "<output_root>/stage-inspections",
  "intermediate_asset_dir": "<output_root>/intermediate-assets",
  "report_dir": "<output_root>/report"
}
```

Reject adapter artifacts outside this path contract. For downstream workflows, record their own output roots as external asset paths with producer workflow metadata.
