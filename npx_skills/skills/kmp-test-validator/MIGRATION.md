# Conversion Note: `kmp-test-validator` → Swarm Skill

Converted from a single controller-support skill (a flat SKILL.md node registry plus 9 sibling node-spec files) into a compliant **Swarm Skill** using `swarmskill-creator` convert mode.

## Source structure (before)

- `SKILL.md` — node registry: node table, required dispatch order (10 steps), trigger boundary, shared return contract, and controller validation rules.
- 9 flat node specs at the skill root, each with Role / Inputs / Mandatory Input Validation & Output Storage / Specific Task / Required Outputs (JSON schema) / Return Shape.

## What was lost in the pre-swarm form

The registry separated controller from nodes and encoded the dispatch order, but it did not encode the team as a first-class artifact: no per-role anti-convergence mottos, no `Forbidden`/`Mandatory` boundary blocks the validator could check, no pasteable `Inline Persona` (each of the 9 dispatches re-derived its contract by hand), no Mermaid topology making the pipeline + remediation loop explicit, and no resource/behavioral guardrails (token/wall-clock budgets, `max_remediation_cycles`, degraded modes). The fidelity-before-tests gate, build-before-tests gate, "Android/SPEC is ground truth", and "never invent a command" invariants lived only in prose.

## Original 0.2 Decomposition

- **Pattern: C (specialization pipeline) + remediation loop.**
  - Gate: `validation-input-contract` (refuse non-migration scenarios).
  - Trust gate: `android-kmp-fidelity-audit` before tests are trusted.
  - Planning: `kmp-validation-plan` (resolve trusted commands; never invent).
  - Build gate: `build-preview-gate` before behavioral tests.
  - Tests: `test-case-decomposition` → `test-execution`.
  - Loop: `validation-remediation` ↔ build/preview gate + test execution.
  - Report: `validation-report` issues the final verdict.
  - Cross-cutting: `validation-workspace-state` ledger refreshed after each node group.
- **Disjointness check: PASS.** Each node owns a distinct slice (ledger vs scenario gate vs fidelity audit vs command planning vs build/preview gate vs case decomposition vs execution vs remediation vs report). The verification-style nodes never edit code (only `validation-remediation` does), and only `validation-report` issues the verdict.

## Content port map

| Source node-spec content | Ported to |
|---|---|
| `## Role` first paragraph | role `## Identity` (rewritten as a 1-line motto + context) |
| `## Specific Task` numbered steps | role `## Inline Persona for Teammate` HANDLER |
| `## Mandatory Input Validation And Output Storage` | role `## Boundary > Mandatory` + Inline Persona CONTROL block |
| implicit do-not / sibling routing | role `## Boundary > Forbidden` |
| `## Required Outputs` JSON schema | role `## Output Schema` + Inline Persona OUTPUTS |
| `## Return Shape` + shared return | role Inline Persona RETURN TO CONTROLLER + SKILL.md § Shared Return Contract |
| Required dispatch order (10 steps) | `workflow.md` staged steps + Mermaid + gates |
| Trigger boundary + controller validation rules | `bind.md` § Behavioral Constraints + SKILL.md § Shared Rules |
| Optional Android Studio MCP context | SKILL.md § Optional Android Studio MCP Context + per-role Inline Persona MCP inputs |

## Original Team-vs-single Delta

The 0.2 conversion preserved every source contract while adding: explicit pipeline + remediation-loop topology with verifiable gates, per-role anti-overlap boundaries that name siblings, self-contained pasteable personas (no re-derivation per dispatch across 9 nodes), resource/token/wall-clock budgets plus a `max_remediation_cycles` bound, failure-routing rules, and concrete degraded modes for missing commands, unsupported previews, and missing MCP.

## Role Reduction Refactor (0.3)

The current active validator reduces 9 roles to 6. See [ROLE_REDUCTION.md](ROLE_REDUCTION.md).

| Old role(s) | Active role |
|---|---|
| `validation-workspace-state` | `validation-workspace-state` |
| `validation-input-contract`, `android-kmp-fidelity-audit` | `validation-intake-fidelity` |
| `kmp-validation-plan`, `build-preview-gate` | `validation-plan-gate` |
| `test-case-decomposition`, `test-execution` | `validation-test-runner` |
| `validation-remediation` | `validation-remediation` |
| `validation-report` | `validation-report` |

The reduction keeps the important gates intact: migration trigger/fidelity trust gate, build-before-tests gate, scoped remediation with mandatory reruns, and report-only final verdict.
