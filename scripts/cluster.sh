#!/usr/bin/env bash
#
# Kubernetes cluster management.

# Exit immediately if a command exits or pipes a non-zero return code.
#
# Flags:
#   -e: Exit immediately when a command pipeline fails.
#   -o: Persist nonzero exit codes through a Bash pipe.
#   -u: Throw an error when an unset variable is encountered.
set -eou pipefail

#######################################
# Show CLI help information.
# Outputs:
#   Writes help information to stdout.
#######################################
usage() {
  case "$1" in
    create)
      cat 1>&2 << EOF
Cluster create
Create Kubernetes cluster

USAGE:
    cluster.sh create [OPTIONS] ENVIRONMENT

OPTIONS:
    -h, --help      Print help information
EOF
      ;;
    delete)
      cat 1>&2 << EOF
Cluster delete
Delete Kubernetes cluster

USAGE:
    cluster.sh delete [OPTIONS] ENVIRONMENT

OPTIONS:
    -h, --help      Print help information
EOF
      ;;
    deploy)
      cat 1>&2 << EOF
Cluster deploy
Deploy Helm chart to Kubernetes cluster

USAGE:
    cluster.sh deploy [OPTIONS] ENVIRONMENT

OPTIONS:
    -h, --help      Print help information
EOF
      ;;
    main)
      cat 1>&2 << EOF
Cluster
Kubernetes cluster manager

USAGE:
    cluster.sh [OPTIONS] [SUBCOMMAND]

OPTIONS:
    -h, --help      Print help information

SUBCOMMANDS:
    create          Boostrap install computer software
    delete          Generate Bootware configuration file
    deploy          Deploy Helm chart to cluster
EOF
      ;;
    *)
      echo "No such usage option '$1'"
      ;;
  esac
}

#######################################
# Deploy Helm chart to local K3D Kubernetes cluster.
#######################################
deploy_cluster() {
  image='registry.localhost:5001/scruffaluff/acronyms:0.1.0'
  docker build --tag "${image}" .
  docker push "${image}"

  helm --namespace acronyms upgrade --install --values scripts/acronyms.yaml \
    acronyms ./src/chart

  kubectl --namespace acronyms wait \
    --for=condition=ready pods \
    --selector=app.kubernetes.io/name=acronyms \
    --timeout=300s

  message='Helm release is deployed to local K3d Kubernetes cluster'
  printf "\n\033[1;32m%s\033[0m\n" "${message}"
}

#######################################
# Setup local K3D Kubernetes cluster.
#######################################
create_cluster() {
  local message

  if ! k3d cluster list acronyms &> /dev/null; then
    k3d cluster create --wait --config scripts/k3d.yaml
  fi

  if ! kubectl get namespace acronyms 2> /dev/null; then
    kubectl create namespace acronyms
  fi

  mkdir -p certs
  if [[ ! (-f certs/wildcard_nip_io.crt && -f certs/wildcard_nip_io.key) ]]; then
    mkcert \
      -cert-file certs/wildcard_nip_io.crt \
      -key-file certs/wildcard_nip_io.key \
      '*.127-0-0-1.nip.io'
  fi

  if ! kubectl --namespace acronyms get secret ingress-tls-certificate &> /dev/null 
  then
    kubectl --namespace kube-system create secret  \
      --cert certs/wildcard_nip_io.crt \
      --key certs/wildcard_nip_io.key \
      tls ingress-tls-certificate

    kubectl --namespace acronyms create secret  \
      --cert certs/wildcard_nip_io.crt \
      --key certs/wildcard_nip_io.key \
      tls ingress-tls-certificate
  fi

  # Kubectl wait does not work if the resource has not yet been created. Visit
  # https://github.com/kubernetes/kubernetes/issues/83242 for more information.
  while ! kubectl --namespace kube-system get deployment traefik &> /dev/null
  do
    sleep 1;
  done

  kubectl apply --filename scripts/traefik.yaml

  helm repo add mailu https://mailu.github.io/helm-charts
  helm --namespace kube-system upgrade --install --values scripts/mailu.yaml \
    mailu mailu/mailu

  message='Local Kubernetes cluster is ready'
  printf "\n\033[1;32m%s\033[0m\n" "${message}"
}

#######################################
# Destroy local K3D Kubernetes cluster.
#######################################
delete_cluster() {
  local message

  if k3d cluster list acronyms &> /dev/null; then
    k3d cluster delete  acronyms
  fi

  message='Local K3D Kubernetes cluster is destroyed'
  printf "\n\033[1;32m%s\033[0m\n" "${message}"
}

#######################################
# Script entrypoint.
#######################################
main() {
  local command

  # Switch current directory to repository root.
  cd "$(dirname "$(dirname "$(realpath "$0")")")"

  if [[ "${1:-}" =~ ^(-h|--help)$ ]]; then
    usage 'main'
    exit 0
  elif [[ "${2:-}" =~ ^(-h|--help)$ ]]; then
    usage "${1}"
    exit 0
  else
    command="${1?Subcommand is required}"
  fi

  "${command}_cluster"
}

# Only run main if invoked as script. Otherwise import functions as library.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
