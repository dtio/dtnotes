# Create let's encrypt cert

certbot certonly --manual -d '*.dtio.app'  --agree-tos --preferred-challenges dns-01 -m  davidtio@fosstech.biz  --server https://acme-v02.api.letsencrypt.org/directory

# Add CA cert to RHEL system

copy ca cert to /etc/pki/ca-trust/source/anchors/
update-ca-trust extractt

# Adding local-path-provisoner

Path is /opt/local-path-provisioner

kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.31/deploy/local-path-storage.yaml

