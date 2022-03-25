# Tilt configuration for local Kubernetes development.
#
# For more information, visit https://docs.tilt.dev.

local_resource("setup", "./setup.sh")
docker_build("backend", "./backend")

k8s_yaml("acronyms.yaml")

k8s_resource("backend", port_forwards=8000)
k8s_resource("postgres", port_forwards=5432)
