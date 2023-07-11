# Tilt configuration for local Kubernetes development.
#
# For more information, visit https://docs.tilt.dev.

docker_build(
    "scruffaluff/acronyms",
    ".",
    dockerfile="scripts/develop.dockerfile",
    live_update=[
        sync("./src/acronyms", "/app/src/acronyms"),
        sync("./src/frontend", "/app/src/frontend"),
    ],
)

yaml = helm(
    "./src/chart",
    name="acronyms",
    namespace="acronyms",
    values=["./scripts/values.yaml"],
)
k8s_yaml(yaml)
