# Tilt configuration for local Kubernetes development.
#
# For more information, visit https://docs.tilt.dev.

docker_build(
    "scruffaluff/acronyms",
    ".",
    dockerfile="Dockerfile.dev",
    live_update=[
        sync("./backend", "/app/backend"),
        sync("./frontend", "/app/frontend"),
    ],
)

yaml = helm(
    "./chart",
    name="acronyms",
    namespace="acronyms",
    values=["./chart/values_local.yaml"],
)
k8s_yaml(yaml)
