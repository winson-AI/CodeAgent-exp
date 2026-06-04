# Execution Guardrails

## Resource Constraints

| Item | Limit | Reason |
|---|---|---|
| `max_parallel_teammates` | 1 | The validator is a strict serial pipeline — each node consumes the prior node's verified artifact; no stage fans out in parallel. |
| `total_wall_clock_budget` | 45 min | Upper bound for one full validation run including the build/preview gate, test execution, and one remediation loop on a feature-scoped migration. |
| `total_token_budget` | 600k tokens | Budget across 6 reduced roles + Leader integration + remediation iterations. |
| `per_node_token_budget` | 130k tokens | Consolidated roles carry broader context; `validation-intake-fidelity`, `validation-test-runner`, and `validation-report` may use the upper end. |
| `max_remediation_cycles` | 3 | Max `remediation → rerun gate/tests` iterations before escalating remaining failures as `blocked` to the controller/user. |
| `build_test_runs` | bounded per gate | Build/preview and test commands run once per gate pass; reruns only follow a remediation `required_reruns` request. |

## Behavioral Constraints

Team-level rules — distinct from each role's own `## Boundary`.

- **Leader-as-orchestrator only**: the Leader (`kmp-test-validator` controller) gates the migration scenario, dispatches nodes in dependency order, validates return payloads + output files, refreshes workspace state, and routes reruns. The Leader does NOT perform a node's detailed audit, run its tests, or apply its fixes.
- **Strict validation output root**: the Leader must lock `output_root = <output_dir or ~/.a2c_agents/validation>/kmp-test-validator` before validator node dispatch. When a migration output root is provided, validation must be written to a parallel `validation` base location, not inside the migration output root. Migration artifacts are read-only inputs referenced by path.
- **Per-node exact paths**: validator nodes write only under the declared validation output root: `workspace-state`, `intake-fidelity`, `plan-gate`, `test-runner`, `remediation/<cycle_id>`, `report`, and `logs`.
- **Role-output content discipline**: required artifacts must contain the content owned by their role, not just the correct filename. `validation_intake_fidelity.*` must contain migration/fidelity trust evidence; `validation_plan_gate.*` must contain trusted commands and build/preview gate evidence; `validation_test_runner.*` must contain Android-anchored cases/results; `validation_remediation.*` must contain confirmed target fixes and required reruns; `kmp_validation_report.*` must contain the final evidence-based verdict.
- **Migration-scenario trigger boundary**: this team validates ONLY Android-to-KMP migration output. If `validation-intake-fidelity` cannot confirm migration evidence (KMP target + Android source/SPEC + migration report/completion), the run is `blocked` — it is never downgraded to generic KMP testing, KMP-only feature work, or isolated Gradle troubleshooting.
- **Hard dependency order (C-pattern)**: workspace state → intake/fidelity → plan/build gate → test runner → remediation loop → report. Fidelity is audited before tests are trusted; the build/preview gate passes before behavioral tests run. A downstream role references upstream outputs by path and must NOT rebuild them; on missing/stale upstream input it returns `needs_rerun`/`blocked`.
- **Android/SPEC is ground truth**: a passing test (or green build) that contradicts Android source/SPEC behavior is a validation failure, not a pass.
- **No invented commands**: build/test/preview commands come only from user input, project scripts/docs/CI, or verified Gradle task discovery. A node that cannot resolve a trustworthy command returns `blocked`.
- **Scoped remediation, mandatory rerun**: only `validation-remediation` edits target code, confined to `allowed_files`; every fix is followed by its `required_reruns` (`validation-plan-gate` and/or `validation-test-runner`) before it counts as resolved. No fix introduces TODO/FIXME or sample-only production data.
- **Stale-artifact discipline**: `validation-workspace-state` is refreshed after each node group; `validation-report` runs only when no required input is stale.
- **Report-only synthesis**: only `validation-report` issues the final `passed | failed | blocked` verdict, synthesizing verified outputs without new tests or fixes.

## Failure Handling

### (a) Teammate failure

| Failure mode | Response |
|---|---|
| Node timeout | Retry once with the same contract. On 2nd timeout, mark the node `[ROLE MISSING — node timed out]` in the workspace ledger; downstream nodes that hard-require it return `blocked`. |
| Malformed output (does not match role `## Output Schema` / shared return, files missing/empty, writes outside validation output root, or artifact content does not match the role duty) | Re-dispatch once with the schema, exact output path, and role-owned output content inlined plus a "previous output was malformed/missing/out-of-duty/out-of-path" preamble. On 2nd failure, mark `[ROLE MISSING — malformed output]`. |
| Node returns `needs_rerun` / `blocked` (missing or stale upstream input) | Refresh/re-run the named upstream node first, then re-dispatch this node. If unresolvable, record the `blocking_gap`. |
| `validation-plan-gate` or `validation-test-runner` returns `failed` | Route fixable target-code failures to `validation-remediation`; on its `required_reruns`, re-run the affected gate/tests. Non-target failures route to migration node / user / environment. |
| Remediation loop does not converge in `max_remediation_cycles` | Escalate remaining failures as `blocked` with evidence to the controller/user; do not mark `passed`. |
| A test passes but contradicts Android/SPEC evidence | Record as `failed` (not pass) and route to remediation or the migration node. |

### (b) Input over-scale degradation

| Trigger condition | Degraded mode |
|---|---|
| Whole-project validation scope with a very large test inventory | Scope `validation-test-runner` to the migrated modules in scope; mark untested areas explicitly in the report rather than running unrelated suites. |
| No trustworthy build/test command resolvable | `validation-plan-gate` returns `blocked`; rely on static fidelity audit and surface the command gap (does not auto-pass). |
| Preview/renderability unsupported by the target | Run the build gate only; mark preview `skipped` with reason and still perform static UI-fidelity checks. |
| `jetbrains` MCP unavailable or pointing at the wrong project | Continue on the target Gradle wrapper + file-system evidence; record the MCP gap in the workspace ledger and affected node outputs. |

### Escalation rules

- If 50%+ of dispatched nodes return `[ROLE MISSING]`, the run is **FAILED** — emit a partial validation report with a `FAILED: insufficient node coverage` header, status `blocked`, and the missing-evidence list.
- If `total_wall_clock_budget` is exceeded, halt in-flight nodes, checkpoint via `validation-workspace-state`, emit whatever verified outputs exist, and tag the report `INCOMPLETE: budget exceeded`.
- If `total_token_budget` is exceeded mid-run, halt new dispatches, let in-flight nodes finish, checkpoint, and emit a partial report tagged `INCOMPLETE: token budget exceeded`.

## Required Path Contract

```json
{
  "output_root": "<output_dir or ~/.a2c_agents/validation>/kmp-test-validator",
  "workspace_state_dir": "<output_root>/workspace-state",
  "intake_dir": "<output_root>/intake-fidelity",
  "plan_gate_dir": "<output_root>/plan-gate",
  "test_runner_dir": "<output_root>/test-runner",
  "remediation_dir": "<output_root>/remediation",
  "report_dir": "<output_root>/report",
  "logs_dir": "<output_root>/logs"
}
```

Validator artifacts outside this path contract are invalid. Migration artifacts remain in their migration output location and are never overwritten or copied as validator outputs.
