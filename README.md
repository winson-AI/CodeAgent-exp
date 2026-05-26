# Multi-CLI Plugins Ecosystem

A cross-CLI plugin repository for AI-powered development workflows. The current release focuses on Android-to-Kotlin Multiplatform (KMP) migration and provides matching distributions for Claude Code, Codex, and Gemini CLI.

## Available Plugins and Extensions

| Toolkit | Description | Claude Code | Codex | Gemini CLI |
|--------|-------------|-------------|-------|------------|
| **[kmp-migration](claude-code-plugins/kmp-migration/)** | End-to-end Android-to-KMP workflow covering source analysis, exploration commands, runnable KMP generation, fidelity validation, targeted KMP fixes, Android Studio MCP integration, `.env` edit protection, and agent memory/skill maintenance for Claude Code. | 0.1.16 | 0.1.2 | 0.1.2 |

## Current Agent and Skill Content

### Claude Code Agents

The Claude Code plugin ships 5 specialized agents in `claude-code-plugins/kmp-migration/agents/`:

| Agent | Purpose |
|-------|---------|
| `android-project-analyst` | Deep Android project analysis for architecture, XML/Compose UI, resources, data/control flow, onboarding docs, and SPEC output (`PRD`, `DESIGN`, `PLAN`, `verification.md`). |
| `android-to-kmp-migrator` | Controller-only Android-to-KMP migration agent that verifies migration intent, dispatches workspace-state, SPEC-delta, target-understanding, resource/theme/navigation/platform/state, UI, dataflow/logic, module/node review-fix, guard/parity/fidelity/build-check, completion-check, and migration-report node skills, and requires KMP validation gates. |
| `kmp-test-validator` | Controller-only post-migration KMP validation agent that verifies migration context, dispatches fidelity audit, validation planning, build/preview, test decomposition/execution, remediation, workspace-state, and reporting node skills. |
| `memory-curator` | Audits and optimizes agent memory stores, including retention/archive/delete recommendations and state recovery records. |
| `skill-maintenance-advisor` | Periodically reviews conversation context and recommends creating or updating reusable skills. |

### Codex and Gemini Skills

The Codex and Gemini distributions currently ship 3 KMP-focused skills:

| Skill | Codex Path | Gemini Path |
|-------|------------|-------------|
| `android-project-analyst` | `codex-plugins/kmp-migration/skills/android-project-analyst/SKILL.md` | `gemini-extensions/kmp-migration/skills/android-project-analyst/SKILL.md` |
| `android-to-kmp-migrator` | `codex-plugins/kmp-migration/skills/android-to-kmp-migrator/SKILL.md` | `gemini-extensions/kmp-migration/skills/android-to-kmp-migrator/SKILL.md` |
| `kmp-test-validator` | `codex-plugins/kmp-migration/skills/kmp-test-validator/SKILL.md` | `gemini-extensions/kmp-migration/skills/kmp-test-validator/SKILL.md` |

Claude Code also contains controller node skill specs under `claude-code-plugins/kmp-migration/skills/android-project-analyst/`, `claude-code-plugins/kmp-migration/skills/android-to-kmp-migrator/`, and `claude-code-plugins/kmp-migration/skills/kmp-test-validator/`.

### Claude Code Commands and Hooks

The Claude Code plugin includes two slash commands:

- `/legacy-android-understand`: invokes `android-project-analyst` in exploration mode for whole-project, module, feature, question, or target-code understanding.
- `/fix-issue-kmp`: fixes known KMP compile issues or migrated use-case failures with focused edits and rerun evidence.

It also includes a `PreToolUse` hook that blocks write/edit tool calls targeting `.env` files. The hook configuration lives in `claude-code-plugins/kmp-migration/hooks/hooks.json`, and its command script lives in `claude-code-plugins/kmp-migration/scripts/pre-edit-protect.sh`.

The Claude Code plugin includes `.mcp.json` with a `jetbrains` MCP server entry for Android Studio or another JetBrains IDE at `http://localhost:64342/sse`. Enable the IDE MCP server from Android Studio's **Settings | Tools | MCP Server** before use.

## Install Guidance

Clone the repository:

```bash
git clone https://github.com/winson/cli-plugins.git
cd cli-plugins
```

### Claude Code

Load the plugin directly during development:

```bash
claude --plugin-dir claude-code-plugins/kmp-migration
```

Or add the local marketplace after Claude Code starts:

```bash
/plugin marketplace add claude-code-plugins
/plugin install kmp-migration
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

## Usage

- Claude Code: invoke the agents by name or describe the Android/KMP task naturally.
- Codex: install `codex-kmp-migration`; the three `SKILL.md` definitions are detected as skills.
- Gemini CLI: install the extension; `GEMINI.md` and the bundled skills provide the migration context.

Example tasks:

```text
Analyze this Android project and generate PRD, DESIGN, and PLAN specs.
Migrate this Android feature module to Kotlin Multiplatform.
Validate this KMP project against the Android source behavior and test cases.
```

## Versioning

When changing plugin behavior, keep these versions aligned:

- `claude-code-plugins/.claude-plugin/marketplace.json`
- `claude-code-plugins/kmp-migration/.claude-plugin/plugin.json`
- `codex-plugins/kmp-migration/.codex-plugin/plugin.json`
- `gemini-extensions/kmp-migration/gemini-extension.json`
- `gemini-extensions/kmp-migration/package.json`

Current Claude Code release: `0.1.16`. Codex and Gemini remain at `0.1.2`.

## Project Structure

```text
cli-plugins/
├── claude-code-plugins/    # Claude Code marketplace and plugin
├── codex-plugins/          # Codex marketplace and plugin
├── gemini-extensions/      # Gemini CLI extension
├── CONTRIBUTING.md         # Contribution guidelines
└── README.md               # This file
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for project structure and contribution guidelines.

## License

MIT
