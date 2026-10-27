import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from upgrade_settings import backup_settings


def test_backup_preserves_every_byte_and_is_once_per_version(tmp_path):
    source = tmp_path / '.locwarp'
    source.mkdir()
    fixtures = {'settings.json': b'{"speed_kmh":19.5,"route_engine":"brouter"}',
                'bookmarks.json': b'{"categories":["mine"],"bookmarks":[]}',
                'routes.json': b'{"routes":[]}', 'unknown-future-key.bin': b'\x00\xff'}
    for name, data in fixtures.items():
        (source / name).write_bytes(data)
    destination = backup_settings(tmp_path)
    for name, data in fixtures.items():
        assert (source / name).read_bytes() == data
        assert (destination / 'data' / name).read_bytes() == data
    (source / 'settings.json').write_text('{"speed_kmh":18}')
    assert backup_settings(tmp_path) is None
    assert (destination / 'data/settings.json').read_bytes() == fixtures['settings.json']


def test_fresh_install_creates_no_fake_settings(tmp_path):
    assert backup_settings(tmp_path) is None
    assert not (tmp_path / '.locwarp').exists()


def test_failed_backup_is_not_marked_complete(tmp_path, monkeypatch):
    from backend.services import macos_upgrade as mod
    source = tmp_path / '.locwarp'
    source.mkdir()
    (source / 'settings.json').write_text('{"untouched":true}')
    def fail(*a, **kw):
        raise OSError('disk full')
    monkeypatch.setattr(mod.shutil, 'copytree', fail)
    import pytest
    with pytest.raises(OSError, match='disk full'):
        backup_settings(tmp_path)
    assert not list(source.glob('.backup*'))
    assert (source / 'settings.json').read_text() == '{"untouched":true}'
