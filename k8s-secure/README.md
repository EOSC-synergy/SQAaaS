# Securing SQAaaS services

Following this guide, the SQAaaS services are deployed with HTTP-only access.
In production environments it is often required to secure those services via
HTTPS.

This guide describes the solution implemented for the production
SQAaaS APIs (
[production](https://api.sqaaas.eosc-synergy.eu),
[staging](https://api-staging.sqaaas.staging.eosc-synergy.eu),
[development](https://api-dev.sqaaas.staging.eosc-synergy.eu).

## OAuth2 Token Introspection
The SQAaaS API server does not (deliberately) have built-in support for
securing the available paths. Instead, it depends on the availability of a
proxy-like solution that requires authentication for any incoming request.
Hence, in order to be successfully authenticated, each HTTP request must
include an OpenID bearer token (available through the request header) that
will be subsequently validated by a process known as *token introspection*.

### The IdP

The selected IdP for the production SQAaaS is the EOSC's
[EGI Checkin](https://aai-dev.egi.eu). The SQAaaS APIs leverage the
`/introspect` path in order check the validity of the incoming token, i.e.
requiring a valid `{active: true}` in the JSON response obtained from the IdP.

In order to be successful, the request to `/introspect` must also include a
basic authorization header `'Authorization: Basic <code>'`, where `code` is
the result of: *base64(<client_id>:<client_secret>)*. The client id and secret
must exist and be enabled in IdP.

## The Setup

The setup leverages the NGINX ingress controller to:
1. Enable HTTPS, through the use of Sectigo certificates.
2. Implement OAuth2 token introspection.

### HTTPS

### Token introspection
