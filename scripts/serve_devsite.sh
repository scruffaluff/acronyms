#!/usr/bin/env bash
#
# Spawns development server with reloading on file changes.

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
      127-0-0-1.nip.io
  fi

  # Build once so that files are guaranteed to exist before backend starts.
  npm run build -- --mode development
  poetry run acronyms \
    --host 127-0-0-1.nip.io \
    --reload \
    --reload-dir backend/acronyms \
    --ssl-certfile certs/wildcard_nip_io.crt \
    --ssl-keyfile certs/wildcard_nip_io.key &

  # Sleeping for 1 second prevents vite from making folder "dist/assets"
  # temporarily unavailable to the backend server.
  sleep 1
  npm run build -- --watch --mode development
}

main
