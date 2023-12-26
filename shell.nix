with import <nixpkgs> {
  config = { allowUnfree = true; };
};

with pkgs;

let
  pythonPackages = python310Packages;
in
mkShell rec {
  packages = [
    bazel
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
  '';
}
