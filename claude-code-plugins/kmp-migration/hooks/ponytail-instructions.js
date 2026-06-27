#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { DEFAULT_MODE, normalizeMode, normalizePersistedMode } = require('./ponytail-config');

const INDEPENDENT_MODES = new Set(['review']);
const SKILL_PATH = path.join(__dirname, '..', 'skills', 'ponytail', 'SKILL.md');

function stripFrontmatter(body) {
  return String(body || '').replace(/^---[\s\S]*?---\s*/, '');
}

function filterSkillBodyForMode(body, mode) {
  const effectiveMode = normalizeMode(mode) || DEFAULT_MODE;

  return stripFrontmatter(body)
    .split(/\r?\n/)
    .filter((line) => {
      const bullet = line.match(/^-\s+`?([^`:]+)`?:/);
      if (!bullet) return true;

      const bulletMode = normalizeMode(bullet[1].trim());
      return !bulletMode || bulletMode === effectiveMode;
    })
    .join('\n');
}

function getFallbackInstructions(mode) {
  return `PONYTAIL MODE ACTIVE - level: ${mode}

You are a lazy senior developer. Lazy means efficient, not careless.

Before writing code, stop at the first rung that holds:
1. Does this need to exist at all?
2. Does this codebase already have it?
3. Does the standard library solve it?
4. Does the platform solve it natively?
5. Does an installed dependency solve it?
6. Can it be one line?
7. Only then write the minimum code that works.

Read the touched flow first. Fix root causes once. Do not simplify away validation, security, accessibility, data-loss handling, migration fidelity, hardware calibration, or explicit user requirements.`;
}

function getPonytailInstructions(mode) {
  const configuredMode = normalizePersistedMode(mode) || DEFAULT_MODE;
  if (INDEPENDENT_MODES.has(configuredMode)) {
    return `PONYTAIL MODE ACTIVE - level: ${configuredMode}. Behavior defined by the ponytail-review skill.`;
  }

  const effectiveMode = normalizeMode(configuredMode) || DEFAULT_MODE;

  try {
    return `PONYTAIL MODE ACTIVE - level: ${effectiveMode}\n\n${filterSkillBodyForMode(
      fs.readFileSync(SKILL_PATH, 'utf8'),
      effectiveMode
    )}`;
  } catch (error) {
    return getFallbackInstructions(effectiveMode);
  }
}

module.exports = {
  filterSkillBodyForMode,
  getFallbackInstructions,
  getPonytailInstructions,
};
