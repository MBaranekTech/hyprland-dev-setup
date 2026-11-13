#!/usr/bin/python3
"""Keep the auto-hiding nwg dock on the leftmost active Hyprland output."""
import fcntl
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time


def choose_output(monitors):
    active = [m for m in monitors if not m.get("disabled", False)
              and m.get("mirrorOf", "none") == "none"]
    return min(active, key=lambda m: (m["x"], m["y"], m["name"])) if active else None


def main():
    runtime = Path(os.environ["XDG_RUNTIME_DIR"])
    instance = os.environ["HYPRLAND_INSTANCE_SIGNATURE"]
    with (runtime / "hypr-left-dock.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        child = None
        current = None
        running = True

        def request_stop(*_args):
            nonlocal running
            running = False

        signal.signal(signal.SIGTERM, request_stop)
        signal.signal(signal.SIGINT, request_stop)

        def stop_child():
            nonlocal child
            if child is not None:
                if child.poll() is None:
                    child.terminate()
                    try:
                        child.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait()
                child = None

        def sync_output():
            nonlocal child, current
            try:
                monitors = json.loads(subprocess.check_output(
                    ["hyprctl", "monitors", "-j"], text=True, timeout=3))
            except (subprocess.SubprocessError, ValueError):
                return
            target = choose_output(monitors)
            signature = tuple(target.get(k) for k in (
                "name", "x", "y", "width", "height", "scale")) if target else None
            if signature == current and (target is None or (
                    child is not None and child.poll() is None)):
                return
            stop_child()
            current = signature
            if target:
                print(f"Dock output: {target['name']} (leftmost, x={target['x']})", flush=True)
                child = subprocess.Popen([
                    str(Path.home() / ".local/bin/nwg-dock-hyprland"),
                    "-d", "-p", "left", "-i", "32", "-hd", "0", "-ml", "8",
                    "-o", target["name"], "-lp", "end", "-c",
                    str(Path.home() / ".config/hypr/scripts/app-menu.sh"),
                ])

        try:
            with socket.socket(socket.AF_UNIX) as events:
                events.connect(str(runtime / "hypr" / instance / ".socket2.sock"))
                events.settimeout(2)
                sync_output()
                last_sync = time.monotonic()
                pending = b""
                while running:
                    refresh = False
                    try:
                        data = events.recv(65536)
                        if not data:
                            break  # Hyprland session ended.
                        pending += data
                        while b"\n" in pending:
                            line, pending = pending.split(b"\n", 1)
                            event = line.split(b">>", 1)[0]
                            if event in (b"monitoradded", b"monitoraddedv2",
                                         b"monitorremoved", b"configreloaded"):
                                refresh = True
                    except socket.timeout:
                        pass
                    # Recover from a crashed dock or a missed output event.
                    if running and (refresh or time.monotonic() - last_sync >= 10):
                        sync_output()
                        last_sync = time.monotonic()
        finally:
            stop_child()


if __name__ == "__main__":
    main()
