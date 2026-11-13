#!/bin/sh
set -eu
entry=$(cliphist list | fuzzel --config="$HOME/.config/hypr/fuzzel.ini" --dmenu --prompt='Clipboard > ') || exit 0
[ -n "$entry" ] || exit 0
printf '%s\n' "$entry" | cliphist decode | wl-copy
