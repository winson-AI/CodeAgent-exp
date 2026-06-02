#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ifPresent = process.argv.includes('--if-present');

async function pathExists(input) {
  try {
    await fs.access(input);
    return true;
  } catch {
    return false;
  }
}

async function listSkillNames(skillsRoot) {
  try {
    const entries = await fs.readdir(skillsRoot, { withFileTypes: true });
    const names = [];
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      if (await pathExists(path.join(skillsRoot, entry.name, 'SKILL.md'))) {
        names.push(entry.name);
      }
    }
    return names.sort();
  } catch {
    return [];
  }
}

async function findSourceSkillsRoot() {
  const candidates = [
    path.join(ROOT, '..', 'claude-code-plugins', 'kmp-migration', 'skills'),
    path.join(ROOT, '..', '..', 'claude-code-plugins', 'kmp-migration', 'skills'),
    path.join(process.env.INIT_CWD ?? '', 'claude-code-plugins', 'kmp-migration', 'skills')
  ].filter(Boolean);

  for (const candidate of candidates) {
    if ((await listSkillNames(candidate)).length > 0) return candidate;
  }
  return null;
}

async function main() {
  const source = await findSourceSkillsRoot();
  const target = path.join(ROOT, 'skills');

  if (!source) {
    if (ifPresent) {
      console.log('[sync-skills] source skills not found; skipping.');
      return;
    }
    throw new Error('Unable to find claude-code-plugins/kmp-migration/skills.');
  }

  await fs.rm(target, { recursive: true, force: true });
  await fs.mkdir(target, { recursive: true });

  const skillNames = await listSkillNames(source);
  for (const skillName of skillNames) {
    await fs.cp(path.join(source, skillName), path.join(target, skillName), { recursive: true });
  }

  console.log(`[sync-skills] synced ${skillNames.length} skills from ${source} -> ${target}`);
}

main().catch((error) => {
  console.error(`[sync-skills] ${error instanceof Error ? error.message : String(error)}`);
  process.exitCode = 1;
});
