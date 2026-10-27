#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON_BIN="${LOCWARP_PYTHON:-python3.13}"
if ! command -v "$PYTHON_BIN" >/dev/null; then
  echo 'Install Python 3.13 and Node.js 24 first (see docs/macos.md).'
  exit 1
fi
"$PYTHON_BIN" -c 'import sys, ssl; assert sys.version_info >= (3,13); assert hasattr(ssl.SSLContext, "set_psk_client_callback")'
if [[ ! -d .venv ]]; then "$PYTHON_BIN" -m venv .venv; fi
.venv/bin/python -c 'import sys, ssl; assert sys.version_info >= (3,13), "Existing .venv requires Python 3.13+; recreate it"; assert hasattr(ssl.SSLContext, "set_psk_client_callback"), "Python SSL lacks TLS-PSK support"'
exec .venv/bin/python start.py
