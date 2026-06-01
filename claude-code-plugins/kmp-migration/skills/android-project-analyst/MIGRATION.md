# Conversion Note: `android-project-analyst` → Swarm Skill

This skill was converted from a single controller-support skill (a flat SKILL.md registry plus 7 sibling node-spec files) into a compliant **Swarm Skill** using `swarmskill-creator` convert mode.

## Source structure (before)

- `SKILL.md` — controller registry describing convert mode, node contracts, dispatch order, and the SPEC output contract.
- 7 flat node specs at the skill root: `ui-understand.md`, `architecture-pattern.md`, `android-ecosystem.md`, `api-list.md`, `resource-understand.md`, `data-flow.md`, `logic-understand.md`. Each contained Role / Inputs / Mandatory Input Validation & Output Storage / Specific Task / Required Outputs / Return Format / Self-Check.

## What was lost in the pre-swarm form

The registry already separated controller from nodes, but it did not encode the team as a first-class artifact: there were no per-role anti-convergence mottos, no `Forbidden`/`Mandatory` boundary blocks the validator could check, no pasteable `Inline Persona` (so each dispatch re-derived the contract by hand), no Mermaid topology making the parallel-then-pipeline shape explicit, and no resource/behavioral guardrails (`max_parallel_teammates`, token/wall-clock budgets, degraded modes). The handoff gates between stages lived only in prose.

## Decomposition

- **Pattern: Mixed B + C.** Stage A (`ui-understand`, `architecture-pattern`, `android-ecosystem`, `api-list`) is parallel decomposition (B) over disjoint slices. Stage B (`resource-understand`, `data-flow`) and Stage C (`logic-understand`) form a specialization pipeline (C) with hard handoff gates — each consumes verified upstream outputs and must not rebuild them.
- **Disjointness check: PASS.** No node's deliverable can substitute for another's — UI surface vs. architecture style vs. platform ecosystem vs. API contracts vs. resources vs. data movement vs. control-flow behavior are mutually exclusive ownership domains, enforced by each role's `## Boundary > Forbidden` naming its siblings.

## Content port map

| Source node-spec content | Ported to |
|---|---|
| `## Role` first paragraph | role `## Identity` (rewritten as a 1-line motto + context) |
| `## Specific Task` numbered steps | role `## Inline Persona for Teammate` HANDLER |
| `## Mandatory Input Validation And Output Storage` | role `## Boundary > Mandatory` + Inline Persona CONTROL block |
| `Do not:` lists + sibling routing | role `## Boundary > Forbidden` |
| `## Required Outputs` JSON/MD | role `## Output Schema` + Inline Persona OUTPUTS |
| `## Return Format` | role Inline Persona RETURN TO CONTROLLER |
| `## Self-Check` | role `## Success Criteria` |
| Controller dispatch order + verification | `workflow.md` (staged steps + gates) |
| Mandatory contract enforcement + agent-only rules | `bind.md` § Behavioral Constraints |
| Node failure / rerun handling | `bind.md` § Failure Handling |
| SPEC output contract + MCP context | `SKILL.md` body (preserved) |

## Team-vs-single delta

The conversion preserves every source contract while adding: explicit parallel/pipeline topology with verifiable gates, per-role anti-overlap boundaries that name siblings, self-contained pasteable personas (no re-derivation per dispatch), resource/token/wall-clock budgets, and concrete degraded modes for large monorepos and missing tooling. The same-name controller subagent in `kmp-migration/agents/android-project-analyst.md` is unchanged in behavior; its `Control Nodes` table now points at `roles/<id>.md`.
