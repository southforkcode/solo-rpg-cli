from typing import List, Optional, Protocol


class MusicPlayerProtocol(Protocol):
    """
    Protocol describing the contract for any background music playback implementation.
    The core domain logic relies on this interface rather than a concrete Pygame
    implementation.
    """

    @property
    def is_playing(self) -> bool:
        """Returns True if music is currently playing, otherwise False."""
        ...

    @property
    def is_paused(self) -> bool:
        """Returns True if music is currently paused, otherwise False."""
        ...

    @property
    def volume(self) -> float:
        """Returns the current playback volume (0.0 to 1.0)."""
        ...

    def play(self, playlist_name: Optional[str] = None) -> bool:
        """
        Start playing the specified playlist.
        If no playlist is specified, plays the default/unnamed playlist.
        Returns True if playback started successfully, False otherwise.
        """
        ...

    def stop(self) -> None:
        """Stops the current playback."""
        ...

    def skip(self) -> None:
        """Skips the currently playing track and moves to the next."""
        ...

    def pause(self) -> None:
        """Pauses the current playback."""
        ...

    def resume(self) -> None:
        """Resumes playback that was previously paused."""
        ...

    def set_volume(self, volume: float) -> None:
        """
        Sets the playback volume.

        Args:
            volume: A float between 0.0 and 1.0.
        """
        ...

    def list_playlists(self) -> List[str]:
        """Returns a list of available playlist names."""
        ...
