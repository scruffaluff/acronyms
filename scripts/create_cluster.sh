#!/usr/bin/env bash
#
# Create local Kubernetes cluster for development.

# Exit immediately if a command exits or pipes a non-zero return code.
#
# Flags:
#   -e: Exit immediately when a command pipeline fails.
#   -o: Persist nonzero exit codes through a Bash pipe.
#   -u: Throw an error when an unset variable is encountered.
set -eou pipefail

#######################################
# Script entrypoint.
#######################################
main() {
  # Switch current directory to repository root.
  cd "$(dirname "$(dirname "$(realpath "$0")")")"


  if ! k3d cluster list acronyms &> /dev/null; then
    k3d cluster create --wait --config scripts/k3d.yaml
  fi

  mkdir -p certs
  if [[ ! (-f certs/wildcard_nip_io.crt && -f certs/wildcard_nip_io.key) ]]; then
    mkcert \
      -cert-file certs/wildcard_nip_io.crt \
      -key-file certs/wildcard_nip_io.key \
      '*.127-0-0-1.nip.io'
  fi

  if ! kubectl --namespace kube-system get secret ingress-tls-certs &> /dev/null 
  then
    kubectl --namespace kube-system create secret  \
      --cert certs/wildcard_nip_io.crt \
      --key certs/wildcard_nip_io.key \
      tls ingress-tls-certs
  fi

  # Kubectl wait does not work if the resource has not yet been created. Visit
  # https://github.com/kubernetes/kubernetes/issues/83242 for more information.
  while ! kubectl --namespace kube-system get deployment traefik &> /dev/null
  do
    sleep 1;
  done

  kubectl apply -f scripts/traefik.yaml

  if ! kubectl get namespace acronyms 2> /dev/null; then
    kubectl create namespace acronyms
  fi

  message='Local Kubernetes cluster is ready'
  printf "\n\033[1;32m%s\033[0m\n" "${message}"
}

main
