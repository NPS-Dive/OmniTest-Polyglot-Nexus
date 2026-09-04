# ==============================================================================
# File: docs/gherkin/person-security.feature
# Purpose: Safe negative tests only (no exploit kits). Expected: reject or clamp.
# Mapping: TC-EDGE-002/004, TC-SEC-API*, k6/security.js, TS-SEC-OWASP-PLATFORM
# Standard: OWASP API Security Top 10:2023
# ==============================================================================

@security @owasp
Feature: Safe handling of abusive Person RPC payloads
  Testers send oversized strings, SQL-looking text, and extreme pagination.
  Expected result is rejection or clamped reads — not data destruction.

  @security @owasp @api4
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

  @security @owasp @api4
  Scenario Outline: Huge SearchByVector top_k is clamped or rejected
    Given I target language "<lang>"
    When I call SearchByVector with top_k 999999 and a 384-dim zero vector
    Then the server responds without crashing
    And the outcome is OK or InvalidArgument or OutOfRange

    Examples:
      | lang   |
      | csharp |
      | python |

  @security @owasp @api3
  Scenario: Oversized first_name does not take the process down
    Given I target language "csharp"
    When I call SearchByFilter with a 20000-character first_name
    Then the outcome is OK or InvalidArgument
    And no shell or SQL batch is executed

  @security @owasp @api3
  Scenario: SQL-looking filter text is treated as data
    Given I target language "csharp"
    When I call SearchByFilter with a SQL-looking first_name
    Then the outcome is OK or InvalidArgument
    And no DROP TABLE side effect occurs

  @security @owasp @api1
  Scenario: Client-supplied bad UUID on CreatePerson is rejected or ignored safely
    Given I target language "csharp"
    When I call CreatePerson with person.id "not-a-uuid"
    Then the outcome is OK with server id or InvalidArgument
    And the process does not crash

  @security @owasp @api3
  Scenario: Extra JSON properties on CreatePerson are ignored
    Given I target language "csharp"
    When I call CreatePerson with unknown fields is_admin and role
    Then unknown fields do not elevate privileges
    And the call completes without crash

  @security @owasp @api8
  Scenario: Bad vector dimensions produce a controlled error
    Given I target language "csharp"
    When I call SearchByVector with an 8-dim vector
    Then the outcome is InvalidArgument or FailedPrecondition
    And error text does not leak stack traces or credentials

  @security @owasp
  Scenario: k6 security profile documents expected handling
    Given k6/security.js is used against a single LANG
    When oversized, SQL-looking, huge-limit, and huge-top_k payloads are sent
    Then checks treat OK/InvalidArgument/OutOfRange as safe
    And Unavailable after a crash is a fail

  @security @owasp @api2 @api5 @api7 @api9 @api10
  Scenario: Platform residual risks are checklist-logged
    Given Invoke-OwaspPlatformChecklist.ps1 is run for a language
    When API2/5/7/8/9/10 items are reviewed
    Then each item is marked complete with residual risk noted
    And N/A items are not reported as automated passes
