"""Back up user data once before the new version writes it. Never reset settings.

No project folder is copied: ~/.locwarp is shared by both source checkouts.
Browser localStorage stays in the same browser/profile at http://localhost:5173.
"""
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

VERSION = '0.2.202-macos.1'


def backup_settings(home=None):
    home = Path(home) if home is not None else Path.home()
    source = home / '.locwarp'
    if not source.exists():
        return None
    marker = source / f'.backup-{VERSION}.json'
    if marker.exists():
        return None
    backup_root = home / '.locwarp-backups'
    backup_root.mkdir(mode=0o700, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    destination = backup_root / f'before-{VERSION}-{stamp}'
    destination.mkdir(mode=0o700)
    try:
        shutil.copytree(source, destination / 'data', symlinks=True)
        # Only record completion after all data was copied; failures block launch.
        temp = marker.with_suffix('.tmp')
        temp.write_text(json.dumps({'version': VERSION, 'backup': str(destination)}, indent=2))
        os.replace(temp, marker)
    except BaseException:
        shutil.rmtree(destination)
        raise
    return destination


if __name__ == '__main__':
    result = backup_settings()
    print(f'設定備份完成：{result}' if result else '無需備份；設定未變更。')
