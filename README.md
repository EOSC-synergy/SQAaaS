# SQAaaS platform

Catch-all repository for the SQAaaS platform, developed under the scope of EOSC-Synergy project.

## Components
* JePL [`jenkins-pipeline-library`](https://github.com/indigo-dc/jenkins-pipeline-library)
* OpenAPI specification [`jenkins-pipeline-library`](https://github.com/eosc-synergy/sqaaas-api-spec)
* API server [`jenkins-pipeline-library`](https://github.com/eosc-synergy/sqaaas-api-server)
* Web GUI [`jenkins-pipeline-library`](https://github.com/eosc-synergy/sqaaas-web)

## Deployment
As simple as using the `kustomization.yaml` file to orchestrate the SQAaaS components in a Kubernetes 
cluster. Hence, from the root path of the repository, run:

```
kubectl apply -k k8s/
```

### Secret tokens
Since SQAaaS leverages GitHub and Jenkins APIs, we will need tokens for those components. The former
`kustomization.yaml` file is expecting them in the following paths (again from the root path of the
repository):
* GitHub API token: `./k8s/.gh_token`
* Jenkins API token: `./k8s/.jk_token`

---
**NOTE**

<span style="color:blue">Not all the SQAaaS components are currently available to be deployed with Kubernetes. We are working
to provide a fully fledged deployment.</span>
---
