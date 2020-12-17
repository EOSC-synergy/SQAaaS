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
must exist and be enabled beforehand in the IdP.

## The Setup

The setup leverages the NGINX ingress controller to:
1. Enable HTTPS, through the use of Sectigo certificates.
2. Implement OAuth2 token introspection.

### HTTPS

#### Create the TLS secrets
The certificates are handled as TLS secrets by Kubernetes, so we need
to create one secret per API endpoint as follows:
```
kubectl create secret generic sqaaas-api-prod-secret --from-file=tls.crt=<absolute-path-to-public-key> --from-file=tls.key=<absolute-path-to-private-key>
```

Substitute `<absolute-path-to-public-key>` and `<absolute-path-to-private-key>`
with the appropriate path locations.

### Token introspection
We will follow the recommendations from
(NGINX)[https://www.nginx.com/blog/validating-oauth-2-0-access-tokens-nginx/]
and use the `auth_request` module in order to validate tokens. This setup uses
the [njs JavaScript module](https://nginx.org/en/docs/njs/) in order to
correctly interpret the HTTP response (JSON format) obtained from the IdP.

#### Compiling njs module
Since the present implementation relies on the [Kubernetes NGINX ingress
controller](https://github.com/kubernetes/ingress-nginx), we will need to shape
the `nginx.conf` file according to our needs. Fortunately, this file is
rendered using a template, the `nginx.tmpl` file.

#### Create the secrets for the OIDC configuration
As already introduced, the token introspection endpoint requires both the
client id and secret to be included in the HTTP request.
