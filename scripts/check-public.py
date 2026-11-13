#!/usr/bin/env python3
"""Check tracked and unignored new files for common accidental private content.

This is a small guardrail, not a guarantee that a repository contains no secrets.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "private key": rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "GitHub token": rb"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})",
    "AWS access key": rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "Slack token": rb"\bxox[baprs]-[A-Za-z0-9-]{20,}",
    "URL credentials": rb"https?://[^\s/:]+:[^\s/@]+@",
    "home-directory identity": rb"/home/" + rb"(?!example(?:/|\b)|user(?:/|\b))[^/\s\"'()]+",
    "telemetry identifier": rb'"crash-reporter-id"\s*:\s*"[0-9a-fA-F-]{36}"',
    "hardware address": rb"(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b",
}


def main():
    names = subprocess.check_output([
        "git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"
    ], cwd=ROOT).decode().split("\0")
    problems = []
    checked = 0
    for name in sorted(set(filter(None, names))):
        path = ROOT / name
        if not path.is_file():
            continue
        if name.endswith((".tar", ".tar.gz", ".tgz", ".zip", ".7z", ".bundle", ".kdbx", ".pem", ".key")):
            problems.append((name, "private archive or credential file"))
            continue
        data = path.read_bytes()
        if data.startswith((b"\x7fELF", b"\x1f\x8b")):
            problems.append((name, "binary or compressed file"))
            continue
        for label, pattern in PATTERNS.items():
            if re.search(pattern, data):
                problems.append((name, label))
        checked += 1
    for name, label in problems:
        print(f"{name}: {label}", file=sys.stderr)
    if problems:
        return 1
    print(f"Public-content check passed for {checked} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
