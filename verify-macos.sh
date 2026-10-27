#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
[[ "$(uname -s)" == Darwin ]] || { echo 'This script requires macOS.'; exit 1; }
[[ -x .venv/bin/python ]] || { echo 'Run ./LocWarp.command once to install dependencies first.'; exit 1; }
LOG_FILE="macos-verification-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG_FILE") 2>&1
sw_vers
uname -m
node --version
.venv/bin/python -c 'import sys, ssl; print(sys.version); assert sys.version_info >= (3,13); assert hasattr(ssl.SSLContext, "set_psk_client_callback")'
.venv/bin/python -m pip install pytest pytest-asyncio
.venv/bin/python -m pytest -q tests
node --experimental-strip-types --test tests/*.test.cjs
(cd frontend && npm ci && npm run build)
.venv/bin/python -m pymobiledevice3 usbmux list
echo "Portable checks complete. Log: $LOG_FILE"
echo 'USB enumeration alone does not verify virtual location, Wi-Fi recovery or packaged app behavior.'
echo 'Perform the real-device checklist in docs/macos.md next.'
