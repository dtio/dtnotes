Setup

4 vCPU
8 GB RAM
Storage: 
- 20 GB (OS)
- 30 GB (Data)

Install fuse-overlayfs and acl



> sudo dnf install podman fuse-overlayfs acl

> sudo setfacl -R -m u:dtio:rx /var/lib/containers/storage

Create .config/containers/storage.conf


[storage]
driver = "overlay" 

[storage.options]
additionalimagestores=["/var/lib/containers/storage"]

[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"



To pull image

> sudo podman pull nginx



To run image

 >  podman run -d --rm -p 8080:80 --name dtnginx nginx

> podman ps -a

> curl localhost:8080

> podman stop dtnginx



You might want to disable firewalld as well














podman login -u davidtio -v docker.io
podman tag p3checklist:0.1 davidtio/p3checklist:0.1
podman push davidtio/p3checklist:0.1
