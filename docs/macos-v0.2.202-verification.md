# macOS v0.2.202 移植驗證

本次執行環境為 Linux x86_64、Python 3.13.16、pymobiledevice3 11.35.0、Node 24.19.0。
上游來源為 v0.2.202 / f8d3fde437694719143e57193c950cc14052d82a。

## 通過

- 13 個 Python 回歸測試：後端資料逐位元保留、備份只執行一次、失敗備份不記錄成功、
  無資料的全新安裝不建立假設定、USB 明確 UDID、停用 WiFi fallback、handle 釋放、取消時清理、
  裝置通道死亡偵測、配對路徑、阻止第二個 userspace 裝置、WiFi 請求不替換 USB、
  功能資訊、已佔用連接埠不啟動重複服務、停止子程序群組。
- 5 個 Node 測試：瀏覽器 localStorage 原鍵值不變且快照不重寫、Electron macOS 選單與
  單一 backend、關窗後重開不重複啟動、Quit 停止 backend、macOS 可執行檔路徑與缺檔提示、
  不在 Mac 執行 PowerShell、保留 Windows 的 exe 行為。
- TypeScript 與 Vite 正式建置；Vite 有上游的大型 chunk 與重複動態 import 提示。
- electron-builder 設定 schema 驗證。
- Shell 與 JavaScript 語法檢查。
- 原始碼啟動流程：backend + Vite 啟動、OpenAPI/手機頁/桌面頁 HTTP 200、
  platform API 回應；停止後輪詢確認 8777/5173 釋放。

- PyInstaller 在 Linux 的 backend 封裝通過，封裝後 OpenAPI、platform API、手機 HTML 回應 HTTP 200，
  SIGTERM 後正常關閉（uvicorn 重新拋出訊號，因此退出碼為 -15）。這不能證明 Mac 可封裝。

## 未驗證

- macOS arm64/x64 原生執行、DMG/ZIP 建置、簽署與公證。
- 真實 iPhone USB 瞬移是否維持、路線移動、鎖屏、斷線重連、DDI 狀態。
- kernel tunnel、WiFi 與多裝置。
- 使用者 Mac 的真實設定：套件不包含個人資料，備份需在本機首次啟動時建立。

mock 測試只能確認我們如何呼叫與釋放 tunnel，不能證明 iOS/macOS 相容性或長時間穩定性。
底層 userspace handle 每程序僅支援一台，預設不提供 WiFi；限制亦列於 README-macOS.md。
