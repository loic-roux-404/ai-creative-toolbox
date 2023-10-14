with import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/nixpkgs-unstable.tar.gz") {
  config = { allowUnfree = true; };
};

with pkgs;

let
  python = python310;
  pythonPackages = python.pkgs;
in
mkShell rec {
  packages = [
    openjdk17
    bazel_6
    bazel-buildtools
    nix
    imagemagick
    terraform
    ffmpeg_4
  ];

  buildInputs = [
    pythonPackages.python
    pythonPackages.pip
    pythonPackages.pytest
    pythonPackages.pytest-cov
    pythonPackages.virtualenv
    pythonPackages.venvShellHook
    pre-commit
    nodejs_18
    (nodePackages.pnpm.override { nodejs = nodejs_18; })
  ];

  nativeBuildInputs = [
    nixpkgs-fmt
    rnix-lsp
    docker-client
    gnumake

    go
    go-outline
    gopls
    gopkgs
    go-tools
    delve
  ];

  venvDir = "./.venv";

  postVenvCreation = ''
    unset SOURCE_DATE_EPOCH
    pip install --pre -r requirements_lock.txt --extra-index-url https://download.pytorch.org/whl/nightly/cpu
    pnpm install
    go mod tidy
    bazel build //...
  '';

  postShellHook = ''
    export MAGICK_HOME=${imagemagick}
    export PATH="$PATH:$MAGICK_HOME/bin"
    MY_LIBS="$MAGICK_HOME/lib:${ffmpeg_4.lib}/lib:${libxml2}"
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$MY_LIBS"
    export DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH:$MY_LIBS"
  '';
}
