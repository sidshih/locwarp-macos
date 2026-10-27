from backend.services.macos_upgrade import backup_settings

if __name__ == "__main__":
    print(backup_settings() or "設定已保留，無需重複備份。")
