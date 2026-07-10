# Architecture

> Gate IDs, artifact trees, dual-subsystem layout, and swarm skill anatomy for the KMP migration toolkit.  
> Canonical contracts live in each skill’s `output-contract.md` (wins on conflict with other docs).  
> Related: [Home](Home.md) · [Skill-Catalog](Skill-Catalog.md) · [Roadmap](Roadmap.md)

---

## 1. System context

CodeAgent-exp ships a **contract-heavy multi-agent operating system** for Android → KMP/CMP migration, plus an adjacent Figma → Compose pipeline (`flow_d2c`).

| Concern | Convention |
| --- | --- |
| Shared artifact base | `agents_root = <output_dir or ~/.a2c_agents>` |
| Stage isolation | Each skill owns one `output_root` under `agents_root` |
| Evidence | Structured JSON + Markdown on disk — chat text is not a gate |
| Authority | Gradle / `kmp-test-validator` beat advisory IDE MCP diagnostics |

```text
User request
  → coding-task-adapter          (A0–A6)
      ├─ only_understand_*  → android-project-analyst (source)
      └─ migration
            → analyst ×2 (source P6 + target P5+)
            → android-to-kmp-migrator (M0–V0, edits target)
            → kmp-test-validator (VG0–VG5, mandatory)
      → adapter-report
```

**Migration skill chain:**

```text
android-project-analyst (P6) → android-to-kmp-migrator (M0–V0) → kmp-test-validator (V0)
```

---

## 2. Modes and routes

| Mode | Adapter route | Analysis | Migrate / validate |
| --- | --- | --- | --- |
| Understand | `only_understand_ui` / `_logic` / `_architecture` / `_overview` | One analyst run on **source** | Stop after understand |
| Migrate | `migration` | **Two** analyst runs: source + target subsystems | Migrator → **required** validator |
| Validation handoff | `validation_handoff` | — | Validator only (needs migrator `V0`) |

**Partial migration** is not a separate route: `migration` with `partial_migration.enabled: true`. Scope must propagate adapter → both analyst runs → migrator → validator. Default is full project unless the user names an explicit module/feature/package/file set.

---

## 3. Stage roots (path templates)

```text
agents_root = <output_dir or ~/.a2c_agents>          # default ~/.a2c_agents

adapter:     <agents_root>/task-adapter/coding-task-adapter
source:      <agents_root>/understand/android-project-analyst/source
target:      <agents_root>/understand/android-project-analyst/target
standalone:  <agents_root>/understand/android-project-analyst   # no subsystem suffix
migration:   <agents_root>/migration/android-to-kmp-migrator
validation:  <agents_root>/validation/kmp-test-validator
```

Adapter `run_manifest.json` records downstream roots, e.g.:

```json
{
  "android-project-analyst-source": "<agents_root>/understand/android-project-analyst/source",
  "android-project-analyst-target": "<agents_root>/understand/android-project-analyst/target",
  "android-to-kmp-migrator": "<agents_root>/migration/android-to-kmp-migrator",
  "kmp-test-validator": "<agents_root>/validation/kmp-test-validator"
}
```

---

## 4. Gate reference

Naming note:

- Adapter write-order `AG0`–`AG6` maps 1:1 to handoff packages **`A0`–`A6`**
- Analyst internal pipeline **`G0`–`G9`**; downstream packages **`P0`–`P6`**
- Migrator leader schedule **`MG0`–`MG17`**; packages **`M0`–`M6`** + **`V0`**
- Validator packages **`VG0`–`VG5`**

### 4.1 Adapter — `A0`–`A6`

| Gate | Ready when |
| --- | --- |
| **A0** | `run_manifest.json` written; `output_root` locked |
| **A1** | `task_route.json` — route known or explicit `blocked` |
| **A2** | Workspace ledger + route stage inspection + intermediate assets |
| **A3** | `workflow_orchestration.json` + `downstream_workflow_index.json` |
| **A4** | Boundary stages pass (or explicit skip); migration must not skip `post_target_understand` or `post_validator` |
| **A5** | `pre_report` stage inspection `status: pass` |
| **A6** | `adapter_report.json` issued |

**Stage inspection IDs:** `route_decision` → `pre_downstream_dispatch` → `post_source_understand` → `post_target_understand` → `post_migrator` → `post_validator` → `pre_report` → `post_report`.

**Minimum evidence before A5 (by route):**

| Route | Evidence |
| --- | --- |
| `only_understand_*` | Focused or full analyst package + SPEC |
| `migration` | source `P6` + target `P5+`, migrator `M6` + `migration_report.*`, validator `VG5` |
| `validation_handoff` | migrator `V0`, validator `VG5` |

### 4.2 Analyst — `P0`–`P6` (and internal `G0`–`G9`)

| Package | Downstream use | Required (summary) |
| --- | --- | --- |
| **P0** | Any read | `run_manifest`, `analysis_workspace_state` |
| **P1** | Module schedule | `module_inventory`, `modules_index` |
| **P2** | Focused dim handoff | Per module: brief, 4 dimensions, tracker |
| **P3** | Per-module migrate plan | P2 + module representations |
| **P4** | Multi-module schedule | P1 + P3 for `assembly_order` + cross-module globals |
| **P5** | Exploration / understand-only | P0–P1 + `global_representation` + SPEC (prd/design/verification) |
| **P6** | **Migrator start** | P4 + P5 + `SPEC/plan.md` |

Internal write order: **G0** manifest → **G1** workspace → **G2** module index → **G3** briefs → **G4** Stage A dims (parallel) → **G5** behavior-logic → **G6** module reps → **G7** cross-module → **G8** global rep → **G9** SPEC.

### 4.3 Migrator — `M0`–`M6` + `V0`

| Package | Ready when |
| --- | --- |
| **M0** | Manifest + `upstream_analyst_index` + workspace state |
| **M1** | Migration module inventory + index |
| **M2** | Target alignment revision + per-module anchors |
| **M3** | Per-module: plan → prep → UI/logic impl + reviews → verification + completion record |
| **M4** | M3 for every module in `assembly_order` + module migration representations |
| **M5** | Global integrate + global migration representation |
| **M6** | Post-integration align + alignment report (entry points + analytics) |
| **V0** | M6 + `migration_report` (+ `target_changed_files[]` when impl required) + analyst SPEC paths |

Leader schedule **MG0–MG17** expands the same sequence (lock → index → TPA → per-module loop → integrate → align → report → invoke validator).

**Build boundary:** migrator verification is static/restoration only — **no** full project compile. Full build belongs to the validator.

### 4.4 Validator — `VG0`–`VG5`

| Gate | Ready when |
| --- | --- |
| **VG0** | Migrator `V0` verified; `upstream_migration_index` written |
| **VG1** | Fidelity **trust** — no unresolved trust blockers |
| **VG2** | Code **build** — `build.status: passed` |
| **VG3** | Fidelity **restoreability** — `restoreability_verdict: passed` |
| **VG4** | Business testing — mandatory `entry_point_launch`; optional behavioral/UI skipped or passed |
| **VG5** | `kmp_validation_report.json` issued |

**Order:** trust → build → **entry_point_launch** → restoreability → optional business → report.  
**Loops:** code-gate fix ≤ 3; migrator supplement ≤ 3.

---

## 5. Artifact trees

### 5.1 Adapter

```text
<agents_root>/task-adapter/coding-task-adapter/
  run_manifest.json
  downstream-index/
  workspace-state/
  route-orchestration/route/ | orchestrate/
  stage-inspections/<stage_id>/
  intermediate-assets/
  report/
```

### 5.2 Analyst (source or target subsystem)

```text
<agents_root>/understand/android-project-analyst[/source|/target]/
  run_manifest.json
  workspace-state/
  module-index/          # module_inventory, modules_index
  modules/<module_id>/
    module_brief.json
    dimension_index.json
    node-results/
      presentation-resource/
      project-architecture/
      data-contract-flow/
      behavior-logic/
    representation/
  global/                # cross_module_*, migration_assembly_basis, global_representation
  SPEC/                  # prd.md, design.md, verification.md, plan.md (migration)
```

### 5.3 Migrator

```text
<agents_root>/migration/android-to-kmp-migrator/
  run_manifest.json
  upstream-index/upstream_analyst_index.json
  module-index/
  global/node-results/   # workspace-state, TPA, integrate, align
  modules/<migration_module_id>/node-results/ ...
  report/                # alignment_report, migration_report
```

**Hard rule:** planning artifacts alone are not success — files under `kmp_target_project_path` must change when implementation is required.

### 5.4 Validator

```text
<agents_root>/validation/kmp-test-validator/
  run_manifest.json
  upstream-index/upstream_migration_index.json
  workspace-state/
  fidelity-gate/trust/ | restoreability/
  code-gate/build/ | fix/<cycle_id>/ | knowledge/
  business-testing/ | entry-point-launch/
  report/
  logs/
```

### 5.5 Cross-cutting filenames

| File | Owner | Purpose |
| --- | --- | --- |
| `run_manifest.json` | Every Leader | Identity, paths, scope, handoff package |
| `*_workspace_state.json` | Workspace-state roles | Ledger, `handoff_gates`, todos |
| `upstream_analyst_index.json` | Migrator | Source + target understand paths |
| `upstream_migration_index.json` | Validator | Migrator `V0` paths |
| `migration_report.json` | Migrator | Scope, changed files, analytics handoff |
| `kmp_validation_report.json` | Validator | Final verdict |

---

## 6. Dual-subsystem layout

| Subsystem | `project_kind` | Path | Gate bar for migrate |
| --- | --- | --- | --- |
| Source | `android_source` | `.../understand/android-project-analyst/source` | **P6** |
| Target | `kmp_target` | `.../understand/android-project-analyst/target` | **P5+** |

Same artifact **format**; distinct roots. Migrator fails closed if source `P6` is false, target is missing, or roots are identical.

**Consumption:**

- Source → module inventory, assembly basis, SPEC, per-module representations/dimensions  
- Target → TPA primary evidence (anchors, alignment); no independent full re-analysis inside migrator  

---

## 7. Swarm skill anatomy

Every core skill ships this bundle:

| File | Role |
| --- | --- |
| `SKILL.md` | Team registry (`kind: swarm-skill`), role IDs, protocol |
| `workflow.md` | Dispatch topology, acceptance criteria |
| `bind.md` | Guardrails, failure handling |
| `output-contract.md` | Canonical paths + gate packages |
| `dependencies.yaml` | Tools, optional MCP, upstream inputs |
| `roles/*.md` | Per-node I/O boundaries |

| Skill | Pattern |
| --- | --- |
| `coding-task-adapter` | Serial control plane |
| `android-project-analyst` | **Mixed B+C** — Stage A dims in parallel (B), then gated `behavior-logic` (C) |
| `android-to-kmp-migrator` | Specialization (C) + fan-outs (B) + review→fix loops |
| `kmp-test-validator` | Serial pipeline + fix/supplement loops |

Controllers route and enforce contracts; nodes write only under assigned `output_dir`. Shared conduct: `operating-instructions`. Scale rule: when full swarm fan-out exceeds budget, **controller-driven degrade** is allowed if recorded honestly in ledgers (never claim V0 for untouched modules).

---

## 8. Cross-cutting concerns

### Rules (`rules/*.mdc`)

| Rule | Purpose |
| --- | --- |
| `stage-node-io-contract` | Input check first; durable output before success |
| `workflow-stage-contracts` | Required gates per workflow |
| `agent-only-output-contract` | Structured artifacts for agents, not prose |
| `phase-document-template-contract` | Phase docs + templates mandatory |
| `status-controller-task-ledger` | todo / done / blocked ledger |
| `fidelity-gate-verification` | Fail-closed fidelity chain |
| `ponytail` | Decision ladder before new code |

### Hooks

| Event | Behavior |
| --- | --- |
| `SessionStart` / `SubagentStart` | Activate / propagate Ponytail |
| `UserPromptSubmit` | Track `/ponytail lite|full|ultra|off` |
| `PreToolUse` (Write/Edit) | Block `.env` / `.env.*` edits |

### JetBrains MCP (optional)

SSE default: `http://localhost:64342/sse`. Used for modules, symbols, diagnostics, rename/format, run configs. **Advisory only** — validator Gradle gates remain authoritative.

### Design mode (migrator)

Frozen per run in `run_manifest.json`:

| `design_mode` | Reference |
| --- | --- |
| `mvi` (default) | `references/kmp-mvi-flowredux.md` |
| `mvvm` | `references/kmp-mvvm.md` |

Both also follow `references/kmp-expert.md`.

---

## 9. Adjacent pipeline: `flow_d2c`

Separate Claude plugin (v0.1.0). Complements KMP when UI truth comes from Figma:

```text
Figma → React → mobile-react-refactor → react-to-compose-ui
                                         ├─ shell-compose
                                         ├─ existing-android-compose
                                         └─ existing-kmp-cmp   ← reuse-first into KMP target
```

Supporting skills: `compose-adapter-generator`, `ui-reconstruction-score`, MCP `anchor-d2c-mcp`.

---

## 10. Multi-CLI distribution

| Channel | What ships |
| --- | --- |
| Claude `kmp-migration` | Full swarm + agents, commands, hooks, rules, MCP |
| Codex / Gemini packages | Core analyst / migrator / validator skills |
| `@code-migration/wow-migrator` | Copies skill tree into Claude, Codex, Cursor, Gemini, OpenCode, OpenClaw, JiuwenSwarm |

Canonical **full** experience (hooks, rules, agents) lives in the Claude plugin tree; npm is the portable skill installer.

---

## See also

- [Skill-Catalog](Skill-Catalog.md) — per-role I/O cheat sheet  
- [Roadmap](Roadmap.md) — G1–G8 closure plan  
- Plugin README: `claude-code-plugins/kmp-migration/README.md`
