Update config.yaml

apiVersion: radm.k8s.io/v1beta1
kind: InitConfiguration
metadata:
  name: RafayAirGapController
spec:
  blueprintVersion: v3  # Use v2 for v2 controller
  networking:         # Interface for core traffic. Default picks primary interface.
    #interface: ens3
    custom-cni-spec-file: ""
    pod-cidr: "10.224.0.0/16"  #change for custom pod CIDR
  deployment:
    type: "airgap"	  # Supports "airgap", "EKS", "GKE" and "AKS".
    ha: false
    size: "M"          # Supports "S","M" and "L".
  backup_restore:
    enabled: false 
    restore: false 
    schedule: "0 0 * * *" #Update with corn experession "*/10 * * * * " for scheduled backup
    bucketName: "" #Storage container name(Bucket Name)
    retentionPeriod : "168h0m0s" #Retention Days for backup
    restoreFolderName: "" # When restore is true update with latest backup name
    resticEnable: false  #Enable to take restic backups
    snapshotsEnabled: false #Enable to take restic snapshots
    region: ""
    # External Blob Storage credentials (must be base64 encoded)
    externalBlobStorage:                   
      username: ""     # Base64 encoded access key ID (username)
      password: ""     # Base64 encoded secret access key (password)
      endpoint: ""     # External Blob Storage endpoint URL https://<backupstorage.example.com>:9000 or http://<Storage_IP>:9000
  proxy:
    host: ""
    ip: ""
    port: 
    no-proxy: "" 
  monitoring:                              # For external monitoring infra using AMP
    integrations:
      alerting:
        slack_url: ""   # Add Slack webhook Url "https://hooks.slack.com/services/xxxxxxxxxxxxxxxxxxxxxxxxxx"
        notification: false  
      external_logging:
        enabled: false
        endpoint: ""
        port: "9200"
        user_name: ""
        user_password: ""  #use the base64 encoded value
      external_metrics:
        enabled: false
  cert-manager:
    external: false
  metrics-server:
    external: false  
  efs-driver:
    external: false 
  alb-controller:
    external: false
  openbao:
    enabled: true
  grafana:
    smtp:
      enabled: false                        # Enable or disable SMTP for Grafana
      fromAddress: "alerts@domain.com"      # Email address that sends the alerts
      fromName: "Grafana SMTP"              # Display name for alert emails
      host: "smtp.test.com:587"             # SMTP server and port (e.g., Gmail, SES)
      user: "smtp@gmail.com"                # Username for SMTP authentication
      password: "Y2hhbmdlcGx6"              # Base64-encoded password or secret reference
  vault:
    enabled: false
    address: ""
    vault_namespace: admin   
    external_service_configs:
      - elasticsearch: 
          enable: true
          secret_mount_path: "secret"
          secret_path: "elasticsearch/config"        
  engine_api:
    blob_provider: "s3"
    blob_bucket: "engine-objects"
    region: "us-west-2"
  external_blob_storage:        # False, if storing EM and cost metrics in minio
    enabled: false
  tsdb_backup:
    enabled: false
    bucket_region: ""      
  cost_metrics:
    enabled: false
    # Provide InfluxDB Write Endpoint as "<NodeIP>:9096". Example: "129.146.20.21:9096"
    # If using LoadBalancer, provide the LoadBalancer IP or endpoint.
    db_write_endpoint: ""
    # Provide InfluxDB Read Endpoint as "<NodeIP>:8086". Example: "129.146.20.21:8086"
    # If service is LoadBalancer, provide the DB Relay service LoadBalancer endpoint.
    db_read_endpoint: ""
    # Use "LoadBalancer/hostPort" of InfluxDB service. 
    db_service_type: "hostPort"
  namespace_labels:      #add all the labels "key: value" pairs below  
    Owner: Rafay   
  pod_tolerations:       #add all the requried pod tolerations below
    enable: false        # set to true to apply pod tolerations
    tolerations:
      - key: ""
        operator: ""
        value: ""
        effect: ""
      - key: ""
        operator: ""
        value: ""
        effect: ""
      # Add more tolerations as needed
  repo:
    archive-directory: /root/archive
    unarchive-path: /tmp
    rafay-registry:
      type: ""
      registry-subpath: "rafay"
      registry-archive:
        file: rafay-registry.tar.gz
      ecr:
        aws-irsa-role: ""
        aws-region: ""
        aws-ecr-endpoint: ""
      jfrog:
        user_name: ""
        password: ""
        endpoint: ""
        insecure: false  
    infra-archive:
      images-file: "rafay-infra-images.tar.gz"
    dep-archive:
    - name: istio-1.22.2
      file: istio-1.22.2-blueprint.tar.gz
      images-file-v3: "rafay-istio-1.22.2-images.tar.gz"
    - name: istio-1.16.7
      file: istio-1.16.7-blueprint.tar.gz
      images-file-v2: "rafay-istio-1.16.7-images.tar.gz"
    - name: rafay-dep
      file: rafay-dep.tar.gz
      images-file-v2: "rafay-dep-images-v2.tar.gz"
      images-file-v3: "rafay-dep-images-v3.tar.gz"
    app-archive:
    - name: rafay-core
      file: rafay-core.tar.gz
      images-file: "rafay-core-images.tar.gz"
    cluster-images-archive:
    - name: rafay-cluster-images
      file: rafay-cluster-images.tar.gz
    cluster-assets-archive:  
    - name: rafay-cluster-assets
      file: rafay-cluster-assets.tar.gz      
  app-config:
    generate-self-signed-certs: true         # TRUE creates self-signed certs for all controller endpoints. FALSE will use certs updated at console-certificates.certificate
    console-certificates:                    # add the wildcard cert for the star-domain only when generate-self-signed-certs is false.
      certificate: ""
      key: ""
    super-user:
      user: admin@rafay.co
      password: Y2hhbmdlMTIz               # Provide the password as a base64-encoded value without extra spaces; you can encode it using https://www.base64encode.org/. 
    partner:
      star-domain: "*.rafay.transcend.local" # Provide the wildcard DNS fqdn for the rafay controller
      name:  Rafay Airgap
     #logo: /logo.png             # Display logo in UI, Default picks rafay logo
      product-name: Rafay SelfHosted Product
      help-desk-email: helpdesk@rafay.co
      notifications-email: notify@rafay.co
  override-config:
    global.secrets.tsdb.gke.storage_account_key: ""  # base64 encoded value of Service account Json 
    global.enable_hosted_dns_server: "false"
    global.external_lb: "false"
    global.use_instance_role: "false"                  # True when controller uses its own IAM role for provisioning clusters.
    global.edge.irsa_role_enabled: "false"
    global.edge.irsa_role_arn: ""
    global.secrets.aws_account_id: "0123456789"       # Used for AWS IAM role based cluster provisioning, Add below secrets after encoding it with Base64.
    global.secrets.aws_access_key_id: "ZHVtbXk="
    global.minReplicaCount: ""
    global.secrets.aws_secret_access_key: "ZHVtbXk="
    global.eaas_api_github_access_token: ""
    global.issuer_name: "" # Custom issuer name
    # Below path "/data" is customisable as per the extra parition created.
    localprovisioner.basePath: "/data/local2"
    core-registry-path: "/data/registry"
    etcd-path: "/data/etcd"


radm init --config config.yaml
radm dependency --config config.yaml

Your Rafay control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) -R $HOME/.kube

Check for the pods to come up using command
  kubectl get po -A 
  You can install rafay dependency application by running command
  sudo radm dependency --config config.yaml

Then you can join any number of worker nodes by running the following on each as root:

radm join 192.168.18.101:6443 --token aj9q81.vx39ut9sdp1x6uns \
    --discovery-token-ca-cert-hash sha256:10b5a088de59041a90c11e8c11aea2ba573faa0b77fbb73f09c06ad5ad7cb8c8  --config config.yaml
