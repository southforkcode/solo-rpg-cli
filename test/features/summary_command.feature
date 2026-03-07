Feature: Summary Command
  As a player
  I want to summarize the current state of my game
  So that I can remember what was happening when I return

  Scenario: Summarize game state
    Given a new summary session
    And a journal entry with title "Entry 1" and content "First note"
    And a journey "Epic Quest" with 5 steps
    When I type the summary command "summary"
    Then the summary should have 1 active journey
    And the summary should have 1 recent journal entry
