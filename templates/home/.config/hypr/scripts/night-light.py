#!/usr/bin/python3
"""Waybar status and controls for Hyprsunset's native color-temperature filter."""
import json
import fcntl
import os
from pathlib import Path
import re
import signal
import socket
import struct
import subprocess
import sys
import time

CONFIG = Path.home() / ".config/hypr/hyprsunset.conf"
RUNTIME = Path(os.environ["XDG_RUNTIME_DIR"])
SOCKET = RUNTIME / "hypr" / os.environ["HYPRLAND_INSTANCE_SIGNATURE"] / ".hyprsunset.sock"


def ipc(*args):
    return subprocess.check_output(
        ["hyprctl", "hyprsunset", *args], text=True, timeout=3).strip()


def saved_temperature():
    match = re.search(r"(?m)^\s*temperature\s*=\s*(\d+)", CONFIG.read_text())
    return int(match[1]) if match else 4500


def state():
    identity = ipc("identity", "get")
    if identity not in ("true", "false"):
        raise ValueError(identity)
    return identity == "false", int(ipc("temperature"))


def save_temperature(value):
    """Persist the evening profile and reload the daemon's cached schedule."""
    value = max(2500, min(6500, int(value)))
    original = CONFIG.read_text()
    updated, count = re.subn(r"(?m)^(\s*temperature\s*=\s*)\d+",
                            lambda m: m[1] + str(value), original, count=1)
    if count != 1:
        raise ValueError("The evening temperature profile is missing.")
    if updated != original:
        # Identify this session's daemon through its IPC socket.
        with socket.socket(socket.AF_UNIX) as connection:
            connection.connect(str(SOCKET))
            pid, uid, _gid = struct.unpack("3i", connection.getsockopt(
                socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))
        if uid != os.getuid():
            raise ValueError("Unexpected Hyprsunset owner.")
        CONFIG.write_text(updated)
        os.kill(pid, signal.SIGTERM)
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            # Reap our own previous child; another process may own the daemon.
            try:
                if os.waitpid(pid, os.WNOHANG)[0] == pid:
                    break
            except ChildProcessError:
                pass
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            try:
                if Path(f"/proc/{pid}/stat").read_text().rsplit(") ", 1)[1].split()[0] == "Z":
                    break
            except FileNotFoundError:
                break
            time.sleep(.05)
        else:
            CONFIG.write_text(original)
            raise RuntimeError("Hyprsunset did not stop; the saved profile was restored.")
        with (RUNTIME / "hyprsunset.log").open("a") as log:
            process = subprocess.Popen([str(Path.home() / ".local/bin/hyprsunset")],
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("Hyprsunset could not restart.")
            try:
                state()
                break
            except (subprocess.SubprocessError, ValueError):
                time.sleep(.05)
        else:
            raise RuntimeError("Hyprsunset did not become available.")
    ipc("temperature", str(value))


def slider():
    enabled, before = state()
    initial = before if enabled else saved_temperature()
    process = subprocess.Popen([
        "zenity", "--scale", "--title=Night Light",
        "--text=Color temperature (K)\nLower = warmer / stronger. Higher = cooler / milder.\nChanges are previewed live. Apply saves the nightly setting.",
        "--min-value=2500", "--max-value=6500", "--step=250",
        f"--value={initial}", "--print-partial", "--width=530",
        "--ok-label=Apply", "--cancel-label=Cancel",
    ], stdout=subprocess.PIPE, text=True)
    selected = initial
    try:
        for line in process.stdout:
            try:
                selected = max(2500, min(6500, int(float(line.strip()))))
            except ValueError:
                continue
            ipc("temperature", str(selected))
        if process.wait() == 0:
            save_temperature(selected)
        else:
            ipc("temperature", str(before))
            if not enabled:
                ipc("identity")
    finally:
        if process.poll() is None:
            process.terminate()


def menu():
    options = ["Adjust warmth (slider)", "Mild - 5000 K", "Medium - 4500 K",
               "Strong - 3500 K", "Very strong - 3000 K",
               "Automatic - 18:00 to 08:00", "Turn off"]
    result = subprocess.run([
        "fuzzel", f"--config={Path.home() / '.config/hypr/fuzzel.ini'}",
        "--dmenu", "--prompt=Night Light > ",
    ], input="\n".join(options) + "\n", text=True, capture_output=True)
    if result.returncode:
        return
    choice = result.stdout.strip()
    if choice == options[0]:
        slider()
    elif choice in options[1:5]:
        save_temperature(int(choice.split()[-2]))
    elif choice == options[5]:
        ipc("reset")
    elif choice == options[6]:
        ipc("identity")


def main():
    try:
        enabled, temperature = state()
        action = sys.argv[1] if len(sys.argv) > 1 else "status"
        if action == "toggle":
            ipc("identity") if enabled else ipc("temperature", str(saved_temperature()))
            return
        if action == "auto":
            ipc("reset")
            return
        if action in ("menu", "slider"):
            with (RUNTIME / "hypr-night-light-settings.lock").open("w") as lock:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    return
                menu() if action == "menu" else slider()
            return
        print(json.dumps({
            "text": f"{temperature}K" if enabled else "Off",
            "class": "on" if enabled else "off",
            "tooltip": (f"Night Light: {temperature} K" if enabled else "Night Light is off")
                       + f"\nSchedule: 18:00–08:00 ({saved_temperature()} K)"
                       + "\nClick: on/off | Right-click: presets and slider"
                       + "\nMiddle-click: restore automatic schedule"
                       + "\nManual overrides last until the next scheduled change.",
        }, ensure_ascii=False))
    except (subprocess.SubprocessError, ValueError, OSError, RuntimeError) as error:
        print(json.dumps({
            "text": "?", "class": "error",
            "tooltip": f"Hyprsunset is unavailable: {error}",
        }, ensure_ascii=False))
        if len(sys.argv) > 1:
            subprocess.run(["notify-send", "Night Light", str(error)], check=False)


if __name__ == "__main__":
    main()
