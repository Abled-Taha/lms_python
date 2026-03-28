{
  description = "Development environment for Nix Users";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            mise
            cacert
            # Add system dependencies needed for node-gyp or native modules here
            # e.g., python3, pkg-config, libvips
          ];

          shellHook = ''
            # SSL/TLS libraries to the Nix-provided certificates
            export SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt

            # This ensures mise-installed tools are available in the PATH
            eval "$(mise activate bash)"

            echo "Nix shell loaded: mise is now available."
          '';
        };
      });
}
