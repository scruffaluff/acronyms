# Tilt configuration for local Kubernetes development.
#
# For more information, visit https://docs.tilt.dev.

local_resource("setup", "./setup.sh")
docker_build("acronyms-backend", "./backend")

k8s_yaml("acronyms.yaml")
