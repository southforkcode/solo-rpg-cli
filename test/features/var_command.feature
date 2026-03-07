Feature: Variable Tracking
  As a player
  I want to track variables like HP, Gold, and specific states
  So I don't need to use external tools for character sheets

  Scenario: Setting a string variable
    Given the game is initialized
    When I type "var set Class Fighter"
    Then I should see "Variable 'Class' set to Fighter."
    When I type "var get Class"
    Then I should see "Class: Fighter"

  Scenario: Setting an integer variable
    Given the game is initialized
    When I type "var set HP 20"
    Then I should see "Variable 'HP' set to 20."
    When I type "var get HP"
    Then I should see "HP: 20"

  Scenario: Updating an integer variable
    Given the game is initialized
    And I type "var set Gold 10"
    When I type "var update Gold 5"
    Then I should see "Variable 'Gold' updated to 15."
    When I type "var update Gold -8"
    Then I should see "Variable 'Gold' updated to 7."

  Scenario: Updating a non-existent variable
    Given the game is initialized
    When I type "var update missing 1"
    Then I should see "Variable 'missing' not found."

  Scenario: Updating a string variable
    Given the game is initialized
    And I type "var set Name Bob"
    When I type "var update Name 1"
    Then I should see "Cannot update non-numeric variable 'Name'"

  Scenario: Listing variables
    Given the game is initialized
    And I type "var set str 16"
    And I type "var set dex 14"
    When I type "var list"
    Then I should see "str: 16"
    And I should see "dex: 14"

  Scenario: Deleting a variable
    Given the game is initialized
    And I type "var set foo 1"
    When I type "var delete foo"
    Then I should see "Variable 'foo' deleted."
    When I type "var get foo"
    Then I should see "Variable 'foo' not found."

  Scenario: Using variables in macros
    Given the game is initialized
    And I type "var set AC 15"
    And a file "macros.txt" with the following content:
      """
      defmacro checkAC
        if AC > 10 then
            return "Good AC"
        else
            return "Bad AC"
        endif
      endmacro
      """
    And I load macros from "macros.txt"
    When I type "/checkAC"
    Then I should see "Good AC"
