# CodeAgent-exp Wiki

> Cross-CLI AI coding plugins for **Android → Kotlin Multiplatform (KMP/CMP)** migration and **Figma → Compose** design-to-code.  
> Repo: [winson-AI/CodeAgent-exp](https://github.com/winson-AI/CodeAgent-exp) · License: MIT  
> Last reviewed: 2026-07-10

---

## Table of Contents

1. [Background](#1-background)
2. [Supported Functions](#2-supported-functions)
3. [Gap Analysis: Toward Complete Auto-Migration & Atomic AI-Coding](#3-gap-analysis-toward-complete-auto-migration--atomic-ai-coding)

---

## 1. Background

### 1.1 Why this project exists

HarmonyOS NEXT no longer ships AOSP compatibility. Client work that used to be **Android + iOS** became **three platforms**, with roughly **3× people-months** if each feature is rewritten per stack. Among cross-platform options, **KMP/CMP** is a strong Android→multi-end base because:

- Kotlin is already the Android native language — stock code can be reshaped instead of rewritten into RN/Flutter.
- Build outputs are native libraries per platform — no extra runtime tax on host apps.
- Android and HarmonyOS share many container/callback shapes; adaptation is often naming and toolchain, not full redesign.

**A2K (Android to KMP)** is the product idea behind this repo: put migration domain knowledge into **installable Agent Skills**, then run a **multi-agent pipeline** so humans review and decide while agents do mechanical translation, platform fill-in, and self-validation.

Public practice (Bilibili / B站) showed the same pattern in production: logic-first KMP (2024), CMP message home (late 2024), HarmonyOS CMP (2025), with AI-assisted analysis → SPEC → generation → compile/visual loops yielding ~**70%** migration efficiency gains — still with a human “last mile” for pixels and edge behavior.

### 1.2 Evolution path (from local memory & sibling projects)

This GitHub tree is the **skill/plugin delivery layer**. It grew out of earlier experiments still present on the machine:

| Layer | Location (local) | Role |
| --- | --- | --- |
| Early framework (Python multi-agent) | `~/kmp-migration-framework`, `~/CodeBase/Offline/a2k_agent` | Harness, memory, explorer/planner/generator/evaluator, SPEC (PRD/DESIGN/PLAN), skills hub — strong architecture, historically weak on *real* code translation |
| Session / product memory | `~/.hermes/memories`, Claude agent-memory, A2K decks under `~/Documents` | Build-first order: Comprehension → Migration → Build(+BugFix) → Test → Report; HarmonyOS as a first-class target |
| Open-source skill installer lineage | `kmp-migration` / `@code-migration/wow-migrator` | One-click install of migration skills into many AI CLIs |
| **This repo** | `CodeAgent-exp` | Portable **Swarm Skills + plugins** for Claude Code, Codex, Gemini, Cursor, OpenCode, OpenClaw, JiuwenSwarm |

Internal TODO (`TODE.md`) still points at the next product bets:

1. **Stock understanding + AST/LSP static analysis**
2. **Incremental development** — expand scope from migration into day-to-day coding
3. **Knowledge sedimentation** — insect/knowledge DB + data flywheel

### 1.3 What this repository is today

A **multi-CLI plugin ecosystem** that ships:

1. **`kmp-migration`** — end-to-end Android→KMP swarm (adapter → analyst → migrator → validator), with contracts, hooks, JetBrains MCP, Ponytail guardrails.
2. **`flow_d2c`** (Claude Code) — Figma → React → mobile React → Compose, with UI scoring and adapter generation.
3. **Distribution** — Claude marketplace plugins, Codex plugin, Gemini extension, and npm package `@code-migration/wow-migrator` (`0.2.11`) that copies the same skill tree into multiple agents.

Design principles (from `CONTRIBUTING.md`):

- Platform-agnostic skill markdown where possible  
- Zero-install / portable extensions  
- High-fidelity, domain-specific workflows (not generic “write some KMP”)

### 1.4 Operating model in one picture

```text
User request
    │
    ▼
coding-task-adapter          (route + stage gates A0–A6)
    │
    ├─ understand_* ──► android-project-analyst (P0–P6 SPEC)
    │
    └─ migration ────► analyst ×2 (source + target subsystems)
                            │
                            ▼
                   android-to-kmp-migrator (M0–V0, edit target)
                            │
                            ▼
                   kmp-test-validator (VG0–VG5, build/fix loops)
```

Artifacts default under `~/.a2c_agents/{understand,migration,validation}/` (or a run-specific `output_dir`). Large runs (e.g. Telegram-scale) may **degrade to controller-driven** execution when full swarm fan-out exceeds token/wall-clock budget — recorded honestly in ledgers rather than claiming full V0.

---

## 2. Supported Functions

### 2.1 Distribution matrix

| Toolkit | Path | Version (approx.) | Purpose |
| --- | --- | --- | --- |
| Claude `kmp-migration` | `claude-code-plugins/kmp-migration/` | `0.1.30` | Full swarm + agents, commands, hooks, rules, JetBrains MCP |
| Claude `flow_d2c` | `claude-code-plugins/flow_d2c/` | `0.1.0` | Figma→Compose design-to-code |
| Codex KMP | `codex-plugins/kmp-migration/` | `0.1.2` | Analyst / migrator / validator skills |
| Gemini KMP | `gemini-extensions/kmp-migration/` | `0.1.2` | Same three skills + `GEMINI.md` + local MCP entry |
| npm installer | `npx_skills/` → `@code-migration/wow-migrator` | `0.2.11` | Install skills into Claude, Codex, Cursor, Gemini, OpenCode, OpenClaw, JiuwenSwarm |

### 2.2 KMP migration — core swarm skills

#### Front door: `coding-task-adapter`

- Classifies intent: `only_understand_*` vs `migration` vs `validation_handoff`
- Preserves **partial migration** scope when requested
- Dual-understand for migrate: **source subsystem + target subsystem**
- Stage ledger + intermediate asset records + final adapter report (`A0`–`A6`)

#### Understand: `android-project-analyst`

Module-first analysis across four dimensions per module:

| Dimension role | Captures |
| --- | --- |
| `presentation-resource` | Screens, XML/Compose UI, navigation, local/remote resources |
| `project-architecture` | Gradle topology, layers, DI, Jetpack, Android-only constraints |
| `data-contract-flow` | APIs, models, repos, cache/error/pagination, analytics/埋点 |
| `behavior-logic` | Actions, lifecycle, state machines, side effects, cross-module flows |

Outputs: module representations, cross-module assembly basis, global representation, SPEC (`prd.md`, `design.md`, `plan.md` when migrating, `verification.md`). Gates `P0`–`P6`.

#### Migrate: `android-to-kmp-migrator`

Consumes both understand subsystems; **edits real files** under `kmp_target_project_path`:

| Phase | Roles / work |
| --- | --- |
| Prep | Target project assistant, planning gate (capability map, deps/platform), presentation + state/data prep |
| Per module | UI implementation → review/fix → logic (+ analytics) → review/fix → static verification |
| Global | Integrate (glue, entry points, analytics SDK) → align vs Android |
| Handoff | Completion report → mandatory `kmp-test-validator` at `V0` |

Architecture modes: **MVI/FlowRedux (default)** or **MVVM**, plus shared `kmp-expert` conventions. Gates `M0`–`V0`.

#### Validate: `kmp-test-validator`

| Gate | Meaning |
| --- | --- |
| Fidelity `trust` | Pre-build Android/SPEC vs KMP consistency |
| Code `build` / `fix` | Compile/preview scenarios; fix loop (max cycles) |
| Entry-point launch | Mandatory startup parity check |
| Fidelity `restoreability` | Post-build restoreability; migrator supplement loop |
| Business testing | Optional behavioral cases + Figma UI comparison |
| Report | Evidence-backed passed / failed / blocked (`VG0`–`VG5`) |

#### Shared conduct & guardrails

- `operating-instructions` — verification labels, scope, rollback honesty  
- `ponytail` / `ponytail-review` — decision ladder before writing new code  
- Hooks — block `.env` edits; Ponytail lifecycle  
- Rules — stage/node I/O contracts, fidelity fail-closed chain, task ledgers  
- Optional **JetBrains MCP** — modules, symbols, diagnostics, build/run configs (advisory; Gradle gates remain authoritative)

#### Claude-only agents & commands

- Agents: analyst, migrator, validator, `memory-curator`, `skill-maintenance-advisor`  
- Commands: `/legacy-android-understand`, `/fix-issue-kmp`

### 2.3 Design-to-code — `flow_d2c`

| Skill | Function |
| --- | --- |
| `flow_figma_compose_wf` | Top-level Figma → React → Compose orchestrator |
| `mobile-react-refactor` | Mobile-responsive, interaction-aware React |
| `react-to-compose-ui` | Optimized React → Android/KMP/CMP Compose; shell vs existing-repo integration |
| `compose-adapter-generator` | Draft Compose-library adapter bundles |
| `ui-reconstruction-score` | Screenshot fidelity scoring vs design |
| `anchor-d2c-mcp` | Figma-to-code convert + screenshot MCP tools |

### 2.4 What a successful run already produces

- Structured **understand artifacts** (module + global + SPEC)  
- **Target KMP edits** (not plan-only) with migration report  
- **Validation evidence** (build/preview/entry/fidelity, optional business/UI)  
- Machine-routable JSON/Markdown under strict path contracts for resume and handoff

---

## 3. Gap Analysis: Toward Complete Auto-Migration & Atomic AI-Coding

This section contrasts **what the repo already encodes** with what a **fully automatic, atomic AI-coding path** still needs — combining repo TODOs, A2K evolution notes, large-project run feedback, and general practice for reliable agent coding systems.

### 3.1 Capability maturity snapshot

| Capability | Today | Gap to “complete auto” |
| --- | --- | --- |
| Task routing & stage gates | Strong (adapter + ledgers) | Needs durable multi-session orchestrator outside a single chat |
| Stock understanding | Strong prompt/skill structure | Weak **AST/LSP/graph** grounding; still LLM-grep heavy |
| SPEC as contract | Strong PRD/DESIGN/PLAN/verification | Weak **executable** acceptance (tests generated from SPEC) |
| Code migration | Strong role pipeline + review/fix | Soft on **semantic equivalence**, View→Compose rewrite, HarmonyOS toolchain |
| Build/fix loop | Present (validator code gate) | Not yet a hardened **error-DB + replay** product loop |
| Visual/behavior parity | Optional / user-supplied cases | No default **auto case gen + screenshot diff + auto-fix** |
| Incremental *dev* (post-migration) | Out of scope | Explicit TODO: migration → ongoing feature coding |
| Knowledge flywheel | Memory curator / skill advisor hooks | No shared **insect knowledge + ranked fix corpus** across runs |
| Scale | Controller degrade for huge apps | No automatic **vertical slicing planner** with cost budgets |

### 3.2 Gaps for a complete auto-migration path

#### G1 — Deterministic comprehension (AST / LSP / Codegraph)

**Need:** Module graphs, call graphs, resource ownership, DI graphs, and API contracts from tools — not only from model reading.

**Why:** LLM-only understand drifts on 100k+ LOC modules; Telegram-class runs already force controller degrade.

**Atomic coding implication:** Each understand node should be an **idempotent tool job** (`analyze_module`, `extract_api_surface`) with checksummed inputs/outputs, not a free-form chat turn.

#### G2 — Executable SPEC & verification ladder

A2K already defines a strength ladder (compile → contract → semantic → multi-theme/locale/platform). The repo encodes gates in markdown; it does not yet **own**:

- Auto-generated unit/UI tests from SPEC  
- Golden screenshots / visual diff as default  
- Risk-adaptive gate selection (high-risk modules → stronger verify)

Without this, “passed” can mean “compiled and looked plausible.”

#### G3 — Closed-loop generation with ranked remediations

Validator fix loops exist, but a complete path needs:

- Persistent **compile-error → fix pattern** DB (insect knowledge)  
- Replay of failing Gradle/IDE logs as first-class tools  
- Supplement routing that re-enters migrator at the **smallest failing atom** (file/symbol), not whole-module rewrites

#### G4 — Platform completeness (especially HarmonyOS)

Skills emphasize Android→KMP/CMP and expect/actual patterns. Full auto still needs packaged skills for:

- `ohosArm64` toolchain / interop (karakum, NMB/knoi-class patterns)  
- Third-party KMP availability checks (`klibs.io`-style) as automated gates  
- Proxy-model and DI bridge recipes as **executable templates**, not only prose

#### G5 — UI technology debt automation

CMP assumes Compose. View/XML-heavy modules need an explicit **rewrite lane** (or D2C merge from Figma) with separate cost/risk scoring. Today that is mostly human judgment inside planning-gate.

#### G6 — Partial migration → continuous coding

`TODE.md` calls out expanding from migration to **incremental development**. Missing pieces:

- Feature-request → atomic tasks against an existing KMP baseline  
- Regression harness that always reuses migration SPEC + validation corpus  
- Safe edit scopes (allowed files, API freeze, analytics parity) as machine-enforced policy

#### G7 — Orchestration outside the chat window

Swarm skills assume a capable host agent. A complete product path needs:

- Checkpoint/resume across days (framework had this; plugin layer is chat-session bound)  
- Budget-aware planner (tokens, wall clock, module priority)  
- CI entrypoints (`wow-migrator` + headless agent) with audit logs

#### G8 — Honest coverage metrics

Large runs must not claim M4/M6/V0 for untouched modules (already a memory rule). Product gap: **dashboard of module coverage %**, restoreability %, and human-required residual — exportable for PMs.

### 3.3 Gaps for atomic & auto AI-coding (cross-cutting)

Atomic AI-coding means: **one verifiable unit of work in, one evidence-backed unit out**, composable into pipelines.

| Atomic building block | Status in repo | Missing for auto path |
| --- | --- | --- |
| Typed task atom (inputs, tools, outputs, gate id) | Strong in skill contracts | Runtime schema validation + schema versioning |
| Tool-first edit (LSP rename, format, diagnostics) | Optional JetBrains MCP | Mandatory pre/post diagnostic diff on every edit atom |
| Smallest failing command | `/fix-issue-kmp` pattern | Universal “bisect to atom” for all stages |
| Idempotent artifact store | Path contracts under `~/.a2c_agents` | Content-addressed cache + stale detection as a service |
| Human gate only at decision points | Review/fix roles | Explicit approval API for architecture/DI/platform choices |
| Learning loop | Skill-maintenance-advisor, memory-curator | Offline eval harness + promotion of skills from successful runs |
| D2C ↔ A2K merge | Separate plugins | Unified “design truth + code truth” when Figma and Legacy both exist |

### 3.4 Recommended closure order (practical roadmap)

1. **AST/LSP-backed understand** for architecture + data-contract dimensions (closes G1; feeds better SPEC).  
2. **Error-knowledge DB + fix-issue as default validator path** (closes G3).  
3. **Default visual/behavior smoke pack** generated from SPEC screens/flows (closes G2 partially).  
4. **Budgeted vertical slicer** for mega-apps (formalize controller-degrade into a first-class planner).  
5. **HarmonyOS/platform skill pack** as optional target profile (closes G4).  
6. **Post-migration coding mode** reusing adapter + validator (closes G6 / `TODE`).  
7. **Headless CI orchestrator** with coverage dashboard (closes G7–G8).

### 3.5 Bottom line

**CodeAgent-exp already delivers a serious, contract-heavy multi-agent migration *operating system* across CLIs** — routing, dual understand, module-first migrate, fidelity/build validation, D2C, and installers.

It is **not yet a fully automatic migration or general atomic coding product**: comprehension is still model-heavy, verification is not fully executable by default, platform/HarmonyOS and View→Compose lanes are incomplete, knowledge does not compound into a shared fix corpus, and long-running / CI-native orchestration remains thin.

Closing those gaps turns today’s “high-skill agent playbook” into a **deterministic pipeline of atomic, tool-verified coding jobs** with humans only at true decision boundaries.

---

## Appendix

### A. Key local memory sources used for this wiki

- `~/Downloads/A2K技术方案设计以及B站落地实践.md` — A2K rationale, pipeline, B站 practice, open-source installer story  
- `~/kmp-migration-framework/MIGRATE_A2K_SESSION_REVIEW.md` & `EVOLUTION_ROADMAP.md` — earlier framework strengths/gaps  
- `~/.hermes/memories/MEMORY.md` — build-first multi-agent architecture notes  
- `~/.claude/agent-memory/kmp-migration-android-to-kmp-migrator/` — swarm scale-degrade feedback  
- Repo `README.md`, `TODE.md`, `claude-code-plugins/kmp-migration/README.md`, skill `SKILL.md` files  

### B. Quick install pointers

```bash
# Claude Code (dev)
claude --plugin-dir claude-code-plugins/kmp-migration
claude --plugin-dir claude-code-plugins/flow_d2c

# npm skills into detected agents
npm install -g @code-migration/wow-migrator
wow-migrator install --yes
```

### C. Related wiki pages (optional expansions)

| Page | Suggested content |
| --- | --- |
| [Architecture](Architecture.md) | Gate IDs, artifact trees, dual-subsystem layout |
| [Skill-Catalog](Skill-Catalog.md) | Per-role I/O cheat sheet |
| [Roadmap](Roadmap.md) | Track G1–G8 with owners and acceptance tests |
