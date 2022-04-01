# Tilt configuration for local Kubernetes development.
#
# For more information, visit https://docs.tilt.dev.

local_resource("setup", "./dev.sh")
docker_build("scruffaluff/acronyms-backend", "./backend")
docker_build(
    "scruffaluff/acronyms-frontend",
    "./frontend",
    dockerfile="frontend/Dockerfile.dev",
    live_update=[
        sync("./frontend/src", "/repo/src")
    ],
)

yaml = helm(
    "./chart",
    name="acronyms",
    namespace="acronyms",
    values=["./chart/values_dev.yaml"],
)
k8s_yaml(yaml)
