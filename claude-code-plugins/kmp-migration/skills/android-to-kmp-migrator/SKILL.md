---
name: android-to-kmp-migrator
description: |
  9-role reduced module-first Swarm Skill that migrates Legacy Android into an existing KMP target using upstream analyst P6 artifacts, target-project-assistant alignment, consolidated planning/prep/implementation roles, global integrate+align phase, and kmp-test-validator handoff — without full-project build during migration.
  Use when analyst package P6 exists and the user wants module-first porting then whole-system assembly.
  Do NOT use for Legacy Android analysis only, KMP-only feature work, or non-migration refactors.
version: "0.6"
kind: swarm-skill
disable-model-invocation: true
roles:
  - id: migration-workspace-state
    kind: ai_agent
    purpose: Migration ledger — handoff gates M0–V0, plan-vs-code gaps, stale outputs, rerun hooks. No code edits.
    skills: []
    tools: [git]
  - id: target-project-assistant
    kind: ai_agent
    purpose: Target KMP owner — global baseline, per-module anchors, alignment revision, consult log.
    skills: []
    tools: [rg]
  - id: migration-planning-gate
    kind: ai_agent
    purpose: Merged planning + dependency/platform gate — SPEC deltas, source-to-target map, capability map, ready_for_implementation.
    skills: []
    tools: [rg]
  - id: migration-prep
    kind: ai_agent
    purpose: Merged presentation + state/data prep — tokens, resources, routes, state/models/API expectations.
    skills: []
    tools: [rg, curl]
  - id: module-implementation
    kind: ai_agent
    purpose: Merged UI + logic implementation by mode — ui first, then logic after UI approval.
    skills: []
    tools: [rg]
  - id: module-node-review-fix
    kind: ai_agent
    purpose: Review or scoped fix by mode; fresh re-review after every fix.
    skills: []
    tools: [rg, git]
  - id: migration-verification
    kind: ai_agent
    purpose: Module static checks + UI/logic restoration vs analyst — no full project build.
    skills: []
    tools: [rg, git]
  - id: global-migration-phase
    kind: ai_agent
    purpose: Global integrate (cross-module wiring) then align (analyst vs target comparison) by mode.
    skills: []
    tools: [rg]
  - id: completion-report
    kind: ai_agent
    purpose: Readiness and migration_report modes; validation handoff to kmp-test-validator.
    skills: []
    tools: [rg, git]
---

# Android To KMP Migrator Swarm Skill

Reduced **9-role** module-first migrator. Consolidates overlapping planning, prep, implementation, and global-phase duties while preserving mode boundaries and safety gates.

**Canonical contract**: [output-contract.md](output-contract.md)

## Role Reduction Summary (13 → 9)

| Reduced role | Former roles merged |
|---|---|
| `migration-planning-gate` | `migration-analysis-planning` + `dependency-platform-gate` |
| `migration-prep` | `presentation-integration` + `state-data-prep` |
| `module-implementation` | `ui-implementation` + `logic-implementation` (`mode: ui \| logic`) |
| `global-migration-phase` | `global-system-integration` + `post-integration-alignment` (`mode: integrate \| align`) |

**Kept distinct**: `migration-workspace-state`, `target-project-assistant`, `module-node-review-fix`, `migration-verification`, `completion-report`.

## Protocol Summary

0. Pre-flight — [dependencies.yaml](dependencies.yaml): `rg` / `git` / `curl`, optional `jetbrains` MCP (`optional_mcp`), upstream analyst **P6** (`upstream_inputs`); record `dependency_preflight` in `run_manifest.json`.
1. Verify analyst **P6**; `run_manifest.json`, `upstream_analyst_index.json`.
2. Migration inventory + `modules_migration_index.json`.
3. Workspace state init.
4. TPA `global_baseline`.
5. **Per module** (assembly_order): TPA `module_anchors` → **planning-gate** → **prep** → review/fix → **implementation `ui`** → review/fix → **implementation `logic`** → review/fix → verification → completion record → readiness → module representation.
6. **Global phase `integrate`** → **`align`** + alignment report.
7. Global representation + completion-report `report` mode.
8. **kmp-test-validator** when **V0** ready.

## Roles

| id | Modes | Role file |
|---|---|---|
| `migration-workspace-state` | — | [roles/migration-workspace-state.md](roles/migration-workspace-state.md) |
| `target-project-assistant` | `global_baseline`, `module_anchors`, `consult` | [roles/target-project-assistant.md](roles/target-project-assistant.md) |
| `migration-planning-gate` | — | [roles/migration-planning-gate.md](roles/migration-planning-gate.md) |
| `migration-prep` | — | [roles/migration-prep.md](roles/migration-prep.md) |
| `module-implementation` | `ui`, `logic` | [roles/module-implementation.md](roles/module-implementation.md) |
| `module-node-review-fix` | `review`, `fix` | [roles/module-node-review-fix.md](roles/module-node-review-fix.md) |
| `migration-verification` | — | [roles/migration-verification.md](roles/migration-verification.md) |
| `global-migration-phase` | `integrate`, `align` | [roles/global-migration-phase.md](roles/global-migration-phase.md) |
| `completion-report` | `readiness`, `report` | [roles/completion-report.md](roles/completion-report.md) |

## Files

| File | Contents |
|---|---|
| [output-contract.md](output-contract.md) | Paths, upstream P6, packages M0–V0 |
| [workflow.md](workflow.md) | Topology, steps, gates |
| [bind.md](bind.md) | Limits, constraints, failures |
| [dependencies.yaml](dependencies.yaml) | CLI + optional MCP per role |
| [roles/](roles/) | Nine active role specs |

## Handoff Gates

| Package | Unlocks |
|---|---|
| `M2` | Target alignment (TPA) |
| `M3` | Per-module complete |
| `M4` | All modules migrated |
| `M5` | Global integrate |
| `M6` | Global align passed |
| `V0` | kmp-test-validator |

## Shared Rules

- Analyst **P6** required; TPA owns all target Q&A.
- Mode boundaries non-negotiable: `ui`/`logic`, `integrate`/`align`, `review`/`fix`.
- No full project build in migrator.
- JSON artifacts are machine-routable source of truth.
