Feature: Macro Command
  As a player
  I want to define and execute macros
  So that I can automate repetitive commands

  Scenario: Execute a simple macro that echoes text
    Given a new macro testing session
    And a file "macros.txt" exists in the game directory with content:
      """
      defmacro test_echo txt:str
        echo("${txt}")
      endmacro
      """
    When I reload macros
    And I run macro "/test_echo Hello world"
    Then the macro output should contain "Hello"

  Scenario: Execute a macro that rolls dice and evaluates conditions
    Given a new macro testing session
    And a file "macros.txt" exists in the game directory with content:
      """
      defmacro skill_check
        my_roll = roll("1d20")
        if my_roll.total > 10 then
          echo("Success")
        else
          echo("Failure")
        endif
      endmacro
      """
    When I reload macros
    And I run macro "/skill_check"
    Then the macro output should contain either "Success" or "Failure"
