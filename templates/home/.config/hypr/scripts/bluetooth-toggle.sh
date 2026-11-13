#!/bin/sh
set -eu
if LC_ALL=C bluetoothctl show | rg -q 'Powered: yes'; then
    target=off
else
    target=on
fi
if bluetoothctl power "$target"; then
    notify-send Bluetooth "Bluetooth turned $target."
else
    notify-send Bluetooth 'Unable to change Bluetooth power. Open the device manager for details.'
    exit 1
fi
