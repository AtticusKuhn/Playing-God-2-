{ pkgs ? import <nixpkgs-unstable> {} }:
with pkgs;let
  xdsl = ps: ps.callPackage ./xdsl.nix {};
  my-python-packages = ps: with ps; [
    pygame
    requests
    pyproj
    aiohttp
    aiofiles
  ];
  my-python = pkgs.python3.withPackages my-python-packages;
in
mkShell {
  buildInputs = [
    my-python
    pkgs.black
    pkgs.ruff
    ];
}
