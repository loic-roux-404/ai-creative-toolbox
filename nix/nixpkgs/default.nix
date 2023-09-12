{ system ? builtins.currentSystem, ... }:

import (builtins.fetchTarball {
  name = "nixos-21.11-2021-12-04";
  # URL obtained from https://status.nixos.org/
  url = "https://github.com/NixOS/nixpkgs/archive/refs/tags/23.05.tar.gz";
  # Hash obtained using `nix-prefetch-url --unpack <url>`
  sha256 = "10wn0l08j9lgqcw8177nh2ljrnxdrpri7bp0g7nvrsn9rkawvlbf";
}) {
  inherit system;
  overlays = [];
  config = {};
}
