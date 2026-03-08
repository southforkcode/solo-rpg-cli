Feature: Generating and using Settings Loaded Tables

  Scenario: Roll on a custom table included from the game settings
    Given a new campaign
    And a custom table named "test_imported" with items "Item_One,Item_Two" exists in "borrowed" directory
    And a setting file configuring table "custom_table" points to the "test_imported" table
    When I enter a command "table roll custom_table"
    Then the table output should contain "Item_One" or "Item_Two"
