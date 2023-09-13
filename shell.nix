{ pkgs ? import ./nix/nixpkgs { } }:

with pkgs;

let
  pythonPackages = python3Packages;
in mkShell rec {
  packages = [ bazelisk buildifier buildozer nix tesseract imagemagick go ];
  buildInputs = [
    pythonPackages.python
    pythonPackages.pip
    pythonPackages.venvShellHook
  ];
  venvDir = "./.venv";

  postVenvCreation = ''
    unset SOURCE_DATE_EPOCH
    pip install -r requirements_lock.txt
  '';

  postShellHook =  ''
    export MAGICK_HOME=${pkgs.imagemagick}
    export PATH="$PATH:$MAGICK_HOME/bin"
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$MAGICK_HOME/lib"
  '';

}
