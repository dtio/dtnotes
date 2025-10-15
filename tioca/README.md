podman build -t davidtio/tioca:0.1 .
podman login docker.io
davidtio
sxxxxxxxx1
podman push davidtio/tioca:0.1

podman run --name tioca -d --rm -v ./instance:/app/instance:Z -p 5000:5000 davidtio/tioca:0.1
