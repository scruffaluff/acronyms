# Tilt configuration for local Kubernetes development.
#
# For more information, visit https://docs.tilt.dev.

local_resource("setup", "./scripts/create_cluster.sh")

docker_build(
    "scruffaluff/acronyms",
    ".",
    dockerfile="Dockerfile",
    # live_update=[
    #     sync("./backend", "/repo/src"),
    #     sync("./frontend", "/repo/src"),
    # ],
)

yaml = helm(
    "./chart",
    name="acronyms",
    namespace="acronyms",
    values=["./chart/values_local.yaml"],
)
k8s_yaml(yaml)
