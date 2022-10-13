#!/usr/bin/env bash
#
# Install dependencies needed for repository development.

# Exit immediately if a command exits or pipes a non-zero return code.
#
# Flags:
#   -e: Exit immediately when a command pipeline fails.
#   -o: Persist nonzero exit codes through a Bash pipe.
#   -u: Throw an error when an unset variable is encountered.
set -eou pipefail

HELM_VERSION='3.9.2'
K3D_VERSION='5.4.6'
KUBECTL_VERSION='1.25.1'
MKCERT_VERSION='1.4.4'
TARGETARCH='amd64'

#######################################
# Install repository dependencies for Linux.
# Arguments:
#   Whether to use sudo.
#######################################
setup_linux() {
  # Install base dependencies by available package manager.
  #
  # Do not use 'command --search'. It is not portable across platforms.
  #
  # Flags:
  #   -x: Check if file exists and execute permission is granted.
  if [[ -x "$(command -v apk)" ]]; then
    ${1:+sudo} apk update
    ${1:+sudo} apk add  curl git nss-tools tar zip
  elif [[ -x "$(command -v apt-get)" ]]; then
    DEBIAN_FRONTEND=noninteractive ${1:+sudo} apt-get -qq update
    DEBIAN_FRONTEND=noninteractive ${1:+sudo} apt-get -qq install -y \
      curl git libnss3-tools tar zip
  elif [[ -x "$(command -v dnf)" ]]; then
    ${1:+sudo} dnf check-update || true
    ${1:+sudo} dnf install -y curl git nss-tools tar zip
  elif [[ -x "$(command -v pacman)" ]]; then
    ${1:+sudo} pacman -Suy --noconfirm
    ${1:+sudo} pacman -S --noconfirm curl git nss tar zip
  else
    error "Unable to find supported package manager"
  fi

  if [[ ! -x "$(command -v helm)" ]]; then
    echo "Installing Helm"
    curl -LSfs "https://get.helm.sh/helm-v${HELM_VERSION}-linux-${TARGETARCH}.tar.gz" -o /tmp/helm.tar.gz
    tar fvx /tmp/helm.tar.gz -C /tmp
    sudo install "/tmp/linux-${TARGETARCH}/helm" /usr/local/bin/
    rm -fr /tmp/helm*
  fi

  if [[ ! -x "$(command -v k3d)" ]]; then
    echo "Installing K3d"
    curl -LSfs "https://github.com/k3d-io/k3d/releases/download/v${K3D_VERSION}/k3d-linux-${TARGETARCH}" -o /usr/local/bin/k3d
    sudo chmod 755 /usr/local/bin/k3d
  fi

  if [[ ! -x "$(command -v kubectl)" ]]; then
    echo "Installing Kubectl"
    curl -LSfs "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/${TARGETARCH}/kubectl" -o /usr/local/bin/kubectl
    sudo chmod 755 /usr/local/bin/kubectl
  fi

  if [[ ! -x "$(command -v mkcert)" ]]; then
    echo "Installing Mkcert"
    curl -LSfs "https://github.com/FiloSottile/mkcert/releases/download/v${MKCERT_VERSION}/mkcert-v${MKCERT_VERSION}-linux-${TARGETARCH}" -o /usr/local/bin/mkcert
    sudo chmod 755 /usr/local/bin/mkcert
  fi

  echo "Installing Helm plugins"
  helm plugin install https://github.com/datreeio/helm-datree
}

#######################################
# Install repository dependencies for Macos.
#######################################
setup_macos() {
  # On Apple silicon, brew is not in the system path after installation.
  export PATH="/opt/homebrew/bin:${PATH}"

  # Install XCode command line tools if not already installed.
  #
  # Homebrew depends on the XCode command line tools.
  # Flags:
  #   -p: Print path to active developer directory.
  if ! xcode-select -p &> /dev/null; then
    log "Installing command line tools for XCode"
    sudo xcode-select --install
  fi

  # Install Rosetta 2 for Apple Silicon if not already installed.
  #
  # TODO: Create better check to see if Rosetta 2 is already installed.
  # Flags:
  #   -d: Check if path exists and is a directory.
  #   -p: Print machine processor name.
  if [[ "$(uname -p)" == "arm" && ! -d "/opt/homebrew" ]]; then
    softwareupdate --agree-to-license --install-rosetta
  fi

  # Install Homebrew if not already installed.
  #
  # FLAGS:
  #   -L: Follow redirect request.
  #   -S: Show errors.
  #   -f: Fail silently on server errors.
  #   -s: Disable progress bars.
  #   -x: Check if file exists and execute permission is granted.
  if [[ ! -x "$(command -v brew)" ]]; then
    log "Installing Homebrew"
    curl -LSfs "https://raw.githubusercontent.com/Homebrew/install/master/install.sh" | bash
  fi

  brew install git helm k3d kubectl mkcert nss
}

#######################################
# Install repository depdencies based on operating system.
#######################################
main() {
  local os_type
  local use_sudo=""

  # Check if user is not root.
  if [[ "${EUID}" -ne 0 ]]; then
    use_sudo=1
  fi

  # Get operating system.
  #
  # FLAGS:
  #   -s: Print the kernel name.
  os_type="$(uname -s)"

  case "${os_type}" in
    Darwin)
      setup_macos
      ;;
    Linux)
      setup_linux "${use_sudo}"
      ;;
    *)
      error "Operating system ${os_type} is not supported"
      ;;
  esac
}

main
