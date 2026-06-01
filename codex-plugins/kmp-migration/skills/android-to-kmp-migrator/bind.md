# Execution Guardrails

## Resource Constraints

| Item | Limit | Reason |
|---|---|---|
| `max_parallel_teammates` | 5 | Matches the largest parallel fan-out (Stage Prep: theme/resource/navigation/platform/state). Stage Verify runs ≤4 in parallel; the analysis chain and review→fix loops are serial. |
| `total_wall_clock_budget` | 90 min | Upper bound for one full migration run including the analysis chain, prep, UI, logic, review→fix loops, and verification on a feature-scoped migration. Whole-project scope should be split per § (b). |
| `total_token_budget` | 1.5M tokens | Budget across all 20 nodes + Leader integration + review→fix iterations; prevents one node or loop from exhausting context. |
| `per_node_token_budget` | 120k tokens | Per node soft cap; implementation nodes (`ui-mockup-implementation`, `dataflow-logic-implementation`) and `prd-completion-check` may use the upper end. |
| `max_review_fix_cycles` | 3 per slice | Max `review → fix → re-review` iterations for one module/node scope before escalating the slice as `blocked` to the controller/user. |
| `incremental_build_runs` | 1 per Verify pass | One smallest-trustworthy build/check per verification pass; reruns only after a routed fix. |

## Behavioral Constraints

Team-level rules — distinct from each role's own `## Boundary`.

- **Leader-as-orchestrator only**: the Leader (`android-to-kmp-migrator` controller) verifies the trigger, builds the shared brief, dispatches nodes in dependency order, verifies outputs, routes reruns, and invokes `kmp-test-validator`. The Leader does NOT implement migration code, fix findings, or substitute any node's work.
- **Hard dependency order (C-pattern)**: the analysis chain (delta-review → target-understand → alignment) precedes the dependency gate, which precedes implementation. UI implementation precedes dataflow/logic implementation. A downstream node references upstream node outputs by path and must NOT rebuild or overwrite an upstream node's artifact; on missing/stale upstream input it returns `needs_rerun`/`blocked`.
- **Mandatory review→fix→re-review loop**: after any node changes files, `module-node-migration-review` runs; on `needs_fix`, `module-node-migration-fix` applies only assigned `must_fix` findings inside `allowed_files`, then a re-review is mandatory. No downstream gate consumes a slice whose latest review is not `approved`.
- **Dependency gate authority**: only `dependency-resolution` may justify a build-config change; target build configuration is read-only to every other node. No node adds dependencies, root Gradle/settings files, or wrappers.
- **Single-project invariant**: migrated code stays inside one KMP target project; no migrated sub-module becomes a standalone project. Android-only APIs never enter `commonMain`.
- **No placeholder completion**: no implementation node may return `completed` with TODO/FIXME/stub/sample-only-data in production paths as its deliverable.
- **Failure routing, not mediation**: when a verification node fails or nodes disagree, the Leader routes the failure verbatim to the responsible node (recorded in the workspace-state ledger and `prd_completion_check`); it does not silently reconcile or average.
- **Stale-artifact discipline**: `migration-workspace-state` is refreshed after major node completions; any output whose upstream changed afterward is marked stale and must be re-run before consumption.
- **Validation boundary**: only `prd-completion-check` issues `ready_for_validation` readiness, only `migration-report` assembles the validation handoff, and only `kmp-test-validator` (invoked by the Leader afterward) validates. SPEC guides migration, but raw Legacy Android source wins when evidence conflicts.

## Failure Handling

### (a) Teammate failure

| Failure mode | Response |
|---|---|
| Node timeout | Retry once with the same contract. On 2nd timeout, mark the slice `[ROLE MISSING — node timed out]` in the workspace ledger and `prd_completion_check`; downstream nodes that hard-require it return `blocked`. |
| Malformed output (does not match role `## Output Schema` / shared return, or files missing/empty) | Re-dispatch once with the schema inlined and a "previous output was malformed/missing" preamble. On 2nd failure, mark `[ROLE MISSING — malformed output]`. |
| Node returns `needs_rerun` / `blocked` (missing or stale upstream input) | Refresh/re-run the named upstream node first, then re-dispatch this node. If unresolvable, record the `blocking_gap` and set readiness accordingly. |
| Review→fix loop does not converge in `max_review_fix_cycles` | Escalate the slice as `blocked` with the unresolved `must_fix` findings to the controller/user; do not force-approve. |
| Verification node (`source-set-placement-guard` / `api-contract-parity` / `ui-render-fidelity-check` / `incremental-build-check`) returns `failed` | Route each failure to its `route_to_node`, re-run that node, re-enter the review→fix loop, then re-run the verification node. |
| Node attempts to rebuild another node's artifact or edit outside scope | Reject as out-of-scope; re-dispatch with the role `## Boundary > Forbidden` restated. |

### (b) Input over-scale degradation

| Trigger condition | Degraded mode |
|---|---|
| Whole-project migration on a large monorepo (e.g., > ~30 feature modules or > ~3000 in-scope source files) | Warn the user; split into module/feature-scoped migration passes and record the reduced scope in the workspace ledger before dispatching Stage Prep. |
| `total_token_budget` projected to overflow before verification | Complete the analysis chain + dependency gate + current slice, checkpoint via `migration-workspace-state`, and continue in a follow-up run; mark uncovered scope explicitly. |
| No trustworthy incremental build command from `target-project-understand` | `incremental-build-check` returns `blocked`; rely on source-set guard + parity + render static checks and surface the build gap to `prd-completion-check` (does not auto-pass). |
| `jetbrains` MCP unavailable or pointing at the wrong project | Continue on file-system evidence and the target Gradle wrapper; record the MCP gap in the workspace ledger and affected node outputs. |

### Escalation rules

- If 50%+ of dispatched nodes in a stage return `[ROLE MISSING]`, the run is **FAILED** — emit a partial migration report with a `FAILED: insufficient node coverage` header, readiness `blocked`, and the missing-evidence list.
- If `total_wall_clock_budget` is exceeded, halt in-flight nodes, checkpoint via `migration-workspace-state`, emit whatever verified outputs exist, and tag the report `INCOMPLETE: budget exceeded`.
- If `total_token_budget` is exceeded mid-run, halt new dispatches, let in-flight nodes finish, checkpoint, and emit a partial report tagged `INCOMPLETE: token budget exceeded`.
