curl -sfL https://get.k3s.io | sh -

ip a add 192.168.18.40/24 dev ens33

curl -sfL https://get.k3s.io | K3S_URL=https://k3s.transcend.local:6443 K3S_TOKEN=K101c2e36316ffb0dacd89bf7dcb8b19474ef164aa9bf8821e7d809c26d2dd5576d::server:2a330108332ca3320cbbd3aa1a5ca6bd sh -

# Install K3S First Master Node

curl -sfL https://get.k3s.io | K3S_TOKEN=DTK3SCLUSTER INSTALL_K3S_EXEC="--disable=traefik --disable=servicelb" sh -s - server \
    --cluster-init \
    --tls-san=k3s.dtlab.net

curl https://kube-vip.io/manifests/rbac.yaml > /var/lib/rancher/k3s/server/manifests/kube-vip-rbac.yaml

kube-vip-rbac.yaml

apiVersion: v1
kind: ServiceAccount
metadata:
  name: kube-vip
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "true"
  name: system:kube-vip-role
rules:
  - apiGroups: [""]
    resources: ["services/status"]
    verbs: ["update"]
  - apiGroups: [""]
    resources: ["services", "endpoints"]
    verbs: ["list","get","watch", "update"]
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["list","get","watch", "update", "patch"]
  - apiGroups: ["coordination.k8s.io"]
    resources: ["leases"]
    verbs: ["list", "get", "watch", "update", "create"]
  - apiGroups: ["discovery.k8s.io"]
    resources: ["endpointslices"]
    verbs: ["list","get","watch", "update"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["list"]

---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: system:kube-vip-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:kube-vip-role
subjects:
- kind: ServiceAccount
  name: kube-vip
  namespace: kube-system


export VIP=192.168.8.40
export INTERFACE=ens33
export KVVERSION=v0.8.9

alias kube-vip="ctr image pull ghcr.io/kube-vip/kube-vip:$KVVERSION; ctr run --rm --net-host ghcr.io/kube-vip/kube-vip:$KVVERSION vip /kube-vip"

kube-vip manifest daemonset \
    --interface $INTERFACE \
    --address $VIP \
    --inCluster \
    --taint \
    --controlplane \
    --arp \
    --leaderElection

kube-vip-ds.yaml

apiVersion: apps/v1
kind: DaemonSet
metadata:
  creationTimestamp: null
  labels:
    app.kubernetes.io/name: kube-vip-ds
    app.kubernetes.io/version: v0.8.9
  name: kube-vip-ds
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: kube-vip-ds
  template:
    metadata:
      creationTimestamp: null
      labels:
        app.kubernetes.io/name: kube-vip-ds
        app.kubernetes.io/version: v0.8.9
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node-role.kubernetes.io/master
                operator: Exists
            - matchExpressions:
              - key: node-role.kubernetes.io/control-plane
                operator: Exists
      containers:
      - args:
        - manager
        env:
        - name: vip_arp
          value: "true"
        - name: port
          value: "6443"
        - name: vip_nodename
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: vip_interface
          value: ens33
        - name: vip_cidr
          value: "24"
        - name: dns_mode
          value: first
        - name: cp_enable
          value: "true"
        - name: cp_namespace
          value: kube-system
        - name: vip_leaderelection
          value: "true"
        - name: vip_leasename
          value: plndr-cp-lock
        - name: vip_leaseduration
          value: "5"
        - name: vip_renewdeadline
          value: "3"
        - name: vip_retryperiod
          value: "1"
        - name: address
          value: 192.168.18.40
        image: ghcr.io/kube-vip/kube-vip:v0.8.9
        imagePullPolicy: IfNotPresent
        name: kube-vip
        resources: {}
        securityContext:
          capabilities:
            add:
            - NET_ADMIN
            - NET_RAW
      hostNetwork: true
      serviceAccountName: kube-vip
      tolerations:
      - effect: NoSchedule
        operator: Exists
      - effect: NoExecute
        operator: Exists
  updateStrategy: {}


# Install K3S Additional Master Node

  curl -sfL https://get.k3s.io | K3S_TOKEN=TSK3SCLUSTER INSTALL_K3S_EXEC="--disable=traefik --disable=servicelb" sh -s - server \
    --server https://k3s.transcend.local:6443 \
    --tls-san=k3s.transcend.local  

# Install K3S Worker Node 

  Get K3S_TOKEN from /var/lib/rancher/k3s/server/node-token from Master Node

  curl -sfL https://get.k3s.io | K3S_TOKEN=DTK3SCLUSTER K3S_URL=https://k3s.dtlab.net:6443 sh - 

MsigDxc123#

curl -sfL https://get.k3s.io |  K3S_TOKEN=SGDXCUMASCLUSTER K3S_URL=https://sgdxcumas.msigsap.com:6443 sh -
# Setup MetalLB

# Helm installation

curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

# Adding helm repositories

helm repo add metallb https://metallb.github.io/metallb
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add csi-driver-nfs https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/charts
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml 
cp /etc/rancher/k3s/k3s.yaml .kube/config

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
  - 192.168.18.50-192.168.18.59

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

# Labelling worker nodes

node-role.kubernetes.io/worker true

# Adding node selector

    spec:
      nodeSelector: 
        node-role.kuberentes.io/master: "true"
      automountServiceAccountToken: false

# Setup Kubernetes dashboard

helm repo add kubernetes-dashboard https://kubernetes.github.io/dashboard/

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml 
helm upgrade --install kubernetes-dashboard kubernetes-dashboard/kubernetes-dashboard --create-namespace --namespace kubernetes-dashboard

kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443 --address 192.168.18.40

kubedash-lb.yaml

---
apiVersion: v1
kind: Service
metadata:
  name: kubernetes-dashboard-lb
  namespace: kubernetes-dashboard
spec:
  type: LoadBalancer
  loadBalancerIP: 172.16.8.70
  ports:
    - port: 443
      protocol: TCP
      targetPort: 8443
  selector:
    app.kubernetes.io/name: kong 
    app.kubernetes.io/instance: kubernetes-dashboard
    app.kubernetes.io/component: app

kubedash-rbac.yaml

apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard

 


# kong-ingress

helm repo add kong https://charts.konghq.com
helm install kong-ingress kong/ingress --namespace kong-ingress --create-namespace

# hello-rancher


openssl req -subj '/CN=kong.transcend.local' -new -newkey rsa:2048 -sha256 \
  -days 365 -nodes -x509 -keyout server.key -out server.crt \
  -addext "subjectAltName = DNS:kong.transcend.local" \
  -addext "keyUsage = digitalSignature" \
  -addext "extendedKeyUsage = serverAuth" 2> /dev/null;
  openssl x509 -in server.crt -subject -noout

kubectl create secret tls kong.transcend.local --namespace kubernetes-dashboard --cert=./server.crt --key=./server.key

kubectl patch --type json ingress echo -p='[{
    "op":"add",
	"path":"/spec/tls",
	"value":[{
        "hosts":["kong.transcend.local"],
		"secretName":"kong.transcend.local"
    }]
}]'

kubectl -n kubernetes-dashboard patch --type json ingress kubernetes-dashboard-ingress -p='[{
    "op":"add",
        "path":"/spec/tls",
        "value":[{
        "hosts":["kong.transcend.local"],
                "secretName":"kong.transcend.local"
    }]
}]'

# Ingress Controller

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
  loadBalancerIP: 192.168.18.51

# Rancher Setup


helm repo add jetstack https://charts.jetstack.io

kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.17.1/cert-manager.crds.yaml
helm install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace --version v1.17.1
kubectl -n cert-manager rollout status deploy/cert-manager

helm repo add rancher-stable https://releases.rancher.com/server-charts/stable

helm install rancher rancher-stable/rancher --namespace cattle-system --create-namespace --set hostname=rancher.dtlab.net --set bootstrapPassword=P@ssw0rd --set replicas=1 --version=2.10.3    
kubectl -n cattle-system rollout status deploy/rancher

rancher-lb.yaml

apiVersion: v1
kind: Service
metadata:
  annotations:
    meta.helm.sh/release-name: rancher
    meta.helm.sh/release-namespace: cattle-system
  labels:
    app: rancher
    app.kubernetes.io/managed-by: Helm
    chart: rancher-2.11.0
    heritage: Helm
    release: rancher
  name: rancher
  namespace: cattle-system
spec:
  ports:
  - name: http
    port: 80
    protocol: TCP
    targetPort: 80
  - name: https-internal
    port: 443
    protocol: TCP
    targetPort: 444
  selector:
    app: rancher
  sessionAffinity: None
  type: LoadBalancer
  loadBalancerIP: 172.16.8.71
status:
  loadBalancer: {}

# Preventing workload from running on master nodes

key=value:effect

k3s-controlplane=true:NoExecute

Sample App

rancher/hello-world
kennethreitz/httpbin

workload.user.cattle.io/workloadselector: apps.deployment-demo-hellorancher

Rafay API key

ra2.f27f8f06b5b5508877c8bddc51ac8b8531d92e54.03cb778b5ecc0c6de963e133b65d2ab65e71d34f680e9e46a779981ddda0310b