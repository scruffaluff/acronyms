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

if [[ ! "$(kubectl -n kube-system get secret default-tls-certs)" ]]; then
  kubectl --namespace kube-system \
    create secret tls default-tls-certs  \
    --cert certs/star_nip_io.crt \
    --key certs/star_nip_io.key
fi

kubectl apply -f chart/dev.yaml

if [[ ! "$(kubectl get namespace acronyms)" ]]; then
  kubectl create namespace acronyms
fi

if [[ ! "$(kubectl -n acronyms get secret acronyms)" ]]; then
  kubectl --namespace acronyms \
    create secret generic acronyms \
    --from-literal database-password="${ACRONYMS_POSTGRES_PASSWORD?}" \
    --from-literal database-user="${ACRONYMS_POSTGRES_USER?}"
fi
