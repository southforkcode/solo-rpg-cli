# Solo RPG CLI - User Guide

## Commands

### `journey`
Manage your character's journeys. In an RPG campaign, characters are almost always on a journey or several journeys at once.

- `journey start "Title"`: Start a new journey. You will be prompted for a multi-line description, a difficulty, and an optional number of steps.
- `journey list [-active|-paused|-completed|-all]`: List journeys matching a specific state (default: `-active`).
- `journey progress "Title"`: Progress a journey by one step. If the number of steps matches the goal, the journey automatically completes.
- `journey pause "Title"`: Pause a journey putting it on hold.
- `journey resume "Title"`: Resume a paused journey.
- `journey complete "Title"`: Mark a journey as completed unconditionally.
- `journey stop "Title"`: Stop a journey indefinitely.
- `journey remove "Title"`: Remove a journey completely (requires confirmation).

*Note: Starting, progressing, pausing, resuming, completing, and stopping a journey will automatically add a corresponding journal entry to keep track of your campaign's narrative.*


### `journal`
Manage your journal entries.

- `journal add [title]`: Adds a journal entry with an optional title.
- `journal list [top]`: Lists journal entries optionally up to the last N entries.
- `journal delete|del <identifier>`: Deletes a journal entry by its index or title.


### `roll`
Roll dice. (e.g., `roll 1d20 + 2`)
