# Multi-CLI Plugins Ecosystem

A cross-CLI repository for AI-powered development workflows. It currently ships Android-to-Kotlin Multiplatform (KMP) migration tooling across several coding agents, plus a Claude Code design-to-code workflow for Figma-to-Compose work.

## Repository Overview

| Path | Contents |
| --- | --- |
| `claude-code-plugins/` | Claude Code plugin marketplace with `kmp-migration` and `flow_d2c`. |
| `codex-plugins/` | Codex plugin distribution for the KMP migration skills. |
| `gemini-extensions/` | Gemini CLI extension distribution for the KMP migration skills. |
| `npx_skills/` | npm package `@code-migration/wow-migrator` for installing KMP skills into multiple AI coding tools. |
| `CONTRIBUTING.md` | Contribution and plugin-creation guidelines. |

## Available Tooling

| Toolkit | Path | Current Version | Purpose |
| --- | --- | --- | --- |
| `kmp-migration` for Claude Code | `claude-code-plugins/kmp-migration/` | `0.1.30` | End-to-end Android-to-KMP workflow covering task routing, Android project analysis, SPEC generation, bounded KMP migration, KMP validation, targeted KMP fixes, JetBrains MCP-assisted code intelligence, workflow contracts, `.env` edit protection, and agent memory/skill maintenance. |
| `flow_d2c` for Claude Code | `claude-code-plugins/flow_d2c/` | `0.1.0` | Figma to React to optimized mobile React to Android/KMP/CMP Compose workflow with UI reconstruction scoring, Compose adapter bundle generation, and the `anchor-d2c-mcp` Figma-to-code MCP server. |
| `codex-kmp-migration` | `codex-plugins/kmp-migration/` | `0.1.2` | Codex skill distribution for Android project analysis, Android-to-KMP migration, and migrated KMP validation. |
| `kmp-migration` for Gemini CLI | `gemini-extensions/kmp-migration/` | `0.1.2` | Gemini extension containing the same three KMP-focused skills plus `GEMINI.md` context and a local MCP entry point. |
| `@code-migration/wow-migrator` | `npx_skills/` | `0.2.10` | npm installer that copies the bundled Android/KMP swarm skills into Claude Code, Codex, Cursor, Gemini, OpenCode, OpenClaw, and JiuwenSwarm skill directories. |

## KMP Migration Content

The KMP migration toolkit is shared across Claude Code, Codex, Gemini, and the npm skill installer. The current npm bundle mirrors the Claude Code KMP `skills/` directory and includes:

| Agent or Skill | Purpose |
| --- | --- |
| `operating-instructions` | Shared baseline operating rules for KMP migration swarm skills, including verification labels, scope control, rollback handling, and final honesty reporting. |
| `coding-task-adapter` | Front-door router that classifies Android/KMP migration requests, preserves partial-migration scope, invokes the right downstream workflow, records stage gates, and emits the final adapter report. |
| `android-project-analyst` | Analyzes legacy Android projects for architecture, XML/Compose UI, resources, APIs, data flow, control flow, and SPEC output. |
| `android-to-kmp-migrator` | Migrates Android behavior into a KMP/CMP target with source understanding, target understanding, resource/theme/navigation/platform/state mapping, UI and logic implementation, review/fix loops, build gates, and migration reporting. |
| `kmp-test-validator` | Validates migrated KMP output against Android source behavior, SPEC evidence, migration reports, build/preview gates, optional business/Figma UI tests, and supplied test cases. |

The Claude Code KMP plugin additionally ships:

- Agents: `android-project-analyst`, `android-to-kmp-migrator`, `kmp-test-validator`, `memory-curator`, and `skill-maintenance-advisor`.
- Slash commands: `/legacy-android-understand` and `/fix-issue-kmp`.
- Hook protection: a `PreToolUse` hook that blocks writes to `.env` files.
- MCP configuration: a JetBrains IDE MCP server entry at `http://localhost:64342/sse` for optional Android Studio project/code intelligence.
- Rules: stage/node input contracts, durable output requirements, workflow gates, and machine-routable agent artifact contracts.

## Design-To-Code Content

`flow_d2c` is a Claude Code plugin for converting Figma designs into Compose implementations. It contains:

- `flow_figma_compose_wf`: top-level Figma to React to Compose workflow orchestrator.
- `mobile-react-refactor`: refactors generated React into a mobile-responsive, interaction-aware React flow.
- `react-to-compose-ui`: translates optimized React into Android/KMP/CMP Compose and can integrate into an existing target repo.
- `compose-adapter-generator`: creates draft Compose-library adapter bundles for later integration.
- `ui-reconstruction-score`: compares design screenshots with implementation screenshots and reports fidelity issues.
- `tools/anchor-d2c-mcp`: MCP server exposing Figma-to-code conversion and screenshot-fetching tools.

## Install Guidance

Clone the repository:

```bash
git clone https://github.com/winson-AI/cli-plugins.git
cd cli-plugins
```

### Claude Code

Load a plugin directly during development:

```bash
claude --plugin-dir claude-code-plugins/kmp-migration
claude --plugin-dir claude-code-plugins/flow_d2c
```

Or add the local marketplace after Claude Code starts:

```bash
/plugin marketplace add claude-code-plugins
/plugin install kmp-migration
/plugin install flow_d2c
```

### Codex

Add the Codex marketplace from the `codex-plugins` directory, then install `codex-kmp-migration` from the plugin UI.

```bash
cd codex-plugins
codex plugin marketplace add .
```

### Gemini CLI

Install the Gemini extension from its extension directory:

```bash
cd gemini-extensions/kmp-migration
gemini extensions install .
gemini extensions list
```

### npm Skill Installer

Install the skill installer globally:

```bash
npm install -g @code-migration/wow-migrator
```

Then install the bundled KMP skills into detected tools:

```bash
wow-migrator install --yes
wow-migrator install --platform cursor,codex --yes
wow-migrator list
```

Set `WOW_MIGRATOR_SKIP_POSTINSTALL=1` during `npm install` to skip automatic postinstall skill installation.

## Usage Examples

```text
Analyze this Android project and generate PRD, DESIGN, and verification specs.
Migrate this Android feature module to Kotlin Multiplatform.
Validate this migrated KMP project against the Android source behavior and test cases.
Convert this Figma flow into Compose and integrate it into the existing KMP app.
```

## Versioning

When changing plugin behavior, keep these manifests aligned with the related distribution:

- `claude-code-plugins/.claude-plugin/marketplace.json`
- `claude-code-plugins/kmp-migration/.claude-plugin/plugin.json`
- `claude-code-plugins/flow_d2c/.claude-plugin/plugin.json`
- `codex-plugins/kmp-migration/.codex-plugin/plugin.json`
- `gemini-extensions/kmp-migration/gemini-extension.json`
- `gemini-extensions/kmp-migration/package.json`
- `npx_skills/package.json`

Current versions: Claude Code `kmp-migration` is `0.1.30`, Claude Code `flow_d2c` is `0.1.0`, Codex and Gemini KMP distributions are `0.1.2`, and the npm skill installer is `0.2.10`.

## Project Structure

```text
cli-plugins/
├── claude-code-plugins/
│   ├── .claude-plugin/          # Claude Code marketplace registry
│   ├── kmp-migration/           # Android-to-KMP Claude Code plugin
│   └── flow_d2c/                # Figma-to-Compose Claude Code plugin
├── codex-plugins/
│   └── kmp-migration/           # Codex KMP migration plugin
├── gemini-extensions/
│   └── kmp-migration/           # Gemini CLI KMP migration extension
├── npx_skills/                  # npm skill installer package
├── CONTRIBUTING.md              # Contribution guidelines
└── README.md                    # This file
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for project structure and contribution guidelines.

## License

MIT
