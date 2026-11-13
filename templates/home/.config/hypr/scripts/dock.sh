#!/bin/sh
# Follow the leftmost active output, including monitor hotplug/reconfiguration.
exec /usr/bin/python3 "$HOME/.config/hypr/scripts/dock-monitor.py"
