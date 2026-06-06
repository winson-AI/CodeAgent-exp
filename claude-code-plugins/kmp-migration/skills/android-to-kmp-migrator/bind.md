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

## Behavioral Constraints

- **Skill chain (mandatory)**:
  - **Before migrator**: `android-project-analyst` MUST finish and produce package **P6** (`handoff_gates.P6.ready = true`). If P6 is missing or stale, return `blocked` and dispatch analyst — do not start migrator nodes.
  - **After migrator**: when package **V0** is ready, Leader MUST invoke `kmp-test-validator` (MG17). Migrator completion without validator dispatch is invalid.
- **Role schedule**: dispatch only role IDs listed in [SKILL.md](SKILL.md).
- **Mode discipline**:
  - `module-implementation`: `ui` then `logic` — separate invocations
  - `global-migration-phase`: `integrate` (edits) then `align` (read-only) — separate invocations
  - `module-node-review-fix`: `review` then optional `fix` then fresh `review`
- **TPA monopoly**: all target Q&A through `target-project-assistant`.
- **Analyst P6 gate**: required before dispatch.
- **Output contract**: [output-contract.md](output-contract.md) paths only.
- **Handoff gates**: persist **M0**–**M6**, **V0** in workspace ledger.

## Failure Handling

| Failure | Response |
|---|---|
| Unknown or invalid role ID | Reject; use role from `SKILL.md` registry |
| `ui` and `logic` combined | Reject invocation |
| `integrate` and `align` combined | Reject invocation |
| Verification restoration failed | Rerun `module-implementation` or `migration-prep`; no completion record |
| Align omissions | Rerun `rerun_modules` or `global-migration-phase integrate` |
| Entry point alignment failed | `rerun_global_integration` — rewire KMP app shell in integrate mode |
| Build requested in migrator | Block; route to kmp-test-validator |
| Migrator invoked before analyst P6 | Block; dispatch `android-project-analyst` first |
| V0 ready but validator not invoked | Block; dispatch `kmp-test-validator` at MG17 |

## Dependencies

Pre-flight reads [dependencies.yaml](dependencies.yaml): `rg`, `git`, `curl`, optional `jetbrains` MCP. Record per-role `used_by` in manifest.
