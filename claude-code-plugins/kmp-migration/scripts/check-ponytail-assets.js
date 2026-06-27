#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const requiredFiles = [
  'skills/ponytail/SKILL.md',
  'skills/ponytail-review/SKILL.md',
  'hooks/hooks.json',
  'hooks/ponytail-activate.js',
  'hooks/ponytail-config.js',
  'hooks/ponytail-instructions.js',
  'hooks/ponytail-mode-tracker.js',
  'hooks/ponytail-runtime.js',
  'hooks/ponytail-subagent.js',
];

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const missing = requiredFiles.filter((relativePath) => !fs.existsSync(path.join(root, relativePath)));
if (missing.length) {
  console.error(`Missing Ponytail assets:\n${missing.join('\n')}`);
  process.exit(1);
}

const skill = read('skills/ponytail/SKILL.md');
for (const phrase of [
  'Does this need to exist at all?',
  'Does this codebase already have',
  'Does the language or standard library',
  'Does the platform already provide',
  'Only then write the minimum new code',
]) {
  if (!skill.includes(phrase)) {
    console.error(`Ponytail skill is missing ladder phrase: ${phrase}`);
    process.exit(1);
  }
}

const hooks = JSON.parse(read('hooks/hooks.json'));
for (const event of ['SessionStart', 'SubagentStart', 'UserPromptSubmit', 'PreToolUse']) {
  if (!hooks.hooks || !Array.isArray(hooks.hooks[event])) {
    console.error(`hooks/hooks.json is missing ${event}`);
    process.exit(1);
  }
}

const { getPonytailInstructions } = require('../hooks/ponytail-instructions');
const context = getPonytailInstructions('full');
if (!context.includes('PONYTAIL MODE ACTIVE') || !context.includes('Core Function')) {
  console.error('Ponytail instruction builder did not return expected context.');
  process.exit(1);
}

console.log('Ponytail assets OK');
