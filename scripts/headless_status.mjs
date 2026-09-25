#!/usr/bin/env node
/**
 * headless_status.mjs — inspect a headless run directory.
 *
 * Usage:
 *   node scripts/headless_status.mjs <run-dir>
 *
 * Prints status.json, the last ~40 lines of stdout.log, and stderr.log
 * (only if non-empty). No external dependencies.
 */
import fs from 'node:fs';
import path from 'node:path';

function tail(file, lines = 40, maxCols = 600) {
  try {
    const data = fs.readFileSync(file, 'utf8');
    const parts = data.split(/\r?\n/);
    // drop trailing empty line from split, then take last N
    while (parts.length && parts[parts.length - 1] === '') parts.pop();
    if (!parts.length) return null;
    return parts
      .slice(-lines)
      .map((line) =>
        typeof maxCols === 'number' && line.length > maxCols
          ? `${line.slice(0, maxCols)}… [+${line.length - maxCols} chars]`
          : line,
      )
      .join('\n');
  } catch {
    return null;
  }
}

const runDir = path.resolve(process.argv[2] || '');
if (!runDir || !fs.existsSync(runDir)) {
  process.stderr.write('headless_status: ERROR: run dir not found\n');
  process.exit(1);
}

const statusRaw = tail(path.join(runDir, 'status.json'), 1000, 4000);
if (statusRaw) {
  process.stdout.write('=== status.json ===\n' + statusRaw + '\n');
} else {
  process.stdout.write('=== status.json === (missing)\n');
}

// Extract the final assistant text block(s) from the JSON event stream.
function finalAnswer(file, maxCols = 2000) {
  try {
    const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/);
    const texts = [];
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const ev = JSON.parse(line);
        if (ev?.part?.type === 'text' && typeof ev.part.text === 'string') {
          texts.push(ev.part.text);
        }
      } catch {
        /* ignore non-JSON lines */
      }
    }
    if (!texts.length) return null;
    const joined = texts.join('\n').trim();
    return joined.length > maxCols ? joined.slice(0, maxCols) + '…' : joined;
  } catch {
    return null;
  }
}

const stdoutPath = path.join(runDir, 'stdout.log');
const answer = finalAnswer(stdoutPath);
if (answer) {
  process.stdout.write('=== worker answer ===\n' + answer + '\n');
} else {
  process.stdout.write('=== worker answer === (none yet / still running)\n');
}

const stdout = tail(stdoutPath, 12, 300);
process.stdout.write('=== stdout.log (tail, compact) ===\n' + (stdout ?? '(empty/missing)') + '\n');

const stderr = tail(path.join(runDir, 'stderr.log'), 20, 300);
if (stderr) {
  process.stdout.write('=== stderr.log (tail) ===\n' + stderr + '\n');
}
