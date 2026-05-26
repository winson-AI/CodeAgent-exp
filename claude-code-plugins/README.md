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
| [kmp-migration](kmp-migration/) | End-to-end Android to KMP migration toolkit. Includes specialized agents for project analysis, source-to-source migration, fidelity-first test validation, memory curation, skill maintenance, Android understanding, targeted KMP issue fixing, and `.env` edit protection. | 0.1.15 |
| [flow_d2c](flow_d2c/) | Figma → React → optimized mobile React → Android/KMP/CMP Compose design-to-code workflow. Bundles the orchestrator skill, the React refactor and Compose translation skills, a Compose-library adapter generator, a UI reconstruction scoring skill, and the `anchor-d2c-mcp` MCP server for Figma-to-code conversion. | 0.1.0 |

### kmp-migration

**What it ships:**
- 5 specialized agents:
  - `android-project-analyst`: Deep Android architecture, UI, data/control flow analysis, and SPEC generation.
  - `android-to-kmp-migrator`: Runnable Android-to-KMP migration with mandatory compile, preview, and use-case validation.
  - `kmp-test-validator`: High-fidelity validation against Android behavior and provided test cases.
  - `memory-curator`: Agent memory audit, cleanup recommendations, and recovery state records.
  - `skill-maintenance-advisor`: Periodic advice for creating or updating reusable skills from conversation context.
- 2 slash commands:
  - `/legacy-android-understand`: Invoke `android-project-analyst` in exploration mode for project, module, feature, question, or target-code understanding.
  - `/fix-issue-kmp`: Fix known KMP compile issues or migrated use-case failures with targeted edits, command logs, and rerun evidence.
- 1 hook:
  - `PreToolUse` `.env` protection: blocks write/edit tool calls targeting `.env` files.
- Supporting scripts and configuration for plugin hooks, MCP/LSP integration, monitors, and settings.

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
│   ├── skills/                   # Auto-invoked skills
│   ├── commands/                 # Slash commands
│   ├── agents/                   # Specialized subagents
│   ├── hooks/                    # Tool-layer enforcement
│   ├── scripts/                  # Hook and utility scripts
│   ├── monitors/                 # Monitor configuration
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
