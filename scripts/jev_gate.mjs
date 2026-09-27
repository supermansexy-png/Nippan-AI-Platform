#!/usr/bin/env node
/**
 * jev_gate.mjs — decision-gate SIGNAL helper (T-068).
 *
 * Sends ONE short, self-contained situation text to the Jev screening endpoint
 * (https://opencode.ai/zen/v1/systemone, model opencode/jev-1.13-free) and
 * prints a JSON signal for three gates:
 *   1. review tier          — signal only; never the deciding authority
 *   2. Owner approval needed — signal only; never the deciding authority
 *   3. auth/tenant flag      — signal only; never the deciding authority
 *
 * ============================ USAGE RULES =================================
 * SIGNal NOT DECISION — this output is a screening signal for the deciding
 * role. It is NEVER the deciding authority where a written rule applies, and
 * NEVER the sole gate for an L3 task (a different-model review is still
 * required). Where the project rules already answer the question, follow the
 * written rule, not this tool.
 *
 * ============================ INPUT HARD RULES ============================
 * The input situation text must be short, generic, and self-contained.
 * It must NEVER contain:
 *   - secrets, tokens, credentials, keys or private material
 *   - customer data or anything identifying a customer or tenant
 *   - repository code or file contents
 * Paraphrase the situation in plain words instead. What is sent to the
 * endpoint is exactly the text passed on the command line (or via stdin) plus
 * the three questions below — nothing else is read from disk or the repo.
 *
 * ============================ OUTPUT PROTOCOL =============================
 * On success (HTTP 200 + parseable answer): prints ONE JSON object on stdout
 * with fields:
 *   { tool, ts, input_bytes, signal:
 *     { review_tier:            "L1" | "L2" | "L3",
 *       owner_approval_needed:  0 | 1,
 *       touches_auth_tenant:    0 | 1,
 *       raw: <full model answer object> } }
 * On ANY failure (missing/empty input, HTTP != 200, 429, service down,
 * timeout, unparseable answer): prints "NO SIGNAL" to STDERR, exits
 * non-zero, and the deciding role proceeds exactly as today — fail TOWARD
 * THE HUMAN. This tool NEVER emits "assume L1" or any substitute signal.
 *
 * Exit codes: 0 = signal produced · 2 = timeout · 3 = missing/empty input ·
 *             4 = HTTP 429 · 5 = other non-200 HTTP · 6 = network error ·
 *             7 = HTTP 200 but unparseable answer.
 *
 * Usage:
 *   node scripts/jev_gate.mjs "<short situation text>"
 *   node scripts/jev_gate.mjs --stdin          (reads the text from stdin)
 *   node scripts/jev_gate.mjs --help
 *
 * No external dependencies (Node >= 18 ESM). Budget: Jev free tier, $0.
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const ENDPOINT = 'https://opencode.ai/zen/v1/systemone';
const MODEL = 'jev-1.13-free'; // provider-prefixed slug: opencode/jev-1.13-free
const TIMEOUT_MS = 20000;

const HELP = [
  'jev_gate.mjs — decision-gate SIGNAL helper (T-068) — signal only, not a decision.',
  '',
  'Usage:',
  '  node scripts/jev_gate.mjs "<short situation text>"',
  '  node scripts/jev_gate.mjs --stdin',
  '',
  'Input hard rules: NO secrets, NO customer data, NO repo code in the text.',
  'On any failure: prints NO SIGNAL, exits non-zero, deciding role proceeds as',
  'today. Never "assume L1".',
].join('\n');

function noSignal(code, reason) {
  process.stderr.write(`jev_gate: NO SIGNAL (${reason}) — deciding role proceeds as today, never "assume L1".\n`);
  process.exit(code);
}

// ---- input ----------------------------------------------------------------
const argv = process.argv.slice(2);

if (argv.includes('--help') || argv.includes('-h')) {
  process.stdout.write(HELP + '\n');
  process.exit(0);
}

let input = '';
if (argv.includes('--stdin')) {
  input = fs.readFileSync(0, 'utf8');
} else if (argv.length > 0) {
  input = argv.join(' ');
} else {
  noSignal(3, 'missing input — pass a short situation text or --stdin');
}

input = input.trim();
if (input.length === 0) {
  noSignal(3, 'empty input — no text to screen');
}
if (input.length > 4000) {
  noSignal(3, `input too long (${input.length} chars > 4000) — keep it short and self-contained`);
}

// ---- credential (same local file the pilot used; value is never printed) ---
function loadKey() {
  const candidates = [
    process.env.OPENCODE_API_KEY,
    process.env.OPENCODE_AUTH_FILE,
  ].filter(Boolean);
  if (process.env.OPENCODE_API_KEY) return process.env.OPENCODE_API_KEY;

  const authPath = path.join(os.homedir(), '.local', 'share', 'opencode', 'auth.json');
  try {
    const parsed = JSON.parse(fs.readFileSync(authPath, 'utf8'));
    if (parsed && typeof parsed.opencode?.key === 'string') return parsed.opencode.key;
  } catch {
    /* fallthrough to error below */
  }
  noSignal(6, `no opencode credential found (auth.json missing or unreadable under ${authPath})`);
}

// ---- three gates, matching the T-067 pilot question set --------------------
const questions = {
  review_tier: {
    type: 'choice',
    instructions: 'Which review level does this require?',
    criteria: {
      L1: 'reversible and non-sensitive',
      L2: 'moderate risk, needs a second model and owner sign-off',
      L3: 'hard to undo, or touches auth, tenant isolation, production or data',
    },
  },
  needs_owner_approval: {
    type: 'noul',
    instructions: 'Does this need explicit Owner approval before it can be accepted as done?',
  },
  touches_auth_tenant: {
    type: 'noul',
    instructions: 'Does this touch authentication, authorisation or tenant isolation?',
  },
};

// ---- POST -------------------------------------------------------------------
const controller = new AbortController();
const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

let res;
try {
  res = await fetch(ENDPOINT, {
    method: 'POST',
    signal: controller.signal,
    headers: {
      Authorization: 'Bearer ' + loadKey(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ model: MODEL, state: input, questions }),
  });
} catch (err) {
  clearTimeout(timer);
  const reason = err && err.name === 'AbortError'
    ? `timeout after ${TIMEOUT_MS}ms`
    : `network error: ${err && err.message ? err.message : err}`;
  noSignal(6, reason);
}
clearTimeout(timer);

if (res.status === 429) {
  noSignal(4, `HTTP 429 rate-limited by the screening service`);
}
if (!res.ok) {
  noSignal(5, `HTTP ${res.status} from screening service`);
}

let payload;
try {
  payload = await res.json();
} catch (err) {
  noSignal(7, `HTTP 200 but unparseable body: ${err && err.message ? err.message : err}`);
}

// ---- extract the three gates -------------------------------------------------
const answers = payload && typeof payload === 'object' ? payload.answers : undefined;
const tierRaw = answers?.review_tier?.choice;
const tier = tierRaw === 'L1' || tierRaw === 'L2' || tierRaw === 'L3' ? tierRaw : null;
const owner = typeof answers?.needs_owner_approval?.noul === 'number'
  ? (answers.needs_owner_approval.noul >= 0.5 ? 1 : 0)
  : null;
const auth = typeof answers?.touches_auth_tenant?.noul === 'number'
  ? (answers.touches_auth_tenant.noul >= 0.5 ? 1 : 0)
  : null;

if (tier === null || owner === null || auth === null) {
  noSignal(7, 'HTTP 200 but gate fields missing/unexpected shape');
}

const out = {
  tool: 'jev_gate',
  ts: new Date().toISOString(),
  input_bytes: Buffer.byteLength(input, 'utf8'),
  signal: {
    review_tier: tier,
    owner_approval_needed: owner,
    touches_auth_tenant: auth,
    raw: answers,
  },
};
process.stdout.write(JSON.stringify(out, null, 2) + '\n');
