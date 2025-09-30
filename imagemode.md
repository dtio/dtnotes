podman build -t davidtio/p3checklist:0.9 .
podman login -u davidtio -v docker.io
sxxxxxxx01
podman push davidtio/p3checklist:0.9

podman build -t rhel.oru07s6lxxf9.instruqt.io:5000/test-bootc .
podman push rhel.oru07s6lxxf9.instruqt.io:5000/test-bootc

podman run --rm --privileged \
        --volume .:/output \
        --volume ./config.json:/config.json \
        --volume /var/lib/containers/storage:/var/lib/containers/storage \
        registry.redhat.io/rhel10/bootc-image-builder:10.0 \
        --type qcow2 \
        --config config.json \
         rhel.oru07s6lxxf9.instruqt.io:5000/test-bootc

Dockerfile
===
FROM registry.redhat.io/rhel10/rhel-bootc:10.0

ADD etc /etc

RUN dnf install -y httpd
RUN systemctl enable httpd
===

podman login -u davidtio -v docker.io
sxxxxxxx01

podman build -t davidtio/dtrhel10 .

config.toml
===
[[customizations.user]]
name = "dtio"
password = "F055tech"
groups = ["wheel"]
===

sudo podman pull docker.io/davidtio/dtrhel10:latest

sudo podman login

sudo podman run --rm --privileged \
        --volume .:/output \
        --volume ./config.toml:/config.toml \
        --volume /var/lib/containers/storage:/var/lib/containers/storage \
        registry.redhat.io/rhel10/bootc-image-builder:10.0 \
        --type qcow2 \
        --config config.toml \
         davidtio/dtrhel10

sudo bootc status --format yaml
sudo bootc upgrade --check
sudo bootc upgrade
sudo bootc rollback

sudo bootc switch davidtio/dtrhel10:latest
sudo bootc switch davidtio/dtrhel10:0.1
