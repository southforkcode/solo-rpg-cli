Feature: Journal Command
  As a player
  I want to keep a journal of my adventure
  So that I can remember what happened

  Scenario: Add a journal entry
    Given a new standard session
    When I type the command "journal add Session Start"
    And I enter journal text:
      """
      I wake up in a field.
      ...
      """
    Then the command output should be "Journal entry added."
    And the journal should have 1 entry
    And the first journal entry should have title "Session Start"
    And the first journal entry should contain "I wake up in a field."

  Scenario: Add a journal entry with default title
    Given a new standard session
    When I type the command "journal add"
    And I enter journal text:
      """
      I wake up in a field.
      ...
      """
    Then the command output should be "Journal entry added."
    And the journal should have 1 entry
    And the first journal entry title should start with "Note at"

  Scenario: Cancel a journal entry
    Given a new standard session
    When I type the command "journal add Session Start"
    And I enter journal text and press ctrl-c:
      """
      I wake up in a field.
      """
    Then the command output should be "Note cancelled."
    And the journal should have 0 entries

  Scenario: List journal entries
    Given a new standard session
    And a journal entry with title "Entry 1" and content "First note"
    And a journal entry with title "Entry 2" and content "Second note"
    When I type the command "journal list"
    Then the output should contain "Entry 1"
    And the output should contain "First note"
    And the output should contain "Entry 2"
    And the output should contain "Second note"

  Scenario: Delete a journal entry by index
    Given a new standard session
    And a journal entry with title "Entry 1" and content "First note"
    And a journal entry with title "Entry 2" and content "Second note"
    When I type the command "journal del 1"
    Then the command output should be "Journal entry '1' deleted."
    And the journal should have 1 entry
    And the first journal entry should have title "Entry 2"

  Scenario: Delete a journal entry by title
    Given a new standard session
    And a journal entry with title "Entry 1" and content "First note"
    And a journal entry with title "Entry 2" and content "Second note"
    When I type the command "journal delete Entry 2"
    Then the command output should be "Journal entry 'Entry 2' deleted."
    And the journal should have 1 entry
    And the first journal entry should have title "Entry 1"
