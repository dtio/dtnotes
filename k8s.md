# Jumphost

RDP to 10.138.55.45

Id: 10.138.55.45\transcend_admin

Pwd: Welcome10*

# Prereq

# sysctl params required by setup, params persist across reboots
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF

# Apply sysctl params without reboot
sudo sysctl --system

# Install containerd

dnf install containerd.io

# Create containerd configuration

containerd config default > /etc/containerd/config.toml

sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml

systemctl restart containerd

# Disable swap

swapoff -a
sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# Installation of K8tools

sudo setenforce 0
sudo sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config

# This overwrites any existing configuration in /etc/yum.repos.d/kubernetes.repo
cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.32/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.32/rpm/repodata/repomd.xml.key
exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
EOF

sudo yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes

sudo systemctl enable --now kubelet

kubeadm init --pod-network-cidr=172.18.0.0/16 --control-plane-endpoint "sgdxcumas.msigsap.com:6443"

kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.29.3/manifests/tigera-operator.yaml

curl https://raw.githubusercontent.com/projectcalico/calico/v3.29.3/manifests/custom-resources.yaml -O

Update the correct pod_cidr value

kubectl create -f custom-resources.yaml

# Joining other nodes 

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

  export KUBECONFIG=/etc/kubernetes/admin.conf

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

You can now join any number of control-plane nodes by copying certificate authorities
and service account keys on each node and then running the following as root:

  kubeadm join sgdxcumas.msigsap.com:6443 --token gl3keu.hh7xasgdeyggrit9 \
        --discovery-token-ca-cert-hash sha256:aca04f5eea4f950f5f853aab998920f2ad1336f4d864c8e3bae6525dfc8d61c7 \
        --control-plane

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join sgdxcumas.msigsap.com:6443 --token gl3keu.hh7xasgdeyggrit9 \
        --discovery-token-ca-cert-hash sha256:aca04f5eea4f950f5f853aab998920f2ad1336f4d864c8e3bae6525dfc8d61c7

# Adding NFS Storage

helm repo add csi-driver-nfs https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/charts

helm install csi-driver-nfs csi-driver-nfs/csi-driver-nfs --namespace kube-system --version 4.11.0

sc-sgdxcunfs.yaml

    apiVersion: v1
    items:
    - allowVolumeExpansion: true
      apiVersion: storage.k8s.io/v1
      kind: StorageClass
      metadata:
        annotations:
          storageclass.kubernetes.io/is-default-class: "true"
        name: sc-sgdxcunfs
      parameters:
        server: sgdxcunfs
        share: /nfs
      provisioner: nfs.csi.k8s.io
      reclaimPolicy: Retain
      volumeBindingMode:

kubectl apply -f sc-sgdxcunfs.yaml


kubectl patch storageclass sc-sgdxcunfs -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

# Setup sgdxcnpdepl

kubeadm init --pod-network-cidr=172.28.0.0/16 --control-plane-endpoint "sgdxnpdepl.msigsap.com:6443"

kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.29.3/manifests/tigera-operator.yaml

curl https://raw.githubusercontent.com/projectcalico/calico/v3.29.3/manifests/custom-resources.yaml -O

You can now join any number of control-plane nodes by copying certificate authorities
and service account keys on each node and then running the following as root:

  kubeadm join sgdxnpdepl.msigsap.com:6443 --token 1e31mi.ecp3lyk6ksk3ihld \
        --discovery-token-ca-cert-hash sha256:716cd46e1ac35d2fe47d08144c58b304e20264dd1bfc913003c830b6ea04752f \
        --control-plane

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join sgdxnpdepl.msigsap.com:6443 --token 1e31mi.ecp3lyk6ksk3ihld \
        --discovery-token-ca-cert-hash sha256:716cd46e1ac35d2fe47d08144c58b304e20264dd1bfc913003c830b6ea04752f

# Setup Metal LB

helm repo add metallb https://metallb.github.io/metallb

helm install metallb metallb/metallb --namespace metallb-system --create-namespace

For single node, remove the taint

kubectl taint nodes --all node-role.kubernetes.io/control-plane-

metallb-pool.yaml

    # Metallb address pool
    apiVersion: metallb.io/v1beta1
    kind: IPAddressPool
    metadata:
      name: cluster-pool
      namespace: metallb-system
    spec:
      addresses:
      # VIP IP Address Pool
      - 10.138.55.50/32


    ---
    # L2 configuration
    apiVersion: metallb.io/v1beta1
    kind: L2Advertisement
    metadata:
      name: metallb-k3s
      namespace: metallb-system
    spec:
      ipAddressPools:
      - cluster-pool

# Adding ingress controller

helm install <name> ingress-nginx/ingress-nginx --namespace <name>-nginx-ingress --create-namespace  --set ingressClass=<name>-nginx --set controller.ingressClassResource.name=<name>-nginx

kubectl patch svc <name>-ingress-nginx-controller -n pas-nginx-ingress -p '{"spec": {"loadBalancerIP":"10.138.55.50"}}' 

      
