# macOS 分支維護

- 上游來源： https://github.com/keezxc1223/locwarp
- 基底 tag：`v0.2.202`（f8d3fde437694719143e57193c950cc14052d82a）。
- 分支：`macos`。
- 移植版 tag：`v0.2.202-macos.1`。
- 目前維持已回報可用的 v0.2.202，不包含 v0.2.203 的 WiFi 更新。
- 原始 LICENSE 不修改；移植修改同樣以 MIT 提供。

## 後續合併上游

將自己的 fork 設為 `origin`，原作者設為 `upstream`。
在乾淨的 `macos` 分支建立升級分支後，合併選定的上游 tag；不要用新版 ZIP 直接覆蓋。
先處理衝突，再驗證設定備份、19.5 km/h 預設、USB 與停止程序。
測試及實機檢查完成後再合併回 `macos`，使用新的移植 tag 發布。
不要 force-push 上游歷史，亦不要改寫已發布的 tag。

## 發布檢查

1. 保留 LICENSE、上游連結、非官方移植標示及已知限制。
2. 執行 `./verify-macos.sh`；另外在真實 Mac/iPhone 執行 README 的定位與重連檢查。
3. 確認沒有 `.venv`、`node_modules`、日誌、個人設定、API Key、簽署私鑰或配對紀錄。
4. 發布原始碼 ZIP；沒有在 Mac 建置與驗證過的 App 不當成正式 Mac 安裝檔。
5. 若發布包含依賴的 App，另整理第三方授權聲明。
6. 將 release 標為 pre-release，直到有足夠的實機驗證。

不要把使用者的裝置序號、完整定位紀錄或配對檔放進公開 issue。
本分支的 macOS 問題由 fork 自己追蹤，不自動向原作者送出 issue 或 PR。
