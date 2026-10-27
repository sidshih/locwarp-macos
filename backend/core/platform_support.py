"""macOS transport policy. NativeRemotedTunnel is deliberately not used."""
import os
import sys
from pathlib import Path


def use_userspace_tunnel():
    if sys.platform != 'darwin':
        return False
    mode = os.getenv('LOCWARP_MACOS_TUNNEL', 'userspace')
    if mode not in ('userspace', 'kernel'):
        raise ValueError('LOCWARP_MACOS_TUNNEL must be userspace or kernel; native mode was removed')
    return mode == 'userspace'


def lockdown_directory():
    if sys.platform == 'win32':
        return Path(os.environ.get('ALLUSERSPROFILE', 'C:/ProgramData')) / 'Apple' / 'Lockdown'
    return Path('/var/db/lockdown') if sys.platform == 'darwin' else Path('/var/lib/lockdown')


def connection_transport_closed(conn):
    """pymobiledevice3 11.35.0 clears this public handle on transport death."""
    if not use_userspace_tunnel() or conn.tunnel_context is None:
        return False
    return conn.tunnel_context.rsd is None


def require_wifi_mode():
    """Avoid replacing a healthy USB tunnel with an incompatible kernel tunnel."""
    if use_userspace_tunnel():
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail={
            'code': 'macos_usb_mode',
            'message': '目前是 macOS USB 模式，已保留 WiFi 設定但暫停 WiFi 連線。請使用 USB；WiFi 需以 kernel 模式另外驗證。',
        })
