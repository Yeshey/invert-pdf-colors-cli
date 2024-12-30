{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";

  # built based on this template https://github.com/NixOS/templates/blob/master/python/flake.nix
  # With the help of this video: https://www.youtube.com/watch?v=oqXWrkvZ59g

  # This issue is why we use unshare --user inkscape: https://gitlab.com/inkscape/inkscape/-/issues/4716 

  outputs = { self, nixpkgs, poetry2nix }:
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});

      developmentAndRuntimePackages = system: with pkgs.${system}; [ 
        ghostscript
        imagemagick
        inkscape
        pdftk
        poppler_utils
      ];
    in
    {
      packages = forAllSystems (system: let
        inherit (poetry2nix.lib.mkPoetry2Nix { pkgs = pkgs.${system}; }) mkPoetryApplication;
      in {
        default = mkPoetryApplication { 
          projectDir = self; 
          #nativeBuildInputs = [
          #  pkgs.${system}.cmatrix
          #];
          #buildInputs = [
          #  pkgs.${system}.cmatrix
          #];
          propagatedBuildInputs = with pkgs.${system}; [
            
          ] ++ developmentAndRuntimePackages system; # runTime packages
        };
      });

      devShells = forAllSystems (system: let
        inherit (poetry2nix.lib.mkPoetry2Nix { pkgs = pkgs.${system}; }) mkPoetryEnv;
      in {
        default = pkgs.${system}.mkShellNoCC {
          packages = with pkgs.${system}; [
            (mkPoetryEnv { projectDir = self; })
            poetry
          ] ++ developmentAndRuntimePackages system; # development packages (`nix develop` or `direnv allow`)
        };
      });

      apps = forAllSystems (system: let
        inherit (poetry2nix.lib.mkPoetry2Nix { pkgs = pkgs.${system}; }) mkPoetryApplication;
      in {
        default = {
          program = "${self.packages.${system}.default}/bin/start";
          type = "app";
        };
      });

    };
}