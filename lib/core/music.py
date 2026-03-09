import threading
import time
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from pathlib import Path

import pygame


class MusicManager:
    def __init__(self, gamedir: Path):
        self.gamedir = gamedir
        self.music_dir = gamedir / "music"
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.current_playlist: list[Path] = []
        self.current_track_index = 0
        self.is_playing = False
        self.is_paused = False
        self.volume = 1.0

        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Start a daemon thread to monitor playback
        self._playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self._playback_thread.start()

    def _playback_loop(self):
        while True:
            time.sleep(0.5)
            if self.is_playing and not pygame.mixer.music.get_busy() and not self.is_paused:
                self._play_next_track()

    def _play_next_track(self):
        if not self.current_playlist:
            self.is_playing = False
            return

        self.current_track_index = (self.current_track_index + 1) % len(self.current_playlist)
        track_path = self.current_playlist[self.current_track_index]
        self._load_and_play(track_path)

    def _load_and_play(self, track_path: Path):
        try:
            pygame.mixer.music.load(str(track_path))
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
        except pygame.error:
            # Skip unplayable files
            self._play_next_track()

    def play(self, playlist_name: str | None = None) -> bool:
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

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

    def skip(self):
        if self.is_playing:
            self.stop()
            self._play_next_track()

    def pause(self):
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True

    def resume(self):
        if self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

    def list_playlists(self) -> list[str]:
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
