This folder contains the current _adhoc_ deployment of the SQAaaS platform, as
made available by EOSC-Synergy project.

## APIs

### Deployment

The APIs are exposed through HTTPS via the Kubernetes'
[Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/deploy/):
1. The Kubernetes cluster is deployed (using
   [IM dashboard](https://appsgrycap.i3m.upv.es:31443/im-dashboard/login)) on
   top of an OpenStack VM.

2. The _Bare-metal_ provider is used when deploying the ingress controller:
   2.1. Using NodePort:
   ```
   $ sudo kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v0.41.2/deploy/static/provider/baremetal/deploy.yaml
   ```
   2.2. Edit the Service to set ports 80 and 443 for `nodePort`:
   ```
   $ sudo kubectl edit svc ingress-nginx-controller -n ingress-nginx
     (..)
     apiVersion: v1
     kind: Service
     (..)
     spec:
       ports:
       - name: http
         nodePort: 80
         port: 80
         protocol: TCP
         targetPort: http
       - name: https
         nodePort: 443
         port: 443
         protocol: TCP
         targetPort: https
     (..)
   ```

3. Each API endpoint (development, staging, production) has been deployed
   individually, i.e. with its own Deployment and Service definitions.
   - Development: [deploy_sqaaas-api-dev.yaml](deploy_sqaaas-api-dev.yaml)
   - Staging: [deploy_sqaaas-api-stage.yaml](deploy_sqaaas-api-stage.yaml)
   ```
   $ sudo kubectl apply -f deploy_sqaaas-api-dev.yaml
   $ sudo kubectl apply -f deploy_sqaaas-api-stage.yaml
   ```

4. TLS secrets are used to secure the API endpoints:
   ```
   $ sudo kubectl create secret generic sqaaas-api-dev-secret --from-file=tls.crt=/opt/cloudadm/certs/api-dev.sqaaas.eosc-synergy.eu.pem --from-file=tls.key=/opt/cloudadm/certs/api-dev.sqaaas.eosc-synergy.eu.key
   $ sudo kubectl create secret generic sqaaas-api-stage-secret --from-file=tls.crt=/opt/cloudadm/certs/api-staging.sqaaas.eosc-synergy.eu.pem --from-file=tls.key=/opt/cloudadm/certs/api-staging.sqaaas.eosc-synergy.eu.key
   ```

5. Finally, create the ingress rules, including the former TLS secrets:
   ```
   $ sudo kubectl apply -f sqaaas-api-ingress.yaml
   ```

### Testing
- Development API:
  ```
  $ curl https://api-dev.sqaaas.eosc-synergy.eu/pipeline/1
  ```
- Staging API:
  ```
  $ curl https://api-staging.sqaaas.eosc-synergy.eu/v1/pipeline/
  ```
