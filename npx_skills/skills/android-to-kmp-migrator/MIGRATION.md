# Conversion Note: `android-to-kmp-migrator` → Swarm Skill

Converted from a single controller-support skill (a flat SKILL.md node registry plus 20 sibling node-spec files) into a compliant **Swarm Skill** using `swarmskill-creator` convert mode.

## Source structure (before)

- `SKILL.md` — node registry: node table, required dispatch order (13 controller steps), shared input contract, shared return shape, and shared rules.
- 20 flat node specs at the skill root, each with Role / Inputs / Mandatory Input Validation & Output Storage / Specific Task / Do-not list / Required Outputs (JSON schema) / Shared Return Shape / Return Shape.

## What was lost in the pre-swarm form

The registry separated controller from nodes and even encoded the staged dispatch order, but it did not encode the team as a first-class artifact: no per-role anti-convergence mottos, no `Forbidden`/`Mandatory` boundary blocks the validator could check, no pasteable `Inline Persona` (each of the 20 dispatches re-derived its contract by hand), no Mermaid topology making the pipeline + parallel fan-outs + review→fix loops explicit, and no resource/behavioral guardrails (parallel cap, token/wall-clock budgets, `max_review_fix_cycles`, degraded modes). Stage gates and the single-project / dependency-gate invariants lived only in prose.

## Decomposition

- **Pattern: C (specialization pipeline) + embedded B (parallel fan-outs) + review→fix loops.**
  - Serial analysis chain: `legacy-spec-delta-review` → `target-project-understand` → `migration-alignment`.
  - Hard gate: `dependency-resolution` (minimal-change) before any implementation.
  - Parallel prep (B): `theme-design-system-mapping`, `resource-migration`, `navigation-migration`, `platform-api-replacement`, `state-model-mapping`.
  - Sequential implementation: `ui-mockup-implementation` before `dataflow-logic-implementation`.
  - Review→fix loop after any file-changing node: `module-node-migration-review` ↔ `module-node-migration-fix`.
  - Parallel verify (B): `source-set-placement-guard`, `api-contract-parity`, `ui-render-fidelity-check`, `incremental-build-check`.
  - Completion + report: `prd-completion-check` → `migration-report` → `kmp-test-validator` handoff.
  - Cross-cutting: `migration-workspace-state` ledger refreshed after major completions.
- **Disjointness check: PASS.** Each node owns a distinct slice (state ledger vs SPEC delta vs target understanding vs alignment vs dependency gate vs theme vs resource vs navigation vs platform vs state/model vs UI vs logic vs review vs fix vs source-set guard vs API parity vs render vs build vs completion vs report). `module-node-migration-review` and `-fix` are intentionally complementary (read-only judge vs scoped editor) and gated as a loop, not overlapping.

## Content port map

| Source node-spec content | Ported to |
|---|---|
| `## Role` first paragraph | role `## Identity` (rewritten as a 1-line motto + context) |
| `## Specific Task` numbered steps | role `## Inline Persona for Teammate` HANDLER |
| `## Mandatory Input Validation And Output Storage` | role `## Boundary > Mandatory` + Inline Persona CONTROL block |
| `Do not:` lists + sibling routing | role `## Boundary > Forbidden` |
| `## Required Outputs` JSON schema | role `## Output Schema` + Inline Persona OUTPUTS |
| `## Return Shape` + shared return | role Inline Persona RETURN TO CONTROLLER + SKILL.md § Shared Return Shape |
| Required dispatch order (13 steps) | `workflow.md` staged steps + Mermaid + gates |
| Mandatory node contract enforcement + shared rules | `bind.md` § Behavioral Constraints + SKILL.md § Shared Rules |
| Shared return status semantics + controller handling | SKILL.md § Shared Return Shape |
| Optional Android Studio MCP context | SKILL.md § Optional Android Studio MCP Context + per-role Inline Persona MCP inputs |

## Team-vs-single delta

The conversion preserves every source contract while adding: explicit pipeline + parallel + loop topology with verifiable gates, per-role anti-overlap boundaries that name siblings, self-contained pasteable personas (no re-derivation per dispatch across 20 nodes), resource/token/wall-clock budgets plus a `max_review_fix_cycles` bound, failure-routing rules, and concrete degraded modes for large monorepos and missing tooling. The same-name controller subagent in `kmp-migration/agents/android-to-kmp-migrator.md` is unchanged in behavior; its node table now points at `roles/<id>.md`.
