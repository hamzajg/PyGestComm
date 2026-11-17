# tls-termination — specifications by example

Feature: tls-termination

  @w1 @secure-mode
  Scenario: Secure mode settings apply
    Given DJANGO_SECURE_SSL=1 in the environment
    When Django settings load
    Then SECURE_PROXY_SSL_HEADER trusts X-Forwarded-Proto
    And SECURE_SSL_REDIRECT, secure cookies, and HSTS are enabled

  @w1 @documentation
  Scenario: Deployment is documented
    Given the repository
    When a deployer reads docs/DEPLOYMENT.md and deploy/Caddyfile
    Then they can put HTTPS in front of the API and point the client at it

  @w1 @dev-mode
  Scenario: Dev mode unchanged
    Given DJANGO_SECURE_SSL is unset
    When Django settings load
    Then SECURE_SSL_REDIRECT is off and no proxy header is trusted
