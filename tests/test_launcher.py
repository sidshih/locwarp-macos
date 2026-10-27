import importlib.util
import socket
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('locwarp_launcher', Path(__file__).resolve().parents[1] / 'start.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


@pytest.mark.skipif(launcher.os.name == 'nt', reason='POSIX occupied-port handling')
@pytest.mark.parametrize('method,port_attribute', [
    ('start_backend', 'BACKEND_PORT'), ('start_frontend', 'FRONTEND_PORT')])
def test_busy_port_cannot_masquerade_as_launched_service(monkeypatch, method, port_attribute):
    with socket.socket() as server:
        server.bind(('127.0.0.1', 0))
        server.listen()
        monkeypatch.setattr(launcher, port_attribute, server.getsockname()[1])
        with pytest.raises(RuntimeError, match='already occupied'):
            getattr(launcher, method)()
        assert launcher.procs == []

@pytest.mark.skipif(launcher.os.name == 'nt', reason='POSIX process groups')
def test_cleanup_stops_grandchild_listener(monkeypatch, tmp_path):
    import subprocess
    import sys
    import time
    ready = tmp_path / 'ready.txt'
    child_code = '''import socket, signal, pathlib, sys
signal.signal(signal.SIGTERM, signal.SIG_IGN)
s = socket.socket()
s.bind(('127.0.0.1', 0))
s.listen()
pathlib.Path(sys.argv[1]).write_text(str(s.getsockname()[1]))
signal.pause()
'''
    parent_code = 'import subprocess, sys, signal; subprocess.Popen([sys.executable, "-c", sys.argv[1], sys.argv[2]]); signal.pause()'
    proc = subprocess.Popen([sys.executable, '-c', parent_code, child_code, str(ready)], start_new_session=True)
    monkeypatch.setattr(launcher, 'procs', [proc])
    try:
        for _ in range(100):
            if ready.exists():
                break
            time.sleep(.01)
        assert ready.exists(), 'child did not start'
        port = int(ready.read_text())
        assert launcher.is_port_open(port)
        launcher.cleanup()
        for _ in range(100):
            if not launcher.is_port_open(port):
                break
            time.sleep(.01)
        assert not launcher.is_port_open(port)
        assert proc.poll() is not None
    finally:
        import os, signal
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()
