# v0.2.202-macos.1 — Experimental macOS port

Unofficial macOS port based on keezxc1223/locwarp v0.2.202
(f8d3fde437694719143e57193c950cc14052d82a), distributed under the retained MIT license.

- Adds a macOS launcher, process cleanup, Electron menus, and a Mac build script.
- Uses pymobiledevice3 11.35.0 userspace USB tunnels for iOS 17.4+.
- Backs up existing backend data before first launch and snapshots browser preferences.
- Sets the cycling preset to 19.5 km/h; existing custom speeds remain unchanged.

## Scope and validation

Default macOS mode supports one USB device. Wi-Fi auto-connect is disabled; saved Wi-Fi preferences remain intact.
Kernel tunnels, Wi-Fi, multiple devices, Intel/Apple Silicon packaged builds, signing, and notarization are not validated.

The implementation previously passed 13 Python and 5 Node tests, frontend build, builder schema, source start/stop,
and Linux PyInstaller/HTTP checks. The user reported normal operation on their Mac/iPhone on 2026-10-18.
Long-duration location stability and broad hardware compatibility remain unverified.

This pre-release distributes source only. See README-macOS.md before upgrading. Keep the old version available.
