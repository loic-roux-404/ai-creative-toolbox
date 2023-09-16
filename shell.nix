with import <nixpkgs>
{
    config.allowUnfree = true;
};

with pkgs;

let
  python = python311;
  pythonPackages = python.pkgs;
in
mkShell rec {
  packages = [
    openjdk17
    bazel-buildtools
    nix
    imagemagick
    terraform
  ];

  buildInputs = [
    pythonPackages.python
    pythonPackages.pip
    pythonPackages.venvShellHook
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
    bazelisk
  ];

  venvDir = "./.venv";

  postVenvCreation = ''
    unset SOURCE_DATE_EPOCH
    pip install -r requirements_lock.txt
  '';

  postShellHook = ''
    export MAGICK_HOME=${pkgs.imagemagick}
    export PATH="$PATH:$MAGICK_HOME/bin"
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$MAGICK_HOME/lib"
    export GOPATH="${pkgs.go_1_21}/share/go/packages"
  '';
}
