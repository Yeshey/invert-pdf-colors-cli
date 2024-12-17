{
  inputs = {
    # Default nixpkgs (unstable)
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    # Older nixpkgs version (pinned)
    oldnixpkgs.url = "https://github.com/NixOS/nixpkgs/archive/9957cd48326fe8dbd52fdc50dd2502307f188b0d.tar.gz";

    # Systems input for multi-system builds
    systems.url = "github:nix-systems/default";
  };

  outputs = { self, systems, nixpkgs, oldnixpkgs, ... }:
  let
    # Helper to apply a function over all systems
    eachSystem = f:
      nixpkgs.lib.genAttrs (import systems) (system: f system);

  in {
    devShells = eachSystem (system:
      let
        # Default pkgs (unstable)
        pkgs = nixpkgs.legacyPackages.${system};

        # Older pkgs (specific commit)
        pkgs-old = import oldnixpkgs {
          inherit system;
        };

        # Define a Ruby environment
        rubyEnv = pkgs.ruby.withPackages (ruby-pkgs: with ruby-pkgs; [
          parallel  # Optional: for parallel processing
        ]);

        # Older version of Inkscape
        olderInkscape = pkgs-old.inkscape;

      in {
        default = pkgs.mkShell {
          packages = [
            rubyEnv
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

          shellHook = ''
            export SELF_CALL=xxx

            echo "Ruby PDF Inverter shell is ready! All dependencies installed."
            echo "Run with ./pdfinvert.rb input.pdf inverted_sample.pdf"
          '';
        };
      });
  };
}
