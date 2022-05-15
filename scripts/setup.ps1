# If unable to execute due to policy rules, run                                                                                                                                          
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser.

#Requires -RunAsAdministrator

# Exit immediately if a PowerShell Cmdlet encounters an error.
$ErrorActionPreference = 'Stop'

# Script entrypoint.
Function Main() {
    $RepoPath = Split-Path "$PSScriptRoot" -Parent

    k3d cluster list scruffabum 2>&1 | Out-Null
    If ($LastExitCode) {
        k3d cluster create --wait --config "$RepoPath/scripts/k3d.yaml"
    }

    mkdir -Force "$RepoPath/certs"
    mkcert -install
    mkcert `
        -cert-file "$RepoPath/certs/star_nip_io.crt" `
        -key-file "$RepoPath/certs/star_nip_io.key" `
        '*.127-0-0-1.nip.io'

    kubectl --namespace kube-system get secret default-tls-certs 2>&1 | Out-Null
    If ($LastExitCode) {
        kubectl --namespace kube-system create secret `
            --cert "$RepoPath/certs/star_nip_io.crt" `
            --key "$RepoPath/certs/star_nip_io.key" `
            tls default-tls-certs
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

    kubectl --namespace acronyms get secret acronyms 2>&1 | Out-Null
    If ($LastExitCode) {
        kubectl --namespace acronyms create secret generic acronyms `
            --from-literal database-password="$Env:ACRONYMS_POSTGRES_PASSWORD" `
            --from-literal database-user="$Env:ACRONYMS_POSTGRES_USERNAME"
    }

    Write-Output 'Development environment is ready'
}

Main
