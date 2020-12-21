# SQAaaS platform

This is a catch-all repository for the SQAaaS platform, which is developed under the scope of EOSC-Synergy project.

![image](https://drive.google.com/uc?export=view&id=1aylGtnLwcSQA6qwfccxfQKhcGM5LIkZl)

## Components
* JePL [`jenkins-pipeline-library`](https://github.com/indigo-dc/jenkins-pipeline-library)
* OpenAPI specification [`sqaaas-api-spec`](https://github.com/eosc-synergy/sqaaas-api-spec)
* API server [`sqaaas-api-server`](https://github.com/eosc-synergy/sqaaas-api-server)
* Web GUI [`sqaaas-web`](https://github.com/eosc-synergy/sqaaas-web)

## Deployment

### Infrastructure deployment

The Kubernetes cluster is deployed (using
   [IM dashboard](https://appsgrycap.i3m.upv.es:31443/im-dashboard/login)) on
   top of EGI Cloud Compute federation.

The APIs are exposed through HTTPS via the Kubernetes'
[Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/deploy/) that is automatically installed
by the IM.

### APIs deployment

As simple as using the `kustomization.yaml` file to orchestrate the SQAaaS API
server in a Kubernetes cluster. Hence, from the root path of the repository, run:

```
kubectl apply -k k8s
```

#### Prerequisites
The former `kustomization.yaml` file is expecting a set of data, i.e. secret
tokens and the main configuration file, in order to perform the deployment with
success.

*Note: the paths are relative to the root path of the repository*

##### Secret tokens
SQAaaS API leverages GitHub and Jenkins APIs, and accordingly, we will need
tokens for those components. In particular:
* GitHub API token: `./k8s/.gh_token`
* Jenkins API token: `./k8s/.jk_token`

##### Configuration file
The SQAaaS API can be customized through a INI configuration file. An [sample
INI file](https://github.com/EOSC-synergy/sqaaas-api-server/blob/master/etc/sqaaas.ini.sample)
is distributed with the application.
* SQAaaS API INI file: `./k8s/sqaaas.ini`

### Testing
The deployed API server can be accessed through the following URI: `http://<master_node_ip>/sqaaas/v1/`
 
As an example, the following example lists the currently existing pipelines:
```
$ curl http://<master_node_ip>/sqaaas/v1/pipeline
```
  
### Staging and development APIs
Additionally, within the development process, it could be useful to deploy the staging (stub) and 
development (mock) API servers. The `./k8s/` folder contains the YAMLs for deploying these APIs, so
it is just a matter of adding them to the `./k8s/kustomization.yaml` file in the same way it was done
with the production API:
```
resources:
(..)
- sqaaas-api-dev.yaml
- sqaaas-api-staging.yaml
(..)
```

Similarly, once re-deployed, the following command requests the list of pipelines for the staging and
development APIs:

- Staging API:
  ```
  $ curl http://<master_node_ip>/sqaaas-stage/v1/pipeline/
  ```
- Development API:
  ```
  $ curl http://<master_node_ip>/sqaaas-dev/pipeline/
  ```

---
**NOTE**

<span style="color:blue">Not all the SQAaaS components are currently available to be deployed with Kubernetes. We are working
to provide a fully fledged deployment.</span>
---
