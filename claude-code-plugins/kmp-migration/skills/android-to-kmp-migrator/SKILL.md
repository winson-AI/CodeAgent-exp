---
name: android-to-kmp-migrator
description: |
  Module-first Swarm Skill that migrates Legacy Android into an existing KMP target by editing target KMP source after analyst P6 understanding — planning/prep/implementation roles create and update files under kmp_target_project_path, global integrate wires cross-module glue, then mandatory kmp-test-validator handoff — without full-project build during migration.
  Use only after android-project-analyst has finished and package P6 is ready, when the user wants module-first porting with real target code changes then whole-system assembly followed by validation.
  Do NOT invoke before android-project-analyst completes P6. Do NOT treat planning or analysis artifacts alone as migration success — target KMP files MUST be edited. Do NOT treat migrator completion as final without invoking kmp-test-validator at V0. Do NOT use for Legacy Android analysis only, KMP-only feature work, or non-migration refactors.
version: "0.9"
kind: swarm-skill
disable-model-invocation: false
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
    purpose: Planning and dependency/platform gate — SPEC deltas, source-to-target map, capability map, ready_for_implementation.
    skills: []
    tools: [rg]
  - id: migration-prep
    kind: ai_agent
    purpose: Presentation and state/data prep — tokens, resources, routes, state/models/API expectations.
    skills: []
    tools: [rg, curl]
  - id: module-implementation
    kind: ai_agent
    purpose: Target KMP module implementation by mode — edit/create KMP UI files first, then logic after UI approval.
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
    purpose: Target KMP global integrate (edit cross-module glue + entry point wiring) then align (read-only analyst vs target comparison incl. entry points) by mode.
    skills: []
    tools: [rg]
  - id: completion-report
    kind: ai_agent
    purpose: Readiness and migration_report modes; validation handoff to kmp-test-validator.
    skills: []
    tools: [rg, git]
---

# Android To KMP Migrator Swarm Skill

Module-first migrator for Legacy Android → KMP target assembly. **Upstream analyst P6 is read-only input; this skill's job is to edit the target KMP project** under `kmp_target_project_path`.

**Canonical contract**: [output-contract.md](output-contract.md)

## Protocol Summary

0. Pre-flight — [dependencies.yaml](dependencies.yaml): `rg` / `git` / `curl`, optional `jetbrains` MCP (`optional_mcp`), upstream analyst **P6** (`upstream_inputs`); **identify `design_mode` from user input (default `mvi`)**; record `dependency_preflight` and `design_mode` in `run_manifest.json`.
1. Verify analyst **P6**; `run_manifest.json`, `upstream_analyst_index.json`.
2. Migration inventory + `modules_migration_index.json`.
3. Workspace state init.
4. TPA `global_baseline`.
5. **Per module** (assembly_order): TPA `module_anchors` → **planning-gate** → **prep** → review/fix → **implementation `ui`** → review/fix → **implementation `logic`** → review/fix → verification → completion record → readiness → module representation.
6. **Global phase `integrate`** (cross-module glue + **entry point wiring**) → **`align`** (incl. **entry point alignment** vs Android) + alignment report.
7. Global representation + completion-report `report` mode.
8. **kmp-test-validator** — **mandatory** when **V0** ready (MG17).

## Design Mode (architecture pattern)

The migrator targets one presentation architecture per run, selected at **pre-flight (Step 0)** by the Leader from the **user input**, then frozen for the whole run and recorded in `run_manifest.json` → `design_mode`.

| `design_mode` | Architecture reference | When chosen |
|---|---|---|
| `mvi` **(default)** | [references/kmp-mvi-flowredux.md](references/kmp-mvi-flowredux.md) | Default when user input gives no clear signal; or user mentions MVI, FlowRedux, state machine, reducer, intent, unidirectional, sealed `State`/`Action`, `dispatch`, `inState`, `onEnter` |
| `mvvm` | [references/kmp-mvvm.md](references/kmp-mvvm.md) | User mentions MVVM, shared `ViewModel`, `StateFlow`/`uiState`, `viewModelScope`, `collectAsStateWithLifecycle`, KMP-ObservableViewModel, SKIE |

Both modes also follow [references/kmp-expert.md](references/kmp-expert.md) for base KMP/CMP conventions.

**Rules**:
- **Default is `mvi`** — when the user input contains no explicit or implied architecture signal, the Leader MUST select `mvi`.
- Record the decision as `design_mode: { value, source: "user_input | default", signals: [] }` in `run_manifest.json` at **MG0**.
- The Leader passes `design_mode` and the resolved `architecture_reference_path` to every architecture-producing role (planning-gate, prep, module-implementation, module-node-review-fix, global-migration-phase) and to TPA for target-pattern detection.
- `design_mode` is **fixed for the run**; a mid-run change requires a fresh run, not in-place mutation.

## Skill Chain (mandatory)

```text
android-project-analyst (P6) → android-to-kmp-migrator (M0–V0) → kmp-test-validator (V0)
```

| Order | Skill | Gate | Rule |
|---|---|---|---|
| 1 | `android-project-analyst` | **P6** | MUST finish before migrator dispatch. If P6 missing/stale → run analyst first; migrator returns `blocked`. |
| 2 | `android-to-kmp-migrator` | **M0**–**V0** | Runs only on analyst P6 artifacts; produces `migration_report.*` at **V0**. |
| 3 | `kmp-test-validator` | **V0** | MUST be invoked after migrator **V0**; migration incomplete without validator dispatch. |

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
| [roles/](roles/) | Role specs |
| [references/](references/) | Architecture references: `kmp-mvi-flowredux.md` (MVI, default), `kmp-mvvm.md` (MVVM), `kmp-expert.md` (base KMP/CMP) |

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

- **Skill chain**: `android-project-analyst` **P6** before migrator; `kmp-test-validator` **after** migrator **V0** — both mandatory.
- **Design mode**: identified from user input at pre-flight, **default `mvi`**; frozen for the run; architecture-producing roles MUST follow the resolved `architecture_reference_path` (`kmp-mvi-flowredux.md` for `mvi`, `kmp-mvvm.md` for `mvvm`).
- **Target KMP edit mandate**: after analyst P6 understanding, migrator roles MUST create or update production files under `kmp_target_project_path`. Planning-only or artifact-only completion is invalid.
- **Roles that edit target** (record `changed_files[]` or `integration_changed_files[]`):
  - `migration-prep` — optional scaffold edits (theme, resources, routes, models) when planning allows
  - `module-implementation` `ui` / `logic` — required per-module UI and logic port
  - `module-node-review-fix` `fix` — scoped remediation in `allowed_files`
  - `global-migration-phase` `integrate` — cross-module glue and entry-point wiring
- **Read-only on target**: `target-project-assistant`, `migration-planning-gate`, `migration-verification`, `global-migration-phase` `align`, `completion-report`.
- Analyst **P6** required; TPA owns all target Q&A.
- Mode boundaries non-negotiable: `ui`/`logic`, `integrate`/`align`, `review`/`fix`.
- No full project build in migrator.
- JSON artifacts are machine-routable source of truth.
