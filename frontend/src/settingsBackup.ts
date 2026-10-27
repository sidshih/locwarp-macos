// Snapshot old preferences before the new React application reads or writes them.
// Keep all original keys, including Wi-Fi pins and custom speeds, untouched.
export const BROWSER_BACKUP_KEY = 'locwarp.backup.before-0.2.202-macos.1'

export function backupBrowserSettings(storage: Storage): void {
  if (storage.getItem(BROWSER_BACKUP_KEY) !== null) return
  const values: Record<string, string> = {}
  for (let i = 0; i < storage.length; i++) {
    const key = storage.key(i)
    if (key?.startsWith('locwarp.') && !key.startsWith('locwarp.backup.')) {
      const value = storage.getItem(key)
      if (value !== null) values[key] = value
    }
  }
  storage.setItem(BROWSER_BACKUP_KEY, JSON.stringify({ created: new Date().toISOString(), values }))
}
