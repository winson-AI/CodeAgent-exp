# Execution Guardrails

## Resource Constraints

| Item | Limit | Reason |
|---|---|---|
| `max_parallel_teammates` | 1 | Serial pipeline per module |
| `total_wall_clock_budget` | 90 min per module batch | Module-first migration schedule |
| `total_token_budget` | 1.2M tokens per batch | Leader + role dispatches per module |
| `per_node_token_budget` | 160k tokens | Planning-gate, prep, module-implementation carry broader context |
| `max_review_fix_cycles` | 3 per slice | Before `blocked` escalation |

## Build Boundary

- Migrator: `syntax_check`, static checks, restoration parity only.
- **Forbidden**: `incremental_build` in migrator.
- **kmp-test-validator**: full compile/build/test at package **V0**.

## Target KMP Edit Mandate

- Analyst **P6** is read-only input. Migrator success requires **editing the target KMP project** at `kmp_target_project_path`.
- **Edit-owning roles**: `migration-prep` (optional scaffold), `module-implementation` `ui`/`logic` (required), `module-node-review-fix` `fix`, `global-migration-phase` `integrate`.
- **Read-only on target**: TPA, `migration-planning-gate`, `migration-verification`, `global-migration-phase` `align`, `completion-report`.
- When planning tasks require file changes, `changed_files[]` MUST be non-empty and paths MUST resolve under `kmp_target_project_path`.
- `migration_report.json` MUST aggregate `target_changed_files[]` before **V0**.

## Behavioral Constraints

- **Skill chain (mandatory)**:
  - **Before migrator**: `android-project-analyst` MUST finish and produce package **P6** (`handoff_gates.P6.ready = true`). If P6 is missing or stale, return `blocked` and dispatch analyst — do not start migrator nodes.
  - **After migrator**: when package **V0** is ready, Leader MUST invoke `kmp-test-validator` (MG17). Migrator completion without validator dispatch is invalid.
- **Design mode**: at pre-flight the Leader identifies `design_mode` from user input — **default `mvi`** when no architecture signal is present. It is recorded in `run_manifest.json`, **frozen for the run**, and every architecture-producing role MUST follow the resolved `architecture_reference_path` (`references/kmp-mvi-flowredux.md` for `mvi`, `references/kmp-mvvm.md` for `mvvm`). Both modes also follow `references/kmp-expert.md`.
- **Role schedule**: dispatch only role IDs listed in [SKILL.md](SKILL.md).
- **Mode discipline**:
  - `module-implementation`: `ui` then `logic` — separate invocations
  - `global-migration-phase`: `integrate` (edits) then `align` (read-only) — separate invocations
  - `module-node-review-fix`: `review` then optional `fix` then fresh `review`
- **TPA monopoly**: all target Q&A through `target-project-assistant`.
- **Analyst P6 gate**: required before dispatch.
- **Output contract**: [output-contract.md](output-contract.md) paths only.
- **Handoff gates**: persist **M0**–**M6**, **V0** in workspace ledger.
- **State monitor discipline**: `migration-workspace-state` MUST refresh `migration_todo_list[]` and `pipeline_steps[]` after every major group. Leader reads `migration_status.pipeline_summary.current_step_id` and pending todos before dispatch; do not skip refresh between node groups.

## Failure Handling

| Failure | Response |
|---|---|
| Unknown or invalid role ID | Reject; use role from `SKILL.md` registry |
| `design_mode` not identified at pre-flight | Default to `mvi`; record `source: default` in `run_manifest.json` |
| Architecture-producing dispatch missing `design_mode` | Reject; re-dispatch with `design_mode` + `architecture_reference_path` |
| Code produced against wrong architecture vs `design_mode` | `needs_rerun` owning role with correct reference |
| `ui` and `logic` combined | Reject invocation |
| `integrate` and `align` combined | Reject invocation |
| Verification restoration failed | Rerun `module-implementation` or `migration-prep`; no completion record |
| Analytics restoration failed (`analytics_restoration` check or `global_alignment_results.analytics` failed) | Rerun `module-implementation` `logic` for missing 埋点; rerun `global-migration-phase integrate` for SDK wiring gaps |
| Align omissions | Rerun `rerun_modules` or `global-migration-phase integrate` |
| Entry point alignment failed | `rerun_global_integration` — rewire KMP app shell in integrate mode |
| Build requested in migrator | Block; route to kmp-test-validator |
| Migrator invoked before analyst P6 | Block; dispatch `android-project-analyst` first |
| V0 ready but validator not invoked | Block; dispatch `kmp-test-validator` at MG17 |
| Analysis/planning only — no target edits when required | Block package M3; rerun `module-implementation` or `migration-prep` |
| `changed_files` outside `kmp_target_project_path` | Block; rerun owning edit role |
| Empty `target_changed_files` in `migration_report.json` when scope required edits | Block package V0 |

## Dependencies

Pre-flight reads [dependencies.yaml](dependencies.yaml): `rg`, `git`, `curl`, optional `jetbrains` MCP. Record per-role `used_by` in manifest.
