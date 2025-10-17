podman build -t davidtio/tiokube:0.1 .
podman login docker.io
davidtio
sxxxxxxxx1
podman push davidtio/tiokube:0.1

podman run --name tiokube -d --rm -v ./data:/app/data:Z -p 5000:5000 davidtio/tiokube:0.1
