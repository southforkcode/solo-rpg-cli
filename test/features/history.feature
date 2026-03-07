Feature: Command History 
  In order to review previous commands and easily journal them
  As a player
  I want to access command history correctly with `_` and `//`

  Scenario: Basic history retrieval with no arguments
    Given a new repl session
    When I enter the repl command "roll 1d20"
    And I enter the repl command "roll 2d6"
    And I enter the repl command "oracle 'Is it safe?'"
    And I enter the repl command "_"
    Then the repl output should contain "oracle 'Is it safe?'"

  Scenario: Journaling the last command correctly using //
    Given a new repl session
    When I enter the repl command "oracle 'Is it safe?' --odds certain"
    And I enter the repl command "roll 1d20"
    And I enter the repl command "//"
    And I enter the repl command "journal list"
    Then the repl output should contain "roll 1d20"
    And the repl output should not contain "oracle"

  Scenario: Fetching specific offsets
    Given a new repl session
    When I enter the repl command "oracle 'First command'"
    And I enter the repl command "oracle 'Second command'"
    And I enter the repl command "_ 1"
    Then the repl output should contain "First command"
