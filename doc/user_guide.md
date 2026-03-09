# Solo RPG CLI - User Guide

The Solo RPG CLI is designed to streamline your solo role-playing experience by offering integrated tools for tracking narrative progress, journaling, and rolling dice. 

## Functional Areas

- **Journeys**: Track long-term goals or physical travel. Journeys can be started, progressed step-by-step, paused, and completed.
- **Journals**: Maintain a log of your adventure. Journey updates automatically create journal entries, but you can also log freeform notes.
- **Dice & Rolling**: A built-in dice roller supporting standard RPG notation including advantage, disadvantage, and flat modifiers.
- **Reporting**: Quickly view the current state of your game using the summary command.
- **Macros**: A DSL (Domain-Specific Language) to script complex, multi-step game mechanics or tables, streamlining repeated actions.

---

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

### `roll` (alias: `r`)
Roll dice with support for standard notation, advantage/disadvantage, and flat modifiers.

**Syntax:** `roll <dice> [adv|dis] [modifier]`

- `<dice>`: Number of dice to roll (e.g. `3d6`, `d20`, `1d100`).
- `[adv|dis]`: Optional advantage (`adv`) or disadvantage (`dis`).
- `[modifier]`: Optional mathematical modifier (e.g. `+ 4`, `- 2`).

**Examples:**
- `roll 1d20`
- `roll 2d6 + 3`
- `roll d20 adv`
- `roll d20 dis + 2`

### `summary` (alias: `s`)
Summarize the current state of the game.
This command prints out the last 5 journal entries and a list of all currently active journeys.

### `macro` (alias: `macros`)
Manage macros within your game.

- `macro list`: List all available macros (both global and local to the campaign).
- `macro reload`: Reload macro definitions from disk, useful for testing changes to macro files without restarting the CLI.

### `music` (alias: `m`)
Manage non-blocking background music playback to enhance your game ambiance. The app supports `.mp3`, `.wav`, and `.ogg` files.

- `music list`: List available playlists.
- `music play [playlist]`: Start playing a specific playlist. If no playlist is provided, it will play audio files placed directly in the `<gamedir>/music/` folder.
- `music stop`: Stop playback.
- `music pause`: Pause playback.
- `music resume`: Resume paused playback.
- `music next` / `music skip`: Skip to the next track in the playlist.
- `music vol [0-100]`: Check or set the playback volume (e.g., `m vol 50` for 50%).

#### Playlist Configuration
There are two ways to define playlists:
1. **Directory Scanning**: Create folders inside `<gamedir>/music/` (e.g. `<gamedir>/music/ambient/`) and place your audio files directly inside. The folder name becomes the playlist.
2. **Configuration File**: For more control, create a `<gamedir>/music.toml` file with a `[music.playlists]` block:
   ```toml
   [music.playlists.custom_mix]
   tracks = [
       "music/ambient/track1.mp3",
       "music/combat/epic_fight.mp3"
   ]
   ```
   *Note: Track paths in `music.toml` should be relative to your main `<gamedir>`.*

---

## Macros

The macro system allows you to define complex logic, roll multiple dice, evaluate conditions, and output narrative results seamlessly.

Macros are typically defined in `.txt` files within a `macros` folder in your game directory or the global macro directory.

### Defining a Macro
Macros are defined using a simple scripting syntax:

```text
defmacro <name> <arg_name>:<type>[=<default>] ...
  // Macro body
endmacro
```

- **Types**: Arguments can be typed (e.g., `int`).
- **Defaults**: Arguments can have default values.

### Built-in Functions
- `roll("<dice_string>")`: Rolls the given dice. Returns an object with fields like `.total`.
- `echo("<string>")`: Prints output to the console. Supports string interpolation using `${variable}`.

### Variables and Operations
Variables can be assigned directly:
```text
action_die = roll("1d6")
challenge = roll("1d10")
score = action_die.total + stat
```

### Control Flow
You can use `if / elseif / else / endif` blocks for logic:

```text
if score > challenge.total then
  echo("Success!")
elseif score == challenge.total then
  echo("Tie!")
else
  echo("Failure.")
endif
```

### Complete Example
Here is an example `action_roll` macro that mimics a popular solo RPG mechanic:

```text
defmacro action_roll stat:int adds:int=0
  action_die = roll("1d6")
  challenge1 = roll("1d10")
  challenge2 = roll("1d10")

  action_score = action_die.total + stat + adds
  if action_score > 10 then
    action_score = 10
  endif

  hits = 0
  if action_score > challenge1.total then
    hits = hits + 1
  endif
  if action_score > challenge2.total then
    hits = hits + 1
  endif

  match = 0
  if challenge1.total == challenge2.total then
    match = 1
  endif

  echo("Action Score: ${action_score}")
  echo("Challenge Dice: ${challenge1.total}, ${challenge2.total}")
  
  if hits == 2 then
    if match == 1 then
      echo("Strong Hit with a Match")
    else
      echo("Strong Hit")
    endif
  elseif hits == 1 then
    if match == 1 then
      echo("Weak Hit with a Match")
    else
      echo("Weak Hit")
    endif
  else
    if match == 1 then
      echo("Miss with a Match")
    else
      echo("Miss")
    endif
  endif
endmacro
```
To run this macro in the CLI, you would simply type:
```text
> action_roll 2
```
(where `2` is the value passed to the `stat` argument).

---

## Game Settings & Table Includes

In addition to standard functional components, the CLI supports an externalized static settings mechanism via the `settings/` directory in your game directory. You can utilize TOML (`*.toml`) configuration files to load application settings dynamically.

### Table Includes
The primary capability of the `settings` feature is **Table Includes**. This lets you define rollable tables stored outside of your main `tables/` directory (e.g. referencing global folders, or other campaign references).

**To explicitly map a table:**
Create a TOML file (e.g., `settings/game.toml`) containing a `[tables]` block:

```toml
[tables]
# Points 'external_names' directly to the absolute or relative path
external_names = "../shared_tables/names.txt"
```
The imported file resolves relative to the `settings/` folder and operates identically to standard tables. In the REPL, type `$external_names` to roll the imported table.

**To load tables via glob parameters:**
If you want to pull multiple tables out of a specific directory without manually tracking them, you can utilize the `*` wildcard:

```toml
[tables]
# Sweeps the shared_tables folder for any .txt files containing 'encounters'
all_encounters = "../shared_tables/*_encounters.txt"
```
The file stem (file name minus extension) acts as the table name for all swept files automatically (i.e. if the glob resolved `forest_encounters.txt`, the table name becomes `$forest_encounters`).
