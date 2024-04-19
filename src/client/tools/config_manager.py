import settings
import json
import os


class ConfigManager:
    @staticmethod
    def get_config() -> dict:
        if not os.path.exists(settings.CONFIG_FILE):
            base_config: dict = {
                "music_dir": "",
                "hitmo_integration_include": False,
                "local_search": True,
                "download_on_play": False
            }

            json.dump(base_config, open(settings.CONFIG_FILE, 'w'))

        return json.load(open(settings.CONFIG_FILE, 'r'))

    @staticmethod
    def update_config(new_config: dict) -> None:
        json.dump(new_config, open(settings.CONFIG_FILE, 'w'))
