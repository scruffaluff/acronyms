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

  # Build once so that files are guaranteed to exist before backend starts.
  npm run build -- --mode development
  poetry run acronyms \
    --reload \
    --reload-dir backend/acronyms &

  # Sleeping for 1 second prevents vite from making folder "dist/assets"
  # temporarily unavailable to the backend server.
  sleep 1
  npx vite build --watch --mode development
}

main
