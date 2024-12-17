{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    systems.url = "github:nix-systems/default";
  };

  outputs = { systems, nixpkgs, ... } @ inputs:
  let
    eachSystem = f:
      nixpkgs.lib.genAttrs (import systems) (
        system:
          f nixpkgs.legacyPackages.${system}
      );
  in {
    devShells = eachSystem (pkgs:
      let
        rubyEnv = pkgs.ruby.withPackages (ruby-pkgs: with ruby-pkgs; [
          parallel  # Optional: for parallel processing
        ]);
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

            #pkgs.python3Packages.pymupdf
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
  };
}