# KMP Skills Installer

Install the KMP migration skills into common AI coding tools through `npm install`.

## Install From This Repo

The package is not published to the npm registry yet. Install it from the local package directory:

```bash
npm install -g /Users/winson/CodeBase/Online/cli-plugins/npx_skills
```

Or, from the repository root:

```bash
npm install -g ./npx_skills
```

To install from a tarball:

```bash
cd /Users/winson/CodeBase/Online/cli-plugins/npx_skills
npm pack
npm install -g ./code-migration-wow-migrator-0.1.0.tgz
```

After publishing this package to npm, the registry install command will be:

```bash
npm install -g @code-migration/wow-migrator
```

The package runs `postinstall` and installs bundled skills into detected tools.
Set `KMP_SKILLS_SKIP_POSTINSTALL=1` to skip the automatic install.

## Commands

```bash
kmp-skills install --yes
kmp-skills install --target "Claude Code,Codex"
kmp-skills uninstall --target all --yes
kmp-skills list
kmp-skills config
```

## Supported Targets

| Tool | Detection | Skills directory |
| --- | --- | --- |
| OpenClaw | `~/.openclaw` or `openclaw` | `~/.openclaw/skills` |
| Claude Code | `~/.claude` or `claude` | `~/.claude/skills` |
| OpenCode | `~/.config/opencode` or `opencode` | `~/.config/opencode/skills` |
| Codex | `~/.codex` or `codex` | `~/.codex/skills` |
| Cursor | `~/.cursor` or `cursor` | `~/.cursor/skills` |
| Gemini | `~/.gemini` or `gemini` | `~/.gemini/skills` |
| JiuwenSwarm | `~/.jiuwenswarm` or Jiuwen CLI commands | `~/.jiuwenswarm/agent/workspace/skills` |

## Configuration

The installer creates:

```text
~/.kmp-skills/config.json
```

Edit it to add custom tools or paths. The shape is:

```json
{
  "tools": [
    {
      "name": "Claude Code",
      "markerDir": "~/.claude",
      "commands": ["claude"],
      "skillsDir": "~/.claude/skills"
    }
  ]
}
```

## Publishing From This Repo

Before packing or publishing, sync the current plugin skills into this package:

```bash
cd npx_skills
npm run sync:skills
npm pack
```

`prepare` and `prepack` also run the sync script when the monorepo source is available.

Publish with the existing `code-migration` npm org scope:

```bash
npm publish --access public
```

If npm returns `E404 Scope not found`, confirm that the npm org exists and the
current npm user has publish access:

```bash
npm whoami
npm org ls code-migration
```

For this package, `npm org ls code-migration` should list your user with owner
or publish-capable access. After that, publish and install with:

```bash
npm publish --access public
npm install -g @code-migration/wow-migrator
```
