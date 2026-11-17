# commercial-management-api — specifications by example
# Scenario tags @w<N> map items to delivery waves (see WAVES.md / BACKLOG.md).

Feature: commercial-management-api

  @w1 @domain
  Scenario: CRUD round-trips per resource
    Given an authenticated client
    When it lists, creates, updates, and deletes a record on each of
      client, article, devis, facture, bonliv
    Then every operation returns the documented JSON shape and persists

  @w1 @documents
  Scenario: Document lifecycle works
    Given a client and articles exist
    When a devis is created with nested lignes, validated, and converted
    Then totals are computed, the facture copies client+lines, the devis
    becomes converti, and terminal documents reject writes

  @w1 @auth
  Scenario: Auth lifecycle works
    Given a Django user exists
    When credentials are posted to /api/token
    Then an access+refresh pair is issued, Bearer calls succeed,
      refresh rotates and blacklists the old token, verify validates,
      and logout revokes the refresh token

  @w1 @assistant
  Scenario: Assistant covers the domain
    Given records exist across all five resources
    When count/search questions are posted to /api/assistant/ask
    Then answers resolve the correct resource, including bonliv aliases
