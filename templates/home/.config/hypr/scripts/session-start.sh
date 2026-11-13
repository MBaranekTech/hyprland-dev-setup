#!/bin/sh
# Run only inside Hyprland. Import the display before portal/polkit activation.
set -eu
dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP HYPRLAND_INSTANCE_SIGNATURE
systemctl --user start hyprpolkitagent.service
waybar -c "$HOME/.config/hypr/waybar.json" -s "$HOME/.config/hypr/waybar.css" &
systemctl --user start swaync.service
hypridle &
nm-applet --indicator &
wl-paste --type text --watch cliphist store &
wl-paste --type image --watch cliphist store &
wait
