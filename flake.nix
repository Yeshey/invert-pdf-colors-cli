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
            ]))
          ];

          # export bc of https://gitlab.com/inkscape/inkscape/-/issues/4716, also whyy using unshare in ruby code 
          shellHook = ''
            export SELF_CALL=xxx
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
