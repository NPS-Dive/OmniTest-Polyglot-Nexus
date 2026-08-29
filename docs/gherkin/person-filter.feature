# ==============================================================================
# File: docs/gherkin/person-filter.feature
# Purpose: BDD for PersonService.SearchByFilter.
# Mapping: TC-FUNC-002, TC-EDGE-001, TC-EDGE-004
# ==============================================================================

@functional
Feature: Filter persons by optional fields
  Isolation is by table: python never reads persons_go, etc.

  @functional
  Scenario Outline: Filter by first_name prefix-like value
    Given I target language "<lang>"
    When I call SearchByFilter with first_name "A"
    Then the RPC succeeds or returns an empty page
    And every returned person belongs to that language table only

    Examples:
      | lang   |
      | cpp    |
      | python |
      | java   |
      | go     |
      | csharp |
      | node   |

  @functional
  Scenario: Empty filter is a page, not an error
    Given I target language "python"
    When I call SearchByFilter with an empty body
    Then the RPC succeeds
    And the handler does not require every optional field

  @security
  Scenario: SQL-looking first_name is parameterized
    Given I target language "python"
    When I call SearchByFilter with first_name "Robert'); DROP TABLE persons_python;--"
    Then the RPC is handled safely (OK or InvalidArgument)
    And table persons_python still exists
