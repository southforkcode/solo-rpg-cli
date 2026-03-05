Feature: Roll Command

  Scenario: Roll a basic set of dice
    When I execute the roll command with "1d20"
    Then the roll command returns a result
    And the roll result should be between 1 and 20

  Scenario: Roll with implicit 1 die
    When I execute the roll command with "d6"
    Then the roll command returns a result
    And exactly 1 die was rolled
    And the roll result should be between 1 and 6

  Scenario: Roll multiple dice
    When I execute the roll command with "3d6"
    Then the roll command returns a result
    And exactly 3 dice were rolled
    And the roll result should be between 3 and 18

  Scenario: Roll with advantage
    When I execute the roll command with "1d20 adv"
    Then the roll command returns a result
    And exactly 2 dice were rolled
    And the roll has advantage

  Scenario: Roll with disadvantage
    When I execute the roll command with "1d20 dis"
    Then the roll command returns a result
    And exactly 2 dice were rolled
    And the roll has disadvantage

  Scenario: Roll with positive modifier
    When I execute the roll command with "1d10 + 4"
    Then the roll command returns a result
    And the roll result should be between 5 and 14

  Scenario: Roll with negative modifier
    When I execute the roll command with "1d8 - 2"
    Then the roll command returns a result
    And the roll result should be between -1 and 6

  Scenario: Advantage and modifier
    When I execute the roll command with "1d20 adv + 2"
    Then the roll command returns a result
    And exactly 2 dice were rolled
    And the roll has advantage
    And the roll result should be between 3 and 22

  Scenario: Missing 'd' character
    When I execute the roll command with "120"
    Then the roll command raises a SyntaxError

  Scenario: Unknown advantage modifier
    When I execute the roll command with "1d20 advv"
    Then the roll command raises a SyntaxError

  Scenario: Missing command arguments
    When I execute the roll command without arguments
    Then the roll command raises a SyntaxError
