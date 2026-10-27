#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
[[ "$(uname -s)" == Darwin ]] || { echo 'Build on macOS.'; exit 1; }
PYTHON_BIN="${LOCWARP_PYTHON:-python3.13}"
ARCH="$(uname -m)"
case "$ARCH" in arm64) TARGET=arm64 ;; x86_64) TARGET=x64 ;; *) exit 1 ;; esac
"$PYTHON_BIN" -c 'import sys, ssl; assert sys.version_info >= (3,13); assert hasattr(ssl.SSLContext, "set_psk_client_callback")'
[[ -d .venv ]] || "$PYTHON_BIN" -m venv .venv
.venv/bin/python -c 'import sys, ssl; assert sys.version_info >= (3,13), "Existing .venv requires Python 3.13+; recreate it"; assert hasattr(ssl.SSLContext, "set_psk_client_callback"), "Python SSL lacks TLS-PSK support"'
.venv/bin/python -c "import platform; assert platform.machine() == '$ARCH', 'Python architecture must match the build host'"
.venv/bin/python -m pip install -r backend/requirements.txt pyinstaller
ROOT_DIR="$PWD"
(cd backend && ../.venv/bin/python -m PyInstaller locwarp-backend.spec --noconfirm --distpath "$ROOT_DIR/dist-py" --workpath "$ROOT_DIR/build-py/backend")
(cd frontend && npm ci && npm run build && npx electron-builder --mac dmg zip --"$TARGET")
echo "Built $TARGET artifacts in frontend/release/"
