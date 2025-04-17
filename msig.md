# Nodes

| Hostname | IP | Type |
|----------|----|------|
| sgdxcumas | 10.138.55.35 | Master |
| sgdxcun1 | 10.138.55.92 | Worker |
| sgdxcun2 | 10.138.55.100 | Worker |
| sgdxcun3 | 10.138.55.114 | Worker |
| sgdxcun4 | 10.138.55.115 | Worker |

Username: dxcapp01
Password: MsigDxc123#

# NFS Storage

Hostname: sgdxcunfs

IP: 10.138.55.60

share: ???

# Applications

| Hostname | IP | Public IP | FQDN |
|----------|----|-----------|------|
| Enterprise Link | 10.138.55.x | 10.138.227.91 | https://dxceportaluat1.msigsap.com |
| PolicyAdmin | 10.138.55.x | 10.138.227.92 | https://dxcpolicyadminuat1.msigsap.com |
| ProductAdmin | 10.138.55.x | 10.138.227.93 | https://dxcproductadminuat1.msigsap.com |
| SiSense BI | 10.138.55.x | 10.138.227.98 | https://dxcsisenseuat1.msigsap.com |
| Rancher | 10.138.55.50 |  | https://rancheruat.msigsap.com |
| Harbor | 10.138.55.x |  | https://harbor.msigsap.com |

# Metal LB 

\# VIP IP Address Pool
- 10.138.55.32
- 10.138.55.34
- 10.138.55.38
- 10.138.55.46
- 10.138.55.63

\# VIP for rancher manager
- 10.138.55.50

\# VIP for application
- 10.138.55.74
- 10.138.55.84
- 10.138.55.85
- 10.138.55.88

# Installing Master Node

sgdxcumas # curl -sfL https://get.k3s.io | K3S_TOKEN=SGDXCUMASCLUSTER INSTALL_K3S_EXEC="--disable=traefik --disable=servicelb" sh -s - server \
    --cluster-init \
    --tls-san=sgdxcumas.msigsap.com

# Installing Worker Node

sgdxcun[1-4] # curl -sfL https://get.k3s.io |  K3S_TOKEN=SGDXCUMASCLUSTER K3S_URL=https://sgdxcumas.msigsap.com:6443 sh -

# Preparing .kube/config

sgdxcumas > mkdir .kube
sgdxcumas > sudo cp /etc/rancher/k3s/k3s.yaml .kube/config
sgdxcumas > sudo chown dxcapp01.dxcapp01 .kube/config
sgdxcumas > scp .kube/config sgdxcun1:~
sgdxcumas > scp .kube/config sgdxcun2:~
sgdxcumas > scp .kube/config sgdxcun3:~
sgdxcumas > scp .kube/config sgdxcun4:~
sgdxcun1 > mkdir .kube
sgdxcun1 > mv config .kube
sgdxcun2 > mkdir .kube
sgdxcun2 > mv config .kube
sgdxcun3 > mkdir .kube
sgdxcun3 > mv config .kube
sgdxcun4 > mkdir .kube
sgdxcun4 > mv config .kube

# Verifying .kube/config 

> kubectl get nodes
> kubectl get pods -A

# Labelling worker node

>  kubectl label node sgdxcun1 node-role.kubernetes.io/worker=

# Installing MetalLB

helm repo add metallb https://metallb.github.io/metallb

helm install metallb metallb/metallb --namespace metallb --create-namespace

metallb-pool.yaml

    # Metallb address pool
    apiVersion: metallb.io/v1beta1
    kind: IPAddressPool
    metadata:
      name: cluster-pool
      namespace: metallb
    spec:
      addresses:
      # VIP IP Address Pool
      - 10.138.55.32/32
      - 10.138.55.34/32
      - 10.138.55.38/32
      - 10.138.55.46/32
      - 10.138.55.63/32
      # VIP for rancher manager
      - 10.138.55.50/32
      # VIP for application
      - 10.138.55.74/32
      - 10.138.55.84/32
      - 10.138.55.85/32
      - 10.138.55.88/32

    ---
    # L2 configuration
    apiVersion: metallb.io/v1beta1
    kind: L2Advertisement
    metadata:
      name: metallb-k3s
      namespace: metallb
    spec:
      ipAddressPools:
      - cluster-pool

# Install nginx ingress controller

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.1/deploy/static/provider/baremetal/deploy.yaml

nginx-lb.yaml

apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx-controller-loadbalancer
  namespace: ingress-nginx
spec:
  selector:
    app.kubernetes.io/component: controller
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/name: ingress-nginx
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: 80
    - name: https
      port: 443
      protocol: TCP
      targetPort: 443
  type: LoadBalancer
  loadBalancerIP: 10.138.55.32

# Installation of HA Proxy ingress controller

helm repo add haproxytech https://haproxytech.github.io/helm-charts

helm install haproxy-kubernetes-ingress haproxytech/kubernetes-ingress --create-namespace --namespace haproxy-controller

# Install rancher manager

helm repo add rancher-stable https://releases.rancher.com/server-charts/latest

kubectl create namespace cattle-system
kubectl -n cattle-system create secret generic tls-ca --from-file=cacerts.pem
kubectl -n cattle-system create secret tls tls-rancher-ingress --cert=dxcportaluat1.pem --key=dxceportaluat1.key

helm install rancher rancher-latest/rancher --namespace cattle-system --create-namespace --set hostname=dxceportaluat1.msigsap.com --set bootstrapPassword=P@ssw0rd --set replicas=1 --version=2.11.0 --set ingress.tls.source=secret --set privateCA=true




# Restart rancher deployment (in case there is any error)

kubectl rollout restart deploy/rancher -n cattle-system


# RANDOM STUFFS

apiVersion: v1
kind: Service
metadata:
  labels:
    run: haproxy-ingress
  name: haproxy-ingress
  namespace: haproxy-controller
spec:
  selector:
    app.kubernetes.io/instance: haproxy-kubernetes-ingress
    app.kubernetes.io/name: kubernetes-ingress
  ports:
  - name: http
    port: 80
    protocol: TCP
    targetPort: 8080
  - name: https
    port: 443
    protocol: TCP
    targetPort: 8443
  - name: stat
    port: 1024
    protocol: TCP
    targetPort: 1024
  type: LoadBalancer
  loadBalancerIP: 10.138.55.50
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx-controller-loadbalancer
  namespace: ingress-nginx
spec:
  selector:
    app.kubernetes.io/component: controller
    app.kubernetes.io/instance: ingress-nginx
    app.kubernetes.io/name: ingress-nginx
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: 80
    - name: https
      port: 443
      protocol: TCP
      targetPort: 443
  type: LoadBalancer
  loadBalancerIP: 10.138.55.32

apiVersion: v1
items:
- apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    annotations:
      meta.helm.sh/release-name: rancher
      meta.helm.sh/release-namespace: cattle-system
      nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
      nginx.ingress.kubernetes.io/proxy-read-timeout: "1800"
      nginx.ingress.kubernetes.io/proxy-send-timeout: "1800"
    generation: 1
    labels:
      app: rancher
    name: rancher-hp
    namespace: cattle-system
  spec:
    ingressClassName: haproxy
    rules:
    - host: dxceportaluat.msigsap.com
      http:
        paths:
        - backend:
            service:
              name: rancher
              port:
                number: 80
          path: /
          pathType: ImplementationSpecific
    tls:
    - hosts:
      - dxceportaluat.msigsap.com
      secretName: tls-rancher-ingress
  status:
    loadBalancer: {}
kind: List
metadata:
  resourceVersion: ""
apiVersion: v1
items:
- apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    annotations:
      meta.helm.sh/release-name: rancher
      meta.helm.sh/release-namespace: cattle-system
      nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
      nginx.ingress.kubernetes.io/proxy-read-timeout: "1800"
      nginx.ingress.kubernetes.io/proxy-send-timeout: "1800"
    generation: 1
    labels:
      app: rancher
    name: rancher-ingress
    namespace: cattle-system
  spec:
    ingressClassName: nginx
    rules:
    - host: dxceportaluat1.msigsap.com
      http:
        paths:
        - backend:
            service:
              name: rancher
              port:
                number: 80
          path: /
          pathType: ImplementationSpecific
    tls:
    - hosts:
      - dxceportaluat1.msigsap.com
      secretName: tls-rancher-ingress
  status:
    loadBalancer: {}
kind: List
metadata:
  resourceVersion: ""
