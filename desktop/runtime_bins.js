function addDefaultPath(env) {
  const extra = [
    '/usr/local/bin',
    '/opt/homebrew/bin',
    '/usr/bin',
    '/bin',
    (process.env.HOME ? `${process.env.HOME}/.local/bin` : null)
  ].filter(Boolean);
  const current = (env.PATH || process.env.PATH || '').split(':').filter(Boolean);
  const merged = [...new Set([...extra, ...current])];
  env.PATH = merged.join(':');
}

function firstExisting(candidates) {
  for (const p of candidates) {
    try {
      if (p && fs.existsSync(p)) return p;
    } catch {}
  }
  return null;
}

function resolvePython() {
  // Try common locations first (packaged apps often have a minimal PATH)
  return firstExisting([
    '/usr/local/bin/python3',
    '/opt/homebrew/bin/python3',
    '/usr/bin/python3',
    '/Library/Frameworks/Python.framework/Versions/Current/bin/python3',
    '/Library/Frameworks/Python.framework/Versions/3.14/bin/python3',
    '/Library/Frameworks/Python.framework/Versions/3.13/bin/python3',
    '/Library/Frameworks/Python.framework/Versions/3.12/bin/python3'
  ]) || 'python3';
}

function resolveNpm() {
  return firstExisting([
    '/usr/local/bin/npm',
    '/opt/homebrew/bin/npm',
    '/usr/bin/npm'
  ]) || 'npm';
}

module.exports = { addDefaultPath, resolvePython, resolveNpm };
