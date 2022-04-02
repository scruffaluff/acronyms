#!/usr/bin/env bash
#
# Setup dev environment.

# Exit immediately if a command exits or pipes a non-zero return code.
#
# Flags:
#   -e: Exit immediately when a command pipeline fails.
#   -o: Persist nonzero exit codes through a Bash pipe.
#   -u: Throw an error when an unset variable is encountered.
set -eou pipefail

mkdir -p certs 
mkcert \
  -cert-file certs/star_nip_io.crt \
  -key-file certs/star_nip_io.key \
  '*.nip.io'
mkcert -install

kubectl config set-context --current --namespace=kube-system

if [[ ! "$(kubectl get secret default-tls-certs 2> /dev/null)" ]]; then
  kubectl create secret tls default-tls-certs  \
    --cert certs/star_nip_io.crt \
    --key certs/star_nip_io.key
fi

# Kubectl wait does not work if the resource has not yet been created. Visit
# https://github.com/kubernetes/kubernetes/issues/83242 for more information.
while [[ ! "$(kubectl get deployment traefik 2> /dev/null)" ]]; do 
  sleep 1; 
done

kubectl apply -f chart/dev/traefik.yaml

if [[ ! "$(kubectl get namespace acronyms 2> /dev/null)" ]]; then
  kubectl create namespace acronyms
fi

kubectl config set-context --current --namespace=acronyms

if [[ ! "$(kubectl get secret acronyms 2> /dev/null)" ]]; then
  kubectl create secret generic acronyms \
    --from-literal database-password="${ACRONYMS_POSTGRES_PASSWORD?}" \
    --from-literal database-user="${ACRONYMS_POSTGRES_USER?}"
fi
