# Execution Guardrails

## Resource Constraints

| Item | Limit | Reason |
|---|---|---|
| `max_parallel_teammates` | 2 | Matches the reduced per-module fan-out (`presentation-integration` + `state-data-prep`). Other stages are serial or mode-gated. |
| `total_wall_clock_budget` | 90 min per feature module batch | Upper bound for one module-first migration batch including inventory, per-module planning, prep, UI, logic, review/fix, verification, representations, and report. |
| `total_token_budget` | 1.2M tokens per batch | Budget across 10 reduced roles + Leader integration + review/fix iterations + representation synthesis. |
| `per_node_token_budget` | 140k tokens | Consolidated roles carry broader context; implementation and completion/report modes may use the upper end. |
| `max_review_fix_cycles` | 3 per slice | Max `review → fix → re-review` iterations for one module/node scope before escalating the slice as `blocked` to the controller/user. |
| `incremental_build_runs` | 1 per Verify pass | One smallest-trustworthy build/check per verification pass; reruns only after a routed fix. |
| `workspace_state_refreshes` | after every major stage | Required so per-module finish rates, plan-vs-code gaps, and rerun hooks stay current before downstream consumption. |

## Behavioral Constraints

Team-level rules — distinct from each role's own `## Boundary`.

- **Leader-as-orchestrator only**: the Leader (`android-to-kmp-migrator` controller) verifies the trigger, builds the shared brief, dispatches reduced roles in dependency order, verifies outputs, routes reruns, and invokes `kmp-test-validator`. The Leader does NOT implement migration code, fix findings, or substitute any node's work.
- **Strict output root**: the Leader must lock `output_root = <output_dir or ~/.a2c_agents/migration>/android-to-kmp-migrator` before any migration node dispatch. All node outputs, module representations, global representation, report artifacts, logs, and ledgers must be under this root.
- **Module-first schedule**: the Leader must write `module-index/migration_module_inventory.*`, then process each `migration_module_id` through planning, dependency/platform, prep, review/fix, UI, review/fix, logic, review/fix, verification, readiness, and module representation before global aggregation.
- **Per-node exact paths**: module-scoped nodes receive `output_dir = <output_root>/modules/<migration_module_id>/node-results/<node_id>`. Global-only outputs use `<output_root>/global/...`; final reports use `<output_root>/report/...`.
- **Role-output content discipline**: required artifacts must contain the content owned by their role, not just the correct filename. For example, `migration_analysis_planning.*` must contain source-to-target planning evidence, `dependency_platform_gate.*` must contain dependency/platform decisions, `presentation_integration.*` must contain token/resource/navigation prep, `state_data_prep.*` must contain state/model/API prep, `ui_implementation.*` must contain UI implementation evidence, `logic_implementation.*` must contain behavior/data/API implementation evidence, `migration_verification.*` must contain check results, and `migration_report.*` must contain validation handoff evidence.
- **Hard dependency order (C-pattern)**: `migration-analysis-planning` precedes `dependency-platform-gate`, which precedes prep and implementation. `ui-implementation` precedes `logic-implementation`. A downstream node references upstream node outputs by path and must NOT rebuild or overwrite upstream artifacts.
- **Mandatory review→fix→re-review loop**: after any node changes files, `module-node-review-fix` runs in `mode: review`; on `needs_fix`, it runs in `mode: fix` inside `allowed_files`, then a fresh `mode: review` invocation is mandatory. No downstream gate consumes a slice whose latest review is not `approved`.
- **Dependency gate authority**: only `dependency-platform-gate` may justify a build-config change; target build configuration is read-only to every other role. No role adds dependencies, root Gradle/settings files, or wrappers.
- **Single-project invariant**: migrated code stays inside one KMP target project; no migrated sub-module becomes a standalone project. Android-only APIs never enter `commonMain`.
- **No placeholder completion**: no implementation node may return `completed` with TODO/FIXME/stub/sample-only-data in production paths as its deliverable.
- **Failure routing, not mediation**: when a verification node fails or nodes disagree, the Leader routes the failure verbatim to the responsible node (recorded in the workspace-state ledger, `rerun_hooks`, and completion/readiness artifacts); it does not silently reconcile or average.
- **Progress ledger discipline**: `migration-workspace-state` is refreshed after inventory, planning, dependency/platform, prep fan-out, every review/fix loop, UI implementation, logic implementation, verification, readiness, module representation, global representation, and report. The ledger must track per-module `module_progress`, `finish_rate`, `plan_code_gaps`, changed-file ownership, stale outputs, rerun hooks, blockers, and next actions.
- **Stale-artifact discipline**: any output whose upstream changed afterward is marked stale in `migration-workspace-state` and must be re-run before consumption.
- **Plan-vs-code gap discipline**: if the workspace ledger reports planned work without code evidence, unplanned target changes, missing review, missing verification, stale plan/source evidence, or a failed verification route, the Leader must follow the emitted rerun hook before advancing the module.
- **Validation boundary**: only `completion-report` in `mode: readiness` issues readiness, only `completion-report` in `mode: report` assembles the validation handoff, and only `kmp-test-validator` validates. SPEC guides migration, but raw Legacy Android source wins when evidence conflicts.
- **Representation gate**: every scheduled module must have `module_migration_representation.json` and `.md`. `completion-report` in `mode: report` cannot return `ready_for_validation` until every scheduled module representation plus `global_migration_representation.json` and `.md` exists and is non-empty.

## Failure Handling

### (a) Teammate failure

| Failure mode | Response |
|---|---|
| Node timeout | Retry once with the same contract. On 2nd timeout, mark the slice `[ROLE MISSING — node timed out]` in the workspace ledger and `prd_completion_check`; downstream nodes that hard-require it return `blocked`. |
| Malformed output (does not match role `## Output Schema` / shared return, files missing/empty, or artifact content does not match the role duty) | Re-dispatch once with the schema and role-owned output content inlined plus a "previous output was malformed/missing/out-of-duty" preamble. On 2nd failure, mark `[ROLE MISSING — malformed output]`. |
| Node returns `needs_rerun` / `blocked` (missing or stale upstream input) | Refresh/re-run the named upstream node first, then re-dispatch this node. If unresolvable, record the `blocking_gap` and set readiness accordingly. |
| Review→fix loop does not converge in `max_review_fix_cycles` | Escalate the slice as `blocked` with the unresolved `must_fix` findings to the controller/user; do not force-approve. |
| `migration-verification` returns `failed` for any check ID | Route each failure to its reduced `route_to_node`, re-run that node, re-enter the review/fix loop, then re-run the failed check IDs. |
| `migration-workspace-state` reports blocking `plan_code_gaps` | Follow the corresponding `rerun_hooks` before downstream consumption. Missing or stale plans route to `migration-analysis-planning`; unplanned/missing code routes to the owner implementation/prep node; missing review routes to `module-node-review-fix`; missing or failed verification routes to `migration-verification` or its `route_to_node`. |
| `migration-workspace-state` reports low or unknown `finish_rate` due to missing plan evidence | Block implementation progress until planning outputs and planned work units are refreshed. Do not compute completion from changed files alone. |
| Node attempts to rebuild another node's artifact or edit outside scope | Reject as out-of-scope; re-dispatch with the role `## Boundary > Forbidden` restated. |

### (b) Input over-scale degradation

| Trigger condition | Degraded mode |
|---|---|
| Whole-project migration on a large monorepo (e.g., > ~30 feature modules or > ~3000 in-scope source files) | Warn the user; split into `migration_module_id` batches in `migration_module_inventory.*`; process batches without changing `output_root`. |
| `total_token_budget` projected to overflow before verification | Complete the analysis chain + dependency gate + current slice, checkpoint via `migration-workspace-state`, and continue in a follow-up run; mark uncovered scope explicitly. |
| No trustworthy incremental build command from target understanding/planning evidence | `migration-verification` returns `blocked` for `check_id: incremental_build`; rely on completed static verification checks and surface the build gap to `completion-report` (does not auto-pass). |
| `jetbrains` MCP unavailable or pointing at the wrong project | Continue on file-system evidence and the target Gradle wrapper; record the MCP gap in the workspace ledger and affected node outputs. |

### Escalation rules

- If 50%+ of dispatched nodes in a stage return `[ROLE MISSING]`, the run is **FAILED** — emit a partial migration report with a `FAILED: insufficient node coverage` header, readiness `blocked`, and the missing-evidence list.
- If `total_wall_clock_budget` is exceeded, halt in-flight nodes, checkpoint via `migration-workspace-state`, emit whatever verified outputs exist, and tag the report `INCOMPLETE: budget exceeded`.
- If `total_token_budget` is exceeded mid-run, halt new dispatches, let in-flight nodes finish, checkpoint, and emit a partial report tagged `INCOMPLETE: token budget exceeded`.

## Required Path Contract

The controller must pass these values to nodes and reject any output outside the declared path:

```json
{
  "output_root": "<output_dir or ~/.a2c_agents/migration>/android-to-kmp-migrator",
  "module_index_dir": "<output_root>/module-index",
  "module_root": "<output_root>/modules/<migration_module_id>",
  "node_result_dir": "<module_root>/node-results/<node_id>",
  "module_representation_dir": "<module_root>/representation",
  "global_dir": "<output_root>/global",
  "report_dir": "<output_root>/report"
}
```

Each reduced role boundary is justified in `ROLE_REDUCTION.md`. Do not dispatch superseded old role IDs, alias old paths, or write compatibility copies outside this schedule.
