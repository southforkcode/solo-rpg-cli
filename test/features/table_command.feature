Feature: Table Command
  As a solo RPG player
  I want to roll on random tables
  So that I can generate random content like NPCs, loot, or encounters

  Scenario: Listing available tables
    Given a game directory with a "tables" folder containing:
      | filename       | content       |
      | npc_names.txt  | Elara         |
      | loot.csv       | Gold,100      |
    When I execute table command "table list"
    Then the command output should include "Available tables:"
    And the command output should include "npc_names"
    And the command output should include "loot"

  Scenario: Rolling on a text table
    Given a game directory with a "tables" folder containing:
      | filename       | content       |
      | npc_names.txt  | Elara         |
    When I execute table command "table roll npc_names"
    Then the command output should include "Result: Elara"
    And the result should be added to the journal

  Scenario: Rolling on a CSV table
    Given a game directory with a "tables" folder containing:
      | filename       | content       |
      | loot.csv       | Gold\nPotion  |
    When I execute table command "table roll loot"
    Then the command output should include "Result:"
    And the result should be added to the journal

  Scenario: Rolling on a non-existent table
    Given a game directory with a "tables" folder containing:
      | filename       | content       |
      | npc_names.txt  | Elara         |
    When I execute table command "table roll weapons"
    Then the command output should include "Table 'weapons' not found or is empty."

  Scenario: Using an invalid table subcommand
    Given a game directory with a "tables" folder containing:
      | filename       | content       |
      | npc_names.txt  | Elara         |
    When I execute table command "table smash"
    Then a SyntaxError should be raised with "Unknown table subcommand: smash"
