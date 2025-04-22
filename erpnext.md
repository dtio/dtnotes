curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3


helm repo add app-frappe https://helm.erpnext.com
helm repo update

helm upgrade --install frappe-bench --namespace erpnext --create-namespace app-frappe/erpnext -f erpnext-values.yaml

# erpnext-values.yaml

persistence:
  enabled: true
  worker:
    storageClass: local-path
    accessModes:
      - ReadWriteOnce
  size: 8Gi
worker:
  gunicorn: 
    replicaCount: 1
    service:
      type: ClusterIP
      port: 8000
  default:
    replicaCount: 1
  short: 
    replicaCount: 1
  long: 
    replicaCount: 1
  scheduler:
    replicaCount: 1
  socketio:
    replicaCount: 1
    service:
      type: ClusterIP
      port: 9000
jobs:
  createSite:
    enabled: true
    siteName: "en.fosstech.biz"
    adminPassword: "secret"
ingress:
  enabled: true
  ingressName: "erpnext-ingress"
  hosts:
  - host: en.fosstech.biz
    paths:
    - path: /
      pathType: ImplementationSpecific
  tls:
   - secretName: tls-ingress-erpnext
     hosts:
       - en.fosstech.biz

Default username: Administrator
Default password: secret

# Logging in to bench

kubectl exec -it -n erpnext frappe-bench-erpnext-worker-d-889597b7d-qk2bb -- /bin/bash

# Backup

bench --site en.fosstech.biz backup --with-files

# Restore

bench --site en.fosstech.biz restore 20250417_165315-frontend-database.sql.gz --with-public-files 20250417_165315-frontend-files.tar --with-private-files 20250417_165315-frontend-private-files.tar --force

Default mysql password: changeit

bench --site en.fosstech.biz migrate



