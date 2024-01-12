with import <nixpkgs> {
  config = { allowUnfree = true; };
};

with pkgs;

let
  unstableNixpkgs = import (fetchTarball "https://github.com/nixos/nixpkgs/tarball/nixpkgs-unstable") {};
  pythonPackages = unstableNixpkgs.python310Packages;
  py_requirements = with pythonPackages; [
    python
    pip
    pytest
    pytest-cov
    virtualenv
    venvShellHook

    langchain
    sqlalchemy
    transformers
    litellm
    opencv4
    nltk
    easyocr
    ninja
    python-dotenv
    pytorch
    tiktoken
    tenacity
    wand
    watchdog
    pillow
    types-pillow
    openai
    markdown
    joblib
    jinja2
    importlib-metadata
    httpx
    html2text
    google-api-python-client
    google-auth-httplib2
    google-auth-oauthlib
    flask-cors
    debugpy
    beautifulsoup4
    filelock
  ];
in
mkShell {
  packages = [
    bazel
    bazel-buildtools
    nix
    imagemagick
    terraform
    ffmpeg_4
    zulu17
  ];

  buildInputs = py_requirements ++ [
    pre-commit
    nodejs_18
    (nodePackages.pnpm.override { nodejs = nodejs_18; })
  ];

  nativeBuildInputs = [
    nil
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
    pip install -r requirements.txt
    pip freeze > requirements_lock.txt
    sed -i 's/^SQLAlchemy==2.0.21.dev0$/SQLAlchemy==2.0.21/g' requirements_lock.txt
    sed -i 's/^pydantic==1.10.12$/pydantic==2.5.3/g' requirements_lock.txt
    pnpm install
    go mod tidy
    bazel build //...
  '';

  postShellHook = ''
    unset SOURCE_DATE_EPOCH
    export MAGICK_HOME=${imagemagick}
    export PATH="$PATH:$MAGICK_HOME/bin"
    MY_LIBS="$MAGICK_HOME/lib:${ffmpeg_4.lib}/lib"
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$MY_LIBS"
    export DYLD_LIBRARY_PATH="$DYLD_LIBRARY_PATH:$MY_LIBS"
  '';
}
