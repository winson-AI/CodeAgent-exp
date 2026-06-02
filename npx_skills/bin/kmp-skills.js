#!/usr/bin/env node

import { execFile } from 'node:child_process';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import readline from 'node:readline/promises';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CONFIG_DIR = path.join(os.homedir(), '.kmp-skills');
const CONFIG_PATH = path.join(CONFIG_DIR, 'config.json');
const isWindows = process.platform === 'win32';

function expandHome(input) {
  if (!input) return input;
  if (input === '~') return os.homedir();
  if (input.startsWith('~/') || input.startsWith('~\\')) {
    return path.join(os.homedir(), input.slice(2));
  }
  return input;
}

function prettyPath(input) {
  const home = os.homedir();
  const normalized = input.replace(/\\/g, '/');
  const normalizedHome = home.replace(/\\/g, '/');
  return normalized.startsWith(normalizedHome)
    ? `~${normalized.slice(normalizedHome.length)}`
    : normalized;
}

async function pathExists(input) {
  try {
    await fs.access(input);
    return true;
  } catch {
    return false;
  }
}

async function dirExists(input) {
  try {
    return (await fs.stat(input)).isDirectory();
  } catch {
    return false;
  }
}

function execFileAsync(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    execFile(command, args, options, (error, stdout, stderr) => {
      if (error) {
        reject(error);
        return;
      }
      resolve({ stdout, stderr });
    });
  });
}

async function commandExists(command) {
  if (!command) return false;
  const hasPathSeparator = command.includes('/') || command.includes('\\');
  if (hasPathSeparator) return pathExists(command);

  try {
    if (isWindows) {
      await execFileAsync('where', [command], { windowsHide: true });
    } else {
      await execFileAsync('sh', ['-c', `command -v ${shellQuote(command)}`]);
    }
    return true;
  } catch {
    return false;
  }
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

function defaultJiuwenCommands() {
  const home = os.homedir();
  const bin = isWindows ? 'Scripts' : 'bin';
  const exe = isWindows ? '.exe' : '';
  const venv = process.env.VIRTUAL_ENV
    ? [
        path.join(process.env.VIRTUAL_ENV, bin, `jiuwenswarm-start${exe}`),
        path.join(process.env.VIRTUAL_ENV, bin, `jiuwenswarm-acp${exe}`),
        path.join(process.env.VIRTUAL_ENV, bin, `jiuwenswarm-tui${exe}`)
      ]
    : [];

  return [
    ...venv,
    'jiuwenswarm-start',
    'jiuwenswarm-acp',
    'jiuwenswarm-tui',
    path.join(home, 'jiuwenclaw', 'bin', `jiuwenswarm-start${exe}`),
    path.join(home, 'jiuwenclaw', 'bin', `jiuwenswarm-acp${exe}`),
    path.join(home, 'jiuwenclaw', 'bin', `jiuwenswarm-tui${exe}`)
  ];
}

function defaultTools() {
  return [
    {
      name: 'OpenClaw',
      markerDir: '~/.openclaw',
      commands: ['openclaw'],
      skillsDir: '~/.openclaw/skills'
    },
    {
      name: 'Claude Code',
      markerDir: '~/.claude',
      commands: ['claude'],
      skillsDir: '~/.claude/skills'
    },
    {
      name: 'OpenCode',
      markerDir: '~/.config/opencode',
      commands: ['opencode'],
      skillsDir: '~/.config/opencode/skills'
    },
    {
      name: 'Codex',
      markerDir: '~/.codex',
      commands: ['codex'],
      skillsDir: '~/.codex/skills'
    },
    {
      name: 'Cursor',
      markerDir: '~/.cursor',
      commands: ['cursor'],
      skillsDir: '~/.cursor/skills'
    },
    {
      name: 'Gemini',
      markerDir: '~/.gemini',
      commands: ['gemini'],
      skillsDir: '~/.gemini/skills'
    },
    {
      name: 'JiuwenSwarm',
      markerDir: '~/.jiuwenswarm',
      commands: defaultJiuwenCommands(),
      skillsDir: '~/.jiuwenswarm/agent/workspace/skills'
    }
  ];
}

function normalizeTool(raw) {
  if (!raw || typeof raw !== 'object' || !raw.name) return null;
  const skillsDir = raw.skillsDir ?? raw.targets?.skillsDir;
  if (!skillsDir) return null;
  return {
    name: String(raw.name),
    markerDir: raw.markerDir ? String(raw.markerDir) : '',
    commands: Array.isArray(raw.commands) ? raw.commands.map(String).filter(Boolean) : [],
    skillsDir: String(skillsDir)
  };
}

async function loadConfig(options = {}) {
  if (!(await pathExists(CONFIG_PATH))) {
    const config = { tools: defaultTools() };
    if (options.writeDefault) {
      await fs.mkdir(CONFIG_DIR, { recursive: true });
      await fs.writeFile(CONFIG_PATH, `${JSON.stringify(config, null, 2)}\n`, 'utf8');
    }
    return config;
  }

  const raw = await fs.readFile(CONFIG_PATH, 'utf8');
  const parsed = JSON.parse(raw);
  const sourceTools = Array.isArray(parsed.tools)
    ? parsed.tools
    : Array.isArray(parsed.editors)
      ? parsed.editors
      : [];
  const userTools = sourceTools.map(normalizeTool).filter(Boolean);
  const merged = new Map(defaultTools().map((tool) => [tool.name, tool]));
  for (const tool of userTools) merged.set(tool.name, tool);
  return { tools: [...merged.values()] };
}

async function detectTool(tool) {
  const markerFound = tool.markerDir ? await dirExists(expandHome(tool.markerDir)) : false;
  const commandFound = (await Promise.all(tool.commands.map(commandExists))).some(Boolean);
  return {
    installed: markerFound || commandFound,
    markerFound,
    commandFound
  };
}

async function findSkillsRoot() {
  const candidates = [
    path.join(ROOT, 'skills'),
    path.join(process.env.INIT_CWD ?? '', 'claude-code-plugins', 'kmp-migration', 'skills'),
    path.join(ROOT, '..', 'claude-code-plugins', 'kmp-migration', 'skills'),
    path.join(ROOT, '..', '..', 'claude-code-plugins', 'kmp-migration', 'skills')
  ].filter(Boolean);

  for (const candidate of candidates) {
    const names = await listSkillNames(candidate);
    if (names.length > 0) return candidate;
  }
  return null;
}

async function listSkillNames(skillsRoot) {
  try {
    const entries = await fs.readdir(skillsRoot, { withFileTypes: true });
    const names = [];
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const skillPath = path.join(skillsRoot, entry.name);
      if (await pathExists(path.join(skillPath, 'SKILL.md'))) names.push(entry.name);
    }
    return names.sort();
  } catch {
    return [];
  }
}

async function copySkill(skillName, skillsRoot, targetRoot, dryRun) {
  const source = path.join(skillsRoot, skillName);
  const target = path.join(targetRoot, skillName);
  if (dryRun) return;
  await fs.mkdir(targetRoot, { recursive: true });
  await fs.rm(target, { recursive: true, force: true });
  await fs.cp(source, target, { recursive: true });
}

async function installToTool(tool, skillsRoot, skillNames, dryRun) {
  const targetRoot = expandHome(tool.skillsDir);
  for (const skillName of skillNames) {
    await copySkill(skillName, skillsRoot, targetRoot, dryRun);
  }
  return targetRoot;
}

async function uninstallFromTool(tool, skillNames, dryRun) {
  const targetRoot = expandHome(tool.skillsDir);
  let removed = 0;
  for (const skillName of skillNames) {
    const target = path.join(targetRoot, skillName);
    if (await dirExists(target)) {
      removed++;
      if (!dryRun) await fs.rm(target, { recursive: true, force: true });
    }
  }
  return removed;
}

function parseArgs(argv) {
  const flags = {
    yes: false,
    postinstall: false,
    dryRun: false,
    targets: null
  };
  const positional = [];

  for (let index = 0; index < argv.length; index++) {
    const arg = argv[index];
    if (arg === '--yes' || arg === '-y') flags.yes = true;
    else if (arg === '--postinstall') flags.postinstall = true;
    else if (arg === '--dry-run') flags.dryRun = true;
    else if (arg === '--target' || arg === '--targets') {
      flags.targets = argv[++index]?.split(',').map((item) => item.trim()).filter(Boolean) ?? [];
    } else if (arg.startsWith('--target=')) {
      flags.targets = arg.slice('--target='.length).split(',').map((item) => item.trim()).filter(Boolean);
    } else {
      positional.push(arg);
    }
  }
  return { command: positional[0] ?? 'install', flags };
}

function selectTools(tools, detections, flags) {
  if (flags.targets?.length) {
    const wanted = new Set(flags.targets.map((target) => target.toLowerCase()));
    if (wanted.has('all')) return tools;
    return tools.filter((tool) => wanted.has(tool.name.toLowerCase()));
  }
  if (flags.yes || flags.postinstall) {
    return tools.filter((tool) => detections.get(tool.name)?.installed);
  }
  return tools;
}

async function confirm(message) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  try {
    const answer = await rl.question(`${message} [y/N] `);
    return /^y(es)?$/i.test(answer.trim());
  } finally {
    rl.close();
  }
}

async function installCommand(flags) {
  if (process.env.KMP_SKILLS_SKIP_POSTINSTALL === '1' && flags.postinstall) return;

  const skillsRoot = await findSkillsRoot();
  if (!skillsRoot) {
    const message = 'No bundled KMP skills found. Run `npm run sync:skills` before publishing this package.';
    if (flags.postinstall) {
      console.warn(`[kmp-skills] ${message}`);
      return;
    }
    throw new Error(message);
  }

  const skillNames = await listSkillNames(skillsRoot);
  const { tools } = await loadConfig();
  const detections = new Map();
  for (const tool of tools) detections.set(tool.name, await detectTool(tool));

  const selectedTools = selectTools(tools, detections, flags);
  if (selectedTools.length === 0) {
    console.log('[kmp-skills] No supported AI tools detected. Edit config with `kmp-skills config`.');
    return;
  }

  if (!flags.yes && !flags.postinstall && !flags.dryRun) {
    const toolList = selectedTools.map((tool) => tool.name).join(', ');
    const ok = await confirm(`Install ${skillNames.length} KMP skills to: ${toolList}?`);
    if (!ok) return;
  }

  for (const tool of selectedTools) {
    const targetRoot = await installToTool(tool, skillsRoot, skillNames, flags.dryRun);
    const detected = detections.get(tool.name)?.installed ? 'detected' : 'custom';
    console.log(`[kmp-skills] ${flags.dryRun ? 'Would install' : 'Installed'} ${skillNames.length} skills -> ${tool.name} (${detected}) ${prettyPath(targetRoot)}`);
  }
}

async function uninstallCommand(flags) {
  const skillsRoot = await findSkillsRoot();
  const skillNames = skillsRoot ? await listSkillNames(skillsRoot) : [];
  if (skillNames.length === 0) throw new Error('No bundled skill names found; cannot uninstall safely.');

  const { tools } = await loadConfig();
  const detections = new Map();
  for (const tool of tools) detections.set(tool.name, await detectTool(tool));
  const selectedTools = selectTools(tools, detections, flags);

  if (!flags.yes && !flags.dryRun) {
    const ok = await confirm(`Remove bundled KMP skills from ${selectedTools.length} target(s)?`);
    if (!ok) return;
  }

  for (const tool of selectedTools) {
    const removed = await uninstallFromTool(tool, skillNames, flags.dryRun);
    console.log(`[kmp-skills] ${flags.dryRun ? 'Would remove' : 'Removed'} ${removed} skills from ${tool.name}`);
  }
}

async function listCommand() {
  const skillsRoot = await findSkillsRoot();
  const skillNames = skillsRoot ? await listSkillNames(skillsRoot) : [];
  console.log(`Skills root: ${skillsRoot ? prettyPath(skillsRoot) : '(not found)'}`);
  for (const skillName of skillNames) console.log(`- ${skillName}`);
}

async function configCommand() {
  const config = await loadConfig({ writeDefault: true });
  console.log(`Config path: ${CONFIG_PATH}`);
  console.log(JSON.stringify(config, null, 2));
}

function printHelp() {
  console.log(`kmp-skills

Usage:
  kmp-skills install [--yes] [--target Claude Code,Codex] [--dry-run]
  kmp-skills uninstall [--yes] [--target all] [--dry-run]
  kmp-skills list
  kmp-skills config

Environment:
  KMP_SKILLS_SKIP_POSTINSTALL=1  Skip npm postinstall auto-install.
`);
}

async function main() {
  const { command, flags } = parseArgs(process.argv.slice(2));
  if (command === 'help' || command === '--help' || command === '-h') {
    printHelp();
    return;
  }
  if (command === 'install' || command === 'init') return installCommand(flags);
  if (command === 'uninstall' || command === 'remove') return uninstallCommand(flags);
  if (command === 'list') return listCommand();
  if (command === 'config') return configCommand();
  throw new Error(`Unknown command: ${command}`);
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`[kmp-skills] ${message}`);
  process.exitCode = 1;
});
