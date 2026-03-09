import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from behave import given

from lib.core.state import StateFactory
from lib.presentation.commands.music_command import MusicCommand
from lib.presentation.repl import REPLEnvironment

# Note: We reuse the steps from history_steps.py for the "When I type"
# and "Then the output should contain". Those are more generic, but they need
# the "REPL is running" context set up correctly here.


@given("the REPL is running")
def step_impl_repl_running(context):
    if not hasattr(context, "repl"):
        context.temp_dir = tempfile.mkdtemp()
        context.gamedir = Path(context.temp_dir)
        context.base_dir = context.gamedir

        # We need to mock pygame to avoid initializing audio devices in tests
        import lib.infrastructure.music_player

        # Patch init and methods that throw uninitialized errors
        lib.infrastructure.music_player.pygame.mixer.init = MagicMock()
        lib.infrastructure.music_player.pygame.mixer.music.load = MagicMock()
        lib.infrastructure.music_player.pygame.mixer.music.play = MagicMock()
        lib.infrastructure.music_player.pygame.mixer.music.stop = MagicMock()
        lib.infrastructure.music_player.pygame.mixer.music.pause = MagicMock()
        lib.infrastructure.music_player.pygame.mixer.music.unpause = MagicMock()
        lib.infrastructure.music_player.pygame.mixer.music.get_busy = MagicMock(
            return_value=False
        )
        lib.infrastructure.music_player.pygame.mixer.music.set_volume = MagicMock()

        player = lib.infrastructure.music_player.PygameMusicPlayer(context.gamedir)
        state = StateFactory.create(
            context.gamedir, player
        )
        context.state = state

        # Stop the daemon thread from MusicManager for tests cleanly so it doesn't hang
        state.music_manager._is_playing = False

        from lib.presentation.console import MockConsole

        context.console = MockConsole(inputs=[])
        context.repl = REPLEnvironment(context.base_dir, state, context.console)
        context.repl.command_registry.register(MusicCommand())

        context.output = ""
        context.result = None
        context.last_output = None


@given('the directory "{dir_path}" has been created')
def step_impl_directory_created(context, dir_path):
    # Ensure REPL is initialized if not already
    step_impl_repl_running(context)

    full_path = context.gamedir / dir_path
    full_path.mkdir(parents=True, exist_ok=True)


@given('the directory "{dir_path}" has been created with dummy audio')
def step_impl_directory_created_with_audio(context, dir_path):
    step_impl_directory_created(context, dir_path)
    full_path = context.gamedir / dir_path
    dummy_file = full_path / "dummy.mp3"
    dummy_file.touch()
