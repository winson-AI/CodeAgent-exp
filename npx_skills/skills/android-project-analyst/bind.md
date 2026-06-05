# Execution Guardrails

## Resource Constraints

| Item | Limit | Reason |
|---|---|---|
| `max_parallel_teammates` | 3 | Matches the Stage A foundation fan-out (`presentation-resource`, `project-architecture`, `data-contract-flow`); Stage B is single. |
| `total_wall_clock_budget` | 30 min | Upper bound for one full module-first run; large monorepos should be scoped down per § (b). |
| `total_token_budget` | 560k tokens | Budget across active roles + Leader integration; workspace-state adds ledger checks. |
| `per_node_token_budget` | 120k tokens | Per node soft cap; `behavior-logic` and `data-contract-flow` may use the upper end because they consume or trace broad flow evidence. |
| `resource_download_budget` | 50 files / 50 MB | `presentation-resource` only — caps safe online-resource downloads; excess is recorded in `download_gaps`. |
| `max_modules_per_run` | 20 | Keeps module-first analysis bounded; larger projects must narrow `analysis_scope` or explicitly run multiple scoped passes. |

## Behavioral Constraints

Team-level rules — distinct from each role's own `## Boundary`.

- **Leader-as-orchestrator only**: the Leader (`android-project-analyst` controller) verifies the trigger, builds the shared brief, dispatches nodes, verifies their outputs, refreshes `analysis-workspace-state`, reconciles, and writes SPEC. The Leader does NOT perform a node's detailed analysis, and does NOT invent any presentation/resource/architecture/ecosystem/data/behavior claim that no node traced to a source path.
- **Strict output schedule and paths**: the Leader MUST lock `output_root` before dispatch and write only the declared schedule artifacts: `run_manifest`, `workspace-state`, `module-index` (including `modules_index.json`), per-module `module_brief`, per-module dimension outputs under `node-results/<dimension>/`, per-module `dimension_index.json`, per-module `representation`, cross-module global records (`cross_module_architecture`, `cross_module_data_logic`, `migration_assembly_basis`), `global_representation`, and `SPEC`. Any node output outside its assigned directory is invalid.
- **Workspace-state discipline**: `analysis-workspace-state` is refreshed after module inventory, each module node group, each module representation, global representation, and SPEC. Downstream roles must not consume artifacts that the ledger marks stale; rerun the responsible node/module or mark the affected scope `blocked`.
- **Module-first invariant**: every in-scope source root belongs to an `analysis_modules[]` entry before node dispatch. Every scheduled `module_id` must have a materialized folder under `modules/<module_id>/` and a resolvable entry in `modules_index.json`. Each module must store all four dimension outputs in its module folder before `dimension_index.json` and `module_representation.*` are written. Cross-module architecture and data/logic must be recorded in dedicated `global/` artifacts before `global_representation.*`. The Leader must not build global SPEC directly from raw source or standalone node outputs.
- **Foundation slices, dispatch-time fixed (B-pattern, Stage A)**: each foundation node works ONLY on its assigned slice. Slices are fixed at dispatch and are not renegotiated between nodes; nodes do not see each other's working state during Stage A.
- **Gated handoff, no upstream mutation (C-pattern, Stage B)**: `behavior-logic` references upstream node outputs (by path) and enriches only where behavior analysis requires; it MUST NOT rebuild or overwrite an upstream node's catalog. If upstream data is missing/stale, it returns `needs_rerun`/`blocked` rather than reconstructing it.
- **Mandatory contract enforcement**: every node is dispatched with a complete module-scoped contract (`source_project_path`, `module_id`, `module_scope`, `module_brief_path`, required upstream artifacts, `analysis_scope`, `skill_spec_path`, exact `output_dir`). The Leader rejects any return that lacks required JSON/MD artifacts, omits produced files from `output_files`, writes outside the assigned path, or claims `completed`/`ready_*` without proven output storage.
- **Role-output content discipline**: required artifacts must contain the content owned by their role, not just the correct filename. For example, `presentation_resource.*` must contain screens/resources/navigation/UI-tree evidence, `project_architecture.*` must contain topology/build/dependency/platform evidence, `data_contract_flow.*` must contain APIs/data-source/model/flow evidence, and `behavior_logic.*` must contain action/lifecycle/rule/control-flow evidence. If content belongs to another role, rerun or route rather than accepting it.
- **Conflict handling**: when nodes disagree on a fact affecting architecture, data flow, resources, ecosystem constraints, behavior, or migration, the Leader surfaces it verbatim as `Needs confirmation` in `verification.md`. The Leader does NOT silently pick a winner or average findings.
- **No source modification**: no node and not the Leader may edit the analyzed Android project. `presentation-resource` writes downloads only under `<output_dir>/node-results/presentation-resource/downloaded_resources/` and never stores secrets/cookies/tokens.
- **Agent-only artifacts**: node outputs and SPEC files are structured for downstream agents/controllers, not human presentation; any user-facing summary is produced only after durable artifacts exist.
- **Downstream trigger discipline**: adherence to [output-contract.md](output-contract.md) is a hard trigger condition for downstream handlers. The Leader must evaluate handoff packages `P0`–`P6`, persist `handoff_gates` in the workspace ledger and `SPEC/verification.md`, and set `run_manifest.json` → `handoff_package`. Downstream workflows (`migration-task-adapter`, `android-to-kmp-migrator`, `kmp-test-validator`) MUST return `blocked` when required package paths are missing, empty, out-of-path, stale, or contract-invalid — they MUST NOT infer from chat or partial summaries.

## Failure Handling

### (a) Teammate failure

| Failure mode | Response |
|---|---|
| Node timeout | Retry once with the same contract. On 2nd timeout, mark the node's slice `[ROLE MISSING — node timed out]` in `verification.md` and proceed with remaining outputs (downstream nodes that hard-require it return `blocked`). |
| Malformed output (does not match role `## Output Schema`, files missing/empty, or artifact content does not match the role duty) | Re-dispatch once with the schema and role-owned output content inlined plus a "previous output was malformed/missing/out-of-duty" preamble. On 2nd failure, mark `[ROLE MISSING — malformed output]`. |
| Node returns `blocked` / `needs_rerun` (missing or stale upstream input) | Refresh `analysis-workspace-state`, resolve the named upstream gap first (re-run the upstream node), then re-dispatch this node. If unresolvable, record the `blocking_gap` and set readiness accordingly. |
| Node attempts to rebuild another node's catalog | Reject the return as out-of-scope; re-dispatch with the role `## Boundary > Forbidden` restated. |
| Node writes outside assigned path | Reject the return as invalid; re-dispatch with the exact assigned `output_dir`. Do not move or reuse out-of-path artifacts. |
| Workspace state marks a required artifact stale | Re-run the owning node or rebuild the owning representation before downstream consumption; do not synthesize around the stale artifact. |
| Global representation requested before module representations exist | STOP; write/repair missing module representations first, or mark affected modules `blocked` before cross-module global records. |
| Cross-module global records requested before all module representations exist | STOP; complete per-module `dimension_index.json` and `module_representation.*` first. |
| `modules_index.json` missing or cannot resolve a scheduled `module_id` | STOP; repair module inventory and index before node dispatch. |
| Completion claimed while target handoff package `P*` is false | Reject completion; update `handoff_gates`, set `readiness: blocked`, list `missing_paths` per [output-contract.md](output-contract.md). |
| Downstream handler invoked without required package artifacts | Downstream returns `blocked` with `blocking_gaps`; analyst Leader does not auto-repair unless rerun is requested. |

### (b) Input over-scale degradation

| Trigger condition | Degraded mode |
|---|---|
| Whole-project scope on a large monorepo (e.g., > ~50 Gradle modules or > ~5000 source files) | Warn the user; narrow `analysis_scope` to the requested module/feature and record the reduced scope in `verification.md` before dispatching. |
| Module inventory produces > `max_modules_per_run` modules | Ask to narrow scope or split into multiple runs; do not silently collapse modules into one global analysis. |
| `presentation-resource` finds > 50 downloadable URLs or > 50 MB | Download up to the `resource_download_budget`; record the remainder as `download_gaps` with reason `unavailable` / scope-capped. |
| `total_token_budget` projected to overflow before Stage B | Run Stage A fully, then run `behavior-logic` on the highest-priority UI modules only; mark uncovered modules explicitly in `verification.md`. |
| `jetbrains` MCP unavailable or pointing at the wrong project | Continue on file-system evidence only; record the MCP gap in `verification.md`. |

### Escalation rules

- If 50%+ of dispatched nodes return `[ROLE MISSING]`, the run is **FAILED** — emit a partial SPEC with a `FAILED: insufficient node coverage` header and the missing-evidence list, readiness `blocked`.
- If `total_wall_clock_budget` is exceeded, halt in-flight nodes, emit whatever verified outputs exist, and tag the report `INCOMPLETE: budget exceeded`.
- If `total_token_budget` is exceeded mid-run, halt new dispatches, let in-flight nodes finish, emit a partial report tagged `INCOMPLETE: token budget exceeded`.
