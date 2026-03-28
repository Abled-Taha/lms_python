#!/bin/sh

get_linux_distro() {
    # Check if the standard /etc/os-release file exists and source it
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        # The 'ID' variable contains a single-word identifier (e.g., ubuntu, fedora, centos)
        echo "$ID"
    else
        # Fallback for older or non-standard systems (e.g., using lsb_release if available)
        if command -v lsb_release &> /dev/null; then
            lsb_release -si | tr '[:upper:]' '[:lower:]'
        else
            echo "unknown"
        fi
    fi
}

command_exists() {
  command -v -- "$1" >/dev/null 2>&1
}

DISTRO=$(get_linux_distro)

cp ./.env.template ./.env
read -n 1 -r -s -p $"Kindly verify the entries in '.env' file in the project directory, then press any key to continue.\n" key

case "$DISTRO" in
    nixos)
        echo "Running on NixOS"
        nix develop --command sh -c "mise install && mise run setup && echo 'All setup complete'"
	exit 0
        ;;
    *)
        echo "Running on Linux"
        if command_exists mise; then
        echo "'mise' is available. Proceeding..."
        else
        echo "'mise' is not installed. Please install it to continue." >&2
        exit 1
        fi
        mise install
        mise run setup
        echo 'All setup complete'
    exit 0
        ;;
esac

