"""
persistence.py  —  Save / load leaderboard and settings
"""

import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

DEFAULT_SETTINGS = {
    "sound":       True,
    "car_color":   "red",
    "difficulty":  "normal",   # easy / normal / hard
}


# ── Settings ──────────────────────────────────────────────────────────────

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                data = json.load(f)
            s = DEFAULT_SETTINGS.copy()
            s.update(data)
            return s
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


# ── Leaderboard ───────────────────────────────────────────────────────────

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_score(name, score, distance, coins):
    lb = load_leaderboard()
    lb.append({"name": name, "score": score, "distance": distance, "coins": coins})
    lb.sort(key=lambda x: x["score"], reverse=True)
    lb = lb[:10]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(lb, f, indent=2)
    return lb
