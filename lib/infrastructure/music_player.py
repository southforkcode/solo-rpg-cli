# We must conditionally import tomllib based on python version for typings
import sys
import threading
import time
from pathlib import Path
from typing import List, Optional

import pygame

from lib.core.music import MusicPlayerProtocol

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class PygameMusicPlayer(MusicPlayerProtocol):
    def __init__(self, gamedir: Path):
        self.gamedir = gamedir
        self.music_dir = gamedir / "music"
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.current_playlist: list[Path] = []
        self.current_track_index = 0
        self._is_playing = False
        self._is_paused = False
        self._volume = 1.0

        # Initialize pygame mixer
        pygame.mixer.init()

        # Start a daemon thread to monitor playback
        self._playback_thread = threading.Thread(
            target=self._playback_loop, daemon=True
        )
        self._playback_thread.start()

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def volume(self) -> float:
        return self._volume

    def _playback_loop(self) -> None:
        while True:
            time.sleep(0.5)
            if (
                self._is_playing
                and not pygame.mixer.music.get_busy()
                and not self._is_paused
            ):
                self._play_next_track()

    def _play_next_track(self) -> None:
        if not self.current_playlist:
            self._is_playing = False
            return

        self.current_track_index = (self.current_track_index + 1) % len(
            self.current_playlist
        )
        track_path = self.current_playlist[self.current_track_index]
        self._load_and_play(track_path)

    def _load_and_play(self, track_path: Path) -> None:
        try:
            pygame.mixer.music.load(str(track_path))
            pygame.mixer.music.set_volume(self._volume)
            pygame.mixer.music.play()
            self._is_playing = True
            self._is_paused = False
        except pygame.error:
            # Skip unplayable files
            self._play_next_track()

    def play(self, playlist_name: Optional[str] = None) -> bool:
        # 1. Try to load from music.toml if exists in gamedir
        if playlist_name:
            toml_path = self.gamedir / "music.toml"
            if toml_path.exists() and toml_path.is_file():
                try:
                    with open(toml_path, "rb") as f:
                        config = tomllib.load(f)
                    music_config = config.get("music", {})
                    playlists = music_config.get("playlists", {})
                    if playlist_name in playlists:
                        tracks = playlists[playlist_name].get("tracks", [])
                        files = []
                        for track in tracks:
                            track_file = self.music_dir / track
                            if track_file.exists() and track_file.is_file():
                                files.append(track_file)

                        if files:
                            self.current_playlist = files
                            self.current_track_index = 0
                            self._load_and_play(self.current_playlist[0])
                            return True
                except Exception:
                    pass  # Fallback to directory scan if parsing error or logic fails

            # 2. Fallback to reading directory directly
            playlist_dir = self.music_dir / playlist_name
        else:
            playlist_dir = self.music_dir

        if not playlist_dir.exists() or not playlist_dir.is_dir():
            return False

        files = []
        for ext in ("*.mp3", "*.ogg", "*.wav"):
            files.extend([f for f in playlist_dir.glob(ext) if f.is_file()])

        if not files:
            return False

        self.current_playlist = sorted(files)
        self.current_track_index = 0
        self._load_and_play(self.current_playlist[0])
        return True

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self._is_playing = False
        self._is_paused = False

    def skip(self) -> None:
        if self._is_playing:
            self.stop()
            self._play_next_track()

    def pause(self) -> None:
        if self._is_playing and not self._is_paused:
            pygame.mixer.music.pause()
            self._is_paused = True

    def resume(self) -> None:
        if self._is_playing and self._is_paused:
            pygame.mixer.music.unpause()
            self._is_paused = False

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self._volume)

    def list_playlists(self) -> List[str]:
        if not self.music_dir.exists():
            return []

        playlists = set()

        # 1. Check music.toml configuration in gamedir
        toml_path = self.gamedir / "music.toml"
        if toml_path.exists() and toml_path.is_file():
            try:
                with open(toml_path, "rb") as f:
                    config = tomllib.load(f)
                if "music" in config and "playlists" in config["music"]:
                    playlists.update(config["music"]["playlists"].keys())
            except Exception:
                pass

        # 2. Check physical directories
        for item in self.music_dir.iterdir():
            if item.is_dir():
                playlists.add(item.name)

        return sorted(list(playlists))
