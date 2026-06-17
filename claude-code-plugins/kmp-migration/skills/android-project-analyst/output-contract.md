# Output Contract: File Recording System And Downstream Trigger Gates

This document is the **canonical path and content contract** for `android-project-analyst`. Downstream handlers (`migration-task-adapter`, `android-to-kmp-migrator`, `kmp-test-validator`, and human/agent orchestrators) **MUST treat missing, empty, out-of-path, stale, or schema-invalid artifacts as hard blockers** — they do not infer, reconstruct, or proceed from chat summaries.

The Leader and every node MUST read this file before writing artifacts. `SKILL.md` and `workflow.md` reference this contract; when they diverge, **this file wins on paths, filenames, and trigger gates**.

## Output Root Layout

Lock one `output_root` before any dispatch:

```text
output_root = <output_dir or ~/.a2c_agents/understand>/android-project-analyst

<output_root>/
├── run_manifest.json                          # run identity + handoff package pointer
├── workspace-state/
│   ├── analysis_workspace_state.json          # machine ledger (freshness + inventory)
│   └── analysis_workspace_state.md
├── module-index/
│   ├── module_inventory.json                  # authoritative module schedule
│   ├── module_inventory.md
│   └── modules_index.json                     # machine lookup: module_id → paths
├── modules/
│   └── <module_id>/
│       ├── module_brief.json                  # dispatch contract for this module
│       ├── dimension_index.json               # dimension → artifact path map
│       ├── node-results/
│       │   ├── presentation-resource/
│       │   │   ├── presentation_resource.json
│       │   │   ├── presentation_resource.md
│       │   │   └── downloaded_resources/    # optional; presentation-resource only
│       │   ├── project-architecture/
│       │   │   ├── project_architecture.json
│       │   │   └── project_architecture.md
│       │   ├── data-contract-flow/
│       │   │   ├── data_flow_tracker_report.json
│       │   │   ├── data_flow_tracker_report.md
│       │   │   ├── data_contract_flow.json
│       │   │   └── data_contract_flow.md
│       │   └── behavior-logic/
│       │       ├── behavior_logic.json
│       │       └── behavior_logic.md
│       └── representation/
│           ├── module_representation.json
│           ├── module_representation.md
│           └── module_ui_representation.md      # independent UI-only handoff (Required Markdown trees)
├── global/
│   ├── cross_module_architecture.json
│   ├── cross_module_architecture.md
│   ├── cross_module_data_logic.json
│   ├── cross_module_data_logic.md
│   ├── migration_assembly_basis.json
│   ├── migration_assembly_basis.md
│   ├── global_representation.json
│   └── global_representation.md
└── SPEC/
    ├── prd.md
    ├── design.md
    ├── verification.md
    └── plan.md                                # migration mode only
```

### Path Variables (stable across runs)

| Variable | Resolved path |
|---|---|
| `output_root` | `<output_dir or ~/.a2c_agents/understand>/android-project-analyst` |
| `workspace_state_dir` | `<output_root>/workspace-state` |
| `module_index_dir` | `<output_root>/module-index` |
| `module_root` | `<output_root>/modules/<module_id>` |
| `dimension_dir` | `<module_root>/node-results/<dimension>` |
| `module_representation_dir` | `<module_root>/representation` |
| `global_dir` | `<output_root>/global` |
| `spec_dir` | `<output_root>/SPEC` |

### Filename Invariants (downstream parsers depend on these)

- JSON primary artifacts use **snake_case** basenames matching the dimension or record type (`presentation_resource.json`, not `presentation-resource.json`).
- Dimension folder names use **kebab-case** node ids (`node-results/presentation-resource/`).
- `module_id` folder names use the **same slug** as in `module_inventory.json` and `modules_index.json`.
- No artifact outside `<output_root>/` is valid for gates below.

---

## Write Order (Leader Schedule)

Artifacts MUST be produced in this order. Skipping a layer invalidates downstream trigger gates.

| Step | Gate id | Required artifacts before next step |
|---|---|---|
| 0 | `G0` | `run_manifest.json` |
| 1 | `G1` | `workspace-state/analysis_workspace_state.*` (initialized) |
| 2 | `G2` | `module-index/module_inventory.*`, `module-index/modules_index.json` |
| 3 | `G3` | per `module_id`: `module_brief.json` |
| 4 | `G4` | per `module_id`: all three Stage A dimension JSON+MD pairs |
| 5 | `G5` | per `module_id`: `behavior-logic` dimension JSON+MD pair |
| 6 | `G6` | per `module_id`: `dimension_index.json`, `representation/module_representation.*`, `representation/module_ui_representation.md` |
| 7 | `G7` | `global/cross_module_architecture.*`, `global/cross_module_data_logic.*`, `global/migration_assembly_basis.*` |
| 8 | `G8` | `global/global_representation.*` |
| 9 | `G9` | `SPEC/prd.md`, `SPEC/design.md`, `SPEC/verification.md`, migration-only `SPEC/plan.md` |

---

## Artifact Registry: Path, Owner, Content, Trigger Role

### Run identity

| Path | Owner | Required JSON / content keys | Downstream trigger role |
|---|---|---|---|
| `run_manifest.json` | Leader | `source_project_path`, `mode`, `analysis_scope`, `output_root`, `schedule_version`, `handoff_package`, `allowed_path_roots`, `dependency_preflight`, `timestamp`; migration mode adds `target_project_path` | **All handlers** — resolves `output_root` and declares which gate package this run claims |

`handoff_package` MUST list absolute paths to the gate entry artifacts the run claims ready (see Handoff Packages below).

### Workspace ledger

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `workspace-state/analysis_workspace_state.json` | `analysis-workspace-state` | `module_status`, `node_status`, `artifact_inventory`, `stale_upstream_inputs`, `rerun_history`, `blocking_gaps`, `next_actions`, `handoff_gates` | **All handlers** — refuse consumption when `stale_upstream_inputs` marks a required artifact stale or `handoff_gates.*.ready` is false |

### Module index layer

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `module-index/module_inventory.json` | Leader | `analysis_modules[]`, `module_order[]`, `out_of_scope[]`, per-module `module_id`, `module_type`, `source_roots`, `ui_scope`, `logic_scope`, `data_scope`, `resource_scope`, `depends_on`, `module_output_root` | **Module scheduling** — authoritative partition; migrator maps `module_id` → source scope |
| `module-index/module_inventory.md` | Leader | Boundary evidence and scope notes (no dimension analysis) | Agent-readable scope confirmation |
| `module-index/modules_index.json` | Leader | `schema_version`, `output_root`, `modules[]` with per-entry `module_id`, `status`, `module_output_root`, `module_brief_path`, `dimension_roots`, `representation_paths`, `depends_on` | **Primary routing index** — downstream handlers resolve module folders only through this file |

#### `modules_index.json` minimum schema

```json
{
  "schema_version": "1.0",
  "output_root": "",
  "module_order": [],
  "modules": [
    {
      "module_id": "",
      "status": "scheduled | completed | blocked | out_of_scope",
      "module_output_root": "",
      "module_brief_path": "",
      "dimension_roots": {
        "presentation-resource": "",
        "project-architecture": "",
        "data-contract-flow": "",
        "behavior-logic": ""
      },
      "representation_paths": {
        "dimension_index": "",
        "module_representation_json": "",
        "module_representation_md": "",
        "module_ui_representation_md": ""
      },
      "depends_on": []
    }
  ]
}
```

### Per-module dispatch and dimensions

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `modules/<module_id>/module_brief.json` | Leader | `module_id`, `module_type`, `source_roots`, scopes, `depends_on`, `output_root`, `dimension_output_dirs`, role hints | **Node dispatch** — nodes refuse work without this contract |
| `modules/<module_id>/node-results/presentation-resource/presentation_resource.json` | `presentation-resource` | `module_id`, `screen_inventory`, `ui_layout_view_trees[]` (each with non-empty `tree_text` in `tree_text_format: required-markdown-v1` when `representation_promotion_ready: true`), `navigation_edges`, `cross_module_references[]`, `resource_usage_map`, `representation_promotion`, `evidence_paths` | UI understanding, resource migration, navigation handoff, representation promotion |
| `modules/<module_id>/node-results/project-architecture/project_architecture.json` | `project-architecture` | `module_id`, `module_topology`, `detected_patterns`, `layer_roles`, `cross_module_dependencies[]`, `migration_constraints`, `evidence_paths` | Architecture migration, dependency/platform gate |
| `modules/<module_id>/node-results/data-contract-flow/data_contract_flow.json` | `data-contract-flow` | `module_id`, API/model contracts, `end_to_end_flows`, `cross_module_data_links[]`, `evidence_paths` | Data/API migration, repository mapping |
| `modules/<module_id>/node-results/data-contract-flow/data_flow_tracker_report.json` | `data-contract-flow` | `module_id`, `handler_steps[]`, `coverage_summary`, `follow_ups[]`, `blocking_gaps`, `linked_artifacts` | Investigation coverage gate, workspace ledger, rerun routing |
| `modules/<module_id>/node-results/data-contract-flow/data_flow_tracker_report.md` | `data-contract-flow` | Step coverage table, coverage summary, open follow-ups, blockers | Agent-readable investigation handoff |
| `modules/<module_id>/node-results/behavior-logic/behavior_logic.json` | `behavior-logic` | `module_id`, `screen_logic`, `control_flows`, `cross_module_interactions[]`, upstream alignment refs | Behavior/test planning, control-flow migration |
| `modules/<module_id>/dimension_index.json` | Leader | `module_id`, `dimensions{}` with four entries, each with `node_id`, `output_dir`, `json_path`, `md_path`, `status` | **Per-module completeness gate** — handlers verify all four dimensions before consuming representation |
| `modules/<module_id>/representation/module_representation.json` | Leader | `module_id`, `ui_representation_md_path`, `dimension_traceability[]`, `presentation_slice.ui_layout_view_trees[]` (verbatim `tree_text` from `presentation_resource.json`), synthesized slices per dimension, `intra_module_gaps`, `readiness` | **Module-level handoff** — migrator loads this for a scoped `module_id` |
| `modules/<module_id>/representation/module_ui_representation.md` | Leader | Independent UI-only handoff: entry points, screen inventory summary, every checked screen/section with verbatim Required Markdown `tree_text` blocks (`tree_text_format: required-markdown-v1`), navigation graph, UI gaps | **Primary UI migration handoff** — agents read this for layout/composable restoration without parsing full module synthesis |

#### `module_representation.json` minimum schema (presentation trees)

Leader MUST promote every `ui_layout_view_trees[]` item with `representation_promotion_ready: true` from `presentation_resource.json` into `presentation_slice.ui_layout_view_trees[]` **verbatim** — do not summarize, truncate, or reformat `tree_text`.

```json
{
  "module_id": "",
  "schema_version": "1.0",
  "ui_representation_md_path": "representation/module_ui_representation.md",
  "dimension_traceability": [
    {
      "dimension": "presentation-resource",
      "json_path": "",
      "md_path": "",
      "status": "completed"
    }
  ],
  "presentation_slice": {
    "source_artifact": "node-results/presentation-resource/presentation_resource.json",
    "entry_points": [],
    "screen_inventory": [],
    "ui_layout_view_trees": [
      {
        "screen_name": "",
        "section_name": "",
        "ui_technology": "XML | Compose | mixed | custom view | unknown",
        "layout_or_composable": "",
        "checked_status": "checked | partial | inferred | unknown",
        "source_paths": [],
        "tree_text": "",
        "tree_text_format": "required-markdown-v1",
        "unknowns": [],
        "dimension_source_path": ""
      }
    ],
    "navigation_edges": [],
    "presentation_modules": []
  },
  "intra_module_gaps": [],
  "readiness": "ready | ready_with_assumptions | blocked"
}
```

#### `module_ui_representation.md` (independent UI handoff — Leader writes at G6)

Leader MUST write this file for every module with UI scope (or with `ui_scope: none` and evidence when no UI exists). It is the **canonical standalone UI representation** — not embedded inside `module_representation.md`.

Required structure:

```markdown
# Module UI Representation: <module_id>

> tree_text_format: required-markdown-v1
> presentation_source: node-results/presentation-resource/presentation_resource.json

## Metadata
- module_id: <module_id>
- tree_text_format: required-markdown-v1
- checked_tree_count: <N>
- promotion_ready_count: <N>

## Entry Points
| name | type | source_path | route_or_action |
|---|---|---|---|

## Screen Inventory
| screen_name | ui_technology | layout_or_composable | checked_status |
|---|---|---|---|

## UI Layout Trees

### <screen_name> — <section_name>
- ui_technology: <value>
- layout_or_composable: <value>
- checked_status: <value>
- source_paths: <paths>

```text
<tree_text verbatim — Required Markdown shape>
```

(repeat per checked screen/section)

## Navigation
(Mermaid graph when evidence supports it)

## UI Gaps
(screens/sections with representation_promotion_ready: false or empty tree_text)
```

Rules:
- Every `ui_layout_view_trees[]` item with `representation_promotion_ready: true` MUST appear under `## UI Layout Trees` with its `tree_text` in a ` ```text ` fence, byte-identical to `presentation_resource.json`.
- `module_representation.md` MUST link to this file (`ui_representation_md_path`) and MUST NOT duplicate full tree blocks — summary only.

#### `dimension_index.json` minimum schema

```json
{
  "module_id": "",
  "schema_version": "1.0",
  "dimensions": {
    "presentation-resource": {
      "node_id": "presentation-resource",
      "output_dir": "",
      "json_path": "",
      "md_path": "",
      "status": "completed | blocked | missing",
      "evidence_count": 0
    },
    "project-architecture": { },
    "data-contract-flow": {
      "node_id": "data-contract-flow",
      "output_dir": "",
      "json_path": "",
      "md_path": "",
      "tracker_json_path": "",
      "tracker_md_path": "",
      "status": "completed | blocked | missing",
      "evidence_count": 0
    },
    "behavior-logic": { }
  },
  "representation_ready": false
}
```

Each dimension entry MUST have resolvable `json_path` and `md_path` before `representation_ready` is true. The `data-contract-flow` entry MUST also have resolvable `tracker_json_path` and `tracker_md_path`.

### Cross-module global records (migration assembly basis)

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `global/cross_module_architecture.json` | Leader | `architectural_edges[]` (`from_module_id`, `to_module_id`, `edge_type`, `evidence_paths`), `navigation_glue`, `shared_platform_services`, `di_bridges`, `conflicts[]` | **Inter-module architecture gate** — required before global representation and migrator topology planning |
| `global/cross_module_data_logic.json` | Leader | `shared_contracts[]`, `data_flow_edges[]`, `control_flow_edges[]`, `event_bus_links[]`, `evidence_paths` | **Inter-module data/logic gate** — required for API/state handoff across modules |
| `global/migration_assembly_basis.json` | Leader | `assembly_order[]`, `integration_checkpoints[]`, `shared_contracts_to_preserve[]`, `partial_migration_boundaries[]`, `blockers[]`, `evidence_paths` | **Primary migrator scheduling trigger** — `android-to-kmp-migrator` uses this to order `migration_module_id` work |

#### `migration_assembly_basis.json` minimum schema

```json
{
  "schema_version": "1.0",
  "output_root": "",
  "assembly_order": ["module_id_1", "module_id_2"],
  "integration_checkpoints": [
    {
      "checkpoint_id": "",
      "after_module_id": "",
      "required_artifacts": [],
      "shared_contracts": [],
      "verification_focus": []
    }
  ],
  "shared_contracts_to_preserve": [],
  "partial_migration_boundaries": [],
  "blockers": [],
  "evidence_paths": []
}
```

### Global synthesis and SPEC

| Path | Owner | Required content | Downstream trigger role |
|---|---|---|---|
| `global/global_representation.json` | Leader | `module_summaries[]`, refs to cross-module global records, `global_readiness`, `evidence_index` | **Full-project handoff** — exploration overview and migrator context |
| `SPEC/prd.md` | Leader | Product scope, journeys, entities, rules (evidence-backed) | Exploration + migration product baseline |
| `SPEC/design.md` | Leader | Architecture, modules, integration view citing cross-module global records | Exploration + migration design baseline |
| `SPEC/verification.md` | Leader | Coverage matrix, traceability, `readiness` verdict (`ready \| ready_with_assumptions \| blocked`), `handoff_gates` status | **Universal readiness gate** — downstream workflows read verdict before dispatch |
| `SPEC/plan.md` | Leader (migration only) | Assembly order from `migration_assembly_basis.*`, milestones, source-to-target mapping | **Migration plan gate** — required for `android-to-kmp-migrator` |

---

## Handoff Packages (Downstream Trigger Conditions)

Downstream handlers MUST NOT start unless the declared package gate passes. A gate passes only when **every listed path exists, is non-empty, matches schema/content rules above, and is not marked stale** in `analysis_workspace_state.json`.

### Package `P0` — Run identity

**Trigger for**: any downstream read of this analysis run.

| Required paths |
|---|
| `run_manifest.json` |
| `workspace-state/analysis_workspace_state.json` |

**Fail closed when**: `output_root` mismatch, manifest missing, or ledger reports `blocking_gaps` without explicit `ready_with_assumptions` override in `SPEC/verification.md`.

### Package `P1` — Module index routing

**Trigger for**: per-module analyst rerun, adapter scoped dispatch, migrator module lookup.

| Required paths |
|---|
| `module-index/module_inventory.json` |
| `module-index/modules_index.json` |

**Fail closed when**: `modules_index.json` cannot resolve a requested `module_id`, or `module_order` is empty for in-scope work.

### Package `P2` — Module dimension completeness

**Trigger for**: module representation consumption, focused UI/logic/architecture handoff from `migration-task-adapter`.

| Required paths (per `module_id`) |
|---|
| `modules/<module_id>/module_brief.json` |
| `modules/<module_id>/dimension_index.json` (all four dimensions `status: completed`) |
| all four dimension JSON+MD pairs under `node-results/<dimension>/` |
| `modules/<module_id>/node-results/data-contract-flow/data_flow_tracker_report.json` and `.md` |

**Fail closed when**: any dimension is `missing`, `blocked`, or paths in `dimension_index.json` do not resolve; `data-contract-flow` tracker report is missing, empty, or `handler_steps` do not cover all eleven investigation steps.

### Package `P3` — Module representation handoff

**Trigger for**: `android-to-kmp-migrator` per-module planning scoped to one legacy `module_id`.

| Required paths (per `module_id`) |
|---|
| Package `P2` artifacts |
| `modules/<module_id>/representation/module_representation.json` |
| `modules/<module_id>/representation/module_representation.md` |
| `modules/<module_id>/representation/module_ui_representation.md` |

**Fail closed when**: representation references dimension paths that fail Package `P2`, any `presentation_resource.json` item with `representation_promotion_ready: true` is missing its verbatim `tree_text` in `presentation_slice.ui_layout_view_trees[]`, or the same `tree_text` is missing from `module_ui_representation.md`.

### Package `P4` — Cross-module assembly basis

**Trigger for**: `android-to-kmp-migrator` whole-project or multi-module scheduling.

| Required paths |
|---|
| Package `P1` artifacts |
| Package `P3` artifacts for every `module_id` in `migration_assembly_basis.json` → `assembly_order` |
| `global/cross_module_architecture.json` |
| `global/cross_module_data_logic.json` |
| `global/migration_assembly_basis.json` |

**Fail closed when**: `assembly_order` omits a scheduled module without `out_of_scope` evidence, or cross-module edges lack `evidence_paths`.

### Package `P5` — Exploration SPEC handoff

**Trigger for**: onboarding, documentation-only consumption, adapter `only_understand_*` routes.

| Required paths |
|---|
| Package `P0` artifacts |
| Package `P1` artifacts |
| `global/global_representation.json` |
| `SPEC/prd.md`, `SPEC/design.md`, `SPEC/verification.md` |

**Fail closed when**: `SPEC/verification.md` → `readiness: blocked`.

### Package `P6` — Migration SPEC handoff (full pipeline entry)

**Trigger for**: `android-to-kmp-migrator` controller start, migration-mode adapter orchestration.

| Required paths |
|---|
| Package `P4` artifacts |
| Package `P5` artifacts |
| `global/global_representation.json` |
| `SPEC/plan.md` |

**Fail closed when**: `readiness` is `blocked`, `plan.md` assembly order disagrees with `migration_assembly_basis.json` without documented conflict in `verification.md`, or `run_manifest.json` → `mode` is not `migration`.

---

## Leader Obligations For Downstream Triggers

Before claiming run completion, the Leader MUST:

1. Write `handoff_gates` into `analysis_workspace_state.json` with boolean `ready` flags for `P0`–`P6` and lists of missing paths per false gate.
2. Mirror the same `handoff_gates` summary in `SPEC/verification.md` under a `## Handoff Gates` section.
3. Set `run_manifest.json` → `handoff_package` to the **highest package actually ready** (`P0`..`P6`) and list every artifact path in that package.
4. Never set `readiness: ready` in `verification.md` when the target downstream package gate is false.
5. Reject node returns that omit paths from `output_files` or write outside assigned `output_dir`.

## Node Obligations

Every node MUST:

- Write only under the `output_dir` declared in its dispatch contract.
- Use exact filenames from this contract (JSON snake_case basename, dimension folder kebab-case).
- Include `module_id` in every dimension JSON artifact.
- Populate cross-module pointer arrays (`cross_module_references`, `cross_module_dependencies`, `cross_module_data_links`, `cross_module_interactions`) with `target_module_id` and `source_paths` so the Leader can build Package `P4` without re-reading source.
- `data-contract-flow` MUST write and maintain `data_flow_tracker_report.*` during investigation and list all four output files in `output_files`.

## Invalid Artifact Handling (downstream uniform rule)

| Condition | Downstream handler action |
|---|---|
| Path missing | `blocked` — return `blocking_gaps: [{ "artifact": "<path>", "reason": "missing" }]` |
| File empty | `blocked` — reason `empty` |
| Path outside `output_root` | `blocked` — reason `out_of_path` |
| Stale per workspace ledger | `needs_rerun` — name owning node or Leader integration step |
| Schema/content invalid | `blocked` — reason `invalid_contract`; cite this file section |
| `readiness: blocked` in verification | `blocked` — do not start migration or validation |

Downstream handlers MUST NOT parse chat text, controller summaries, or partial copies when gate artifacts are absent.
