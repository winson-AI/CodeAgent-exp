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
- **Single base root** — resolve `agents_root = <output_dir or ~/.a2c_agents>` once (default `~/.a2c_agents`); derive `output_root` and all downstream roots from it. Adapter own tree: `output_root = <agents_root>/task-adapter/coding-task-adapter`; paths, gates, and path-accuracy validation per [output-contract.md](output-contract.md).
- **Downstream boundary** — analyst/migrator/validator paths derive from the same `agents_root` but are owned by their own contracts; the adapter sets each downstream `output_root` in the dispatch contract and records it in the asset ledger — it does not own their internal trees.
- **Dual understand subsystems** — route `migration` runs the analysis stage as two `android-project-analyst` understand runs (source + target) into distinct understand output roots; both are recorded before migrator dispatch.
- **Validator root** — validation artifacts under parallel `validation` root, not migration root.
- **Stage gates** — every route and downstream boundary gets `stage_inspection.*` with `pass | needs_rerun | blocked`.
- **Asset ledger** — every consumed durable artifact has one record with producer, path, status, freshness.
- **No hidden fallbacks** — missing/stale evidence → rerun request to owning workflow.
- **Migration readiness** — migrator requires fresh source + target understand subsystems; route both analyst understand runs first when missing.
- **Partial migration trigger** — route scoped migration as route `migration` with `partial_migration.enabled` only when the user clearly asks for module/feature/subset migration. Otherwise migrate the whole input project from `source_project_path`.
- **Migration validator mandate** — route `migration` MUST trigger `kmp-test-validator` after migrator `V0`/`M6` evidence; skipping validator invalidates `A4`/`A5` for migration runs.
- **Final verdict** — only `adapter-report` issues adapter final status.

## Failure Handling

| Failure | Response |
|---|---|
| Node timeout | Retry once; then `[ROLE MISSING]` and block dependent stages |
| Malformed or out-of-path output | Rerun owning role with path contract |
| Downstream root not derived from `agents_root` / wrong stage folder | `blocked` reason `path_mismatch`; re-dispatch with the derived `output_root` |
| Path values diverge across manifest/index/ledger/report | `blocked` reason `path_mismatch`; reconcile from `run_manifest.json` |
| Ambiguous route | Rerun mode `route`; then ask user for path/scope |
| Migration missing target understand subsystem | Block `post_migrator`; dispatch the target-understand analyst run before the migrator |
| No explicit partial migration requirement | Treat route `migration` as full-project migration from `source_project_path` |
| Explicit but ambiguous partial migration scope | Block with scope clarification; do not widen to full-project migration |
| Missing stage inspection | Rerun `adapter-workspace-state` for `stage_id` |
| Missing asset record | Rerun workspace state before consumption |
| Downstream missing/stale | Rerun owning downstream workflow |

## Path Contract

Canonical paths and handoff gates `A0`–`A6`: [output-contract.md](output-contract.md).

```json
{
  "agents_root": "<output_dir or ~/.a2c_agents>",
  "output_root": "<agents_root>/task-adapter/coding-task-adapter",
  "downstream_index_dir": "<output_root>/downstream-index",
  "workspace_state_dir": "<output_root>/workspace-state",
  "route_orchestration_dir": "<output_root>/route-orchestration",
  "stage_inspection_dir": "<output_root>/stage-inspections",
  "intermediate_asset_dir": "<output_root>/intermediate-assets",
  "report_dir": "<output_root>/report",
  "downstream_output_roots": {
    "android-project-analyst-source": "<agents_root>/understand/android-project-analyst/source",
    "android-project-analyst-target": "<agents_root>/understand/android-project-analyst/target",
    "android-to-kmp-migrator": "<agents_root>/migration/android-to-kmp-migrator",
    "kmp-test-validator": "<agents_root>/validation/kmp-test-validator"
  }
}
```
