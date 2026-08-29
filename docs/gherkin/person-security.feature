# ==============================================================================
# File: docs/gherkin/person-security.feature
# Purpose: Safe negative tests only (no exploit kits). Expected: reject or clamp.
# Mapping: TC-EDGE-002, TC-EDGE-004, k6/security.js
# ==============================================================================

@security
Feature: Safe handling of abusive Person RPC payloads
  Testers send oversized strings, SQL-looking text, and extreme pagination.
  Expected result is rejection or clamped reads — not data destruction.

  @security
  Scenario Outline: Huge ReadAll limit is clamped or rejected
    Given I target language "<lang>"
    When I call ReadAllPersons with limit 999999
    Then the server responds without crashing
    And at most 500 rows are returned if the call succeeds

    Examples:
      | lang   |
      | cpp    |
      | python |
      | java   |
      | go     |
      | csharp |
      | node   |

  @security
  Scenario: Oversized first_name does not take the process down
    Given I target language "csharp"
    When I call SearchByFilter with a 20000-character first_name
    Then the outcome is OK or InvalidArgument
    And no shell or SQL batch is executed

  @security
  Scenario: k6 security profile documents expected handling
    Given k6/security.js is used against a single LANG
    When oversized, SQL-looking, and huge-limit payloads are sent
    Then checks treat OK/InvalidArgument/OutOfRange as safe
    And Unavailable after a crash is a fail
