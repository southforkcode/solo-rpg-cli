Feature: Managing Journeys
  As a solo RPG player
  I want to manage journeys
  So that I can keep track of my character's current goals

  Scenario: Starting a new journey
    Given a new journey session
    When I type the journey command "journey start Travel Home"
    And I enter journey texts:
      """
      I am going home
      ...
      moderate
      3
      """
    Then the journey command output should be 'Journey "Travel Home" started.'
    And the journey list should have 1 active journey
    And the first journal entry should be "Started Journey: Travel Home"

  Scenario: Progressing a journey
    Given a new journey session
    And a journey "Explore Forest" with 5 steps
    When I type the journey command "journey progress Explore Forest"
    And I enter journey texts:
      """
      Found some tracks.
      """
    Then the journey list should have 1 active journey
    And the journal should have 1 entry
    And the first journal entry should be "Journey Progressed: Explore Forest"

  Scenario: Pausing a journey
    Given a new journey session
    And a journey "Explore Forest" with 5 steps
    When I type the journey command "journey pause Explore Forest"
    And I enter journey texts:
      """
      Need to sleep first.
      """
    Then the journey "Explore Forest" should be "paused"
    And the first journal entry should be "Journey Paused: Explore Forest"

  Scenario: Completing a journey automatically
    Given a new journey session
    And a journey "Short Trip" with 1 steps
    When I type the journey command "journey progress Short Trip"
    And I enter journey texts:
      """
      I arrived.
      """
    Then the journey "Short Trip" should be "completed"
    And the first journal entry should be "Journey Progressed: Short Trip (Completed)"

  Scenario: Removing a journey
    Given a new journey session
    And a journey "Bad Trip" with 5 steps
    When I type the journey command "journey remove Bad Trip"
    And I enter journey texts:
      """
      Y
      """
    Then the journey command output should be 'Journey "Bad Trip" removed.'
    And the journey list should have 0 active journey
