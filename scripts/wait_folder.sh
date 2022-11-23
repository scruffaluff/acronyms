#!/usr/bin/env bash
#
# Waits until frontend assets are ready for the backend server.

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

  # Frontend clears dist folder and rebuilds assets during each compile. There
  # is a small time window where the assets exist before the frontend clears
  # the dist folder. Sleeping for 1 second ensures the wait loop begins after
  # the dist folder has been cleared.
  sleep 1

  until [[ -d 'dist/assets' ]]; do
    sleep 1
  done
}

main
