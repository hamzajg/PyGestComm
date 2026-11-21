# contact-phone-format — specifications by example
# Scenario tags @w<N> map items to delivery waves (see WAVES.md / BACKLOG.md).

Feature: contact-phone-format
  Client phone numbers are identifiers, not quantities. The API stores and
  returns them as canonical text so leading zeros, a leading + and search keep
  working, while integer-era payloads from the deployed client still succeed.

  @w1 @happy-path
  Scenario: Phone numbers keep leading zeros
    Given the API is running and an operator is authenticated
    When a client is created with phone "0123456789"
    Then the stored value is "0123456789" and a list request returns it unchanged

  @w1 @happy-path
  Scenario: Formatted phone numbers are canonicalised
    Given the API is running and an operator is authenticated
    When a client is created with phone "01 23.45-67/89" and second phone "+33 (0)6 12 34 56 78"
    Then the stored values are "0123456789" and "+330612345678"

  @w1
  Scenario: Legacy integer phone payloads are accepted
    Given the deployed client still posts integer phone values
    When a client is created with the JSON number 11111111
    Then the request succeeds and the stored value is "11111111"

  @w1
  Scenario: Zero and blank mean no phone
    Given the legacy client sends 0 for an empty phone field
    When a client is created with phone 0 and second phone ""
    Then both stored values are "" and a list request shows two empty strings

  @w1
  Scenario: Invalid phone numbers are rejected
    Given the API is running and an operator is authenticated
    When a client is created with phone "abc" or with "++33612345678" or with 21 digits
    Then the request is rejected with a field error naming the phone field

  @w1
  Scenario: Both phone fields behave identically
    Given a client payload where only the second phone is formatted
    When the client is created
    Then the second phone is canonicalised by the same rule as the first

  @w1
  Scenario: Existing numbers survive the migration
    Given the development database holds clients with integer phones 11111111 and 0
    When the migration is applied
    Then the first becomes "11111111" and the second becomes ""

  @w1 @happy-path
  Scenario: Assistant finds clients by phone
    Given a client whose canonical phone is "0612345678"
    When the operator asks the assistant for "find client 06 12 34 56 78"
    Then that client is returned
    And asking for "find client 0612345678" returns the same client
