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

  mkdir -p certs
  if [[ ! (-f certs/wildcard_nip_io.crt && -f certs/wildcard_nip_io.key) ]]; then
    mkcert \
      -cert-file certs/wildcard_nip_io.crt \
      -key-file certs/wildcard_nip_io.key \
      '*.127-0-0-1.nip.io'
  fi

  npx vite build --watch --mode development &

  acronyms \
    --host acronyms.127-0-0-1.nip.io \
    --port 8443 \
    --reload \
    --reload-delay 1.0 \
    --reload-dir backend/acronyms \
    --reload-dir dist \
    --ssl-certfile certs/wildcard_nip_io.crt \
    --ssl-keyfile certs/wildcard_nip_io.key
}

main
