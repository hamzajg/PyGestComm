# document-numbering — specifications by example

Feature: document-numbering

  @w1 @auto-number
  Scenario: Auto-number on create
    Given no devis exists with a DEV- code
    When a devis is created without codeDevis
    Then it receives codeDevis DEV-0001
    And a second codeless devis receives DEV-0002

  @w1 @explicit-wins
  Scenario: Explicit codes win
    Given the numbering helper exists
    When a devis is created with codeDevis "J-DEV-99999"
    Then the code is stored verbatim and no sequence is consumed

  @w1 @per-type
  Scenario: Sequences are per type
    Given devis DEV-0007 and facture FAC-0003 exist
    When a bonliv is created without a code
    Then it receives BL-0001 independently of the other sequences
