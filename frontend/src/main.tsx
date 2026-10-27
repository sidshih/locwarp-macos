import { backupBrowserSettings } from './settingsBackup'
import React from 'react'
import ReactDOM from 'react-dom/client'
import 'leaflet/dist/leaflet.css'
import App from './App'
import './styles.css'
import { I18nProvider } from './i18n'

try { backupBrowserSettings(localStorage) } catch (error) { console.warn('LocWarp browser settings backup failed:', error) }

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <I18nProvider>
      <App />
    </I18nProvider>
  </React.StrictMode>
)
