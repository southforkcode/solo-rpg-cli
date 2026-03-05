Feature: Dice Roller

  Scenario: Rolling a single die
    Given 1 die of 6 sides
    When I roll the dice
    Then the result should be between 1 and 6

  Scenario: Rolling a die with a modifier
    Given 1 die of 10 sides
    And a modifier of 2
    When I roll the dice
    Then the result should be between 3 and 12

  Scenario: Rolling a die with advantage
    Given 1 die of 20 sides
    And the roll has advantage
    When I roll the dice
    Then 2 dice should be rolled
    And the total should be the highest die result

  Scenario: Rolling a die with disadvantage
    Given 1 die of 20 sides
    And the roll has disadvantage
    When I roll the dice
    Then 2 dice should be rolled
    And the total should be the lowest die result

  Scenario: Rolling multiple dice
    Given 3 dice of 6 sides
    When I roll the dice
    Then 3 dice should be rolled
    And the total should be the sum of the dice results
