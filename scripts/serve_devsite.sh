#!/usr/bin/env bash
#
# Spin up development server.

# Exit immediately if a command exits or pipes a non-zero return code.
#
# Flags:
#   -e: Exit immediately when a command pipeline fails.
#   -o: Persist nonzero exit codes through a Bash pipe.
#   -u: Throw an error when an unset variable is encountered.
set -eou pipefail

ACRONYMS_RESET_TOKEN="$(openssl rand -base64 32)"
export ACRONYMS_SMTP_HOST='localhost'
ACRONYMS_SMTP_PASSWORD="$(openssl rand -base64 16)"
export ACRONYMS_SMTP_PORT='1025'
export ACRONYMS_SMTP_TLS='false'
export ACRONYMS_SMTP_USERNAME='admin@acronyms.127-0-0-1.nip.io'
ACRONYMS_VERIFICATION_TOKEN="$(openssl rand -base64 32)"
export ACRONYMS_RESET_TOKEN
export ACRONYMS_SMTP_PASSWORD
export ACRONYMS_VERIFICATION_TOKEN

# Ensure that Javascript assests are available when backend first starts.
npx vite build --mode development

npx concurrently --kill-others --names 'backend,email,frontend' \
  'poetry run acronyms --reload --reload-dir src/acronyms' \
  "maildev --incoming-user ${ACRONYMS_SMTP_USERNAME} --incoming-pass ${ACRONYMS_SMTP_PASSWORD}" \
  'vite build --watch --mode development'
