# If unable to execute due to policy rules, run                                                                                                                                          
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser.

#Requires -RunAsAdministrator

# Exit immediately if a PowerShell Cmdlet encounters an error.
$ErrorActionPreference = 'Stop'

# Script entrypoint.
Function Main() {
    Set-Location "$(Split-Path "$PSScriptRoot" -Parent)"

    k3d cluster list scruffabum 2>&1 | Out-Null
    If ($LastExitCode) {
        k3d cluster create --wait --config scripts/k3d.yaml
    }

    mkdir -Force "$RepoPath/certs"
    mkcert -install
    mkcert `
        -cert-file certs/wildcard_nip_io.crt `
        -key-file certs/wildcard_nip_io.key `
        '*.127-0-0-1.nip.io'

    kubectl --namespace kube-system get secret ingress-tls-certificate 2>&1 | Out-Null
    If ($LastExitCode) {
        kubectl --namespace kube-system create secret `
            --cert certs/wildcard_nip_io.crt `
            --key certs/wildcard_nip_io.key `
            tls ingress-tls-certificate
    }

    # Kubectl wait does not work if the resource has not yet been created. Visit
    # https://github.com/kubernetes/kubernetes/issues/83242 for more
    # information.
    kubectl --namespace kube-system get deployment traefik 2>&1 | Out-Null
    While ($LastExitCode) {
        Start-Sleep -Seconds 1
        kubectl --namespace kube-system get deployment traefik 2>&1 | Out-Null
    }

    kubectl apply -f scripts/traefik.yaml

    kubectl get namespace acronyms 2>&1 | Out-Null
    If ($LastExitCode) {
        kubectl create namespace acronyms
    }

    Write-Output 'Local Kubernetes cluster is ready'
}

Main
