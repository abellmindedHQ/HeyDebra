#!/usr/bin/env node
/**
 * BlueBubbles Attachment Poller
 *
 * Workaround for OpenClaw SSRF guard blocking BB attachment downloads.
 * Polls the BB API for recent messages with attachments and downloads
 * them to ~/.openclaw/media/inbound/ where OpenClaw can read them.
 *
 * Usage:
 *   node bb-attachment-poll.js              # Run once
 *   node bb-attachment-poll.js --watch      # Poll every 30s
 *   node bb-attachment-poll.js --since 60   # Check last 60 minutes
 *
 * Env vars (reads from ~/.openclaw/.env automatically):
 *   BLUEBUBBLES_PASSWORD  - BB server password
 *
 * See: memory/bluebubbles-attachment-bug.md
 * Remove this script once OpenClaw ships the SSRF fix (commits 7d93970/dd41a78).
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const { execSync } = require('child_process');

// --- Config ---
const BB_HOST = '127.0.0.1';
const BB_PORT = 1234;
const MEDIA_DIR = path.join(process.env.HOME || '/Users/debra', '.openclaw/media/inbound');
const ENV_FILE = path.join(process.env.HOME || '/Users/debra', '.openclaw/.env');
const STATE_FILE = path.join(process.env.HOME || '/Users/debra', '.openclaw/cache/bb-poll-state.json');
const POLL_INTERVAL_MS = 30_000; // 30 seconds
const DEFAULT_LOOKBACK_MINUTES = 10;

// --- Load env ---
function loadEnv() {
  try {
    const envContent = fs.readFileSync(ENV_FILE, 'utf8');
    for (const line of envContent.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const eqIdx = trimmed.indexOf('=');
      if (eqIdx === -1) continue;
      const key = trimmed.slice(0, eqIdx);
      const val = trimmed.slice(eqIdx + 1);
      if (!process.env[key]) process.env[key] = val;
    }
  } catch (e) {
    // .env not found, rely on existing env
  }
}

const BB_PASSWORD = (() => {
  loadEnv();
  return process.env.BLUEBUBBLES_PASSWORD;
})();

if (!BB_PASSWORD) {
  console.error('ERROR: BLUEBUBBLES_PASSWORD not set. Check ~/.openclaw/.env');
  process.exit(1);
}

// --- State management ---
function loadState() {
  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  } catch {
    return { lastPollEpochMs: 0, downloadedGuids: [] };
  }
}

function saveState(state) {
  const dir = path.dirname(STATE_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  // Keep only last 500 GUIDs to prevent unbounded growth
  state.downloadedGuids = state.downloadedGuids.slice(-500);
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

// --- HTTP helpers ---
function bbRequest(method, apiPath, jsonBody) {
  return new Promise((resolve, reject) => {
    const sep = apiPath.includes('?') ? '&' : '?';
    const fullPath = `${apiPath}${sep}password=${encodeURIComponent(BB_PASSWORD)}`;
    const bodyStr = jsonBody ? JSON.stringify(jsonBody) : null;

    const opts = {
      hostname: BB_HOST,
      port: BB_PORT,
      path: fullPath,
      method: method,
      headers: {},
    };
    if (bodyStr) {
      opts.headers['Content-Type'] = 'application/json';
      opts.headers['Content-Length'] = Buffer.byteLength(bodyStr);
    }

    const req = http.request(opts, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        const body = Buffer.concat(chunks);
        if (res.headers['content-type']?.includes('json')) {
          try {
            resolve({ status: res.statusCode, data: JSON.parse(body.toString()), raw: null });
          } catch (e) {
            reject(new Error(`JSON parse error: ${e.message} — body: ${body.toString().slice(0, 200)}`));
          }
        } else {
          resolve({ status: res.statusCode, data: null, raw: body });
        }
      });
      res.on('error', reject);
    });
    req.on('error', reject);
    if (bodyStr) req.write(bodyStr);
    req.end();
  });
}

function bbDownload(apiPath, destPath) {
  return new Promise((resolve, reject) => {
    const sep = apiPath.includes('?') ? '&' : '?';
    const fullPath = `${apiPath}${sep}password=${encodeURIComponent(BB_PASSWORD)}`;

    const opts = {
      hostname: BB_HOST,
      port: BB_PORT,
      path: fullPath,
      method: 'GET',
    };

    const file = fs.createWriteStream(destPath);
    const req = http.request(opts, (res) => {
      if (res.statusCode !== 200) {
        file.close();
        try { fs.unlinkSync(destPath); } catch {}
        reject(new Error(`HTTP ${res.statusCode} downloading attachment`));
        return;
      }
      res.pipe(file);
      file.on('finish', () => { file.close(); resolve(); });
      file.on('error', (e) => { try { fs.unlinkSync(destPath); } catch {} reject(e); });
    });
    req.on('error', (e) => { file.close(); try { fs.unlinkSync(destPath); } catch {} reject(e); });
    req.end();
  });
}

// --- Extension mapping ---
function mimeToExt(mime) {
  const map = {
    'image/jpeg': '.jpg', 'image/png': '.png', 'image/gif': '.gif',
    'image/heic': '.heic', 'image/heif': '.heif', 'image/webp': '.webp',
    'image/tiff': '.tiff', 'video/mp4': '.mp4', 'video/quicktime': '.mov',
    'audio/mpeg': '.mp3', 'audio/mp4': '.m4a', 'audio/x-caf': '.caf',
    'application/pdf': '.pdf',
  };
  return map[mime] || '';
}

// --- Main poll logic ---
async function pollOnce(lookbackMinutes) {
  const state = loadState();
  const sinceMs = lookbackMinutes
    ? Date.now() - lookbackMinutes * 60_000
    : Math.max(state.lastPollEpochMs - 60_000, Date.now() - 10 * 60_000); // 1min overlap

  // Ensure media dir exists
  if (!fs.existsSync(MEDIA_DIR)) fs.mkdirSync(MEDIA_DIR, { recursive: true });

  // Fetch recent messages via POST /api/v1/messages/query
  // BB API uses epoch ms for the 'after' parameter
  let messages;
  try {
    const queryBody = {
      limit: 50,
      sort: 'DESC',
      after: sinceMs,
      with: ['attachment'],
    };
    const resp = await bbRequest('POST', '/api/v1/messages/query', queryBody);
    if (resp.status !== 200) {
      console.error(`BB API error: HTTP ${resp.status}${resp.data ? ' — ' + JSON.stringify(resp.data).slice(0, 200) : ''}`);
      return;
    }
    messages = resp.data?.data || resp.data || [];
  } catch (e) {
    console.error(`BB API fetch failed: ${e.message}`);
    return;
  }

  if (!Array.isArray(messages)) {
    console.error('Unexpected API response format:', typeof messages);
    return;
  }

  let downloaded = 0;
  for (const msg of messages) {
    const attachments = msg.attachments || [];
    for (const att of attachments) {
      const guid = att.guid;
      if (!guid) continue;
      if (state.downloadedGuids.includes(guid)) continue;

      const ext = mimeToExt(att.mimeType || att.uti || '') ||
                  (att.transferName ? path.extname(att.transferName) : '.bin');
      const filename = `${guid}${ext}`;
      const destPath = path.join(MEDIA_DIR, filename);

      if (fs.existsSync(destPath)) {
        state.downloadedGuids.push(guid);
        continue;
      }

      try {
        await bbDownload(`/api/v1/attachments/${guid}/download`, destPath);
        state.downloadedGuids.push(guid);
        downloaded++;
        const size = fs.statSync(destPath).size;
        console.log(`✅ ${filename} (${(size / 1024).toFixed(1)}KB) — ${att.mimeType || 'unknown type'}`);
      } catch (e) {
        console.error(`❌ Failed to download ${guid}: ${e.message}`);
      }
    }
  }

  state.lastPollEpochMs = Date.now();
  saveState(state);

  if (downloaded === 0) {
    console.log(`[${new Date().toLocaleTimeString()}] No new attachments (checked ${messages.length} messages)`);
  } else {
    console.log(`[${new Date().toLocaleTimeString()}] Downloaded ${downloaded} new attachment(s)`);
  }
}

// --- CLI ---
async function main() {
  const args = process.argv.slice(2);
  const watchMode = args.includes('--watch');
  const sinceIdx = args.indexOf('--since');
  const lookback = sinceIdx !== -1 ? parseInt(args[sinceIdx + 1], 10) : undefined;

  console.log(`BlueBubbles Attachment Poller`);
  console.log(`BB Server: ${BB_HOST}:${BB_PORT}`);
  console.log(`Media dir: ${MEDIA_DIR}`);
  console.log(`Mode: ${watchMode ? `watching (every ${POLL_INTERVAL_MS / 1000}s)` : 'one-shot'}`);
  console.log('---');

  await pollOnce(lookback);

  if (watchMode) {
    setInterval(() => pollOnce(), POLL_INTERVAL_MS);
  }
}

main().catch((e) => {
  console.error(`Fatal: ${e.message}`);
  process.exit(1);
});
