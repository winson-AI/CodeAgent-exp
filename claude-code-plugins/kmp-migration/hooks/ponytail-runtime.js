const fs = require('fs');
const path = require('path');
const { getClaudeDir } = require('./ponytail-config');

const STATE_FILE = '.ponytail-active';
const statePath = path.join(getClaudeDir(), STATE_FILE);

function setMode(mode) {
  fs.mkdirSync(path.dirname(statePath), { recursive: true });
  fs.writeFileSync(statePath, mode, 'utf8');
}

function clearMode() {
  try {
    fs.unlinkSync(statePath);
  } catch (error) {
    // Missing state means Ponytail is already off.
  }
}

function readMode() {
  try {
    return fs.readFileSync(statePath, 'utf8').trim() || null;
  } catch (error) {
    return null;
  }
}

function writeHookOutput(event, mode, context = '') {
  if (event === 'SubagentStart') {
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: event,
        additionalContext: context,
      },
    }));
    return;
  }

  if (event === 'UserPromptSubmit') {
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: event,
        additionalContext: context || `PONYTAIL MODE ${mode.toUpperCase()}`,
      },
    }));
    return;
  }

  process.stdout.write(context);
}

module.exports = {
  clearMode,
  readMode,
  setMode,
  writeHookOutput,
};
