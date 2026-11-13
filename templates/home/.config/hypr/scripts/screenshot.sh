#!/bin/sh
set -eu
region=$(slurp) || exit 0
[ -n "$region" ] || exit 0
picture_root=$(xdg-user-dir PICTURES)
target_dir="$picture_root/Screenshots"
mkdir -p "$target_dir"
target_file="$target_dir/$(date +%Y-%m-%d_%H-%M-%S).png"
grim -g "$region" "$target_file"
wl-copy --type image/png < "$target_file"
exec "$HOME/.local/bin/satty" --filename "$target_file" --output-filename "$target_file"
