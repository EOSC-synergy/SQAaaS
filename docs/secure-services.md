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

Since the APIs use Kubernetes, the [NGINX ingress
controller](https://github.com/kubernetes/ingress-nginx), known as 
*ingress-nginx*, will be the one in charge of acting as the reverse proxy
for the APIs. Two main actions are required for the *ingress-nginx* to perform:

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

#### Extending *ingress-nginx* controller
In order to implement the former NGINX solution for the token introspection, 
we need to shape the `nginx.conf` file according to our needs. To this end, 
Kubernetes [NGINX annotations](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/)
provide the appropriate means, but as we will show, the current version
(`controller-v0.41.2`) does not satisfy the whole set of settings needed to
set up the token introspection. Hence, some of them will be added directly in
the `nginx.tmpl` template. 

On the one hand, through the annotations we can include the [new locations and
the call to `auth_request`](https://github.com/EOSC-synergy/ingress-nginx/blob/custom/controller-v0.41.2/deploy/static/provider/baremetal/sqaaas-ingress.yaml#L6-L34)
in the server block, while, on the other hand, [direct modifications in the
`nginx.tmpl` file](https://github.com/kubernetes/ingress-nginx/compare/master...EOSC-synergy:custom/controller-v0.41.2#diff-cbf382cc05c9f274b5db56a581b335dba8ecb80fd96a8f1a6a068b2594c9b1ca) are needed for those statements outside the scope of server
block that are not currently allowed by the *ingress-nginx* implementation.

##### Compiling the njs module
The [Docker image](https://github.com/EOSC-synergy/ingress-nginx/blob/custom/controller-v0.41.2/rootfs/Dockerfile)
used by the controller *does not use the NGINX package provided by the Alpine
distribution*, so the njs module cannot be installed via Alpine apk package 
manager and instead needs to be manually compiled using the same NGINX version
deployed in the image. The njs module compatible with the NGINX 1.19.4 (used
by `controller-v0.41.2`) is available in our [fork repository](https://github.com/EOSC-synergy/ingress-nginx/tree/custom/controller-v0.41.2/rootfs/etc/nginx/modules).

##### Adding the NGINX required files
Apart from the njs module file, there are 2 *include statements* in the
modified `nginx.tmpl` template. Both are available in the
[oauth2_token_introspection folder](https://github.com/EOSC-synergy/ingress-nginx/tree/custom/controller-v0.41.2/rootfs/etc/nginx/oauth2_token_introspection).

Note that the folder contains a template version of the `main.conf` file, where
the required OAuth2 configuration variables are set using environment
variables. The rationale of doing this through a template is that those 
envinronment variables will be set as Kubernetes secrets, and as such, only
accessible when deploying the controller. Hence, the solution is to use a
[preliminary container (`initContainers`)](https://github.com/EOSC-synergy/ingress-nginx/blob/custom/controller-v0.41.2/deploy/static/provider/baremetal/deploy.yaml#L408-L445)
that substitutes the variable values and places the resultant `main.conf` file
in a separate volume, which will be subsequently mounted in the 
`/etc/nginx/oauth2_token_introspection/vars` path, as expected by the NGINX
controller configuration. As already mentioned, the environment variables must
be defined as Secrets.
