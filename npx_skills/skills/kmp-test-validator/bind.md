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
- **Dependency order**: workspace → fidelity-gate `trust` → code-gate `build` → [fix loop] → fidelity-gate `restoreability` → [supplement loop] → business-testing → report.
- **Read-only fidelity**: `validation-fidelity-gate` never runs commands or edits code.
- **Single production editor**: only `validation-code-gate` mode `fix` edits target production code.
- **Three compile scenarios**: `user_specified` → `global_tool_search` → `default_gradle_kmp`.
- **Two fix knowledge paths**: `error_knowledge_path` when configured; else `model_inference`.
- **Restoreability-preserving fixes**: no delete/stub of migrated behavior; missing modules → migrator supplement.
- **Optional business testing**: submodules require user inputs; skip is not pass-by-omission.
- **Report-only verdict**: only `validation-report` issues `passed | failed | blocked`.

## Failure Handling

| Failure mode | Response |
|---|---|
| Code-gate `build` compile failed | Code-gate mode `fix` → rerun `build` |
| Fidelity-gate `restoreability` needs supplement | Leader invokes migrator if under max cycles |
| Fix uses forbidden delete/stub | Reject; record violation; route supplement or `blocked` |
| Fix cycles exhausted | `blocked` with evidence |
| Business submodule failure | Code-gate `fix` if target-code; else `failed` |
| Unknown or invalid role ID | Re-dispatch with active role + mode from `SKILL.md` |

## Degraded Modes

| Trigger | Effect |
|---|---|
| Migrator V0 not ready | `blocked` |
| No `error_knowledge_path` | Fix uses `model_inference` only |
| No test cases or Figma refs | `VG4` skipped explicitly |
| Preview unsupported | Build only; preview `skipped` with reason |
| jetbrains / Figma MCP unavailable | Gradle + filesystem; record gap |
