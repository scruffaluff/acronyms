# Tilt configuration for local Kubernetes development.
#
# For more information, visit https://docs.tilt.dev.

local_resource("setup", "./chart/dev/setup.sh")

docker_build(
    "scruffaluff/acronyms-backend",
    "./backend",
    dockerfile="backend/Dockerfile.dev",
    live_update=[
        sync("./backend/src", "/repo/src")
    ],
)
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
    values=["./chart/dev/values.yaml"],
)
k8s_yaml(yaml)
