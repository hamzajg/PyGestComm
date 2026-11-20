# protected-delete-conflict — specifications by example
# Scenario tags @w<N> map items to delivery waves (see WAVES.md / BACKLOG.md).

Feature: protected-delete-conflict

  @w1 @happy-path
  Scenario: Deleting a client used by a document returns a conflict
    Given a client referenced by a devis and a facture
    When the client deletes DELETE /api/client/<id>
    Then the API answers 409 with a detail naming the blocking records
    And no 500 response is produced

  @w1 @error-path
  Scenario: Deleting an article used by a document line returns a conflict
    Given an article used by a devis line and a bonliv line
    When the article DELETE /api/article/<id> is requested
    Then the API answers 409 and the article still exists

  @w1 @error-path
  Scenario: Deleting a quote referenced by an invoice returns a conflict
    Given a valide devis converted into a facture
    When DELETE /api/devis/<id> is requested
    Then the terminal-state lock answers 400 for the converti devis
    And a brouillon devis referenced by a facture answers 409

  @w1 @happy-path
  Scenario: Deleting an unreferenced client still succeeds
    Given a client with no documents
    When DELETE /api/client/<id> is requested
    Then the API answers 204
    And a follow-up GET answers 404
