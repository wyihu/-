const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn, execFile } = require('child_process');
const http = require('http');

const { addDefaultPath, resolvePython, resolveNpm } = require('./runtime_bins');

let pyProc = null;
let feProc = null;

const ROOT = process.env.VIDEO_CLIP_TAGGER_ROOT || path.join(process.env.HOME || '', 'projects', 'video-clip-tagger');
const LOG_DIR = path.join(process.env.HOME || '', 'ai-video-factory', 'logs');
const LOG_FILE = path.join(LOG_DIR, 'desktop-electron.log');

function log(...args) {
  try {
    fs.mkdirSync(LOG_DIR, { recursive: true });
    fs.appendFileSync(LOG_FILE, `[${new Date().toISOString()}] ${args.map(a => (typeof a === 'string' ? a : JSON.stringify(a))).join(' ')}\n`);
  } catch {}
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function httpOk(url) {
  return new Promise((resolve) => {
    try {
      const u = new URL(url);
      const req = http.request({
        method: 'GET',
        hostname: u.hostname,
        port: u.port,
        path: u.pathname,
        timeout: 1500
      }, (res) => resolve(!!(res.statusCode && res.statusCode >= 200 && res.statusCode < 500)));
      req.on('timeout', () => { req.destroy(); resolve(false); });
      req.on('error', () => resolve(false));
      req.end();
    } catch {
      resolve(false);
    }
  });
}

async function ensureOllama() {
  const ok = await httpOk('http://127.0.0.1:11434/api/tags');
  if (ok) return;

  try {
    execFile('ollama', ['serve'], { detached: true, stdio: 'ignore' }, () => {});
  } catch (e) {
    log('ollama serve execFile failed', String(e));
  }

  for (let i = 0; i < 25; i++) {
    if (await httpOk('http://127.0.0.1:11434/api/tags')) return;
    await sleep(200);
  }
  log('ollama not reachable after wait');
}

function trackChild(name, proc) {
  if (!proc) return;
  proc.on('error', (e) => log(`${name} spawn error`, String(e)));
  proc.on('exit', (code, signal) => log(`${name} exit`, { code, signal }));
}

async function startBackend() {
  if (pyProc) return;
  if (await httpOk('http://127.0.0.1:8000/health')) {
    log('backend already running, reusing');
    return;
  }

  const env = { ...process.env };
  env.PYTHONUNBUFFERED = '1';
  addDefaultPath(env);

  const py = resolvePython();
  log('starting backend', { py, cwd: path.join(ROOT, 'backend'), path: env.PATH });

  pyProc = spawn(py, ['-m', 'uvicorn', 'backend.api.main:app', '--host', '127.0.0.1', '--port', '8000'], {
    cwd: path.join(ROOT, 'backend'),
    env,
    stdio: 'ignore'
  });
  trackChild('backend', pyProc);
}

async function startFrontend() {
  if (feProc) return;
  if (await httpOk('http://127.0.0.1:3000/')) {
    log('frontend already running, reusing');
    return;
  }

  const env = { ...process.env };
  env.NEXT_PUBLIC_API_BASE = 'http://localhost:8000';
  addDefaultPath(env);

  const npm = resolveNpm();
  log('starting frontend', { npm, cwd: path.join(ROOT, 'frontend'), path: env.PATH });

  feProc = spawn(npm, ['run', 'dev', '--', '--port', '3000'], {
    cwd: path.join(ROOT, 'frontend'),
    env,
    stdio: 'ignore'
  });
  trackChild('frontend', feProc);
}

async function waitForServices() {
  for (let i = 0; i < 80; i++) {
    const api = await httpOk('http://127.0.0.1:8000/health');
    const ui = await httpOk('http://127.0.0.1:3000/');
    if (api && ui) return;
    await sleep(250);
  }
  log('services did not become ready in time');
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    title: 'Video Clip Tagger',
    icon: path.join(__dirname, 'assets', 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

function stopChildren() {
  if (feProc) {
    try { feProc.kill('SIGTERM'); } catch {}
    feProc = null;
  }
  if (pyProc) {
    try { pyProc.kill('SIGTERM'); } catch {}
    pyProc = null;
  }
}

process.on('uncaughtException', (e) => {
  log('uncaughtException', String(e?.stack || e));
});

app.whenReady().then(async () => {
  log('app ready', { ROOT });
  await ensureOllama();
  await startBackend();
  await startFrontend();
  await waitForServices();
  createWindow();
});

app.on('window-all-closed', () => {
  stopChildren();
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
  stopChildren();
});
