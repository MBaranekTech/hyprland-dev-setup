#!/bin/sh
set -eu
choice=$(printf '%s\n' 'Lock' 'Suspend' 'Log out' 'Restart' 'Power off' | fuzzel --config="$HOME/.config/hypr/fuzzel.ini" --dmenu --prompt='Session > ') || exit 0
case "$choice" in
    Lock) loginctl lock-session ;;
    Suspend) systemctl suspend ;;
    'Log out'|'Restart'|'Power off')
        confirmation=$(printf '%s\n' 'Cancel' "Confirm: $choice" | fuzzel --config="$HOME/.config/hypr/fuzzel.ini" --dmenu --prompt='Confirm > ') || exit 0
        [ "$confirmation" = "Confirm: $choice" ] || exit 0
        case "$choice" in
            'Log out') hyprctl dispatch exit ;;
            Restart) systemctl reboot ;;
            'Power off') systemctl poweroff ;;
        esac
        ;;
esac
