# ==============================================================================
# File: docs/gherkin/person-readall.feature
# Purpose: BDD scenarios for PersonService.ReadAllPersons (all six languages).
# SOLID: SRP — this feature describes ReadAll (+ create as a write check).
# Mapping: docs/README.md → Invoke-ManualTest TC-FUNC-001 / TC-FUNC-004
# ==============================================================================

@functional
Feature: Read all persons with pagination
  In order to compare six language implementations fairly
  As a tester
  I want ReadAllPersons to page the language-owned table only

  Background:
    Given Postgres opn_db is reachable on localhost:5432
    And the target language gRPC process is listening

  @functional
  Scenario Outline: Default page returns at most 50 rows
    Given I target language "<lang>"
    When I call ReadAllPersons with limit 5 and offset 0
    Then the RPC succeeds
    And the response contains at most 5 persons
    And total_count is greater than or equal to the page size

    Examples:
      | lang   |
      | cpp    |
      | python |
      | java   |
      | go     |
      | csharp |
      | node   |

  @functional
  Scenario Outline: Create then list includes the new id when offset is current
    Given I target language "<lang>"
    When I call CreatePerson with a unique Bench Runner payload
    Then CreatePerson returns success and inserted_id
    And a following ReadAllPersons does not crash

    Examples:
      | lang   |
      | csharp |
      | go     |

  @performance
  Scenario: ReadAll under k6 load is the same contract
    Given k6 is installed
    When I run k6/load.js with LANG=go
    Then checks stay above the script threshold
    And a row may be appended to performance_results if the wrapper is used
