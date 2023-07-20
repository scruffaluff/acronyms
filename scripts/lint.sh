#!/usr/bin/env bash
#
# Execute all linter checks.

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

  poetry run black --check .
  poetry run ruff check .
  poetry run mypy .

  pnpm format:test
  pnpm lint:test
  pnpm typecheck

  helm lint --strict src/chart
}

main
