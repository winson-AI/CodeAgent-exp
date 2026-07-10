# Skill Catalog

> Per-skill and per-role I/O cheat sheet for KMP migration and `flow_d2c`.  
> Canonical definitions: `skills/*/SKILL.md` + `roles/*.md` + `output-contract.md`.  
> Related: [Home](Home.md) · [Architecture](Architecture.md) · [Roadmap](Roadmap.md)

---

## 1. KMP migration swarm skills

### Index

| Skill | Version | Kind | Primary gates |
| --- | --- | --- | --- |
| [coding-task-adapter](#11-coding-task-adapter) | 0.2 | Front-door router | A0–A6 |
| [android-project-analyst](#12-android-project-analyst) | 0.8 | Understand / SPEC | P0–P6 |
| [android-to-kmp-migrator](#13-android-to-kmp-migrator) | 0.9 | Target code edits | M0–V0 |
| [kmp-test-validator](#14-kmp-test-validator) | 0.6 | Validate + fix loops | VG0–VG5 |
| [operating-instructions](#15-operating-instructions) | — | Shared conduct | — |
| [ponytail](#16-ponytail--ponytail-review) | — | Coding guardrail | — |
| [ponytail-review](#16-ponytail--ponytail-review) | — | Over-engineering review | — |

---

### 1.1 `coding-task-adapter`

**Purpose:** Classify Android/KMP requests, route understand/migration/validation, enforce stage gates, emit the final adapter report.

**Use when:** A controller must decide intent and invoke the right downstream workflow.  
**Do not use for:** Direct source lookup, single-file edits, generic KMP testing without migration context, standalone implementation.

| Role | Modes | Purpose | Key inputs | Key outputs |
| --- | --- | --- | --- | --- |
| `task-route-orchestrator` | `route` \| `orchestrate` | Classify intent / build dispatch contracts | User request, paths | `task_route.*`, `workflow_orchestration.*`, `downstream_workflow_index.*` |
| `adapter-workspace-state` | — | Ledger, stage inspections, asset freshness | Route + downstream roots | `adapter_workspace_state.*`, `stage_inspection.*`, `intermediate_asset_records.*` |
| `adapter-report` | — | Final verdict from verified evidence | All stage evidence | `adapter_report.*` |

**Routes:** `only_understand_ui` \| `_logic` \| `_architecture` \| `_overview` \| `migration` \| `validation_handoff`

**Output root:** `<agents_root>/task-adapter/coding-task-adapter`

---

### 1.2 `android-project-analyst`

**Purpose:** Module-first conversion of Legacy Android (or KMP target) into dimension artifacts, global representation, and SPEC.

**Use when:** Understand, onboard, or migration-prep an Android/KMP project by modules and four dimensions.  
**Do not use for:** Quick symbol lookup, non-Android codebases, single-agent skill authoring.

| Role | Modes | Purpose | Key inputs | Key outputs |
| --- | --- | --- | --- | --- |
| `analysis-workspace-state` | — | Module/node ledger, P0–P6, todos | Manifest, module index | `analysis_workspace_state.*` |
| `presentation-resource` | — | Screens, UI tech, nav, resources | Module scope, source roots | `presentation_resource.*`, downloads |
| `project-architecture` | — | Gradle topology, layers, DI, platform | Module scope | `project_architecture.*` |
| `data-contract-flow` | — | APIs, models, repos, streams, 埋点 | Module scope | `data_contract_flow.*`, `data_flow_tracker_report.*` |
| `behavior-logic` | — | Actions, lifecycle, state machines, side effects | Verified Stage A dims | `behavior_logic.*` |

**Pattern:** Mixed B+C — Stage A dims in parallel, then gated `behavior-logic`. Leader writes module reps, cross-module globals, SPEC.

**Subsystems:** `source` (`android_source`, P6 for migrate) · `target` (`kmp_target`, P5+).

**SPEC outputs:** `prd.md`, `design.md`, `verification.md`, migration-only `plan.md`.

**Output root:** `<agents_root>/understand/android-project-analyst[/source|/target]`

---

### 1.3 `android-to-kmp-migrator`

**Purpose:** After analyst P6 (+ target subsystem), transfer requested modules into an existing KMP target by editing real files, then hand off to validator.

**Use when:** Module-first porting with real target changes and mandatory validation.  
**Do not use before:** Analyst P6. Do not treat plans alone as success. Do not skip validator at V0.

| Role | Modes | Purpose | Key inputs | Key outputs |
| --- | --- | --- | --- | --- |
| `migration-workspace-state` | — | Todo/pipeline, M0–V0, stale/rerun | Upstream index | `migration_workspace_state.*` |
| `target-project-assistant` | `global_baseline` \| `module_anchors` \| align | Target KMP owner | Target understand subsystem | `target_alignment_revision.*`, `target_module_anchors.json` |
| `migration-planning-gate` | — | SPEC deltas, capability map, deps/platform | Source+target evidence | `migration_planning_gate.*` (`ready_for_implementation`) |
| `migration-prep` | — | Tokens, resources, routes, state/API/analytics expectations | Planning gate | Prep artifacts under module `node-results` |
| `module-implementation` | `ui` \| `logic` | Edit/create KMP UI then logic (+埋点) | Prep + anchors | Target file edits + impl records |
| `module-node-review-fix` | `review` \| `fix` | Review or scoped fix; re-review after fix | Impl outputs | Review/fix records |
| `migration-verification` | — | Static UI/logic/analytics restoration (no full build) | Module outputs | `migration_verification.*` |
| `global-migration-phase` | `integrate` \| `align` | Cross-module glue, entry points, analytics SDK; then read-only align | All module M3+ | `global_system_integration.*`, `post_integration_alignment.*` |
| `completion-report` | `readiness` \| `report` | Module/global readiness; migration report; validator handoff | M5–M6 evidence | `module_completion_record`, `migration_report.*` |

**Design mode:** `mvi` (default) or `mvvm` — frozen in `run_manifest.json`.

**References:**

| File | When |
| --- | --- |
| `references/kmp-mvi-flowredux.md` | Default MVI / FlowRedux |
| `references/kmp-mvvm.md` | Shared ViewModel / StateFlow |
| `references/kmp-expert.md` | Base KMP/CMP conventions |

**Output root:** `<agents_root>/migration/android-to-kmp-migrator`  
**Edits:** under `kmp_target_project_path` only.

---

### 1.4 `kmp-test-validator`

**Purpose:** Validate migration output against Android/SPEC/migrator evidence: fidelity, build/fix, entry launch, optional business/UI tests.

**Use when:** After migrator V0, or explicit migrated-behavior validation with Android + KMP + report.  
**Do not use for:** Generic KMP testing, KMP-only features, isolated Gradle troubleshooting, Android analysis.

| Role | Modes | Purpose | Key inputs | Key outputs |
| --- | --- | --- | --- | --- |
| `validation-workspace-state` | — | Ledger, VG0–VG5, fix/supplement counts | Migrator V0 | `validation_workspace_state.*` |
| `validation-fidelity-gate` | `trust` \| `restoreability` | Pre-build trust; post-build restoreability | Android/SPEC/KMP | `validation_fidelity_trust.*`, `validation_restoreability_audit.*` |
| `validation-code-gate` | `build` \| `fix` | Compile/preview; fix target on failure | Build cmds, logs | `validation_code_build.*`, `validation_code_fix.*`, knowledge entries |
| `validation-business-testing` | `entry_point_launch` \| `behavioral` \| `ui_comparison` | Mandatory entry launch; optional cases/Figma | User cases / Figma refs | `validation_business_testing.*`, entry-point records |
| `validation-report` | — | Final passed/failed/blocked | All gate evidence | `kmp_validation_report.*` |

**Loops:** code-gate fix ≤ 3; migrator supplement ≤ 3.

**Output root:** `<agents_root>/validation/kmp-test-validator`

---

### 1.5 `operating-instructions`

**Purpose:** Shared baseline conduct for every dispatched role — verification labels, scope control, rollback honesty, final reporting.

**Use when:** Always included as `skills: [operating-instructions]` on role dispatches.  
**Not a standalone workflow.**

---

### 1.6 `ponytail` / `ponytail-review`

| Skill | Purpose |
| --- | --- |
| `ponytail` | Decision ladder before writing code: skip → reuse project → stdlib → platform → dependency → one-liner → then new code |
| `ponytail-review` | Review diffs for over-engineering and removable complexity |

**Modes:** `lite` \| `full` \| `ultra` \| `off` (hooks + `/ponytail`). Env: `PONYTAIL_DEFAULT_MODE`.

---

## 2. Claude agents and commands

### Agents (`agents/`)

| Agent | Maps to |
| --- | --- |
| `android-project-analyst` | Analyst swarm controller |
| `android-to-kmp-migrator` | Migrator swarm controller |
| `kmp-test-validator` | Validator swarm controller |
| `memory-curator` | Audit/retain/archive agent memory |
| `skill-maintenance-advisor` | Recommend new/updated skills from conversation patterns |

> Prefer `skills/*/SKILL.md` role IDs over older IDs that may linger in agent markdown.

### Commands (`commands/`)

| Command | Purpose |
| --- | --- |
| `/legacy-android-understand` | Exploration-mode analyst; SPEC under understand root |
| `/fix-issue-kmp` | Targeted compile or use-case fix + rerun evidence |

---

## 3. `flow_d2c` skills

| Skill | Purpose | Main inputs | Main outputs |
| --- | --- | --- | --- |
| `flow_figma_compose_wf` | Top-level Figma → React → Compose orchestrator | Figma URLs/token, Android/Compose dirs | Phased React + Compose artifacts |
| `mobile-react-refactor` | Mobile-responsive, interaction-aware React | Generated React + screenshots | Optimized React + validation |
| `react-to-compose-ui` | Optimized React → Compose; shell or existing repo | Verified React, resources, target type | Compose modules; Gradle verify |
| `compose-adapter-generator` | Draft Compose-library adapter bundles | Library / design tokens context | Adapter package for registry |
| `ui-reconstruction-score` | Design vs implementation fidelity | Design + impl screenshots | Score / issue report |
| `anchor-d2c-mcp` (tools) | Figma convert + screenshot MCP | Figma node / auth | Code + screenshots |

**`react-to-compose-ui` target types:** `shell-compose` \| `existing-android-compose` \| `existing-kmp-cmp` (reuse-first into KMP).

**Pipeline:**

```text
Figma → React → mobile-react-refactor → react-to-compose-ui
                                      (+ adapter registry, ui-reconstruction-score)
```

---

## 4. Quick “which skill?” matrix

| User intent | Skill |
| --- | --- |
| “Analyze this Android app / feature” | `coding-task-adapter` → `android-project-analyst` |
| “Migrate X into our KMP app” | Adapter → dual analyst → `android-to-kmp-migrator` → `kmp-test-validator` |
| “Validate this migrated module” | `kmp-test-validator` (or `validation_handoff`) |
| “Fix this KMP compile / use-case failure” | `/fix-issue-kmp` or validator code-gate `fix` |
| “Figma to Compose in our KMP repo” | `flow_d2c` → `react-to-compose-ui` (`existing-kmp-cmp`) |
| “Keep the agent from overbuilding” | `ponytail` / `ponytail-review` |

---

## See also

- [Architecture](Architecture.md) — gates and artifact trees  
- [Roadmap](Roadmap.md) — gaps G1–G8  
- Plugin README: `claude-code-plugins/kmp-migration/README.md`
