# LocWarp v0.2.202 — macOS 移植版（實驗版）

上游基底：keezxc1223/locwarp tag `v0.2.202`，commit
`f8d3fde437694719143e57193c950cc14052d82a`。此版本是第三方移植，並非原作者的 macOS 官方發布。

## 從舊版升級：保留現有設定

1. 在舊版啟動的 Terminal 按 Enter，停止所有服務。不要刪除舊資料夾。
2. 把整個 `locwarp-macos-v0.2.202` 資料夾解壓縮到下載項目，與舊版並列。
3. 雙擊新版資料夾的 `LocWarp.command`。第一次會安裝獨立的 Python/Node 依賴。
4. 使用**原本同一個瀏覽器、同一個使用者設定檔**，開啟 `http://localhost:5173`。
   不要改成 `127.0.0.1:5173`、無痕視窗或另一個瀏覽器，因為它們有不同的儲存空間。
5. 確認原有書籤、路線、地圖與速度設定，再接上 USB、解鎖 iPhone、確認「信任」與開發者模式。
6. 測試穩定後，再把桌面替身改指向新版的 `LocWarp.command`。

**不用從舊資料夾複製程式、`.venv` 或 `node_modules`。**

保留與備份方式：

| 資料 | 處理方式 |
| --- | --- |
| 設定、書籤、路線、最近位置等後端資料 | 繼續使用原本的 `~/.locwarp`，不重置、不刪除未知欄位 |
| 後端備份 | 新版第一次啟動前，完整複製至 `~/.locwarp-backups/before-0.2.202-macos.1-時間/data`；備份失敗就停止啟動 |
| 地圖、語言、介面偏好、自訂速度、WiFi 釘選 | 使用同一瀏覽器原有 localStorage；載入 React 前儲存一次快照，保留原始鍵值 |
| 瀏覽器備份 | localStorage 的 `locwarp.backup.before-0.2.202-macos.1`，內容為 `created` 與 `values`；不會上傳 |
| USB 與 RemotePairing 配對紀錄 | 保持原位置，不刪除、不重建 |
| 腳踏車預設 | 前端、後端、手機控制頁一致為 **19.5 km/h**；已存的自訂速度仍優先 |

這份下載不包含你 Mac 的個人設定。備份是在你自己的 Mac 第一次執行時進行。
兩個版本共用後端資料，因此**不要同時執行**。

若看到 Apple 無法驗證警告，確認檔案來源後，可到「系統設定 → 隱私權與安全性」允許該檔案開啟。

## USB 與 WiFi 的範圍

macOS 預設使用 pymobiledevice3 **11.35.0** 的 `UserspaceRsdTunnel`，以明確 UDID 選取 USB 裝置。
不使用先前的 `NativeRemotedTunnel`，也不會將 USB 連線自動改走 Bonjour/WiFi。

- iOS 17.4 以上：預設免管理員 USB tunnel。
- iOS 16：保留上游舊式 USB 流程，尚未做 Mac 實機驗證。
- iOS 17.0–17.3：不支援預設免管理員模式。
- **預設一次一台 iPhone**，這是 userspace TCP/IP stack 的程序級限制。
- **預設暫停 WiFi Tunnel 與 WiFi 自動連線**，既有 IP、釘選與開關設定保留。
  手動啟動 WiFi 會顯示目前是 USB 模式，並保留已連線的 USB 裝置。
- `LOCWARP_MACOS_TUNNEL=kernel` 保留上游 kernel tunnel，僅供開發者另外驗證；需要系統建立虛擬介面的權限。
  本套件不自動提權、不要求以 root 執行整個 App。kernel/WiFi/多裝置尚未做 Mac 實測。
- 不支援舊版 `LOCWARP_MACOS_TUNNEL=native`，避免意外沿用已知不穩的路徑。

偵測到 userspace handle 關閉時，即使 USB 線仍插著，也會觸發裝置斷線流程，再由 USB watchdog 嘗試重連。
已有 Network 連線的同 UDID 不會再被當成新 USB 裝置每秒重連。
重連不保證會還原斷線前的瞬移或模擬路線；請先確認裝置狀態，必要時重新按瞬移或開始。

## 環境與驗證

需要 Python 3.13（含 TLS-PSK）與 Node.js 24。可沿用舊版已安裝的 Python 與 Node。
若 Python 指令不是 `python3.13`，可在 Terminal 指定：

```sh
LOCWARP_PYTHON=python3 ./LocWarp.command
```

執行檢查：

```sh
./verify-macos.sh
```

檢查程式不會自動更改 iPhone 的位置。請再手動驗證：

1. USB 連線後，確認舊書籤、路線、自訂速度與地圖偏好。
2. 瞬移到測試座標，觀察至少 10 分鐘，並比較 iPhone 上地圖顯示的位置。
3. 以 19.5 km/h 開始模擬路線，測試暫停與繼續。
4. 鎖定／解鎖 iPhone，觀察位置與連線；Mac 在測試期間保持喚醒。
5. 拔除 USB，確認畫面斷線；插回後確認自動重連，並重新發送位置。
6. 若失敗，從設定頁開啟日誌，保留 `~/.locwarp/logs/backend.log` 中失敗前後的紀錄。

### 回到舊版

先停止新版，再使用舊資料夾的 `LocWarp.command`。舊版仍讀取同一份後端資料與瀏覽器偏好。
如果需要完整回復升級前資料，請先退出所有版本，另外保存目前 `~/.locwarp`，再將上述備份的 `data`
複製為 `~/.locwarp`；不要只覆蓋部分 JSON。瀏覽器偏好可由備份鍵的 `values` 還原。

## 獨立 App

仍可先使用 Terminal 啟動的瀏覽器版。要在 Mac 建立 Electron App：

```sh
./build-macos.sh
```

產物在 `frontend/release`。Apple Silicon 與 Intel 必須分別在相應架構的 Mac 建置。
未使用 Apple 憑證簽署或公證。瀏覽器版和 Electron 有各自的介面設定儲存空間：
**升級時先繼續使用瀏覽器版**，不要同時切換到 Electron，以免看起來像設定遺失。

本次在 Linux 執行程式測試與建置檢查；沒有 Mac/iPhone，因此不是實機驗證通過的發布。
詳細驗證範圍見 `docs/macos-v0.2.202-verification.md`。
