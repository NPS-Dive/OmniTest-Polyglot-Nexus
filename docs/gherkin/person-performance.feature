# ==============================================================================
# File: docs/gherkin/person-performance.feature
# Purpose: BDD for k6 gRPC profiles (load, stress, spike, endurance, scalability,
#          concurrency, compare) against PersonService.ReadAllPersons.
# SOLID: SRP — performance scenarios only. Security negatives stay in
#        person-security.feature. Addressing: k6/lib/endpoints.js.
# Mapping: apps/benchmark-runner/k6/*.js, Invoke-AllLanguagePerf.ps1
# ==============================================================================

@performance
Feature: PersonService performance profiles
  The same ReadAllPersons contract is exercised under k6 so six language
  implementations can be compared on p90 / p95 / p98 / p99.

  Background:
    Given k6 is installed
    And the target language gRPC process is listening
    And scripts import lib/endpoints.js

  @performance
  Scenario Outline: Load profile stays within default duration thresholds
    Given I target language "<lang>"
    When I run k6/load.js with LANG="<lang>"
    Then grpc_req_duration p90 p95 p98 p99 are recorded
    And checks stay above the script threshold

    Examples:
      | lang   |
      | cpp    |
      | python |
      | java   |
      | go     |
      | csharp |
      | node   |

  @performance
  Scenario Outline: Stress profile ramps VUs without crashing the process
    Given I target language "<lang>"
    When I run k6/stress.js with LANG="<lang>"
    Then the server accepts ReadAllPersons under rising VU count
    And a performance_results row may be appended

    Examples:
      | lang   |
      | cpp    |
      | python |
      | java   |
      | go     |
      | csharp |
      | node   |

  @performance
  Scenario Outline: Spike profile absorbs a sudden VU burst
    Given I target language "<lang>"
    When I run k6/spike.js with LANG="<lang>"
    Then the process stays up through the spike and cool-down
    And checks treat connection loss as a fail

    Examples:
      | lang   |
      | cpp    |
      | python |
      | java   |
      | go     |
      | csharp |
      | node   |

  @performance
  Scenario Outline: Endurance soak holds 5 VUs for 2 minutes
    Given I target language "<lang>"
    When I run k6/endurance.js with LANG="<lang>"
    Then ReadAllPersons with limit 10 is invoked for the soak window
    And p90 p95 p98 p99 remain defined at the end of the run

    Examples:
      | lang   |
      | cpp    |
      | python |
      | java   |
      | go     |
      | csharp |
      | node   |

  @performance
  Scenario Outline: Scalability ramps 0 to 5 to 10 to 20 to 0
    Given I target language "<lang>"
    When I run k6/scalability.js with LANG="<lang>"
    Then ReadAllPersons is invoked at each VU stage
    And duration percentiles are tagged with lang "<lang>"

    Examples:
      | lang   |
      | cpp    |
      | python |
      | java   |
      | go     |
      | csharp |
      | node   |

  @performance
  Scenario Outline: Concurrency profile applies connection pressure
    Given I target language "<lang>"
    When I run k6/concurrency.js with LANG="<lang>"
    Then many VUs share the same PersonService endpoint
    And Unavailable after a crash is a fail

    Examples:
      | lang   |
      | cpp    |
      | python |
      | java   |
      | go     |
      | csharp |
      | node   |

  @performance
  Scenario Outline: Compare profile walks every language from one script
    Given I run k6/compare.js (3 VUs, about 30s)
    When each VU invokes ReadAllPersons for language "<lang>"
    Then metrics are tagged with lang "<lang>"
    And the six endpoints share the same payload and proto

    Examples:
      | lang   |
      | cpp    |
      | python |
      | java   |
      | go     |
      | csharp |
      | node   |
