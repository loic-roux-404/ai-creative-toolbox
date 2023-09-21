{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python38
    pkgs.python38Packages.numpy
  ];
}
