Feature: Background Music Control
  As a player
  I want to control background ambient music from the REPL
  So that I can immerse myself in the game

  Scenario: Listing available playlists
    Given the REPL is running
    And the directory "music/ambient" has been created
    When I type "m list"
    Then the output should contain "Available Playlists:"
    And the output should contain "- ambient"

  Scenario: Playing a playlist
    Given the REPL is running
    And the directory "music/battle" has been created
    When I type "music play battle"
    Then the output should contain "Error: Playlist 'battle' not found or contains no compatible audio."

  Scenario: Playing default music directory
    Given the REPL is running
    And the directory "music" has been created with dummy audio
    When I type "music play"
    Then the output should contain "Playing music from playlist 'default'."

  Scenario: Missing playlist name with empty directory
    Given the REPL is running
    When I type "m play"
    Then the output should contain "Error: No compatible audio found in the music directory, and no playlist specified."

  Scenario: Stopping playback
    Given the REPL is running
    When I type "m stop"
    Then the output should contain "Music stopped."

  Scenario: Skipping a track
    Given the REPL is running
    When I type "m skip"
    Then the output should contain "Skipped to next track."

  Scenario: Pausing and resuming music
    Given the REPL is running
    When I type "m pause"
    Then the output should contain "Music paused."
    When I type "m resume"
    Then the output should contain "Music resumed."

  Scenario: Changing volume
    Given the REPL is running
    When I type "m vol 50"
    Then the output should contain "Volume set to 50%"
    When I type "m vol"
    Then the output should contain "Current volume: 50%"

  Scenario: Playing a playlist from TOML config
    Given the REPL is running
    And the directory "music/toml_bgm" has been created with dummy audio
    And a file "music.toml" with the following content:
      """
      [music.playlists.custom_mix]
      tracks = ["toml_bgm/dummy.mp3"]
      """
    When I type "m play custom_mix"
    Then the output should contain "Playing music from playlist 'custom_mix'."
