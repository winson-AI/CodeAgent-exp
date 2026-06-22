# Execution Guardrails

## Resource Constraints

| Item | Limit | Reason |
|---|---|---|
| `max_parallel_teammates` | 1 | Serial pipeline with mode dispatches |
| `total_wall_clock_budget` | 45 min | Full validation including loops |
| `total_token_budget` | 600k tokens | Leader + role dispatches + loops |
| `per_node_token_budget` | 130k tokens | Mode-based roles carry broader context |
| `max_fix_cycles` | 3 | Max code-gate `fix` → rerun `build`/business-testing iterations |
| `max_migrator_supplement_cycles` | 3 | Max restoreability gap → migrator supplement iterations |

## Behavioral Constraints

- **Leader orchestrates only** — dispatches roles with explicit `mode`; runs both controller loops.
- **Canonical contract**: [output-contract.md](output-contract.md) wins on paths and `VG0`–`VG5`.
- **Role schedule**: dispatch only role IDs listed in [SKILL.md](SKILL.md).
- **Dependency order**: workspace → fidelity-gate `trust` → code-gate `build` → [fix loop] → business-testing `entry_point_launch` → fidelity-gate `restoreability` → [supplement loop] → optional business-testing submodules → report.
- **Read-only fidelity**: `validation-fidelity-gate` never runs commands or edits code.
- **Single production editor**: only `validation-code-gate` mode `fix` edits target production code.
- **Three compile scenarios**: `user_specified` → `global_tool_search` → `default_gradle_kmp`.
- **Compile error knowledge loop**: fix mode looks up `code-gate/knowledge/compile_error_knowledge.json` first, then optional `error_knowledge_path`, then `model_inference`; verified fixes persist under `knowledge/entries/` after `VG2` pass.
- **Restoreability-preserving fixes**: no delete/stub of migrated behavior; missing modules → migrator supplement.
- **Mandatory entry point launch**: `entry_point_launch` runs for every migration `V0` handoff after `VG2`; optional business submodules require user inputs; skip is not pass-by-omission.
- **Partial mock-machine scope**: approved mock-machine harnesses may satisfy only partial migration current-module checks. They must be explicit in preflight, scoped to current module/feature, non-release (`must_not_ship`), and recorded in build/restoreability/report artifacts.
- **State monitor discipline**: `validation-workspace-state` MUST refresh `validation_todo_list[]` and `pipeline_steps[]` after every validator node group; Leader reads `validation_status.pipeline_summary.current_step_id` before next dispatch.
- **Report-only verdict**: only `validation-report` issues `passed | failed | blocked`.

## Failure Handling

| Failure mode | Response |
|---|---|
| Code-gate `build` compile failed | Code-gate mode `fix` → rerun `build` |
| Fidelity-gate `restoreability` needs supplement | Leader invokes migrator if under max cycles |
| Fix uses forbidden delete/stub | Reject; record violation; route supplement or `blocked` |
| Fix cycles exhausted | `blocked` with evidence |
| Entry point launch failure | Code-gate mode `fix` if shell/glue fixable → rerun `build` and `entry_point_launch`; else migrator supplement via restoreability |
| Business submodule failure | Code-gate `fix` if target-code; else `failed` |
| Mock machine requested for full-project validation | Reject; only partial current-module checks may use mock machine |
| Mock machine used without preflight approval | Block and rerun without mock or add explicit approved preflight |
| Mock machine masks missing migrated logic | Fail restoreability; route to migrator supplement |
| Unknown or invalid role ID | Re-dispatch with active role + mode from `SKILL.md` |

## Degraded Modes

| Trigger | Effect |
|---|---|
| Migrator V0 not ready | `blocked` |
| No local knowledge index yet | Leader initializes empty `compile_error_knowledge.json` |
| No knowledge match and no `error_knowledge_path` | Fix uses `model_inference` |
| No test cases or Figma refs | Optional `VG4` submodules skipped explicitly — `entry_point_launch` still required |
| Launch environment unavailable | `entry_point_launch` `blocked` unless post-build static entry evidence verified on disk |
| Partial module dependency unavailable and mock machine approved | Run scoped current-module check with mock-machine evidence; final report marks release replacement follow-up |
| Preview unsupported | Build only; preview `skipped` with reason |
| jetbrains / Figma MCP unavailable | Gradle + filesystem; record gap |
