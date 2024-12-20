# actually, nix run isn't working, idk how to fix it, maybe look at something like:
# https://github.com/snowfallorg/nix-software-center/blob/main/flake.nix

{
  inputs = {
    # Default nixpkgs (unstable)
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    # Systems input for multi-system builds
    systems.url = "github:nix-systems/default";
  };

  outputs = { self, systems, nixpkgs, ... }:
  let
    # Helper to apply a function over all systems
    eachSystem = f:
      nixpkgs.lib.genAttrs (import systems) (system: f system);

  in {
    devShells = eachSystem (system:
      let
        # Default pkgs (unstable)
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        default = pkgs.mkShell {
          packages = [
            pkgs.ghostscript
            pkgs.imagemagick
            pkgs.inkscape
            pkgs.pdftk
            pkgs.poppler_utils  # For pdftocairo
            pkgs.coreutils
            (pkgs.python312.withPackages (python-pkgs: with python-pkgs; [
              pymupdf
              pypdf
            ]))
            pkgs.fontconfig
          ];

          shellHook = ''
            # bc of https://gitlab.com/inkscape/inkscape/-/issues/4716, also why using unshare in code 
            export SELF_CALL=xxx

            # for this error? https://askubuntu.com/questions/359753/gtk-warning-locale-not-supported-by-c-library-when-starting-apps-from-th
            export LC_ALL="en_US"
            export LANG="en_US"
            export LANGUAGE="en_NZ"
            export C_CTYPE="en_US"
            export LC_NUMERIC=
            export LC_TIME=en"en_US"
            # or (https://discourse.nixos.org/t/fonts-in-nix-installed-packages-on-a-non-nixos-system/5871/8)
            set --global --export FONTCONFIG_FILE ${pkgs.fontconfig.out}/etc/fonts/fonts.conf

            echo "Ruby PDF Inverter shell is ready! All dependencies installed."
            echo "Run with ./pdfinvert.rb input.pdf inverted_sample.pdf"
          '';
        };
      });

    # Default app to run the Python script
    apps = eachSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python312.withPackages (python-pkgs: with python-pkgs; [ pymupdf ]);
      in {
        default = {
          type = "app";
          program = "${pkgs.writeShellScript "run-pdf-inverter" ''
            #!/bin/sh
            exec ${pythonEnv}/bin/python3 ${self}/py.py "$@"
          ''}";
        };
      });


    # Provide a package for the script if desired
    packages = eachSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        default = pkgs.buildEnv {
          name = "pdf-inverter";
          paths = [
            pkgs.ghostscript
            pkgs.imagemagick
            pkgs.inkscape
            pkgs.pdftk
            pkgs.poppler_utils
            pkgs.coreutils
            (pkgs.python312.withPackages (python-pkgs: with python-pkgs; [ pymupdf ]))
          ];
        };
      });
  };
}
