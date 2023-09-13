# { pkgs ? import ../nix/nixpkgs { } }:

# with pkgs;

# mkShell {
    # TODO add MODULE.bazel and module own requirements.txt
    # packages = [ tesseract imagemagick ];

    # shellHook = ''
    #     export MAGICK_HOME=${pkgs.imagemagick}
    #     export PATH="$PATH:$MAGICK_HOME/bin"
    #     export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$MAGICK_HOME/lib"
    # '';
# }
