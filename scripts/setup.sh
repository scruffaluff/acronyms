#!/usr/bin/env bash
#
# Create local Kubernetes cluster for development.

# Exit immediately if a command exits or pipes a non-zero return code.
#
# Flags:
#   -E: Inheret trap on ERR signal for all functions and sub shells.
#   -e: Exit immediately when a command pipeline fails.
#   -o: Persist nonzero exit codes through a Bash pipe.
#   -u: Throw an error when an unset variable is encountered.
set -Eeou pipefail

#######################################
# Notify user if unexpected error with diagnostic information.
#
# Line number reporting will only be highest calling function for earlier
# versions of Bash.
#######################################
handle_panic() {
  local bold_red="\033[1;31m"
  local default="\033[0m"

  message="$0 panicked on line $2 with exit code $1"
  printf "${bold_red}error${default}: %s\n" "${message}" >&2
}

#######################################
# Script entrypoint.
#######################################
main() {
  repo_path="$(dirname "$(dirname "$(realpath "$0")")")"

  if ! k3d cluster list acronyms &> /dev/null; then
    k3d cluster create --wait --config "${repo_path}/scripts/k3d.yaml"
  fi

  mkdir -p "${repo_path}/certs"
  mkcert \
    -cert-file "${repo_path}/certs/star_nip_io.crt" \
    -key-file "${repo_path}/certs/star_nip_io.key" \
    '*.127-0-0-1.nip.io'

  if ! kubectl --namespace kube-system get secret default-tls-certs &> /dev/null 
  then
    kubectl --namespace kube-system create secret  \
      --cert "${repo_path}/certs/star_nip_io.crt" \
      --key "${repo_path}/certs/star_nip_io.key" \
      tls default-tls-certs
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

  if ! kubectl --namespace acronyms get secret acronyms 2> /dev/null; then
    kubectl --namespace acronyms create secret generic acronyms \
      --from-literal database-password="${ACRONYMS_POSTGRES_PASSWORD?}" \
      --from-literal database-user="${ACRONYMS_POSTGRES_USERNAME?}"
  fi

  message='Development environment is ready'
  printf "\n\033[1;32m%s\033[0m\n" "${message}"
}

main
