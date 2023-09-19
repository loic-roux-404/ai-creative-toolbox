with import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/nixpkgs-unstable.tar.gz") {
  #sandbox = false;
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
    ffmpeg_5
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
    export CFLAGS="-stdlib=libc++
    pip install -r requirements_lock.txt
    pnpm install
    go mod tidy
    bazel build //...
  '';

  postShellHook = ''
    export MAGICK_HOME=${pkgs.imagemagick}
    export FFMPEG_ROOT=${pkgs.ffmpeg_4.lib}
    export PATH="$PATH:$MAGICK_HOME/bin"
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$MAGICK_HOME/lib:$FFMPEG_ROOT/lib"
    export GOPATH="${pkgs.go_1_21}/share/go/packages"
  '';
}
