# Securing SQAaaS APIs

The SQAaaS APIs are deployed in the production environment using HTTPS and
the paths are protected using OAuth2 tokens (but in the case of the
development API). This guide describes the current setup, which uses the
Kubernetes'
[NGINX ingress controller](https://github.com/kubernetes/ingress-nginx) or
*ingress-nginx*.

The SQAaaS APIs are accessible through the following endpoints:
* Production: https://api.sqaaas.eosc-synergy.eu/v1
* Staging: https://api-staging.sqaaas.staging.eosc-synergy.eu/v1
* Development: https://api-dev.sqaaas.staging.eosc-synergy.eu

## OAuth2 Token Introspection
The SQAaaS API server code does not (deliberately) implement the authentication
of the available paths. Instead, it relies on the availability of an external
authentication mechanism that must be put on top, which validates any incoming
request. Hence, in order to be successfully authenticated, the current approach
requires that each HTTP request includes an OpenID bearer token (set in the
request header) that will be subsequently validated by a process known as *token
introspection*.

### The IdP

The selected IdP is the EOSC's [EGI Checkin](https://aai-dev.egi.eu). The
SQAaaS APIs leverage the `/introspect` path, provided by the IdP, in order
check the validity of the incoming token, i.e. requiring a valid
`{active: true}` JSON response.

In order to be successful, the request to `/introspect` must also include a
basic authorization header `'Authorization: Basic <code>'`, where `code` is
the result of: *base64(<client_id>:<client_secret>)*. The client id and secret
must exist and be enabled beforehand in the IdP.

## The Setup

Since the APIs use Kubernetes, the *ingress-nginx* will be the one in charge
of acting as the reverse proxy for the APIs. There are two main
requirements for the *ingress-nginx* controller:

1. Expose the APIs through HTTPS (using Sectigo certificates)
2. Implement OAuth2 token introspection

### HTTPS

#### Create the TLS secrets
The certificates are handled as TLS secrets by Kubernetes, so we need
to create one secret per API endpoint as follows:
```
kubectl create secret generic sqaaas-api-prod-secret --from-file=tls.crt=<absolute-path-to-public-key-file> --from-file=tls.key=<absolute-path-to-private-key-file>
```

This secret has to be used in the [`tls` setting](https://github.com/EOSC-synergy/ingress-nginx/blob/custom/controller-v0.41.2/deploy/static/provider/baremetal/sqaaas-ingress.yaml#L40)
within the ingress controller deployment.

### Token introspection
We will follow the recommendations from
[NGINX](https://www.nginx.com/blog/validating-oauth-2-0-access-tokens-nginx/),
i.e. using the `auth_request` module in order to validate tokens. This setup
relies on the [njs JavaScript module](https://nginx.org/en/docs/njs/) in order
to correctly interpret the HTTP response (JSON format) obtained from the IdP.

#### Extending *ingress-nginx* controller
In order to implement the former NGINX solution for the token introspection,
we need to shape the `nginx.conf` file according to our needs. To this end,
Kubernetes [NGINX annotations](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/)
provide the appropriate means, but as we will show, the current version
(`controller-v0.41.2`) does not satisfy the whole set of settings needed to
set up the token introspection solution. Hence, some of them will be added
directly in the `nginx.tmpl` template.

What we can do through the annotations is to include the [new locations and
the call to `auth_request`](https://github.com/EOSC-synergy/ingress-nginx/blob/custom/controller-v0.41.2/deploy/static/provider/baremetal/sqaaas-ingress.yaml#L6-L34)
in the server block. The [direct modifications in the
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

#### Building the controller image
A new Docker controller image has to be built to add the formerly modified
`nginx.tmpl` template, and adding as well all the associated files being
included in this template (njs module & `oauth2_token_introspection` folder).

You just need to follow the instructions in the `ingress-nginx` repository and
review the [development guidelines](https://kubernetes.github.io/ingress-nginx/development/).
In the end you can run something similar to the following:
```
export TAG=controller-v0.41.2
export REGISTRY=eoscsynergy

make build image
```

Once built locally, be sure to push it to the selected registry and *use the
image in the* [controller deployment](https://github.com/EOSC-synergy/ingress-nginx/blob/custom/controller-v0.41.2/deploy/static/provider/baremetal/deploy.yaml#L332).


### Testing the API
Get the refresh and access token from [EGI Check-in AAI dev](https://aai-dev.egi.eu/fedcloud/) using Fedcloud web interface. After the OIDC validation in web interface, the access token can be generated using the provided command that should appear there with the following syntax:
```
curl -X POST -u '<client id>':'<client secret>' -d 'client_id=<client id>&client_secret=<client secret>&grant_type=refresh_token&refresh_token=<refresh token>&scope=openid%20email%20profile' 'https://aai-dev.egi.eu/oidc/token' | python -m json.tool;
```

The curl command returns the JSON web token (JWT) that have the keys named `access_token` and `token_type` must have the value "Bearer".


Finally, to test the API the following commands should return http 200 code for each deployed endpoint. The following examples are specific for current EOSC Synergy deployment.

* Production:
```
curl -X GET -IH 'Authorization: Bearer <access_token>' https://api.sqaaas.eosc-synergy.eu/v1/openapi.json

curl -X GET -IH 'Authorization: Bearer <access_token>' https://api.sqaaas.eosc-synergy.eu/v1/pipeline/

curl -X GET -IH 'Authorization: Bearer <access_token>' https://api.sqaaas.eosc-synergy.eu/v1/ui/
```

* Staging:
```
curl -X GET -IH 'Authorization: Bearer <access_token>' https://api-staging.sqaaas.eosc-synergy.eu/v1/openapi.json

curl -X GET -IH 'Authorization: Bearer <access_token>' https://api-staging.sqaaas.eosc-synergy.eu/v1/pipeline/

curl -X GET -IH 'Authorization: Bearer <access_token>' https://api-staging.sqaaas.eosc-synergy.eu/v1/ui/
```

* Development (note that in this case v1 is surpressed since api-dev is only a mock server):
```
curl -X GET -IH 'Authorization: Bearer <access_token>' https://api-dev.sqaaas.eosc-synergy.eu/pipeline/
```
