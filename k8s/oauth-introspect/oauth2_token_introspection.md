== Steps
1. Create a ConfigMap object with the new NGINX template content (use the same
 namespace the ingress controller has been deployed: defaults to 
*ingress-nginx* if using the one provided by kubernetes). Assuming that the
new template is in the current path (e.g. check sample
(nginx.tmpl)[nginx.tmpl]), create the ConfigMap as follows:
```
$ sudo kubectl create configmap nginx-configuration --from-file=nginx.tmpl -n ingress-nginx
```

2. Now extend the current controller deployment to add a readonly volume with
the previous content under `/etc/nginx/template/nginx.tmpl`. You can edit the 
deployment directly:
```
$ sudo kubectl edit deploy ingress-nginx-controller -n ingress-nginx
(..)
apiVersion: apps/v1
kind: Deployment
metadata:
  (..)
spec:
  template:
    spec:
      containers:
        (..)
        volumeMounts:
        (..)
        - mountPath: /etc/nginx/template
          name: nginx-template-volume
          readOnly: true
      volumes:
      (..)
      - configMap:
          items:
          - key: nginx.tmpl
            path: nginx.tmpl
          name: nginx-configuration
        name: nginx-template-volume
```

3. Check that the new NGINX template is indeed under
 `/etc/nginx/template/nginx.tmpl`:
```
$ sudo kubectl exec -n ingress-nginx <pod_identifier> cat /etc/nginx/template/nginx.tmpl 
```

== Notes
* The JavaScript module is not available in the controller image. To make it
available in such image you will need to:
  1. Build & push (to your own registry) a new image where the package is
     available.
     1.1. Fork/clone the
          (ingress-nginx)[https://github.com/kubernetes/ingress-nginx] repo
     1.2. Install the (nginx-mod-http-js)[https://github.com/EOSC-synergy/ingress-nginx/blob/custom/controller-v0.41.2/rootfs/Dockerfile#L72].
     1.3. Build the new image:
          ```
          $ export TAG=controller-v0.41.2
          $ export REGISTRY=eoscsynergy

          $ make build image
          ```
     1.4. Push the resultant image:
          ```
          $ docker push ${REGISTRY}/controller:${TAG}
          ```      
  2. Edit the deployment to make it point to your custom Docker image 
create a custom one you need to build & push to a custom registry
