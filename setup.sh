#!/usr/bin/env bash

set -eou pipefail

mkdir -p certs 
mkcert \
  -cert-file certs/star_nip_io.crt \
  -key-file certs/star_nip_io.key \
  '*.nip.io'
mkcert -install

kubectl create secret tls default-tls-certs  \
  --cert certs/star_nip_io.crt \
  --key certs/star_nip_io.key \
  --namespace kube-system

kubectl apply -f manifests/default_tls.yaml
