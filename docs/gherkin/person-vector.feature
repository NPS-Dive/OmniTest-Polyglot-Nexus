# ==============================================================================
# File: docs/gherkin/person-vector.feature
# Purpose: BDD for PersonService.SearchByVector (L2, embedding vector 384).
# Mapping: TC-FUNC-003, TC-EDGE-003, k6 profiles that stay on ReadAll/Filter
# ==============================================================================

@functional
Feature: Vector nearest-neighbour search
  Metric is L2 (<->) on embedding vector(384).

  @functional @performance
  Scenario Outline: Dummy 384-d vector returns at most top_k rows
    Given I target language "<lang>"
    And I send a 384-length vector of small constants
    When I call SearchByVector with top_k 5
    Then the RPC succeeds
    And the page length is at most 5

    Examples:
      | lang   |
      | cpp    |
      | python |
      | java   |
      | go     |
      | csharp |
      | node   |

  @functional @owasp @api4
  Scenario: top_k 0 uses the service default
    Given I target language "java"
    When I call SearchByVector with top_k 0
    Then the server clamps to default 10 (or rejects InvalidArgument)
    And the process stays up

  @performance
  Scenario: Vector search is eligible for k6 comparison
    Given embeddings exist on the language table
    When a performance wrapper records p90 p95 p98
    Then languages are ranked on the same RPC and payload
