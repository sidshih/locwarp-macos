const test = require('node:test')
const assert = require('node:assert/strict')
const { pathToFileURL } = require('node:url')
const path = require('node:path')

test('first render snapshots all LocWarp preferences without changing originals', async () => {
  const { backupBrowserSettings, BROWSER_BACKUP_KEY } = await import(pathToFileURL(path.join(__dirname, '../frontend/src/settingsBackup.ts')))
  const data = new Map([
    ['locwarp.speed.custom', '19.5'], ['locwarp.tunnel.pinned', '["phone"]'],
    ['locwarp.map.center', '[25,121]'], ['other-app', 'untouched'],
  ])
  const storage = { get length() { return data.size }, key: (i) => [...data.keys()][i] ?? null,
    getItem: (key) => data.get(key) ?? null, setItem: (k, v) => data.set(k, v) }
  backupBrowserSettings(storage)
  const snapshot = JSON.parse(storage.getItem(BROWSER_BACKUP_KEY))
  assert.equal(snapshot.values['locwarp.speed.custom'], '19.5')
  assert.equal(snapshot.values['locwarp.tunnel.pinned'], '["phone"]')
  assert.equal(snapshot.values['other-app'], undefined)
  assert.equal(storage.getItem('locwarp.speed.custom'), '19.5')
  storage.setItem('locwarp.speed.custom', '18')
  backupBrowserSettings(storage)
  assert.equal(JSON.parse(storage.getItem(BROWSER_BACKUP_KEY)).values['locwarp.speed.custom'], '19.5')
  assert.equal(storage.getItem('locwarp.speed.custom'), '18')
})
