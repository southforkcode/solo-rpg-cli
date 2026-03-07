Feature: CLI initialization flag
  As a player
  I want to initialize a new game directory with the --init flag
  So that I can start a new game

  Scenario: Attempting to initialize an existing directory
    Given an existing game directory
    When I run the CLI with the init flag
    Then the CLI should print "already exists. Cannot initialize."
    And the CLI should exit with code 1

  Scenario: Initializing a new directory
    Given a non-existent game directory path
    When I run the CLI with the init flag
    Then the CLI should print "Initialized new game directory"
    And the directory should be created
    And the CLI should exit with code 0

  Scenario: Attempting to start the CLI in a non-existent directory without the init flag
    Given a non-existent game directory path
    When I run the CLI without the init flag
    Then the CLI should print "not found. Use --init to create and initialize it."
    And the CLI should exit with code 1

  Scenario: Starting the CLI in an existing directory without the init flag
    Given an existing game directory
    When I run the CLI without the init flag
    Then the CLI should successfully start and exit
