# WOW Migrator

Install Android to Kotlin Multiplatform migration skills into AI coding tools through npm.

## Install

```bash
npm install -g @code-migration/wow-migrator
```

During `npm install`, the package runs `postinstall` and installs the bundled skills into every supported tool it detects on the machine.

To install the CLI but skip automatic skill installation:

```bash
WOW_MIGRATOR_SKIP_POSTINSTALL=1 npm install -g @code-migration/wow-migrator
```

## What Gets Installed

The package bundles these skills:

- `android-project-analyst`
- `android-to-kmp-migrator`
- `kmp-test-validator`

They are copied into each target tool's `skills` directory. Re-running install is idempotent: the bundled skill directories are replaced with the package version.

## CLI Commands

The primary CLI command is `wow-migrator`.

```bash
wow-migrator install --yes
wow-migrator install --platform claude --yes
wow-migrator install --platform cursor,codex --yes
wow-migrator install --target "Claude Code,Codex"
wow-migrator uninstall --target all --yes
wow-migrator list
wow-migrator config
```

## Install By Platform

Use `--platform`, `--target`, or `--tool`. They are aliases and accept a single platform, a comma-separated list, or `all`.

```bash
wow-migrator install --platform claude --yes
wow-migrator install --platform cursor,codex --yes
wow-migrator install --platform all --yes
```

Supported platforms:

| Platform | Aliases | Detection | Skills directory |
| --- | --- | --- | --- |
| OpenClaw | `openclaw`, `open-claw` | `~/.openclaw` or `openclaw` | `~/.openclaw/skills` |
| Claude Code | `claude`, `claude-code`, `claudecode` | `~/.claude` or `claude` | `~/.claude/skills` |
| OpenCode | `opencode`, `open-code` | `~/.config/opencode` or `opencode` | `~/.config/opencode/skills` |
| Codex | `codex`, `openai-codex` | `~/.codex` or `codex` | `~/.codex/skills` |
| Cursor | `cursor` | `~/.cursor` or `cursor` | `~/.cursor/skills` |
| Gemini | `gemini`, `gemini-cli` | `~/.gemini` or `gemini` | `~/.gemini/skills` |
| JiuwenSwarm | `jiuwen`, `jiuwenswarm`, `jiuwen-swarm`, `jiuwenclaw` | `~/.jiuwenswarm` or Jiuwen CLI commands | `~/.jiuwenswarm/agent/workspace/skills` |

## Configuration

View or create the config file:

```bash
wow-migrator config
```

The config file is stored at:

```text
~/.wow-migrator/config.json
```

Edit it to add custom tools, aliases, commands, or skills directories:

```json
{
  "tools": [
    {
      "name": "Claude Code",
      "aliases": ["claude", "claude-code"],
      "markerDir": "~/.claude",
      "commands": ["claude"],
      "skillsDir": "~/.claude/skills"
    }
  ]
}
```

## Other Functions

List bundled skills:

```bash
wow-migrator list
```

Remove bundled skills from selected platforms:

```bash
wow-migrator uninstall --platform claude,cursor --yes
wow-migrator uninstall --platform all --yes
```

Preview an install without writing files:

```bash
wow-migrator install --platform all --dry-run --yes
```
