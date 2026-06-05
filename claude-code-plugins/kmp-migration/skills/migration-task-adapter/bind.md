# Execution Guardrails

## Resource Constraints

| Item | Limit | Reason |
|---|---|---|
| `max_parallel_teammates` | 1 | Serial control plane; stage gates around downstream boundaries |
| `total_wall_clock_budget` | 20 min | Adapter overhead only; downstream workflows keep own budgets |
| `total_token_budget` | 300k | Record contracts and ledgers; do not duplicate downstream analysis |
| `per_node_token_budget` | 90k | Narrow roles cite paths, not full downstream outputs |
| `max_route_retries` | 2 | Persistent ambiguity → user blocker |
| `max_stage_repairs` | 2 per stage | Rerun `adapter-workspace-state`; do not bypass gates |

## Behavioral Constraints

- **Orchestrator only** — classify, route, inspect, record, report. No analysis, migration, validation, or code edits.
- **Route before downstream** — `task-route-orchestrator` mode `route` completes before workflow invoke.
- **Strict output root** — `output_root = <output_dir or ~/.a2c_agents/task-adapter>/migration-task-adapter`; paths and gates per [output-contract.md](output-contract.md).
- **Downstream boundary** — analyst/migrator/validator artifacts stay in their output roots; adapter records paths in asset ledger.
- **Validator root** — validation artifacts under parallel `validation` root, not migration root.
- **Stage gates** — every route and downstream boundary gets `stage_inspection.*` with `pass | needs_rerun | blocked`.
- **Asset ledger** — every consumed durable artifact has one record with producer, path, status, freshness.
- **No hidden fallbacks** — missing/stale evidence → rerun request to owning workflow.
- **Migration readiness** — migrator requires fresh analyst SPEC; route analyst first when missing.
- **Migration validator mandate** — route `migration` MUST trigger `kmp-test-validator` after migrator `V0`/`M6` evidence; skipping validator invalidates `A4`/`A5` for migration runs.
- **Final verdict** — only `adapter-report` issues adapter final status.

## Failure Handling

| Failure | Response |
|---|---|
| Node timeout | Retry once; then `[ROLE MISSING]` and block dependent stages |
| Malformed or out-of-path output | Rerun owning role with path contract |
| Ambiguous route | Rerun mode `route`; then ask user for path/scope |
| Missing stage inspection | Rerun `adapter-workspace-state` for `stage_id` |
| Missing asset record | Rerun workspace state before consumption |
| Downstream missing/stale | Rerun owning downstream workflow |

## Path Contract

Canonical paths and handoff gates `A0`–`A6`: [output-contract.md](output-contract.md).

```json
{
  "output_root": "<output_dir or ~/.a2c_agents/task-adapter>/migration-task-adapter",
  "downstream_index_dir": "<output_root>/downstream-index",
  "workspace_state_dir": "<output_root>/workspace-state",
  "route_orchestration_dir": "<output_root>/route-orchestration",
  "stage_inspection_dir": "<output_root>/stage-inspections",
  "intermediate_asset_dir": "<output_root>/intermediate-assets",
  "report_dir": "<output_root>/report"
}
```
