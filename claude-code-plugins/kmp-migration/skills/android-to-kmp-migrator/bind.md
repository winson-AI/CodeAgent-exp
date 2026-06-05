# Execution Guardrails

## Resource Constraints

| Item | Limit | Reason |
|---|---|---|
| `max_parallel_teammates` | 1 | Reduced pipeline is serial per module (prep and planning-gate consolidated) |
| `total_wall_clock_budget` | 90 min per module batch | 9-role reduced schedule |
| `total_token_budget` | 1.2M tokens per batch | Fewer dispatches; broader consolidated role context |
| `per_node_token_budget` | 160k tokens | Consolidated roles (planning-gate, prep, module-implementation) |
| `max_review_fix_cycles` | 3 per slice | Before `blocked` escalation |
| `active_role_count` | 9 | Do not dispatch superseded 13-role IDs |

## Build Boundary

- Migrator: `syntax_check`, static checks, restoration parity only.
- **Forbidden**: `incremental_build` in migrator.
- **kmp-test-validator**: full compile/build/test at package **V0**.

## Behavioral Constraints

- **9-role schedule only**: active role IDs are listed in [SKILL.md](SKILL.md). Superseded 13-role IDs are invalid returns.
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
| Superseded role ID dispatched | Reject; use reduced role from `SKILL.md` § Role Reduction Summary |
| `ui` and `logic` combined | Reject invocation |
| `integrate` and `align` combined | Reject invocation |
| Verification restoration failed | Rerun `module-implementation` or `migration-prep`; no completion record |
| Align omissions | Rerun `rerun_modules` or `global-migration-phase integrate` |
| Build requested in migrator | Block; route to kmp-test-validator |

## Dependencies

Pre-flight reads [dependencies.yaml](dependencies.yaml): `rg`, `git`, `curl`, optional `jetbrains` MCP. Record per-role `used_by` in manifest.
