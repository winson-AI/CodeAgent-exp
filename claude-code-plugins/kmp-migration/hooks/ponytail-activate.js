#!/usr/bin/env node

const { getDefaultMode } = require('./ponytail-config');
const { getPonytailInstructions } = require('./ponytail-instructions');
const { clearMode, setMode, writeHookOutput } = require('./ponytail-runtime');

const mode = getDefaultMode();

if (mode === 'off') {
  clearMode();
  writeHookOutput('SessionStart', 'off', '');
  process.exit(0);
}

try {
  setMode(mode);
  writeHookOutput('SessionStart', mode, getPonytailInstructions(mode));
} catch (error) {
  // Hooks should not fail the session if the optional guardrail cannot load.
}
