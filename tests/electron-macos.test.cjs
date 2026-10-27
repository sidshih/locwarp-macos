const test = require('node:test')
const assert = require('node:assert/strict')
const vm = require('node:vm')
const fs = require('node:fs')
const path = require('node:path')
const { EventEmitter } = require('node:events')

function harness(platform = 'darwin', backendExists = true) {
  const spawned = [], menus = [], messages = []
  let windows = [], ready, quits = 0
  const app = Object.assign(new EventEmitter(), {
    isPackaged: true, getPath: () => '/tmp/locwarp-test', getLocale: () => 'en',
    whenReady: () => ({ then: (fn) => { ready = fn } }),
    commandLine: { appendSwitch() {} }, disableHardwareAcceleration() {},
    quit() { quits++ }, relaunch() {}, exit() {},
  })
  class Window extends EventEmitter {
    constructor() {
      super()
      this.webContents = Object.assign(new EventEmitter(), { setWindowOpenHandler() {} })
      windows.push(this)
    }
    show() {}
    loadFile() {}
    loadURL() {}
    static getAllWindows() { return windows }
  }
  const electron = {
    app, BrowserWindow: Window,
    Menu: { buildFromTemplate: (template) => template, setApplicationMenu: (menu) => menus.push(menu) },
    shell: { openPath() {}, openExternal() {} }, ipcMain: { handle() {} },
    dialog: { showMessageBoxSync: (msg) => { messages.push(msg); return 1 } },
    session: { defaultSession: { webRequest: { onBeforeSendHeaders() {} } } },
  }
  const spawn = (exe, args, options) => {
    const proc = Object.assign(new EventEmitter(), {
      stdout: new EventEmitter(), stderr: new EventEmitter(), kills: 0,
      kill() { this.kills++ },
    })
    spawned.push({ exe, args, options, proc })
    return proc
  }
  const context = vm.createContext({
    require: (name) => {
      if (name === 'electron') return electron
      if (name === 'child_process') return { spawn }
      if (name === 'fs') return {
        readFileSync() { throw new Error('not found') }, writeFileSync() {}, mkdirSync() {},
        existsSync: () => backendExists,
      }
      if (name === 'os') return { release: () => '10.0.22631' }
      return require(name)
    },
    process: { platform, resourcesPath: '/Applications/Loc Warp.app/Contents/Resources', argv: [],
      stdout: { write() {} }, stderr: { write() {} } },
    __dirname: '/Applications/Loc Warp.app/Contents/Resources/app/electron',
    console: { log() {}, error() {}, warn() {} }, setTimeout, clearTimeout,
  })
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../frontend/electron/main.js'), 'utf8'), context)
  return { app, spawned, menus, messages, ready: () => ready(),
    guard: () => vm.runInContext('tryWindowsLocation()', context),
    closeWindows: () => { windows = []; app.emit('window-all-closed') }, quits: () => quits }
}

test('Mac retains one backend across window close/reopen and stops on Quit', async () => {
  const h = harness()
  await h.ready()
  assert.equal(h.spawned.length, 1)
  assert.match(h.spawned[0].exe, /backend\/locwarp-backend$/)
  h.closeWindows()
  assert.equal(h.spawned[0].proc.kills, 0)
  assert.equal(h.quits(), 0)
  h.app.emit('activate')
  assert.equal(h.spawned.length, 1)
  h.app.emit('before-quit')
  assert.equal(h.spawned[0].proc.kills, 1)
  assert.equal(h.menus[0][0].role, 'appMenu')
})

test('Windows retains exe naming and quits on last window close', async () => {
  const h = harness('win32')
  await h.ready()
  assert.match(h.spawned[0].exe, /locwarp-backend\.exe$/)
  h.closeWindows()
  assert.equal(h.spawned[0].proc.kills, 1)
  assert.equal(h.quits(), 1)
  assert.equal(h.menus[0], null)
})

test('Missing Mac backend shows correct error and launches no process', async () => {
  const h = harness('darwin', false)
  await h.ready()
  assert.equal(h.spawned.length, 0)
  assert.equal(h.quits(), 1)
  assert.equal(h.messages.length, 1)
  assert.doesNotMatch(h.messages[0].detail, /Windows Defender|C:\\Program Files/)
})

test('Mac location bypasses PowerShell', async () => {
  const h = harness()
  const result = await h.guard()
  assert.equal(result.code, 'UNSUPPORTED_PLATFORM')
  assert.equal(h.spawned.length, 0)
})
