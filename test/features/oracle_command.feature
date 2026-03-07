Feature: Oracle Command

  Scenario: Ask a basic question
    When I execute the oracle command with '"Are there guards?"'
    Then the oracle command returns a result
    And the oracle result starts with "Oracle:"
    And the oracle result contains the question "Are there guards?"

  Scenario: Ask a question with specific odds
    When I execute the oracle command with '"Is it raining?" --odds likely'
    Then the oracle command returns a result
    And the oracle result starts with "Oracle:"

  Scenario: Ask a question with missing odds value
    When I execute the oracle command with '"Is it raining?" --odds'
    Then the oracle command raises a SyntaxError

  Scenario: Just ask a question without quotes
    When I execute the oracle command with 'Is the chest locked?'
    Then the oracle command returns a result
    And the oracle result contains the question "Is the chest locked?"

  Scenario: Dump probability table with no arguments
    When I execute the oracle command without arguments
    Then the oracle command returns a result
    And the oracle result starts with "Oracle Probability Table:"
