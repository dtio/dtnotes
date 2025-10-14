Bastion Setup

update dns 

tsbastion01.transcend.local to 192.168.18.31

# mirror registry

Download mirror registry software
https://console.redhat.com/openshift/downloads#tool-mirror-registry

    # ./mirror-registry install tsbastion01.transcend.local --quayRoot /data
 
INFO[2025-06-05 11:56:23] Quay is available at https://tsbastion01.transcend.local:8443 with credentials (init, 7ptiUdvCEPFBJ340aG9ST8L6Q15WIz2u) 

    # podman login -u init -p 7ptiUdvCEPFBJ340aG9ST8L6Q15WIz2u tsbastion01.transcend.local:8443 --tls-verify=false
    Login Succeeded!

https://docs.redhat.com/en/documentation/openshift_container_platform/4.14/html/disconnected_installation_mirroring/installing-mirroring-installation-images

# vCenter CA Trust

curl -k -O https://tsvcenter.transcend.local/certs/download.zip
unzip download.zip
sudo cp certs/lin/* /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust extract

