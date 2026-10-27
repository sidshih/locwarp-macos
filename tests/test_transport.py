import asyncio
import plistlib
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from core import platform_support as platform
from core.device_manager import DeviceManager, _ActiveConnection, _load_pair_record


@pytest.fixture
def mac(monkeypatch):
    monkeypatch.setattr(platform.sys, 'platform', 'darwin')
    monkeypatch.delenv('LOCWARP_MACOS_TUNNEL', raising=False)


def test_paths_and_mode(mac, monkeypatch):
    assert platform.use_userspace_tunnel()
    assert platform.lockdown_directory() == Path('/var/db/lockdown')
    monkeypatch.setenv('LOCWARP_MACOS_TUNNEL', 'kernel')
    assert not platform.use_userspace_tunnel()


def test_exact_pair_record(tmp_path, monkeypatch):
    import core.device_manager as dm
    monkeypatch.setattr(dm, 'lockdown_directory', lambda: tmp_path)
    (tmp_path/'phone.plist').write_bytes(plistlib.dumps({'id':'phone'}))
    assert _load_pair_record('phone') == {'id':'phone'}
    assert _load_pair_record('missing') is None


@pytest.mark.asyncio
async def test_usb_owns_connected_rsd_and_closes_it(mac, monkeypatch):
    import pymobiledevice3.remote.userspace_tunnel as module
    instances = []
    class Handle:
        def __init__(self, **kwargs):
            self.options = kwargs
            self.rsd = SimpleNamespace(close=AsyncMock())
            self.closed = False
            instances.append(self)
        async def __aenter__(self): return self.rsd
        async def aclose(self): self.closed = True; self.rsd = None
        async def __aexit__(self, *args): await self.aclose()
    monkeypatch.setattr(module, 'UserspaceRsdTunnel', Handle)
    dm = DeviceManager()
    lockdown = SimpleNamespace(close=AsyncMock())
    conn = await dm._connect_tunnel('phone', lockdown, '27.0')
    handle = instances[0]
    assert handle.options == {'serial':'phone','remotepairing_fallback':False}
    assert conn.lockdown is handle.rsd
    assert not platform.connection_transport_closed(conn)
    # Simulate upstream transport watcher closing a logical tunnel, cable still in.
    await handle.aclose()
    assert platform.connection_transport_closed(conn)
    dm._connections['phone'] = conn
    await dm.disconnect('phone')
    assert handle.closed
    lockdown.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_cancelled_setup_closes_handle_and_lockdown(mac, monkeypatch):
    import pymobiledevice3.remote.userspace_tunnel as module
    closed = AsyncMock()
    class Handle:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): raise asyncio.CancelledError()
        aclose = closed
    monkeypatch.setattr(module, 'UserspaceRsdTunnel', Handle)
    lockdown = SimpleNamespace(close=AsyncMock())
    with pytest.raises(asyncio.CancelledError):
        await DeviceManager()._connect_tunnel('phone', lockdown, '27.0')
    closed.assert_awaited_once()
    lockdown.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_multi_device_does_not_open_second_stack(mac):
    dm = DeviceManager()
    dm._connections['phone1'] = object()
    with pytest.raises(RuntimeError, match='一次支援一台'):
        await dm.connect('phone2')


@pytest.mark.asyncio
async def test_wifi_request_cannot_replace_usb(mac, monkeypatch):
    from fastapi import HTTPException
    from api import device
    marker = object()
    dm = SimpleNamespace(_connections={'phone':marker})
    monkeypatch.setattr(device, '_dm', lambda:dm)
    with pytest.raises(HTTPException) as error:
        await device.wifi_tunnel_connect(device.WifiTunnelConnectRequest(rsd_address='::1',rsd_port=1))
    assert error.value.status_code == 409
    assert dm._connections['phone'] is marker


@pytest.mark.asyncio
async def test_capabilities_suppress_pin_reconnect_without_deleting_settings(mac):
    from api.system import platform_capabilities
    caps = await platform_capabilities()
    assert caps['wifi_enabled'] is False
    assert caps['max_tunnel_devices'] == 1
