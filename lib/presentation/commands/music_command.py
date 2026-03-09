from rich.console import Console

from lib.core.state import State
from lib.presentation.command import Command
from lib.presentation.lexer import Lexer


class MusicCommand(Command):
    """Command for controlling background music playback."""

    def __init__(self):
        super().__init__()
        self.command = "music"
        self.aliases = ["m", "bgm"]
        self.description = "Control background ambient music"

    def get_completions(self, text_before_cursor: str, state: State) -> list[str]:
        words = text_before_cursor.split()
        if not words:
            return []

        is_new_word = text_before_cursor.endswith(" ")
        subcommands = ["play", "stop", "next", "skip", "pause", "resume", "list", "vol"]

        if len(words) == 1 and not is_new_word:
            return []

        if len(words) == 1 and is_new_word:
            return subcommands

        if len(words) == 2 and not is_new_word:
            prefix = words[1].lower()
            return [c for c in subcommands if c.startswith(prefix)]

        if len(words) == 2 and is_new_word and words[1] == "play":
            return state.music_manager.list_playlists()

        if len(words) == 3 and not is_new_word and words[1] == "play":
            prefix = words[2].lower()
            return [
                p for p in state.music_manager.list_playlists() if p.startswith(prefix)
            ]

        return []

    def execute(self, lexer: Lexer, state: State) -> object:
        subcommand = lexer.next()

        if not subcommand:
            return self.help()

        if subcommand == "play":
            playlist = lexer.next()
            if state.music_manager.play(playlist):
                name = playlist if playlist else "default"
                return f"Playing music from playlist '{name}'."
            else:
                if playlist:
                    return (
                        f"Error: Playlist '{playlist}' not found "
                        f"or contains no compatible audio."
                    )
                return (
                    "Error: No compatible audio found in the music directory, "
                    "and no playlist specified."
                )
        elif subcommand == "stop":
            state.music_manager.stop()
            return "Music stopped."
        elif subcommand in ["next", "skip"]:
            state.music_manager.skip()
            return "Skipped to next track."
        elif subcommand == "pause":
            state.music_manager.pause()
            return "Music paused."
        elif subcommand == "resume":
            state.music_manager.resume()
            return "Music resumed."
        elif subcommand == "list":
            playlists = state.music_manager.list_playlists()
            if not playlists:
                return "No playlists found in the music/ directory."
            return "Available Playlists:\n" + "\n".join(f" - {p}" for p in playlists)
        elif subcommand == "vol":
            vol_str = lexer.next()
            if not vol_str:
                return f"Current volume: {state.music_manager.volume * 100:.0f}%"
            try:
                vol = float(vol_str)
                # If they provided > 1, assume it's a percentage
                if vol > 1.0 or vol_str.isdigit():
                    vol = vol / 100.0
                state.music_manager.set_volume(vol)
                # Calculate the percentage *after* setting to reflect actual clamped vol
                # We do not have direct access to the new volume since it's a property,
                # but we can just use the vol we passed in clamped
                clamped_vol = max(0.0, min(1.0, vol))
                return f"Volume set to {clamped_vol * 100:.0f}%"
            except ValueError:
                return "Error: Invalid volume level."
        else:
            return f"Error: Unknown music subcommand '{subcommand}'."

    def help(self):
        console = Console()
        console.print(
            "[bold cyan]music[/bold cyan]|[bold cyan]m[/bold cyan] "
            "[bold]play[/bold] [italic]<playlist>[/italic] - start playing a playlist"
        )
        console.print(
            "[bold cyan]music[/bold cyan]|[bold cyan]m[/bold cyan] "
            "[bold]stop[/bold] - stop music playback"
        )
        console.print(
            "[bold cyan]music[/bold cyan]|[bold cyan]m[/bold cyan] "
            "[bold]next[/bold]|[bold]skip[/bold] - skip to the next track"
        )
        console.print(
            "[bold cyan]music[/bold cyan]|[bold cyan]m[/bold cyan] "
            "[bold]pause[/bold] - pause music"
        )
        console.print(
            "[bold cyan]music[/bold cyan]|[bold cyan]m[/bold cyan] "
            "[bold]resume[/bold] - resume paused music"
        )
        console.print(
            "[bold cyan]music[/bold cyan]|[bold cyan]m[/bold cyan] "
            "[bold]list[/bold] - list available playlists"
        )
        console.print(
            "[bold cyan]music[/bold cyan]|[bold cyan]m[/bold cyan] "
            "[bold]vol[/bold] \\[[italic]0-100[/italic]] - check or set volume"
        )
