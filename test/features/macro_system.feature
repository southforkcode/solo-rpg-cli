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

  Scenario: Execute a complex macro simulating an Ironsworn Action Roll
    Given a new macro testing session
    And a file "macros.txt" exists in the game directory with content:
      """
      defmacro action_roll stat:int adds:int=0
        action_die = roll("1d6")
        challenge1 = roll("1d10")
        challenge2 = roll("1d10")

        action_score = action_die.total + stat + adds
        if action_score > 10 then
          action_score = 10
        endif

        hits = 0
        if action_score > challenge1.total then
          hits = hits + 1
        endif
        if action_score > challenge2.total then
          hits = hits + 1
        endif

        match = 0
        if challenge1.total == challenge2.total then
          match = 1
        endif

        echo("Action Score: ${action_score}")
        echo("Challenge Dice: ${challenge1.total}, ${challenge2.total}")
        
        if hits == 2 then
          if match == 1 then
            echo("Strong Hit with a Match")
          else
            echo("Strong Hit")
          endif
        elseif hits == 1 then
          if match == 1 then
            echo("Weak Hit with a Match")
          else
            echo("Weak Hit")
          endif
        else
          if match == 1 then
            echo("Miss with a Match")
          else
            echo("Miss")
          endif
        endif
      endmacro
      """
    When I reload macros
    And I run macro "/action_roll 3 1"
    Then the macro output should contain "Action Score:"
    And the macro output should contain "Challenge Dice:"
    And the macro output should match regular expression "(Strong Hit|Weak Hit|Miss)"
