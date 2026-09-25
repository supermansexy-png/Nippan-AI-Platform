#!/usr/bin/env node
/**
 * headless_run.mjs — launch `opencode run` DETACHED in the background.
 *
 * Usage:
 *   node scripts/headless_run.mjs --prompt "<text>" --model <provider/model> \
 *        [--agent <name>] [--label <tag>] [--dir <cwd>]
 *
 * Queue command example:
 *   node scripts/headless_run.mjs --agent worker \
 *        --model opencode/space-bunny-free --label e2e \
 *        --prompt "Read services/core/app/... and report briefly."
 *
 * --model is REQUIRED: a job must never fall back to an unintended default
 * model (T-023 forbids hardcoded models; the model comes from --model per job).
 *
 * Creates <dir>/runs/<UTC-timestamp>-<label>/, spawns opencode detached with
 * stdout/stderr redirected to stdout.log / stderr.log in the run dir, writes
 * status.json, prints ONLY the run dir path to stdout, and exits immediately.
 *
 * No external dependencies (Node >= 18 ESM).
 */
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

function die(msg) {
  process.stderr.write(`headless_run: ERROR: ${msg}\n`);
  process.exit(1);
}

// ---- arg parsing -----------------------------------------------------------
const argv = process.argv.slice(2);
function getArg(flag, fallback, required) {
  const i = argv.indexOf(flag);
  if (i !== -1 && argv[i + 1] !== undefined) return argv[i + 1];
  if (required) die(`missing required ${flag}`);
  return fallback;
}

const prompt = getArg('--prompt', null, true);
const agent = getArg('--agent', 'assistant');
const model = getArg('--model', null, true);
const label = getArg('--label', 'run').replace(/[^A-Za-z0-9._-]/g, '-').slice(0, 64) || 'run';
const dir = path.resolve(getArg('--dir', process.cwd()));

// ---- run directory ----------------------------------------------------------
const now = new Date();
const stamp = now.toISOString().replace(/[:.]/g, '-').slice(0, 19) + 'Z';
const runDir = path.join(dir, 'runs', `${stamp}-${label}`);
fs.mkdirSync(runDir, { recursive: true });

// ---- resolve opencode binary (avoid blind ENOENT) ----------------------------
const isWin = process.platform === 'win32';
const pathDirs = (process.env.PATH || '').split(path.delimiter).filter(Boolean);
const candidates = isWin
  ? ['opencode.exe', 'opencode.cmd', 'opencode.bat']
  : ['opencode'];

function resolveBinary() {
  const exts = isWin ? ['.exe', '.cmd', '.bat', ''] : [''];
  for (const d of pathDirs) {
    for (const c of candidates) {
      const p = path.join(d, c);
      try {
        if (c === '' || exts.includes(path.extname(c))) {
          if (fs.existsSync(p)) {
            // for extensionless entries also require executable-ish file
            if (c !== '' || !isWin) return { file: p, ext: path.extname(c) };
          }
        }
      } catch { /* ignore unreadable dirs */ }
    }
  }
  return null;
}

const resolved = resolveBinary();
if (!resolved) {
  die(`cannot resolve opencode on PATH (looked for ${candidates.join(', ')} in ${pathDirs.length} PATH dirs); nothing spawned, no status.json written`);
}

const scriptExe = path.basename(resolved.file);
const childArgs = ['run', '--format', 'json', '--agent', agent];
childArgs.push('--model', model);
childArgs.push('--auto', prompt);

// On Windows, .cmd/.bat files cannot be spawned directly by Node (EINVAL) —
// they need a shell. Build a safely quoted command line for that case.
function q(s) {
  // cmd.exe-safe double quoting: wrap in quotes, escape embedded quotes/backslashes-at-end.
  return '"' + String(s).replace(/"/g, '""') + '"';
}

let spawnFile = resolved.file;
let spawnArgs = childArgs;
let useShell = false;
if (isWin && (resolved.ext === '.cmd' || resolved.ext === '.bat')) {
  spawnFile = scriptExe;
  spawnArgs = [childArgs.map(q).join(' ')];
  useShell = true;
}

const startedAt = now.toISOString();
const outFd = fs.openSync(path.join(runDir, 'stdout.log'), 'a');
const errFd = fs.openSync(path.join(runDir, 'stderr.log'), 'a');

let child;
try {
  child = spawn(spawnFile, spawnArgs, {
    cwd: dir,
    detached: true,
    stdio: ['ignore', outFd, errFd],
    shell: useShell,
    windowsHide: true,
  });
} catch (e) {
  die(`spawn failed: ${e.message}`);
}

child.on('error', (e) => {
  fs.writeSync(errFd, `\n[headless_run] spawn error: ${e.message}\n`);
});

// Write status.json (pid is available synchronously right after spawn()).
const status = {
  pid: child.pid,
  startedAt,
  prompt,
  agent,
  model: model || null,
  runDir,
  command: [resolved.file, ...childArgs].map((a) => (/\s/.test(a) ? `"${a}"` : a)).join(' '),
};
fs.writeFileSync(path.join(runDir, 'status.json'), JSON.stringify(status, null, 2) + '\n');

// Detach: let the child outlive this process.
child.unref();

// Print ONLY the run dir path.
process.stdout.write(runDir + '\n');
