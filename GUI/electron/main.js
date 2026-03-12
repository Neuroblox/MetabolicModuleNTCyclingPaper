const { app, BrowserWindow, shell } = require('electron')
const { spawn } = require('child_process')
const path = require('path')
const http = require('http')

const PORT = process.env.NT_PORT || '8090'

let juliaProcess = null
let mainWindow = null

// ---------------------------------------------------------------------------
// Locate the Julia server binary and build argv
// ---------------------------------------------------------------------------

function getServerCommand() {
  if (app.isPackaged) {
    // Production: bundled compiled binary from PackageCompiler
    const bin = process.platform === 'win32' ? 'NTCycling.exe' : 'NTCycling'
    return {
      bin: path.join(process.resourcesPath, 'julia-app', 'bin', bin),
      args: [],
    }
  }

  // Development: run via system Julia
  const backendDir = path.join(__dirname, '..', 'backend')
  return {
    bin: process.platform === 'win32' ? 'julia.exe' : 'julia',
    args: [`--project=${backendDir}`, path.join(backendDir, 'src', 'server.jl')],
  }
}

function getPublicDir() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'public')
  }
  return path.join(__dirname, '..', 'backend', 'public')
}

// ---------------------------------------------------------------------------
// Start the Julia HTTP server as a child process
// ---------------------------------------------------------------------------

function startJuliaServer() {
  const { bin, args } = getServerCommand()

  const env = {
    ...process.env,
    NT_PORT: PORT,
    NT_HOST: '127.0.0.1',
    NT_PUBLIC_DIR: getPublicDir(),
  }

  if (app.isPackaged) {
    // Point Julia depot to user-writable location so the packaged app
    // doesn't try to write into its own (potentially read-only) bundle.
    env.JULIA_DEPOT_PATH = path.join(app.getPath('userData'), 'julia-depot')
  }

  console.log(`[julia] Spawning: ${bin} ${args.join(' ')}`)
  juliaProcess = spawn(bin, args, { env, stdio: ['ignore', 'pipe', 'pipe'] })

  juliaProcess.stdout.on('data', (d) => process.stdout.write(`[julia] ${d}`))
  juliaProcess.stderr.on('data', (d) => process.stderr.write(`[julia] ${d}`))

  juliaProcess.on('exit', (code, signal) => {
    console.log(`[julia] Process exited (code=${code} signal=${signal})`)
    juliaProcess = null
  })

  juliaProcess.on('error', (err) => {
    console.error(`[julia] Failed to spawn process: ${err.message}`)
  })
}

// ---------------------------------------------------------------------------
// Poll until the server responds (or timeout)
// ---------------------------------------------------------------------------

function waitForServer(timeoutMs = 180000) {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeoutMs

    const check = () => {
      const req = http.get(`http://127.0.0.1:${PORT}/`, (res) => {
        res.resume() // drain the response
        resolve()
      })
      req.on('error', () => {
        if (Date.now() >= deadline) {
          reject(new Error('Timed out waiting for Julia server to start'))
        } else {
          setTimeout(check, 500)
        }
      })
      req.setTimeout(1000, () => req.destroy())
    }

    check()
  })
}

// ---------------------------------------------------------------------------
// BrowserWindow
// ---------------------------------------------------------------------------

const LOADING_HTML = `data:text/html,<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>NT Cycling Model</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    background: #0f172a;
    color: #e2e8f0;
    font-family: system-ui, -apple-system, sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
  }
  .card {
    text-align: center;
    padding: 2rem 3rem;
  }
  h2 { font-size: 1.5rem; margin-bottom: 0.75rem; color: #f8fafc; }
  p  { color: #94a3b8; font-size: 0.95rem; }
  .spinner {
    width: 40px; height: 40px;
    border: 4px solid #334155;
    border-top-color: #6366f1;
    border-radius: 50%;
    animation: spin 0.9s linear infinite;
    margin: 1.5rem auto 0;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>
  <div class="card">
    <h2>Starting NT Cycling Model</h2>
    <p>Loading Julia server &mdash; this may take a moment on first launch.</p>
    <div class="spinner"></div>
  </div>
</body>
</html>`

const ERROR_HTML = (msg) => `data:text/html,<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>NT Cycling Model – Error</title>
<style>
  body {
    background:#0f172a; color:#e2e8f0;
    font-family:system-ui,sans-serif;
    display:flex; align-items:center; justify-content:center; height:100vh;
  }
  .card { text-align:center; padding:2rem 3rem; max-width:480px; }
  h2 { color:#f87171; margin-bottom:0.75rem; }
  p  { color:#94a3b8; font-size:0.9rem; }
  code { display:block; margin-top:1rem; background:#1e293b;
         padding:0.75rem; border-radius:6px; font-size:0.8rem;
         color:#fca5a5; white-space:pre-wrap; }
</style>
</head>
<body>
  <div class="card">
    <h2>Failed to start server</h2>
    <p>The Julia server did not start. Check the developer console for details.</p>
    <code>${msg}</code>
  </div>
</body>
</html>`

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 920,
    minWidth: 900,
    minHeight: 600,
    title: 'NT Cycling Model',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    show: false,
    backgroundColor: '#0f172a',
  })

  mainWindow.loadURL(LOADING_HTML)
  mainWindow.once('ready-to-show', () => mainWindow.show())

  // Open external links in the system browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  mainWindow.on('closed', () => { mainWindow = null })
}

// ---------------------------------------------------------------------------
// App lifecycle
// ---------------------------------------------------------------------------

app.whenReady().then(async () => {
  startJuliaServer()
  createWindow()

  try {
    await waitForServer()
    if (mainWindow) {
      mainWindow.loadURL(`http://127.0.0.1:${PORT}/`)
    }
  } catch (err) {
    console.error(err)
    if (mainWindow) {
      mainWindow.loadURL(ERROR_HTML(err.message))
    }
  }
})

app.on('window-all-closed', () => {
  // On macOS, keep the app running even when all windows are closed.
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  // Re-create the window on macOS dock click if none open.
  if (mainWindow === null) {
    createWindow()
    mainWindow.loadURL(`http://127.0.0.1:${PORT}/`)
  }
})

app.on('will-quit', () => {
  if (juliaProcess) {
    juliaProcess.kill()
    juliaProcess = null
  }
})
