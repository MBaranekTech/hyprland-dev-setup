# My Hyprland Development Environment

My personal development desktop built around **Ubuntu and Hyprland**.

I created this setup to make my everyday development environment fit the way I work: an editor, a browser, terminals, notes, and a few useful desktop controls that are always easy to reach. This document records the choices behind it and how everything works together.

## Why I built it

I wanted a desktop with predictable window placement, useful keyboard shortcuts, and a consistent layout between my home and work monitors. Hyprland gives me automatic window tiling and workspaces, while the surrounding tools provide the everyday features I use: an application dock, notifications, screenshots, Bluetooth controls, and night light.

I also enjoy shaping the appearance to my preferences. The result is a dark desktop with blue accents, a slightly transparent terminal, and a small, translucent dock inspired by macOS. The goal is a comfortable environment for real development work and daily use.

This is a personal setup that can grow as I discover what helps me work more comfortably.

## Platform

The documented baseline is **Ubuntu 26.04 with Hyprland 0.53.3**, using Hyprland's `.conf` configuration format.

Hyprland runs the Wayland desktop. Individual applications can also use XWayland where needed. Configuration examples intended for newer Hyprland releases may use a different format, so this version is useful context when maintaining the setup.

## Applications I keep close

| Application | Role |
| --- | --- |
| Visual Studio Code | Code editor |
| Brave | Browser for everyday work and development |
| Foot | Regular and drop-down terminals |
| Nautilus / Files | Graphical file management and access to Trash |
| KeePassXC | Password management |
| Obsidian | Notes and personal knowledge |
| Spotify | Music while working |

The dock's pinned order is **Files → Brave → KeePassXC → VS Code → Spotify → Terminal → Obsidian → Trash**. The application launcher is at the bottom. Other running applications can also appear in the dock.

`tmux` is installed and available for persistent terminal sessions.

## Desktop components

| Component | What I use it for |
| --- | --- |
| **Waybar** | Workspaces, clock, year progress, keyboard layout, system status, and quick controls |
| **Fuzzel** | Searching for and launching applications; small selection menus |
| **nwg-dock-hyprland** | A compact application dock on the left edge |
| **Pyprland** | A drop-down terminal that keeps its shell running when hidden |
| **SwayNotificationCenter** | Notification history and Do Not Disturb |
| **grim + slurp + Satty** | Selecting a screenshot region and annotating the result |
| **cliphist + wl-clipboard** | Clipboard history and clipboard integration |
| **Hyprsunset** | Scheduled warm screen colors with manual controls |
| **Hyprlock + Hypridle** | Lock screen, inactivity timers, and display power management |
| **swaybg** | Desktop wallpaper |
| **Blueman** | Bluetooth device management and pairing |
| **nwg-displays** | Graphical monitor configuration when needed |

### Top bar

The top bar provides:

- Workspace navigation.
- Date and time, with **Waycal** opening a calendar below the bar.
- The percentage of the current year that has already passed.
- A **CZ / ENG** keyboard indicator with the active layout highlighted; clicking switches layouts.
- Night light temperature, shown as a compact value such as `4370K`, or `Off`.
- CPU and memory usage, Bluetooth, network, volume, and battery status.
- A notification bell and a session menu.

Bluetooth opens Blueman with a left-click and toggles power with a right-click. The notification bell opens the notification center; right-clicking it toggles Do Not Disturb.

Waybar runs through the `hypr-waybar.service` user service. If the process crashes, systemd restarts it after two seconds. The session starts this service after importing the Wayland environment. Logs are available with `journalctl --user -u hypr-waybar.service`.

### Left dock

The dock uses **32 px icons**, compact spacing, rounded corners, and a **50% opaque background with blur**.

It appears when I move the pointer to the middle of the left edge and hides after I move away. It is restricted to the **leftmost active display**, and a small helper follows monitor changes automatically.

Applications can be pinned or unpinned through their right-click menu. The pinned order is stored in `~/.cache/nwg-dock-pinned`.

### Drop-down terminal

**Super + T** shows or hides a Foot terminal near the top of the active monitor. Its shell stays alive when it is hidden, so commands and terminal state are preserved. It also hides when focus moves elsewhere.

Regular Foot terminals open with **Super + Enter**. Their background uses **85% opacity**.

### Screenshots

I can launch **Screenshot** through the application launcher even when my keyboard has no Print Screen key.

1. Open the launcher and search for `screenshot`.
2. Select a region with the mouse.
3. Use Satty to add arrows, text, shapes, or blur.
4. Press **Enter** to save the result and copy it to the clipboard.

Screenshots are saved under the system Pictures directory in `Screenshots`. Pressing Esc in Satty closes the editor; the original capture has already been saved.

### Night light

Hyprsunset automatically enables warm colors from **18:00 to 08:00**, using local system time.

- **Left-click the temperature:** turn night light on or off.
- **Right-click:** open temperature presets or a slider with live preview.
- **Middle-click:** restore the automatic schedule.

Lower Kelvin values produce warmer colors. Applying a slider setting saves the intensity for future evenings. A manual on/off override lasts until the next scheduled change.

### Locking and wallpaper

The session locks after **15 minutes** of inactivity and turns off displays after **30 minutes**. These timers do not automatically suspend the laptop.

The desktop and lock screen use the same wallpaper. The shared templates expect a user-provided image at `~/Pictures/wallpaper.png`.

## Consistent monitors across locations

My physical arrangement is **external monitor on the left, laptop on the right**.

| Example profile | External display | Resolution | Scale |
| --- | --- | --- | --- |
| High-density display | Generic 4K display | 3840 × 2160 at 60 Hz | 150% |
| Standard-density display | Generic QHD display | 2560 × 1440 at approximately 60 Hz | 100% |

Both external monitors provide a logical workspace of **2560 × 1440**, which lets the laptop keep the same relative position in either setup. The laptop uses **1920 × 1200 at 100%** and is vertically centered beside the external display.

The published `monitors.conf` uses automatic placement. A generic external-left / laptop-right example is provided in [examples/monitors.conf.example](examples/monitors.conf.example). Replace its connector names with your own before using it. Hardware descriptions and serial numbers are excluded from the shared configuration. The example profiles assume one external monitor is connected at a time.

The dock follows whichever active display is furthest left. With only the laptop connected, it belongs to the laptop display.

## Shortcuts I use

**Super** is the Windows-logo key.

| Shortcut | Action |
| --- | --- |
| Super + D | Application launcher |
| Super + Enter | Regular terminal |
| Super + T | Show or hide the drop-down terminal |
| Super + E | Files |
| Super + N | Notification center |
| Super + V | Clipboard history |
| Super + 1–9 | Switch workspace |
| Super + Shift + 1–9 | Move a window to a workspace |
| Super + arrow keys | Focus a neighboring window |
| Super + Shift + arrow keys | Move a window |
| Super + Ctrl + arrow keys | Resize a window |
| Super + Shift + Space | Toggle floating mode |
| Super + F | Toggle fullscreen |
| Super + Shift + Q | Close the active window |
| Super + L | Lock the session |
| Super + Shift + E | Session and power menu |
| Super + Shift + R | Reload Hyprland configuration |
| Alt + Shift | Switch between Czech and English keyboard layouts |
| Print Screen, when available | Select a screenshot region and open Satty |

## Where the configuration lives

| Path | Purpose |
| --- | --- |
| `~/.config/hypr/hyprland.conf` | Main Hyprland configuration |
| `~/.config/hypr/local.conf` | Personal overrides, rules, autostart entries, and additional bindings |
| `~/.config/hypr/monitors.conf` | Home and work monitor profiles |
| `~/.config/hypr/waybar.json` and `waybar.css` | Top bar modules and appearance |
| `~/.config/systemd/user/hypr-waybar.service` | Waybar startup and automatic recovery after a crash |
| `~/.config/hypr/foot.ini` | Terminal appearance |
| `~/.config/hypr/hyprsunset.conf` | Night light schedule and saved temperature |
| `~/.config/hypr/hypridle.conf` | Inactivity timers |
| `~/.config/hypr/hyprlock.conf` | Lock screen appearance |
| `~/.config/hypr/scripts/` | Integration scripts for the desktop |
| `~/.config/pypr/config.toml` | Drop-down terminal configuration |
| `~/.config/satty/config.toml` | Screenshot editor behavior |
| `~/.config/swaync/config.json` | Notification center settings |
| `~/.config/nwg-dock-hyprland/style.css` | Dock appearance |

## Shared configuration

The [templates/home](templates/home) directory contains reviewed text configuration and helper scripts arranged like a home directory. Personal absolute paths are represented by `@HOME@`.

Generate a separate preview using Python 3.11 or newer:

```sh
python3 scripts/render.py
```

This creates an ignored `.rendered/` directory. It does not change the running desktop. Review the generated configuration, customize the monitor rules, provide your wallpaper, and install the required applications before copying selected files into your home directory. Some launchers assume the listed optional applications are available; the VS Code launcher example uses its Snap installation.

The templates target the documented Hyprland version. Install the desktop tools through your distribution or their official upstream projects. The original local setup used Pyprland 3.4.6, Satty 0.22.0, SwayNotificationCenter 0.12.4, Hyprsunset 0.4.0, nwg-dock-hyprland 0.4.11, and Waycal 0.2.1. Their binaries and dependencies are not bundled here.

The session starts SwayNotificationCenter through its user service. Stop any other notification daemon before enabling it. The included service condition restricts that service to a Hyprland session.

After installing or changing user service files, run `systemctl --user daemon-reload`. The session startup script starts `hypr-waybar.service`; start it manually with `systemctl --user start hypr-waybar.service` when applying this change to an existing session.

The [VS Code runtime-argument example](examples/vscode-argv.json) contains only the keyring setting. Merge it into your own runtime arguments if needed; it contains no installation-specific telemetry identifier.

## Privacy and backups

This repository contains sanitized configuration examples. Full machine backups are kept privately outside the repository.

The shared files exclude monitor serial numbers, personal home-directory paths, telemetry identifiers, wallpapers, compiled binaries, application profiles, keyrings, password databases, credentials, clipboard contents, and work projects. Local backups and generated configuration are ignored by Git.

Before committing future changes, run:

```sh
python3 scripts/check-public.py
git diff --cached --check
```

The content check detects selected token formats, private keys, common identifying values, and accidentally tracked archives or binaries. It supports manual review; it cannot prove that a file contains no confidential information.

## Maintaining the setup

The priority is to keep improving the desktop based on actual development work: notice friction, make a focused change, and keep the result understandable.
