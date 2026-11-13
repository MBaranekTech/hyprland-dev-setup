#!/usr/bin/python3
"""Year progress for the Waybar module; calendar UI is provided by Waycal."""
import datetime as dt
import json

now = dt.datetime.now()
start = dt.datetime(now.year, 1, 1)
end = dt.datetime(now.year + 1, 1, 1)
percent = (now - start).total_seconds() / (end - start).total_seconds() * 100
percent_text = f"{percent:.1f}".replace(".", ",")
remaining = (end.date() - now.date()).days
print(json.dumps({
    "text": f"{now.year} · {percent_text} %",
    "tooltip": f"Z roku {now.year} už uplynulo {percent_text} %.\n"
               f"Do roku {now.year + 1} zbývá {remaining} dní.\n"
               "Kliknutím otevřeš Waycal.",
}, ensure_ascii=False))
