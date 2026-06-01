# Execution Guardrails

## Resource Constraints

| Item | Limit | Reason |
|---|---|---|
| `max_parallel_teammates` | 4 | Matches the Stage A foundation fan-out (`ui-understand`, `architecture-pattern`, `android-ecosystem`, `api-list`); Stage B runs ≤2 in parallel, Stage C is single. |
| `total_wall_clock_budget` | 30 min | Upper bound for one full run across all three stages on a whole project; large monorepos should be scoped down per § (b). |
| `total_token_budget` | 600k tokens | Budget across all 7 nodes + Leader integration; prevents one node from exhausting context. |
| `per_node_token_budget` | 90k tokens | Per node soft cap; `logic-understand` and `data-flow` may use the upper end because they consume upstream artifacts. |
| `resource_download_budget` | 50 files / 50 MB | `resource-understand` only — caps safe online-resource downloads; excess is recorded in `download_gaps`. |

## Behavioral Constraints

Team-level rules — distinct from each role's own `## Boundary`.

- **Leader-as-orchestrator only**: the Leader (`android-project-analyst` controller) verifies the trigger, builds the shared brief, dispatches nodes, verifies their outputs, reconciles, and writes SPEC. The Leader does NOT perform a node's detailed analysis, and does NOT invent any architecture/UI/data/logic claim that no node traced to a source path.
- **Disjoint slices, dispatch-time fixed (B-pattern, Stage A)**: each foundation node works ONLY on its assigned slice. Slices are fixed at dispatch and are not renegotiated between nodes; nodes do not see each other's working state during Stage A.
- **Gated handoff, no upstream mutation (C-pattern, Stages B→C)**: a downstream node references upstream node outputs (by path) and enriches only where its own slice requires; it MUST NOT rebuild or overwrite an upstream node's catalog. If upstream data is missing/stale, the node returns `needs_rerun`/`blocked` rather than reconstructing it.
- **Mandatory contract enforcement**: every node is dispatched with a complete contract (`source_project_path`, required upstream artifacts, `analysis_scope`, `skill_spec_path`, `output_dir`). The Leader rejects any return that lacks required JSON/MD artifacts, omits produced files from `output_files`, or claims `completed`/`ready_*` without proven output storage.
- **Conflict handling**: when nodes disagree on a fact affecting architecture/data-flow/ecosystem/migration, the Leader surfaces it verbatim as `Needs confirmation` in `verification.md`. The Leader does NOT silently pick a winner or average findings.
- **No source modification**: no node and not the Leader may edit the analyzed Android project. `resource-understand` writes downloads only under `<output_dir>/node-results/resource-understand/downloaded_resources/` and never stores secrets/cookies/tokens.
- **Agent-only artifacts**: node outputs and SPEC files are structured for downstream agents/controllers, not human presentation; any user-facing summary is produced only after durable artifacts exist.

## Failure Handling

### (a) Teammate failure

| Failure mode | Response |
|---|---|
| Node timeout | Retry once with the same contract. On 2nd timeout, mark the node's slice `[ROLE MISSING — node timed out]` in `verification.md` and proceed with remaining outputs (downstream nodes that hard-require it return `blocked`). |
| Malformed output (does not match role `## Output Schema`, or files missing/empty) | Re-dispatch once with the schema inlined and a "previous output was malformed/missing" preamble. On 2nd failure, mark `[ROLE MISSING — malformed output]`. |
| Node returns `blocked` / `needs_rerun` (missing or stale upstream input) | Resolve the named upstream gap first (re-run the upstream node), then re-dispatch this node. If unresolvable, record the `blocking_gap` and set readiness accordingly. |
| Node attempts to rebuild another node's catalog | Reject the return as out-of-scope; re-dispatch with the role `## Boundary > Forbidden` restated. |

### (b) Input over-scale degradation

| Trigger condition | Degraded mode |
|---|---|
| Whole-project scope on a large monorepo (e.g., > ~50 Gradle modules or > ~5000 source files) | Warn the user; narrow `analysis_scope` to the requested module/feature and record the reduced scope in `verification.md` before dispatching. |
| `resource-understand` finds > 50 downloadable URLs or > 50 MB | Download up to the `resource_download_budget`; record the remainder as `download_gaps` with reason `unavailable` / scope-capped. |
| `total_token_budget` projected to overflow before Stage C | Run Stages A–B fully, then run `logic-understand` on the highest-priority UI modules only; mark uncovered modules explicitly in `verification.md`. |
| `jetbrains` MCP unavailable or pointing at the wrong project | Continue on file-system evidence only; record the MCP gap in `verification.md`. |

### Escalation rules

- If 50%+ of dispatched nodes return `[ROLE MISSING]`, the run is **FAILED** — emit a partial SPEC with a `FAILED: insufficient node coverage` header and the missing-evidence list, readiness `blocked`.
- If `total_wall_clock_budget` is exceeded, halt in-flight nodes, emit whatever verified outputs exist, and tag the report `INCOMPLETE: budget exceeded`.
- If `total_token_budget` is exceeded mid-run, halt new dispatches, let in-flight nodes finish, emit a partial report tagged `INCOMPLETE: token budget exceeded`.
