#!/usr/bin/env node

const fs = require('fs');
const os = require('os');
const path = require('path');

const DEFAULT_MODE = 'full';
const VALID_MODES = ['off', 'lite', 'full', 'ultra', 'review'];
const RUNTIME_MODES = ['off', 'lite', 'full', 'ultra'];

function normalizeMode(mode) {
  if (typeof mode !== 'string') return null;
  const normalized = mode.trim().toLowerCase();
  return RUNTIME_MODES.includes(normalized) ? normalized : null;
}

function normalizeConfigMode(mode) {
  if (typeof mode !== 'string') return null;
  const normalized = mode.trim().toLowerCase();
  return VALID_MODES.includes(normalized) ? normalized : null;
}

function normalizePersistedMode(mode) {
  return normalizeMode(mode) || normalizeConfigMode(mode);
}

function isDeactivationCommand(text) {
  const normalized = String(text || '').trim().toLowerCase().replace(/[.!?\s]+$/, '');
  return normalized === 'stop ponytail' || normalized === 'normal mode';
}

function getConfigDir() {
  if (process.env.XDG_CONFIG_HOME) {
    return path.join(process.env.XDG_CONFIG_HOME, 'ponytail');
  }
  if (process.platform === 'win32') {
    return path.join(
      process.env.APPDATA || path.join(os.homedir(), 'AppData', 'Roaming'),
      'ponytail'
    );
  }
  return path.join(os.homedir(), '.config', 'ponytail');
}

function getConfigPath() {
  return path.join(getConfigDir(), 'config.json');
}

function getClaudeDir() {
  return process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
}

function getDefaultMode() {
  const envMode = normalizeConfigMode(process.env.PONYTAIL_DEFAULT_MODE);
  if (envMode) return envMode;

  try {
    const config = JSON.parse(fs.readFileSync(getConfigPath(), 'utf8'));
    return normalizeConfigMode(config.defaultMode) || DEFAULT_MODE;
  } catch (error) {
    return DEFAULT_MODE;
  }
}

module.exports = {
  DEFAULT_MODE,
  VALID_MODES,
  getClaudeDir,
  getDefaultMode,
  isDeactivationCommand,
  normalizeConfigMode,
  normalizeMode,
  normalizePersistedMode,
};
