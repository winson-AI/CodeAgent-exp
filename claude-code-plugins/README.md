# KMP Migration Toolkit for Claude Code

A collection of specialized agents, commands, and guardrails for knowledge workers migrating Android projects to Kotlin Multiplatform (KMP). Part of the `cli-plugins` ecosystem.

## Install

```bash
# Add the marketplace (one-time)
/plugin marketplace add <repository-url>

# Install the plugin
/plugin install kmp-migration
```

Or load the plugin directly for development:

```bash
claude --plugin-dir ./claude-code-plugins/kmp-migration
```

## Available Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| [kmp-migration](kmp-migration/) | End-to-end Android to KMP migration toolkit orchestrated by a front-door task adapter. Routes understand vs. migration requests, runs dual source+target understanding for migrations, then source-to-source migration and fidelity-first test validation. Includes specialized agents, slash commands, the Ponytail coding guardrail, Android Studio MCP-assisted project/code intelligence, agent-facing stage contracts, and `.env` edit protection. | 0.1.30 |
| [flow_d2c](flow_d2c/) | Figma → React → optimized mobile React → Android/KMP/CMP Compose design-to-code workflow. Bundles the orchestrator skill, the React refactor and Compose translation skills, a Compose-library adapter generator, a UI reconstruction scoring skill, and the `anchor-d2c-mcp` MCP server for Figma-to-code conversion. | 0.1.0 |

### kmp-migration

**Overall orchestration workflow:**

![KMP migration overall orchestration workflow](kmp-migration/assets/overall_migration.png)

The `coding-task-adapter` is the front door: it classifies the request, then drives a staged pipeline with gates between each boundary.

- **Understand mode** (`only_understand_*`) — one `android-project-analyst` run on the source produces the understand results and file system, then stops.
- **Migrate mode** (`migration`) — the analysis stage understands **both** projects, running `android-project-analyst` once on the source (Source Project Subsystem, `P6`) and once on the target (Target Project Subsystem, same file format) into two distinct understand roots. The `android-to-kmp-migrator` then fetches both subsystems, clarifies full vs. partial scope, transfers the requested module from source into the target, and hands off to the mandatory `kmp-test-validator` before the adapter issues its final verdict.

**What it ships:**
- 7 skills (Swarm Skills + guardrails) under `skills/`:
  - `coding-task-adapter`: Front-door orchestrator that routes understand/migration/validation tasks, runs dual source+target understanding for migrations, enforces stage gates, and emits the final adapter report.
  - `android-project-analyst`: Module-first Android (and KMP-target) understanding across presentation/architecture/data/behavior dimensions, cross-module assembly basis, and SPEC generation.
  - `android-to-kmp-migrator`: Source-to-target KMP migration that consumes both understand subsystems and edits the target project, with analytics (埋点) and entry-point restoration.
  - `kmp-test-validator`: Fidelity-first validation (trust + restoreability), build/compile gate, entry-point launch, and business testing against Android behavior and provided test cases.
  - `operating-instructions`: Shared baseline conduct layer included in every dispatched role.
  - `ponytail` / `ponytail-review`: Ponytail coding guardrail (decision ladder + review) that checks whether work can be skipped, reused, or reduced before writing new code.
- 5 specialized agents under `agents/`:
  - `android-project-analyst`, `android-to-kmp-migrator`, `kmp-test-validator` controllers, plus `memory-curator` (memory audit/recovery) and `skill-maintenance-advisor` (periodic skill upkeep advice).
- 2 slash commands:
  - `/legacy-android-understand`: Invoke `android-project-analyst` in exploration mode for project, module, feature, question, or target-code understanding.
  - `/fix-issue-kmp`: Fix known KMP compile issues or migrated use-case failures with targeted edits, command logs, and rerun evidence.
- Hooks (`hooks/hooks.json`):
  - `PreToolUse` `.env` protection: blocks write/edit tool calls targeting `.env` files.
  - Ponytail lifecycle hooks: activate the guardrail on `SessionStart`, propagate it on `SubagentStart`, and track `/ponytail` modes from `UserPromptSubmit`.
- 1 MCP config:
  - `jetbrains`: connects to Android Studio or another JetBrains IDE through the IDE MCP server on `http://localhost:64342/sse`; agents use it optionally for project structure, code intelligence, diagnostics, build hooks, run configs, and IDE-safe edits.
- Agent-facing rules under `rules/`:
  - Stage/node I/O contracts, workflow-stage gates, agent-only output, phase-document templates, status-controller task ledger, fidelity-gate verification, and the Ponytail rule.
- Supporting assets and configuration: workflow diagrams (`assets/`), hook/utility scripts (`pre-edit-protect.sh`, `ktlint-format.sh`, `check-ponytail-assets.js`), output style (`terse`), theme (`dracula`), monitors, and MCP/LSP settings.

Full docs: [kmp-migration/README.md](kmp-migration/README.md)

### flow_d2c

End-to-end design-to-code workflow that turns one or more Figma sections/nodes into runnable Android Jetpack Compose code — and, when the target is a KMP/CMP repo, integrates the resulting business module into the existing codebase instead of generating an isolated demo.

**Pipeline (4 stages, enforced in order):**

1. **Input & capability detection** — normalize Figma URLs into an ordered screen list, resolve the Android project root and Compose output directory, and decide between the bundled `anchor-d2c-mcp` MCP server, an environment-provided Figma-to-React tool, or local React + screenshots.
2. **Figma → React intermediate representation** — generate per-screen React with screenshots, then stitch them into a flow entry (`ValidatedComponent.jsx` at `/validated`) with real React state/event-driven navigation.
3. **React → optimized React** *(sub-agent)* — refactor `ValidatedComponent.jsx` into `RefactoredComponent.jsx` (`/refactored`) that honors the Figma visuals/interactions, recovers mobile-responsive layout, restores high-confidence triggers (buttons, tabs, search/input bars, list items, bottom nav), and abstracts display data behind a mock API / local service boundary.
4. **Optimized React → Compose** *(sub-agent)* — translate to Android/KMP/CMP Compose; for existing repos, first review the Figma task context and target repo (navigation, theme, DI, ViewModel/repository/use case), then incrementally integrate into the existing business module, reusing what's already there.

**What it ships:**

- 5 skills under `flow_d2c/skills/`:
  - `flow_figma_compose_wf` — top-level 4-stage orchestrator; spawns sub-agents for stages 3 and 4 with fixed instructions.
  - `mobile-react-refactor` — single-screen and multi-screen React-flow refactor with layout audit, pixel-diff loop, and mock-API data abstraction.
  - `react-to-compose-ui` — React-to-Compose translation with `reactInputMode` / `targetRepoType` classification, adapter-mode support, resource materialization (SVG → `VectorDrawable`), and third-party reference codebase analysis.
  - `compose-adapter-generator` — offline pre-flight skill that produces draft Compose-library adapter bundles (`manifest.json`, `aliases.json`, `component_knowledge.json`, `prompt.md`) for later manual integration into `react-to-compose-ui/adapters/`.
  - `ui-reconstruction-score` — pairs design vs. implementation screenshots and returns either a stable similarity score or the top 1–2 code-locatable UI issues.
- 1 MCP server under `flow_d2c/tools/`:
  - `anchor-d2c-mcp` — Figma-to-code conversion MCP exposing `figma_to_code_convert` and `figma_to_code_fetch_screenshot`.

## Repository Structure

```
claude-code-plugins/
├── .claude-plugin/
│   └── marketplace.json          # Plugin registry — lists all available plugins
├── kmp-migration/                # Plugin: KMP Migration Toolkit
│   ├── .claude-plugin/
│   │   └── plugin.json           # Plugin manifest
│   ├── skills/                   # Swarm Skills: coding-task-adapter, analyst, migrator, validator, operating-instructions, ponytail(+review)
│   ├── commands/                 # Slash commands (/legacy-android-understand, /fix-issue-kmp)
│   ├── agents/                   # Specialized subagents
│   ├── hooks/                    # Tool-layer enforcement (.env protection + Ponytail lifecycle)
│   ├── rules/                    # Agent-facing stage/node contracts (.mdc)
│   ├── scripts/                  # Hook and utility scripts
│   ├── assets/                   # Workflow diagrams (overall_migration.png/.svg, wf_migration.png)
│   ├── monitors/                 # Monitor configuration
│   ├── output-styles/            # Output styles (terse)
│   ├── themes/                   # Themes (dracula)
│   ├── .mcp.json                 # Plugin MCP configuration
│   ├── .lsp.json                 # Plugin LSP configuration
│   ├── settings.json             # Plugin settings
│   ├── templates/                # Migration templates
│   └── README.md                 # Plugin-specific docs
├── flow_d2c/                     # Plugin: Figma → React → Compose D2C workflow
│   ├── .claude-plugin/
│   │   └── plugin.json           # Plugin manifest
│   ├── skills/                   # 5 skills (orchestrator, refactor, compose, adapter-gen, score)
│   │   ├── flow_figma_compose_wf/
│   │   ├── mobile-react-refactor/
│   │   ├── react-to-compose-ui/
│   │   ├── compose-adapter-generator/
│   │   └── ui-reconstruction-score/
│   └── tools/
│       └── anchor-d2c-mcp/       # Figma-to-code MCP server
├── CONTRIBUTING.md               # How to add a plugin
├── CLAUDE.md                     # Repository instructions for Claude
└── README.md                     # This file
```

## License

MIT
