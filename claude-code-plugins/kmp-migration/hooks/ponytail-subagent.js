#!/usr/bin/env node

const { getPonytailInstructions } = require('./ponytail-instructions');
const { readMode, writeHookOutput } = require('./ponytail-runtime');

const mode = readMode();

if (!mode || mode === 'off') {
  process.exit(0);
}

try {
  writeHookOutput('SubagentStart', mode, getPonytailInstructions(mode));
} catch (error) {
  // Do not block subagent startup if optional context injection fails.
}
