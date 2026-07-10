# Roadmap

> Track gaps **G1–G8** from [Home §3](Home.md#3-gap-analysis-toward-complete-auto-migration--atomic-ai-coding) toward complete auto-migration and atomic AI-coding.  
> Related: [Home](Home.md) · [Architecture](Architecture.md) · [Skill-Catalog](Skill-Catalog.md)

**Status legend:** `todo` · `in_progress` · `done` · `blocked`  
**Owners:** leave blank or assign when work starts. Dates are planning targets, not commitments.

---

## 1. North star

Turn today’s **skill/playbook OS** into a **deterministic pipeline of atomic, tool-verified coding jobs**:

- Comprehension grounded in AST/LSP/graph tools  
- SPEC that drives executable checks  
- Fix knowledge that compounds across runs  
- Humans only at true architecture / platform decisions  

Internal product bets (`TODE.md`): stock understanding + AST/LSP · incremental post-migration coding · knowledge sedimentation.

---

## 2. Gap tracker (G1–G8)

| ID | Gap | Priority | Status | Owner | Target |
| --- | --- | --- | --- | --- | --- |
| [G1](#g1--deterministic-comprehension-ast--lsp--codegraph) | Deterministic comprehension (AST/LSP/Codegraph) | P0 | todo | | |
| [G2](#g2--executable-spec--verification-ladder) | Executable SPEC & verification ladder | P0 | todo | | |
| [G3](#g3--closed-loop-generation--ranked-remediations) | Closed-loop fix + ranked remediations | P0 | todo | | |
| [G4](#g4--platform-completeness-harmonyos) | Platform completeness (HarmonyOS) | P1 | todo | | |
| [G5](#g5--ui-technology-debt-automation) | View/XML → Compose rewrite lane | P1 | todo | | |
| [G6](#g6--partial-migration--continuous-coding) | Post-migration incremental coding | P1 | todo | | |
| [G7](#g7--orchestration-outside-the-chat-window) | Headless / multi-session orchestrator | P1 | todo | | |
| [G8](#g8--honest-coverage-metrics) | Coverage dashboard & residual honesty | P2 | todo | | |

---

## G1 — Deterministic comprehension (AST / LSP / Codegraph)

**Problem:** Understand nodes are still LLM + `rg`-heavy; large apps force controller degrade.

**Work items:**

- [ ] Define tool atoms: `analyze_module`, `extract_api_surface`, `resource_ownership`, `di_graph`
- [ ] Wire JetBrains MCP / LSP / optional Codegraph as **required** evidence for architecture + data-contract dims (not optional color)
- [ ] Checksum inputs → dimension JSON; fail closed on tool failure for P2+
- [ ] Document tool fallback policy when IDE MCP is down

**Acceptance tests:**

1. On a mid-size Android module, `project-architecture` and `data-contract-flow` artifacts cite tool-derived symbol/module lists with file:line evidence for ≥80% of claimed types.  
2. Re-run with unchanged sources produces byte-identical (or schema-stable) dimension JSON hashes.  
3. With MCP disabled, gate status is `blocked` or explicitly `degraded` — never silent guess-complete for P6.

**Depends on:** —  
**Unblocks:** G2, G5 planning accuracy, G8 coverage fidelity

---

## G2 — Executable SPEC & verification ladder

**Problem:** SPEC is rich markdown; “passed” can mean compile-plausible without semantic/visual proof.

**Work items:**

- [ ] Map SPEC screens/flows → generated smoke test stubs (unit + Compose UI where possible)
- [ ] Encode verification ladder in validator: weak (compile) → medium (contract) → strong (behavior) → strongest (theme/locale/platform)
- [ ] Risk-adaptive gate selection from analyst risk tags
- [ ] Default optional visual pack when Figma or screenshot baselines exist

**Acceptance tests:**

1. Migration of a sample feature produces at least one runnable test or scripted check derived from `verification.md` / SPEC flows.  
2. Validator report states ladder level achieved per module; high-risk modules cannot claim VG5 on compile-only.  
3. Missing user test cases still run a **default smoke** (entry + one happy path) or explicit `blocked: missing_smoke`.

**Depends on:** G1 (better SPEC inputs)  
**Unblocks:** G3 quality, G6 regression harness

---

## G3 — Closed-loop generation & ranked remediations

**Problem:** Fix loops exist, but knowledge does not compound into a shared, ranked error→fix corpus.

**Work items:**

- [ ] Promote validator `code-gate/knowledge/` into a durable **insect / error-DB** across runs
- [ ] Rank remediations by success rate; inject top-N into fix prompts
- [ ] Universal “bisect to atom”: map failing Gradle/IDE log → smallest file/symbol edit scope
- [ ] Make `/fix-issue-kmp` the default remediation entry for VG2 failures

**Acceptance tests:**

1. Same compile error class on a second project retrieves ≥1 prior `bug_fix_experience` entry automatically.  
2. Fix mode records `allowed_files` and does not edit outside that set.  
3. After max fix cycles, report includes ranked next actions — not only “failed”.

**Depends on:** G2 (clearer fail signals)  
**Unblocks:** G7 CI reliability

---

## G4 — Platform completeness (HarmonyOS)

**Problem:** Skills emphasize Android→KMP/CMP; HarmonyOS toolchain/interop is prose-level, not packaged gates.

**Work items:**

- [ ] Target profile pack: `ohosArm64` expect/actual templates, interop notes (karakum / NMB / knoi-class patterns)
- [ ] Automated third-party availability check (e.g. klibs-style) in planning-gate
- [ ] Proxy-model + DI bridge recipes as executable templates
- [ ] Optional validator scenario: HarmonyOS compile when toolchain present

**Acceptance tests:**

1. Planning-gate emits `platform_capability_map` with explicit ohos status: `supported` \| `gap` \| `out_of_scope`.  
2. Sample expect/actual PlatformLogger (or equivalent) generated from template and compiles on Android; ohos path documented or gated.  
3. Missing HarmonyOS toolchain yields `skipped` with reason — not a false VG2 pass.

**Depends on:** —  
**Unblocks:** Full A2K three-end story

---

## G5 — UI technology debt automation

**Problem:** CMP assumes Compose; View/XML rewrite cost is mostly human judgment.

**Work items:**

- [ ] Analyst flag: `ui_tech = view | compose | hybrid` with rewrite cost score
- [ ] Explicit **rewrite lane** in planning-gate (or route to `flow_d2c` when Figma exists)
- [ ] Merge policy: design truth vs legacy truth when both present
- [ ] Do not claim UI restoreability for View modules without rewrite plan

**Acceptance tests:**

1. View-heavy module cannot reach M3 UI impl without `rewrite_plan` or `out_of_scope` marker.  
2. When Figma + Legacy both supplied, run manifest records chosen truth source.  
3. Restoreability audit fails closed if UI tech debt unresolved.

**Depends on:** G1 (accurate UI inventory)  
**Unblocks:** Honest G8 UI coverage

---

## G6 — Partial migration → continuous coding

**Problem:** Toolkit stops at migration; day-to-day feature coding on the KMP baseline is out of scope (`TODE`).

**Work items:**

- [ ] Adapter route: `incremental_dev` (feature request against existing KMP + prior SPEC)
- [ ] Reuse validator corpus as regression pack on every incremental change
- [ ] Machine-enforced edit policy: allowed files, API freeze, analytics parity
- [ ] Document “migration done → coding mode” handoff in wiki

**Acceptance tests:**

1. After a migrated sample module, a small feature request runs through adapter without re-running full-project understand.  
2. Incremental run reuses prior `verification` / validation artifacts as regression baseline.  
3. Edits outside `allowed_files` are blocked or reported as contract violation.

**Depends on:** G2, G3  
**Unblocks:** Product expansion beyond one-shot migration

---

## G7 — Orchestration outside the chat window

**Problem:** Swarm skills assume a capable interactive host; multi-day / CI runs are thin.

**Work items:**

- [ ] Checkpoint/resume across sessions (reuse `agents_root` ledgers as source of truth)
- [ ] Budget-aware planner: tokens, wall clock, module priority (formalize controller-degrade)
- [ ] Headless entry: `wow-migrator` + agent CLI with audit log
- [ ] CI example workflow (GitHub Actions or local) for understand-only and validate-only

**Acceptance tests:**

1. Kill mid-migration; resume from same `agents_root` continues at next failed gate without rewriting completed modules.  
2. Budget exceed triggers documented degrade + partial coverage report (G8).  
3. CI job can run `only_understand_overview` or `validation_handoff` non-interactively and upload `adapter_report` / `kmp_validation_report`.

**Depends on:** G3 (stable fix loops)  
**Unblocks:** Enterprise / team use

---

## G8 — Honest coverage metrics

**Problem:** Large runs must not claim M4/M6/V0 for untouched modules; PMs need exportable coverage.

**Work items:**

- [ ] Machine-readable coverage: modules `v0_ready` \| `partial` \| `not_started`
- [ ] Metrics: restoreability %, build pass, human residual checklist
- [ ] Export `coverage_dashboard.json` + short Markdown summary from adapter/migrator/validator
- [ ] Enforce memory rule: never claim gates for modules not actually migrated

**Acceptance tests:**

1. Partial Telegram-scale (or fixture) run produces coverage file where sum of statuses = scheduled modules.  
2. Any `migration_report` claiming V0 for a `not_started` module fails a schema/lint check.  
3. Dashboard lists human-required residuals explicitly.

**Depends on:** G7 degrade planner  
**Unblocks:** Stakeholder reporting

---

## 3. Recommended closure order

```text
G1 (tool-backed understand)
  → G2 (executable SPEC / ladder)
    → G3 (error-DB + atomic fix)
      → G7 (headless / resume) + G8 (coverage)
G4 (HarmonyOS pack)     ── parallel after G1 planning hooks
G5 (View→Compose lane)  ── parallel after G1 UI inventory
G6 (incremental coding) ── after G2 + G3
```

| Wave | Gaps | Outcome |
| --- | --- | --- |
| **Wave 1** | G1, G2, G3 | Trustworthy understand → verify → fix loop |
| **Wave 2** | G4, G5, G7, G8 | Platform + UI debt + CI + honesty |
| **Wave 3** | G6 | Migration toolkit becomes ongoing coding path |

---

## 4. Atomic coding checklist (cross-cutting)

Use this as the definition of done for any new skill/role:

| Building block | Requirement |
| --- | --- |
| Typed task atom | Declared inputs, tools, outputs, gate id, schema version |
| Tool-first edit | Pre/post diagnostics (MCP or compiler) on every edit atom |
| Smallest failing command | Bisect to file/symbol before broad rewrite |
| Idempotent store | Content or checksum under `agents_root`; stale detection |
| Human gate | Only for architecture / DI / platform choices |
| Learning loop | Successful fixes promote to knowledge DB / skill updates |

---

## 5. How to update this page

1. Change **Status** / **Owner** / **Target** in the tracker table.  
2. Check off work items when merged.  
3. When a gap is `done`, link the PR or skill version in the acceptance section.  
4. Keep [Home §3](Home.md#3-gap-analysis-toward-complete-auto-migration--atomic-ai-coding) narrative in sync if priorities change.

---

## See also

- [Home](Home.md) — background and gap narrative  
- [Architecture](Architecture.md) — current gate/artifact model  
- [Skill-Catalog](Skill-Catalog.md) — where new atoms would land  
- Repo `TODE.md` — stock understand · incremental dev · knowledge
