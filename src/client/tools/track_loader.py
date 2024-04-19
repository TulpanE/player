import os
import eyed3
from src.client.tools.config_manager import ConfigManager
from sys import platform


def get_tracks_in_music_dir(sort: bool = False) -> list[eyed3.AudioFile]:
    music_dir: str = ConfigManager.get_config()['music_dir']

    files: list = [
        eyed3.load(f'{music_dir}/{file}')
        for file in os.listdir(music_dir)
        if file.endswith('.mp3')
    ]

    for file in files:
        if not file.tag:
            split_symbol: str = '/' if platform != 'win32' else '\\'
            track_title: list[str] = file.path.split(split_symbol)
            track_title: str = track_title[len(track_title)-1].replace('.mp3', '')

            file.initTag()
            file.tag.title = track_title
            file.tag.artist = 'Unknown'
            file.tag.album = 'Unknown'
            file.tag.save()

    return files if not sort else sorted(files, key=lambda x: x.tag.title)
