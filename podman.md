podman login -u davidtio -v docker.io
podman tag p3checklist:0.1 davidtio/p3checklist:0.1
podman push davidtio/p3checklist:0.1
