"""
DialogueForge - a config editor for the DayZ Dialogue Framework mod.

Single-file Tkinter app. Stdlib only, except for one optional extra:
`pyspellchecker` powers the spellcheck. It is bundled into the release .exe
by PyInstaller; if it isn't installed when running from source, the app still
runs and spellcheck simply switches itself off.
Run with:  python DialogueForge.py   (pip install pyspellchecker for spellcheck)
Build an .exe with build_exe.bat (PyInstaller).

Edits:
  MenuConfig.json
  Dialogues\\NPC_<id>\\*.json
  Dialogues\\Trader_<name>\\*.json
  Dialogues\\Shared\\*.json
  QuestText\\*.json
"""

import json
import os
import re
import copy
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog

# Optional: bundled into the release .exe by PyInstaller, but the app must
# still run from source without it (spellcheck just quietly turns off).
try:
    from spellchecker import SpellChecker
except Exception:
    SpellChecker = None

APP_TITLE = "DialogueForge - DayZ Dialogue Framework config editor"
SETTINGS_FILE = os.path.join(
    os.path.expanduser("~"), ".dialogueforge_settings.json")

# ---------------------------------------------------------------- constants

ACTION_TYPES = [
    "NONE",
    "SHOW_QUEST_LIST",
    "END_CONVERSATION",
    "OPEN_TRADER",
]

# Authorable only inside the live quest-detail step, which the mod builds
# itself. Shown behind an "advanced" toggle so nobody picks them by accident.
ADVANCED_ACTION_TYPES = [
    "ACCEPT_QUEST",
    "DECLINE_QUEST",
    "TURN_IN_QUEST",
]

ACTION_HELP = {
    "NONE": "Go to the node picked in 'Next node'. Set it to (end) to finish.",
    "SHOW_QUEST_LIST": "Opens the live quest list for this NPC.",
    "END_CONVERSATION": "Plays a random farewell line, then closes the window.",
    "OPEN_TRADER": "Traders only. Closes dialogue and opens the market menu.",
    "ACCEPT_QUEST": "Advanced - only meaningful inside the live quest-detail step.",
    "DECLINE_QUEST": "Advanced - only meaningful inside the live quest-detail step.",
    "TURN_IN_QUEST": "Advanced - only meaningful inside the live quest-detail step.",
}

NODE_TYPES = ["STANDARD", "QUEST_LIST", "QUEST_DETAIL"]

# First entry in the "Quest lock" dropdown - means RequiredQuestID = -1,
# i.e. the option is always shown rather than gated behind a finished quest.
NOT_LOCKED_LABEL = "Not locked"

# First entry in a speaker line's "Standard greeting after" dropdown - means
# OverrideQuestID = -1, i.e. the line never takes over as the fixed greeting.
OVERRIDE_NONE_LABEL = "No override"

# Built into the mod as of ConfigVersion 2 - no repacking needed.
FONT_STYLES = [
    ("DEFAULT", "Metron Book, standard sizes"),
    ("LIGHT", "Metron Light - thinner, less shouty"),
    ("LARGE", "Metron Book at 120% - easier at distance or on a TV"),
    ("COMPACT", "Metron Book at 85% - more options without scrolling"),
]

# How each style previews: (text scale, bold speaker name)
FONT_STYLE_PREVIEW = {
    "DEFAULT": (1.0, True),
    "LIGHT": (1.0, False),
    "LARGE": (1.2, True),
    "COMPACT": (0.85, True),
}

POSITIONS = [
    "TOP_LEFT", "TOP_CENTER", "TOP_RIGHT",
    "CENTER_LEFT", "CENTER", "CENTER_RIGHT",
    "BOTTOM_LEFT", "BOTTOM_CENTER", "BOTTOM_RIGHT",
]

COLOR_FIELDS = [
    ("BackgroundColor", "Window panel", [230, 0, 0, 0]),
    ("ResponseBackgroundColor", "Option buttons", [200, 0, 0, 0]),
    ("HoverBorderColor", "Hover border", [255, 255, 215, 0]),
    ("SpeakerNameColor", "Speaker name", [255, 255, 255, 255]),
    ("SpeakerTextColor", "Speaker line", [255, 255, 255, 255]),
    ("ResponseTextColor", "Option text", [255, 220, 220, 220]),
    ("RewardSelectedColor", "Selected reward tile", [230, 90, 70, 20]),
    ("WindowBorderColor", "Window border", [255, 255, 255, 255]),
]

# ---------------------------------------------------------------- themes
# Colours sampled from the mod's own logo.
GOLD = "#e8b33c"

PALETTES = {
    "light": {
        "bg": "#f4f2ec",
        "panel": "#e6e1d5",
        "field": "#fffdf8",
        "fg": "#23262a",
        "hint": "#5f6469",
        "accent": "#8a6c1f",
        "warn": "#9a5410",
        "border": "#c2bcae",
        "select_bg": "#ffe9a8",
        "select_fg": "#23262a",
        "active": "#dbd5c5",
        "trough": "#d6d1c3",
        "gold": GOLD,
        "preview_bg": "#3c4a52",
        "preview_screen": "#5a6b74",
        "preview_edge": "#8fa3ad",
        "preview_text": "#c9d8de",
    },
    "dark": {
        "bg": "#141619",
        "panel": "#1b1e23",
        "field": "#0f1114",
        "fg": "#f2efe8",
        "hint": "#8a929c",
        "accent": GOLD,
        "warn": "#e0a066",
        "border": "#3a4049",
        "select_bg": "#4a3a16",
        "select_fg": "#f0d79a",
        "active": "#2a2e35",
        "trough": "#0f1114",
        "gold": GOLD,
        "preview_bg": "#0e1114",
        "preview_screen": "#2b333a",
        "preview_edge": "#515c66",
        "preview_text": "#8b969f",
    },
}

MENU_PRESETS = {
    "Default (dark)": {},
    "Green terminal": {
        "BackgroundColor": [235, 5, 15, 5],
        "ResponseBackgroundColor": [210, 10, 25, 10],
        "HoverBorderColor": [255, 80, 255, 120],
        "SpeakerNameColor": [255, 140, 255, 170],
        "SpeakerTextColor": [255, 200, 255, 210],
        "ResponseTextColor": [255, 120, 230, 140],
        "WindowBorderColor": [255, 60, 200, 90],
    },
    "Amber CRT": {
        "BackgroundColor": [235, 20, 12, 0],
        "ResponseBackgroundColor": [210, 35, 22, 0],
        "HoverBorderColor": [255, 255, 180, 60],
        "SpeakerNameColor": [255, 255, 190, 90],
        "SpeakerTextColor": [255, 250, 220, 170],
        "ResponseTextColor": [255, 235, 180, 90],
        "WindowBorderColor": [255, 180, 120, 40],
    },
    "Clean white": {
        "BackgroundColor": [240, 245, 245, 245],
        "ResponseBackgroundColor": [230, 225, 225, 225],
        "HoverBorderColor": [255, 40, 90, 200],
        "SpeakerNameColor": [255, 20, 20, 20],
        "SpeakerTextColor": [255, 30, 30, 30],
        "ResponseTextColor": [255, 40, 40, 40],
        "WindowBorderColor": [255, 120, 120, 120],
    },
}


# ---- artwork --------------------------------------------------------------
# Vector-rendered PNGs embedded as base64 so the .exe stays a single file.
# The badge mirrors the Dialogue Framework icon; colours were sampled from
# the mod's own logo (gold #e8b33c, plate #141619, panel #1b1e23).
LOGO_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAISElEQVR42u3dwYoURxjA8X6IEAgZ"
    "gpAElcXF4BI2EMhBkBCEPY2HKOjBBxAPHgXvEcwjbLztNRfJA+zZvMKe8haT/WRXJnG7Z3qmZ6qn"
    "vt/CD2OiBnur/lNd3T3TND2+Pvv8i+m5k3On52bAaJxezM1pM+TX+R84OffaAYadEnN2su7kN/Fh"
    "x0Ow6qv+mYMHVThbejVg8kPSCJj8kDgCJj/UHwEbfmBj8JOlvwMDeUy8+oNVwIcAOCCQzPztvQ4I"
    "5DNtLu4fdjAgn5PGgz2Q9wEi5/+QeR/AQQABAAQAEABAAAABAAQAEABAAAABAAQAEABAAAABAAQA"
    "EABAAAABAAQAEABAAAABAAQAEABAAAABAGoOwN71yez5wxuz45e3Z+/eHMz++fNH2BkxZmPsxhiO"
    "sSwAS4oDZsJTYxBibAtAi7uH12bvjw8NFqoWYzzGugDMiaWSwUEmMebTByDOjbzqk3k1MJb9gcbk"
    "h7wR2HoAlpn8f//xw+y3Z7dnj4/2Zl9+9TXsjBizMXZjDC8TgVQBWHTOHwftxZN9A4kqxFheFILS"
    "ewLNNnf7uw7E21d3DBqqFGO7a+yXvDrQjGHpb/KTOQIlTwWabd3kY/IjAu0RKHWz0FYC0HaHX5wf"
    "GRhk0rYnEHOkygDEpY626tnwI+PGYNt8KHFZsCm1/Pfqj1VA+dOAptSlv7hWajCQUYz9sVwSbEqd"
    "/7vJh8w3C41lH2DjAWg73zEQyKxtXggACIAAgAAIAAiAAIAACAAIgACAAAgACIAAgAAIwIXv9r/9"
    "cKvlX79///H/Ff8c/y7+27p//s1bB7N79x/MHj19RkLxvY8xIAAjDMDPP93ofAum+G/xa1b98018"
    "5kMgACMKQLy6L/uOrKusBEx+hoyAAAwcgPkl/yLxa/su+w14rrLq6YAADLz07/u+7H1OBbz6M/Qq"
    "QAC28Hhllz6PIxvodBGAwgHoepulId6OzCBHAKwAQADsAYA9AFcBwFUA9wHg1V8A3AmIyS8AngXA"
    "swAC4GlAEAABAAEQABAAAQABEAAQAAFAAAQABEAAQAAEAARAAEAABAAEQABAAAQABEAAQAAEAARA"
    "AEAABAAEQABAAAQABEAAQAAEAARAAEAABAAEQABAAHwwyErik4XevrrT+8NI2Zz4fqzziU8C4KPB"
    "lmLijz8EAuDDQTfy4aAmvwgIQNKPB49Vg8m1O3bhdEAABl76b3KQePW3ChCAEQfg8dFe70ESv2fd"
    "bxbjJQCJAvDiyX7vARK/RwAEQACsAARAAATAHoA9AHsAAuAqgKsArgIIgPsArAK8+guAOwFFwOQX"
    "AM8CeBbAswAC4GlAEAABAAEQABAAAQABEAAQAAEAARAAEAABAAEQABAAAQABEAAQAIMAARAAEAAB"
    "AAEQABAAAQABEAAQAAEAARAAEAABAAEQABAAAQABEAAQAAEAAfDBIBv9YJCbtw5m9+4/mD16+oxK"
    "xPczvq8C4KPBOpn49YdAAHw4qMkvAgLg48H/u+w3OfLYxumAAAy89N/kZ8h79bcKEIARB+Dx0V7v"
    "AMTvWfbPNynyEYAdCsCLJ/u9AxC/RwAQACsAAUAA7AHYA8AegKsArgK4CuAqgPsArAK8+guAOwFF"
    "wOQXAM8CeBbAswAC4GlAEAABAAEQABAAAQABEAAQAAEAARAAEAABgOQBePfmYO2n8aAmbU+vxlyp"
    "LgDHL29f+ZeNO/MMBjKKsX/VnIi5Ul0Anj+80XpfvsFARm3Pq8RcqS4Ae9cng7wrD9Sg692rYq5U"
    "F4CufQCrALz6lzv/31oA2k4DwttXdwwMUoix3jYPSiz/txaA8P74UAQw+a8Qc6PE5N9qAO4eXut8"
    "l57aIxBvRHL5HgXx4zpvTLKpHWlXZrY/+UPMjeoD0HVJcH5PoMaNwba3KxviDUqGHpgiMOyGX9c7"
    "VJW69FcsAItOBeZDEAOxlpuF2m78KPn369qNNnnX+17H2F008Usv/YsFIC51LBOBWnQtAUud9qzy"
    "OQoMK+ZAict+xQOQLQJjC0Cfd0+m7slfLADL7gkIwPCTv2tp2uezFVhN6XP+UQXg8upAzauBrtBt"
    "ezC03ZA1/6pkkm7uVb/kbv9oAzB/s1DXABWAza62LpekJuuwYkyXuslnpwIwvz8QBywGbA1BGEMA"
    "uu7EDL/+8s3C929g+Qkf39c45mM5z9+pANSoZABicncN2DG/OiEAArChJzHHuCGFAAjAli61lnr6"
    "DAEQgC0EYJkdf98bBKDCACy74w8CUFkA+uz4gwBUFAA7/ghA0gDY8UcAkgbAjj8CkDgAdvwRgKQB"
    "sOOPACQNgB1/BCBpAOz4IwBJA2DHHwFIGgA7/ghA4gDY8UcAkgbAjj8CkDQAdvwRgKQBsOOPACQN"
    "gB1/BCBpAOz4IwCJA2DHHwFIGgA7/ghA0gDY8UcAkgbAjj8CkDQAdvwRgKQBsOOPACQOgB1/BCBp"
    "AOz4IwBJA2DHHwFIGoCuc347/ghA5QGw448ACIAdfwRAAOz4IwDpA2DyIwBJA2DHHwFIGgA7/ghA"
    "0gDY8UcAkgbAjj8CULm2R3zt+CMACbQ95mvyIwBJ3D289vGJv/gxfu64IACAAAACAAgAIACAAAAC"
    "AAgAIACAAAACAAgAIACAAAACAAgAIACAAAACAAIACAAgAIAAACkCcOpAQEqnEYATBwJSOokATB0I"
    "SGnaxJcDAQnP/y+/zn/y2gGBVF7PB2DigEAqk2b+yyoAEr76/y8CZw4OVO2safu6OBUQAah08n+y"
    "9BcBMPlFAEz+xsYgZNjw6xGBiRDA7k38lV71F8RgevHsgAeIYGQP9lzMzWmfOf0v+Q/P/yIvqv4A"
    "AAAASUVORK5CYII="
)

# A git-branch mark, not GitHub's Octocat: that mark is GitHub's trademark
# and reproducing it here would be overstepping. Swap in the official one
# from https://github.com/logos if you'd rather use it.
GITHUB_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAA6klEQVR42u2Yyw3DIAyGGSSDcOga"
    "DJJBWIRrd2AQTt0ihYpIVRQJxw8gii39R8wX+YFjY9TUjPm8XzbLZ4UsNxtcgdoOShjQcqZqkYT7"
    "1wL040/OBhJoOdyA+12ChNsVKYAOALgBcrflYx0JuHJEgfL1gZjDeMB6QWw4twxRCNRCSdjcARaa"
    "5Wg3/tADLVMuB65+6ChOT/I5oatXArD6AFW+AiogADDVBnxV3QDJmh0wzRriXXbKIpEe+xVQAUcD"
    "osctaTDSwNoDMIpPw8R1h9z/RK/nTQGlVx8jNluXl0e3Wb89c4Gpdnf7Ar+o9GrR/YrRAAAAAElF"
    "TkSuQmCC"
)

WORKSHOP_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAABMUlEQVR42u2YwQ3DIAxFMwiDcOga"
    "3HrsAGUQFuHaHTJITt0iBYlW1DU0WBCcFkv/EAXJL8bfgkzTiBEM4347aSe7s/QWMOE0O62d5HOL"
    "HGBPuBdkCk5Gixb/vGNLyZDzmV9ii2y0QHXoexXlt1nAjuakAQbzqNbbTgIMcCvc/vPlOjutBKna"
    "gAoAWp+ECOdl/6uC7HvwEC4egD8PGAzi3xvEOCWSLQa1BGNGB7iFeFoxzQc1Al0i22KLP45CvhLE"
    "k7NoYpJQScHCJK1BMteNLKCJjdDpopY2EtL4BhkTOnXiji5cM2H8GJBbpr7CbnUjArdUujTZb6U2"
    "JYCV4UxJwypkRLwBInALcfTUmRDgazE4MfUMAMgLDgHkBZcA5AOX2GI+cODnEj84MH74wY04ajwA"
    "EqReq6NHICYAAAAASUVORK5CYII="
)

GITHUB_URL = "https://github.com/ABTT-ESK"
WORKSHOP_URL = ("https://steamcommunity.com/sharedfiles/filedetails/"
                "?id=3767910705")


def load_png(master, data, subsample=1):
    """Return a PhotoImage, or None if Tk can't decode PNG."""
    try:
        image = tk.PhotoImage(master=master, data=data)
        if subsample > 1:
            image = image.subsample(subsample, subsample)
        return image
    except Exception:
        return None


def load_logo(master, subsample=1):
    return load_png(master, LOGO_PNG_B64, subsample)


def quest_id_from_label(text, fallback=1):
    """Pull the leading number out of '12 - Catch a Fish'."""
    match = re.match(r"\s*(\d+)", text or "")
    return int(match.group(1)) if match else fallback


def default_menu_config():
    cfg = {
        "ConfigVersion": 3,
        "Position": "BOTTOM_CENTER",
        "PanelWidth": 0.6,
        "PanelHeight": 0.52,
        "OffsetX": 0.0,
        "OffsetY": 0.0,
        "EdgeMargin": 0.03,
    }
    for key, _label, default in COLOR_FIELDS:
        cfg[key] = list(default)
    cfg["WindowBorderThickness"] = 2
    cfg["VisitedResponseOpacity"] = 0.4
    cfg["FontStyle"] = "DEFAULT"
    cfg["ShowResponseIcons"] = False
    cfg["LayoutOverride"] = ""
    return cfg


def new_response():
    return {
        "Text": "New option",
        "NextNodeID": -1,
        "RequiredQuestID": -1,
        "ActionType": "NONE",
    }


def new_node(node_id):
    return {
        "ID": node_id,
        "Type": "STANDARD",
        "SpeakerText": "",
        "VoiceLineIDs": [],
        "SpeakerLines": [],
        "Responses": [],
    }


def new_tree():
    return {
        "ID": 1,
        "NPCIDs": [],
        "TraderIDs": [],
        "TraderClassNames": [],
        "TraderPositions": [],
        "TraderPositionRadius": 8.0,
        "TraderMinKeyMatches": 2,
        "RootNodeID": 1,
        "GreetingVoiceLineIDs": [],
        "FarewellVoiceLineIDs": [],
        "QuestListTexts": [],
        "NoQuestsTexts": [],
        "NoQuestsBackTexts": [],
        "NoQuestsLeaveTexts": [],
        "NoQuestsVoiceLineIDs": [],
        "QuestListBackTexts": [],
        "OfferBackTexts": [],
        "InProgressBackTexts": [],
        "TurnInBackTexts": [],
        "Nodes": [new_node(1)],
    }


def new_quest_entry(quest_id=1):
    return {
        "QuestID": quest_id,
        "AcceptTexts": [],
        "DeclineTexts": [],
        "TurnInTexts": [],
        "NotYetTexts": [],
        "InProgressTexts": [],
        "QuestListTexts": [],
        "NoQuestsTexts": [],
        "NoQuestsBackTexts": [],
        "NoQuestsLeaveTexts": [],
        "QuestListBackTexts": [],
        "OfferBackTexts": [],
        "InProgressBackTexts": [],
        "TurnInBackTexts": [],
        "RewardSelectText": "",
    }


# ---------------------------------------------------------------- helpers

def argb_to_hex(argb):
    """[A,R,G,B] -> #rrggbb (alpha ignored, used for on-screen swatches)."""
    try:
        _a, r, g, b = [max(0, min(255, int(v))) for v in argb[:4]]
    except Exception:
        r, g, b = 255, 255, 255
    return "#%02x%02x%02x" % (r, g, b)


def blend_over(argb, bg_hex="#202020"):
    """Approximate what an ARGB colour looks like over a backdrop."""
    try:
        a, r, g, b = [max(0, min(255, int(v))) for v in argb[:4]]
    except Exception:
        return bg_hex
    br = int(bg_hex[1:3], 16)
    bg = int(bg_hex[3:5], 16)
    bb = int(bg_hex[5:7], 16)
    f = a / 255.0
    return "#%02x%02x%02x" % (
        int(r * f + br * (1 - f)),
        int(g * f + bg * (1 - f)),
        int(b * f + bb * (1 - f)),
    )


def safe_int(value, fallback=0):
    try:
        return int(str(value).strip())
    except Exception:
        return fallback


def safe_float(value, fallback=0.0):
    try:
        return float(str(value).strip())
    except Exception:
        return fallback


def write_json(path, data):
    folder = os.path.dirname(path)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=4, ensure_ascii=False)


def add_entry_undo(entry):
    """Give a tk/ttk Entry a simple undo/redo stack on Ctrl+Z / Ctrl+Y.

    tk.Text has undo built in; Entry doesn't, so we snapshot the text after
    each edit and step back through the snapshots. After restoring we fire a
    synthetic <KeyRelease> so whatever the entry normally commits on typing
    (marking the file dirty, updating the outline) stays in sync.
    """
    undo_stack = [entry.get()]
    redo_stack = []
    state = {"last": entry.get()}

    def snapshot(_event=None):
        current = entry.get()
        if current != state["last"]:
            undo_stack.append(current)
            state["last"] = current
            del redo_stack[:]

    def restore(value):
        entry.delete(0, tk.END)
        entry.insert(0, value)
        state["last"] = value
        entry.event_generate("<KeyRelease>")

    def undo(_event=None):
        snapshot()
        if len(undo_stack) > 1:
            redo_stack.append(undo_stack.pop())
            restore(undo_stack[-1])
        return "break"

    def redo(_event=None):
        if redo_stack:
            value = redo_stack.pop()
            undo_stack.append(value)
            restore(value)
        return "break"

    def resync(_event=None):
        # Editors reuse one widget for many rows, so refresh the baseline
        # whenever the value is replaced from outside (loading a new item).
        current = entry.get()
        if current != state["last"]:
            del undo_stack[:]
            undo_stack.append(current)
            del redo_stack[:]
            state["last"] = current

    entry.bind("<KeyRelease>", snapshot, add="+")
    entry.bind("<FocusIn>", resync, add="+")
    entry.bind("<Control-z>", undo, add="+")
    entry.bind("<Control-Z>", undo, add="+")
    entry.bind("<Control-y>", redo, add="+")
    entry.bind("<Control-Shift-Z>", redo, add="+")
    return entry


# ---------------------------------------------------------------- spellcheck
# Powered by the optional pyspellchecker package. Everything degrades to a
# no-op when it isn't importable, so the app never depends on it being there.

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’]*")

# Words worth flagging: skip short tokens, anything with a digit, ALL-CAPS
# acronyms (NPC, ID) and CamelCase class names (ExpansionTraderAIDenis) -
# a dialogue tool is full of those and underlining them is just noise.
def spell_checkable(token):
    if len(token) < 3:
        return False
    if any(ch.isdigit() for ch in token):
        return False
    if token.isupper():
        return False
    if any(ch.isupper() for ch in token[1:]):
        return False
    return True


class SpellManager:
    """One shared spellchecker plus a user dictionary the player can grow.

    The English word list is heavy to build, so it's created lazily the first
    time something is actually checked, not at import or startup.
    """

    def __init__(self):
        self.checker = None
        self._built = False
        self.custom = set()
        self.custom_path = os.path.join(
            os.path.expanduser("~"), ".dialogueforge_dictionary.txt")

    def _build(self):
        if self._built:
            return
        self._built = True
        if SpellChecker is None:
            return
        try:
            self.checker = SpellChecker()
        except Exception:
            self.checker = None
            return
        try:
            with open(self.custom_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    word = line.strip().lower()
                    if word:
                        self.custom.add(word)
        except FileNotFoundError:
            pass
        except Exception:
            pass
        if self.custom:
            self.checker.word_frequency.load_words(self.custom)

    def available(self):
        self._build()
        return self.checker is not None

    def known(self, word):
        if not self.available():
            return True
        lowered = word.lower()
        return lowered in self.custom or lowered in self.checker

    def suggest(self, word, limit=7):
        if not self.available():
            return []
        try:
            candidates = self.checker.candidates(word)
        except Exception:
            candidates = None
        if not candidates:
            return []
        ordered = []
        best = self.checker.correction(word)
        if best and best in candidates:
            ordered.append(best)
        for candidate in candidates:
            if candidate not in ordered:
                ordered.append(candidate)
        return ordered[:limit]

    def add_word(self, word):
        word = (word or "").strip().lower()
        if not word:
            return
        self.custom.add(word)
        if self.checker is not None:
            self.checker.word_frequency.load_words([word])
        try:
            with open(self.custom_path, "a", encoding="utf-8") as handle:
                handle.write(word + "\n")
        except Exception:
            pass


SPELL = SpellManager()


def _popup_menu(menu, event):
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()


def attach_text_spellcheck(text):
    """Red-underline misspellings in a tk.Text and offer fixes on right-click."""
    if SpellChecker is None:
        return
    text.tag_configure("spell_bad", foreground="#e05555", underline=True)
    pending = {"id": None}

    def recheck():
        pending["id"] = None
        if not SPELL.available():
            return
        text.tag_remove("spell_bad", "1.0", tk.END)
        content = text.get("1.0", "end-1c")
        for match in WORD_RE.finditer(content):
            token = match.group()
            if not spell_checkable(token) or SPELL.known(token):
                continue
            text.tag_add("spell_bad",
                         "1.0+%dc" % match.start(),
                         "1.0+%dc" % match.end())

    def schedule(_event=None):
        if pending["id"] is not None:
            text.after_cancel(pending["id"])
        pending["id"] = text.after(400, recheck)

    def on_modified(_event=None):
        if text.edit_modified():
            text.edit_modified(False)
            schedule()

    def replace(start, end, word):
        text.delete(start, end)
        text.insert(start, word)
        recheck()
        text.event_generate("<KeyRelease>")

    def on_right_click(event):
        text.focus_set()
        index = text.index("@%d,%d" % (event.x, event.y))
        start = text.index("%s wordstart" % index)
        end = text.index("%s wordend" % index)
        word = text.get(start, end).strip()
        menu = tk.Menu(text, tearoff=0)
        if word and spell_checkable(word) and not SPELL.known(word):
            suggestions = SPELL.suggest(word)
            if suggestions:
                for suggestion in suggestions:
                    menu.add_command(
                        label=suggestion,
                        command=lambda w=suggestion, s=start, e=end:
                        replace(s, e, w))
            else:
                menu.add_command(label="(no suggestions)", state="disabled")
            menu.add_command(
                label="Add \"%s\" to dictionary" % word,
                command=lambda w=word: (SPELL.add_word(w), recheck()))
            menu.add_separator()
        menu.add_command(label="Cut",
                         command=lambda: text.event_generate("<<Cut>>"))
        menu.add_command(label="Copy",
                         command=lambda: text.event_generate("<<Copy>>"))
        menu.add_command(label="Paste",
                         command=lambda: text.event_generate("<<Paste>>"))
        _popup_menu(menu, event)
        return "break"

    text.bind("<<Modified>>", on_modified, add="+")
    text.bind("<Button-3>", on_right_click, add="+")
    text.after_idle(lambda: text.edit_modified(False))


def attach_entry_spellcheck(entry):
    """Right-click spelling suggestions for a single-line Entry.

    Entries can't underline individual words the way a Text can, so the fix is
    offered through the context menu instead."""
    if SpellChecker is None:
        return

    def word_span(x):
        value = entry.get()
        try:
            index = entry.index("@%d" % x)
        except Exception:
            index = len(value)
        left = index
        while left > 0 and (value[left - 1].isalpha()
                            or value[left - 1] in "'’"):
            left -= 1
        right = index
        while right < len(value) and (value[right].isalpha()
                                      or value[right] in "'’"):
            right += 1
        return left, right, value[left:right]

    def replace(left, right, word):
        entry.delete(left, right)
        entry.insert(left, word)
        entry.event_generate("<KeyRelease>")

    def on_right_click(event):
        entry.focus_set()
        left, right, word = word_span(event.x)
        menu = tk.Menu(entry, tearoff=0)
        if word and spell_checkable(word) and not SPELL.known(word):
            suggestions = SPELL.suggest(word)
            if suggestions:
                for suggestion in suggestions:
                    menu.add_command(
                        label=suggestion,
                        command=lambda w=suggestion, l=left, r=right:
                        replace(l, r, w))
            else:
                menu.add_command(label="(no suggestions)", state="disabled")
            menu.add_command(
                label="Add \"%s\" to dictionary" % word,
                command=lambda w=word: SPELL.add_word(w))
            menu.add_separator()
        menu.add_command(label="Cut",
                         command=lambda: entry.event_generate("<<Cut>>"))
        menu.add_command(label="Copy",
                         command=lambda: entry.event_generate("<<Copy>>"))
        menu.add_command(label="Paste",
                         command=lambda: entry.event_generate("<<Paste>>"))
        _popup_menu(menu, event)
        return "break"

    entry.bind("<Button-3>", on_right_click, add="+")


# ---------------------------------------------------------------- widgets

class StringListEditor(ttk.LabelFrame):
    """Reusable add/remove/reorder editor for a list of strings."""

    def __init__(self, master, title, hint="", height=5, on_change=None,
                 on_focus=None):
        ttk.LabelFrame.__init__(self, master, text=title)
        self.on_change = on_change
        self.on_focus = on_focus
        self.items = []

        if hint:
            ttk.Label(self, text=hint, wraplength=340,
                      style="Hint.TLabel").grid(
                row=0, column=0, columnspan=3, sticky="w", padx=6, pady=(4, 0))

        self.listbox = tk.Listbox(self, height=height, exportselection=False)
        self.listbox.grid(row=1, column=0, columnspan=2,
                          sticky="nsew", padx=(6, 0), pady=4)
        scroll = ttk.Scrollbar(self, orient="vertical",
                               command=self.listbox.yview)
        scroll.grid(row=1, column=2, sticky="ns", pady=4, padx=(0, 6))
        self.listbox.configure(yscrollcommand=scroll.set)

        self.entry = ttk.Entry(self)
        self.entry.grid(row=2, column=0, sticky="ew", padx=(6, 4), pady=(0, 4))
        self.entry.bind("<Return>", lambda _e: self.add())
        add_entry_undo(self.entry)
        attach_entry_spellcheck(self.entry)

        buttons = ttk.Frame(self)
        buttons.grid(row=2, column=1, columnspan=2, sticky="e",
                     padx=(0, 6), pady=(0, 4))
        ttk.Button(buttons, text="Add", width=6,
                   command=self.add).pack(side="left")
        ttk.Button(buttons, text="Del", width=5,
                   command=self.remove).pack(side="left", padx=2)
        ttk.Button(buttons, text="\u2191", width=3,
                   command=lambda: self.move(-1)).pack(side="left")
        ttk.Button(buttons, text="\u2193", width=3,
                   command=lambda: self.move(1)).pack(side="left")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        if on_focus:
            self.listbox.bind("<FocusIn>", lambda _e: on_focus(), add="+")
            self.entry.bind("<FocusIn>", lambda _e: on_focus(), add="+")
            self.listbox.bind("<Button-1>", lambda _e: on_focus(), add="+")

    def _fire(self):
        if self.on_change:
            self.on_change()

    def set_items(self, items):
        self.items = [str(i) for i in (items or [])]
        self.refresh()

    def get_items(self):
        return list(self.items)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for item in self.items:
            self.listbox.insert(tk.END, item)

    def add(self):
        value = self.entry.get().strip()
        if not value:
            return
        self.items.append(value)
        self.entry.delete(0, tk.END)
        self.refresh()
        self._fire()

    def remove(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        del self.items[selection[0]]
        self.refresh()
        self._fire()

    def move(self, delta):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        target = index + delta
        if target < 0 or target >= len(self.items):
            return
        self.items[index], self.items[target] = \
            self.items[target], self.items[index]
        self.refresh()
        self.listbox.selection_set(target)
        self._fire()


class CollapsibleSection(ttk.Frame):
    """A titled panel whose body shows or hides when its header is clicked.

    Lets a tab read as a short list of section headers you open as needed,
    instead of every field being on screen at once. Add this section's widgets
    to content()."""

    def __init__(self, master, title, expanded=False, subtitle=""):
        ttk.Frame.__init__(self, master, style="Section.TFrame")
        self._expanded = bool(expanded)

        self.header = ttk.Frame(self, style="SectionHeader.TFrame",
                                cursor="hand2")
        self.header.pack(fill="x")
        self._arrow = ttk.Label(self.header, width=2,
                                style="SectionTitle.TLabel", cursor="hand2")
        self._arrow.pack(side="left", padx=(6, 0), pady=3)
        self._title = ttk.Label(self.header, text=title,
                                style="SectionTitle.TLabel", cursor="hand2")
        self._title.pack(side="left", pady=3)
        if subtitle:
            ttk.Label(self.header, text=subtitle, style="SectionSub.TLabel",
                      cursor="hand2").pack(side="left", padx=10, pady=3)

        # The whole header bar is the click target, not just the words.
        for widget in (self.header, self._arrow, self._title):
            widget.bind("<Button-1>", self._toggle)

        self.body = ttk.Frame(self, style="SectionBody.TFrame")
        self._sync()

    def _toggle(self, _event=None):
        self._expanded = not self._expanded
        self._sync()

    def _sync(self):
        self._arrow.configure(text="▾" if self._expanded else "▸")
        if self._expanded:
            self.body.pack(fill="x")
        else:
            self.body.pack_forget()

    def set_expanded(self, expanded):
        if bool(expanded) != self._expanded:
            self._toggle()

    def content(self):
        """The frame to place this section's widgets in."""
        return self.body


class SpeakerLinesEditor(ttk.LabelFrame):
    """Extra spoken lines for a node. The mod picks one at random from the
    node's main line plus whichever of these the player qualifies for; each
    line can be locked to a completed quest and carry its own voice lines."""

    def __init__(self, master, app, on_change=None):
        ttk.LabelFrame.__init__(
            self, master, text="Extra spoken lines (optional)")
        self.app = app
        self.on_change = on_change
        self.lines = []
        self.current = None
        self.loading = False

        ttk.Label(
            self,
            text="One line is picked at random from the main line above plus "
                 "any of these the player qualifies for. Lock a line to a "
                 "completed quest to reveal it later, so a greeting keeps "
                 "feeling fresh.",
            wraplength=430, style="Hint.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", padx=6, pady=(4, 2))

        self.listbox = tk.Listbox(self, height=4, exportselection=False)
        self.listbox.grid(row=1, column=0, columnspan=2, sticky="nsew",
                          padx=(6, 0), pady=4)
        scroll = ttk.Scrollbar(self, orient="vertical",
                               command=self.listbox.yview)
        scroll.grid(row=1, column=2, sticky="ns", pady=4, padx=(0, 6))
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        tools = ttk.Frame(self)
        tools.grid(row=2, column=0, columnspan=3, sticky="w",
                   padx=6, pady=(0, 4))
        ttk.Button(tools, text="Add line", width=9,
                   command=self.add).pack(side="left")
        ttk.Button(tools, text="Delete", width=8,
                   command=self.remove).pack(side="left", padx=3)
        ttk.Button(tools, text="↑", width=3,
                   command=lambda: self.move(-1)).pack(side="left")
        ttk.Button(tools, text="↓", width=3,
                   command=lambda: self.move(1)).pack(side="left")

        self.detail = ttk.Frame(self)
        self.detail.grid(row=3, column=0, columnspan=3, sticky="ew",
                         padx=6, pady=(0, 6))
        self.detail.columnconfigure(0, weight=1)

        ttk.Label(self.detail, text="Line text").grid(
            row=0, column=0, sticky="w")
        self.text = tk.Text(self.detail, height=3, wrap="word", undo=True,
                            autoseparators=True, maxundo=-1)
        self.text.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        self.text.bind("<KeyRelease>", lambda _e: self.commit_current())
        attach_text_spellcheck(self.text)

        # Both quest dropdowns share one row - there's plenty of width and it
        # keeps the panel short. Labels size to their text so nothing clips.
        locks = ttk.Frame(self.detail)
        locks.grid(row=2, column=0, sticky="w", pady=(0, 2))

        gate_group = ttk.Frame(locks)
        gate_group.pack(side="left", padx=(0, 24))
        ttk.Label(gate_group, text="Quest lock").pack(side="left")
        self.gate = ttk.Combobox(gate_group, width=24)
        self.gate.pack(side="left", padx=(6, 4))
        self.gate.bind("<<ComboboxSelected>>", self.on_gate_changed)
        self.gate.bind("<KeyRelease>", self.on_gate_changed)
        ttk.Button(gate_group, text="Browse...", width=10,
                   command=self.browse_gate).pack(side="left")

        override_group = ttk.Frame(locks)
        override_group.pack(side="left")
        ttk.Label(override_group, text="Standard greeting after").pack(
            side="left")
        self.override = ttk.Combobox(override_group, width=24)
        self.override.pack(side="left", padx=(6, 4))
        self.override.bind("<<ComboboxSelected>>", self.on_override_changed)
        self.override.bind("<KeyRelease>", self.on_override_changed)
        ttk.Button(override_group, text="Browse...", width=10,
                   command=self.browse_override).pack(side="left")

        notes = ttk.Frame(self.detail)
        notes.grid(row=3, column=0, sticky="ew", pady=(0, 4))
        notes.columnconfigure(0, weight=1)
        notes.columnconfigure(1, weight=1)
        self.gate_note = ttk.Label(notes, text="", wraplength=340,
                                   style="Hint.TLabel", justify="left")
        self.gate_note.grid(row=0, column=0, sticky="w", padx=(0, 16))
        self.override_note = ttk.Label(notes, text="", wraplength=340,
                                       style="Hint.TLabel", justify="left")
        self.override_note.grid(row=0, column=1, sticky="w")

        self.voice = StringListEditor(
            self.detail, "Voice lines for this line (optional)",
            "Played only when this line is the one shown.", height=3,
            on_change=self.commit_current)
        self.voice.grid(row=4, column=0, sticky="ew")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.set_current(None)

    def _fire(self):
        if self.on_change and not self.loading:
            self.on_change()

    def set_lines(self, lines):
        self.lines = [dict(line) for line in (lines or [])]
        for line in self.lines:
            line["VoiceLineIDs"] = list(line.get("VoiceLineIDs") or [])
        self.refresh_list()
        self.set_current(None)

    def get_lines(self):
        out = []
        for line in self.lines:
            gate = line.get("RequiredQuestID", -1)
            override = line.get("OverrideQuestID", -1)
            out.append({
                "Text": line.get("Text", ""),
                "RequiredQuestID": gate if gate and gate > 0 else -1,
                "OverrideQuestID": override if override and override > 0 else -1,
                "VoiceLineIDs": list(line.get("VoiceLineIDs") or []),
            })
        return out

    def refresh_quest_choices(self):
        self.gate["values"] = [NOT_LOCKED_LABEL] + self.app.quest_labels()
        self.override["values"] = [OVERRIDE_NONE_LABEL] + self.app.quest_labels()

    def label_for(self, line):
        text = (line.get("Text") or "").strip() or "(no text)"
        if len(text) > 40:
            text = text[:37] + "..."
        tags = []
        gate = line.get("RequiredQuestID", -1)
        if gate and gate > 0:
            tags.append("needs %s" % self.app.quest_label(gate))
        override = line.get("OverrideQuestID", -1)
        if override and override > 0:
            tags.append("greeting after %s" % self.app.quest_label(override))
        if tags:
            return "%s   [%s]" % (text, "; ".join(tags))
        return text

    def refresh_list(self, keep_index=None):
        self.listbox.delete(0, tk.END)
        for line in self.lines:
            self.listbox.insert(tk.END, self.label_for(line))
        if keep_index is not None and 0 <= keep_index < len(self.lines):
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(keep_index)

    def on_select(self, _event=None):
        selection = self.listbox.curselection()
        if selection:
            self.set_current(selection[0])

    def set_current(self, index):
        self.refresh_quest_choices()
        if index is None or index >= len(self.lines):
            self.current = None
            self.loading = True
            self.text.delete("1.0", tk.END)
            self.gate.set(NOT_LOCKED_LABEL)
            self.override.set(OVERRIDE_NONE_LABEL)
            self.voice.set_items([])
            self.loading = False
            self._set_detail_enabled(False)
            self.update_gate_note()
            self.update_override_note()
            return
        self.current = self.lines[index]
        self.loading = True
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", self.current.get("Text", ""))
        self.text.edit_reset()
        gate = self.current.get("RequiredQuestID", -1)
        self.gate.set(self.app.quest_label(gate)
                      if gate and gate > 0 else NOT_LOCKED_LABEL)
        override = self.current.get("OverrideQuestID", -1)
        self.override.set(self.app.quest_label(override)
                          if override and override > 0 else OVERRIDE_NONE_LABEL)
        self.voice.set_items(self.current.get("VoiceLineIDs") or [])
        self.loading = False
        self._set_detail_enabled(True)
        self.update_gate_note()
        self.update_override_note()

    def _set_detail_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.text.configure(state=state)
        self.gate.configure(state=state)
        self.override.configure(state=state)

    def add(self):
        self.lines.append(
            {"Text": "New line", "RequiredQuestID": -1,
             "OverrideQuestID": -1, "VoiceLineIDs": []})
        index = len(self.lines) - 1
        self.refresh_list(keep_index=index)
        self.set_current(index)
        self._fire()

    def remove(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        del self.lines[selection[0]]
        self.refresh_list()
        self.set_current(None)
        self._fire()

    def move(self, delta):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        target = index + delta
        if target < 0 or target >= len(self.lines):
            return
        self.lines[index], self.lines[target] = \
            self.lines[target], self.lines[index]
        self.refresh_list(keep_index=target)
        self.set_current(target)
        self._fire()

    def on_gate_changed(self, _event=None):
        self.update_gate_note()
        self.commit_current()

    def on_override_changed(self, _event=None):
        self.update_override_note()
        self.commit_current()

    def update_gate_note(self):
        if not self.current:
            self.gate_note.configure(text="")
            return
        text = self.gate.get().strip()
        if not text or text == NOT_LOCKED_LABEL:
            self.gate_note.configure(text="Always eligible to be shown.")
            return
        quest_id = quest_id_from_label(text, 0)
        if quest_id <= 0:
            self.gate_note.configure(
                text="Not a quest yet - pick one, or choose \"%s\"."
                     % NOT_LOCKED_LABEL)
        elif self.app.quest_index and self.app.quest_lookup(quest_id) is None:
            self.gate_note.configure(
                text="Quest %d isn't in your quest folder." % quest_id)
        else:
            self.gate_note.configure(
                text="Only shown once quest %d is COMPLETED." % quest_id)

    def update_override_note(self):
        if not self.current:
            self.override_note.configure(text="")
            return
        text = self.override.get().strip()
        if not text or text == OVERRIDE_NONE_LABEL:
            self.override_note.configure(
                text="Just one of the random lines - doesn't take over.")
            return
        quest_id = quest_id_from_label(text, 0)
        if quest_id <= 0:
            self.override_note.configure(
                text="Not a quest yet - pick one, or choose \"%s\"."
                     % OVERRIDE_NONE_LABEL)
        elif self.app.quest_index and self.app.quest_lookup(quest_id) is None:
            self.override_note.configure(
                text="Quest %d isn't in your quest folder." % quest_id)
        else:
            self.override_note.configure(
                text="Becomes the fixed greeting once quest %d is COMPLETED "
                     "(highest such quest wins)." % quest_id)

    def _browse_into(self, combo, note_fn, hint):
        if not self.current:
            return
        if not self.app.ensure_quest_folder():
            return
        if not self.app.quest_index:
            messagebox.showinfo(
                APP_TITLE, "No quest configs found in that folder.",
                parent=self)
            return
        dialog = ChooserDialog(
            self.app, "Pick a quest", self.app.quest_index, hint)
        self.wait_window(dialog)
        if dialog.chosen is None:
            return
        combo.set(self.app.quest_label(dialog.chosen))
        note_fn()
        self.commit_current()

    def browse_gate(self):
        self._browse_into(
            self.gate, self.update_gate_note,
            "This line only shows once the player has COMPLETED the quest.")

    def browse_override(self):
        self._browse_into(
            self.override, self.update_override_note,
            "Once the player has COMPLETED this quest, this line becomes the "
            "NPC's standard greeting.")

    def commit_current(self):
        if self.loading or not self.current:
            return
        self.current["Text"] = self.text.get("1.0", "end-1c")
        gate_text = self.gate.get().strip()
        if not gate_text or gate_text == NOT_LOCKED_LABEL:
            self.current["RequiredQuestID"] = -1
        else:
            self.current["RequiredQuestID"] = max(
                1, quest_id_from_label(gate_text, 1))
        override_text = self.override.get().strip()
        if not override_text or override_text == OVERRIDE_NONE_LABEL:
            self.current["OverrideQuestID"] = -1
        else:
            self.current["OverrideQuestID"] = max(
                1, quest_id_from_label(override_text, 1))
        self.current["VoiceLineIDs"] = self.voice.get_items()
        index = self.lines.index(self.current)
        self.listbox.delete(index)
        self.listbox.insert(index, self.label_for(self.current))
        self.listbox.selection_set(index)
        self._fire()


class ScrollFrame(ttk.Frame):
    """A vertically scrolling container. Add children to .inner.

    Needed because the taller tabs don't fit a 1080p screen once the window
    is anything less than maximised, and clipped controls are unreachable.
    The scrollbar hides itself whenever everything already fits.
    """

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.scrollable = False

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.canvas._scrollframe = self
        self.canvas._theme_bg = "bg"
        self.vbar = ttk.Scrollbar(self, orient="vertical",
                                  command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.on_scroll)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = ttk.Frame(self.canvas)
        self.window = self.canvas.create_window((0, 0), window=self.inner,
                                                anchor="nw")
        self.inner.bind("<Configure>", self.on_inner_resize)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def on_inner_resize(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_resize(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)

    def on_scroll(self, first, last):
        needed = not (float(first) <= 0.0 and float(last) >= 1.0)
        if needed != self.scrollable:
            self.scrollable = needed
            if needed:
                self.vbar.pack(side="right", fill="y")
            else:
                self.vbar.pack_forget()
        self.vbar.set(first, last)

    def scroll_by(self, event):
        if not self.scrollable:
            return
        if getattr(event, "delta", 0):
            steps = -1 if event.delta > 0 else 1
        else:
            steps = -1 if getattr(event, "num", 5) == 4 else 1
        self.canvas.yview_scroll(steps * 3, "units")


class ColorRow(ttk.Frame):
    """Swatch + colour picker + alpha slider, storing [A,R,G,B]."""

    def __init__(self, master, label, value, on_change=None):
        ttk.Frame.__init__(self, master)
        self.value = list(value)
        self.on_change = on_change

        ttk.Label(self, text=label, width=22).grid(row=0, column=0, sticky="w")
        self.swatch = tk.Label(self, width=6, relief="sunken", bd=1)
        # its whole job is to show the chosen colour, so the app theme
        # must not repaint it
        self.swatch._skip_theme = True
        self.swatch.grid(row=0, column=1, padx=4)
        ttk.Button(self, text="Pick colour", width=12,
                   command=self.pick).grid(row=0, column=2, padx=2)

        ttk.Label(self, text="Alpha").grid(row=0, column=3, padx=(10, 2))
        self.alpha = tk.IntVar(value=self.value[0])
        self.slider = ttk.Scale(self, from_=0, to=255, orient="horizontal",
                                length=130)
        self.slider.grid(row=0, column=4)
        self.alpha_label = ttk.Label(self, width=4, text=str(self.value[0]))
        self.alpha_label.grid(row=0, column=5, padx=(4, 0))

        self.rgb_label = ttk.Label(self, width=18, style="Hint.TLabel")
        self.rgb_label.grid(row=0, column=6, padx=(8, 0), sticky="w")

        # Attach the handler only after the initial value and the labels it
        # touches exist, so building the row (which calls set()) can't fire
        # _alpha_moved before alpha_label is created or mark the editor dirty.
        self.slider.set(self.value[0])
        self.slider.configure(command=self._alpha_moved)

        self.refresh()

    def _alpha_moved(self, _event=None):
        self.value[0] = int(float(self.slider.get()))
        self.refresh()
        if self.on_change:
            self.on_change()

    def pick(self):
        result = colorchooser.askcolor(color=argb_to_hex(self.value),
                                       parent=self)
        if not result or not result[0]:
            return
        r, g, b = [int(c) for c in result[0]]
        self.value[1], self.value[2], self.value[3] = r, g, b
        self.refresh()
        if self.on_change:
            self.on_change()

    def refresh(self):
        self.swatch.configure(background=blend_over(self.value))
        self.alpha_label.configure(text=str(self.value[0]))
        self.rgb_label.configure(
            text="[%d, %d, %d, %d]" % tuple(self.value[:4]))

    def set_value(self, value):
        self.value = list(value)
        self.slider.set(self.value[0])
        self.refresh()

    def get_value(self):
        return list(self.value)


# ---------------------------------------------------------------- validation
# Kept at module level so the same rules run whether you're checking the
# tab you're editing or sweeping every file in the profile folder.

def kind_and_key_from_path(path):
    """Work out what a dialogue file is for from the folder holding it."""
    folder = os.path.basename(os.path.dirname(path))
    if folder.startswith("NPC_"):
        return "NPC", folder[4:]
    if folder.startswith("Trader_"):
        return "TRADER", folder[7:]
    if folder == "Shared":
        return "SHARED", ""
    return None, folder


def validate_tree_dict(data, kind, key, quest_index=None):
    issues = []
    warnings = []
    nodes = data.get("Nodes") or []
    key = (key or "").strip()

    if kind is None:
        warnings.append(
            "Sitting in a folder the mod doesn't recognise. Dialogue files "
            "belong in NPC_<id>, Trader_<name> or Shared.")
    elif kind == "SHARED" and not (data.get("NPCIDs") or []):
        issues.append(
            "Shared trees must list at least one NPC ID - the mod cannot "
            "infer them from a Shared folder.")
    elif kind == "NPC" and safe_int(key, 0) <= 0:
        issues.append("Folder name doesn't contain a usable quest NPC ID.")
    elif kind == "TRADER" and not key:
        issues.append("Folder name doesn't contain a trader name.")

    if not nodes:
        issues.append("No nodes at all - this conversation can't open.")

    ids = [n.get("ID") for n in nodes]
    for node_id in set(ids):
        if ids.count(node_id) > 1:
            issues.append(
                "Node ID %s is used %d times. Duplicate IDs silently break "
                "navigation." % (node_id, ids.count(node_id)))
        if node_id is None or not isinstance(node_id, int) or node_id < 1:
            issues.append("Node IDs must be whole numbers starting at 1.")

    root = data.get("RootNodeID")
    if root not in ids:
        issues.append(
            "RootNodeID %s doesn't match any node in this tree." % root)

    # The no-quests step is only ever reached through the live quest list, so
    # wording set here is dead weight if nothing opens that list.
    has_no_quest_wording = data.get("QuestListTexts") \
        or data.get("NoQuestsTexts") \
        or data.get("NoQuestsBackTexts") \
        or data.get("NoQuestsLeaveTexts") \
        or data.get("NoQuestsVoiceLineIDs") \
        or data.get("QuestListBackTexts") \
        or data.get("OfferBackTexts") \
        or data.get("InProgressBackTexts") \
        or data.get("TurnInBackTexts")
    opens_quest_list = False
    for node in nodes:
        for response in (node.get("Responses") or []):
            if response.get("ActionType") == "SHOW_QUEST_LIST":
                opens_quest_list = True
    if has_no_quest_wording and not opens_quest_list:
        warnings.append(
            "This tree sets quest list wording but no option opens the "
            "quest list, so players will never see it.")

    for node in nodes:
        label = "Node %s" % node.get("ID")

        speaker_lines = node.get("SpeakerLines") or []
        if speaker_lines:
            has_open_line = bool((node.get("SpeakerText") or "").strip()) or \
                any(not (ln.get("RequiredQuestID", -1) or 0) > 0
                    for ln in speaker_lines)
            if not has_open_line:
                issues.append(
                    "%s has extra spoken lines but every one is quest-locked "
                    "and there's no main line, so a player who hasn't "
                    "completed those quests sees a blank line." % label)
            for line in speaker_lines:
                if not (line.get("Text") or "").strip():
                    warnings.append(
                        "%s has an extra spoken line with no text." % label)
                gate = line.get("RequiredQuestID", -1)
                if gate and gate > 0 and quest_index and \
                        not any(q["id"] == gate for q in quest_index):
                    warnings.append(
                        "%s has an extra line locked to quest %d, which isn't "
                        "in your quest folder." % (label, gate))
                override = line.get("OverrideQuestID", -1)
                if override and override > 0 and quest_index and \
                        not any(q["id"] == override for q in quest_index):
                    warnings.append(
                        "%s has an extra line set to override after quest %d, "
                        "which isn't in your quest folder." % (label, override))

        responses = node.get("Responses") or []
        if not responses:
            warnings.append(
                "%s has no options - the player can only close the window."
                % label)
        ungated = [r for r in responses
                   if not (r.get("RequiredQuestID", -1) or 0) > 0]
        if responses and not ungated:
            issues.append(
                "%s has every option gated behind a quest. Players who "
                "haven't finished them get a line with no buttons." % label)
        for response in responses:
            if not (response.get("Text") or "").strip():
                warnings.append("%s has an option with no button text."
                                % label)
            action = response.get("ActionType", "NONE")
            if action == "NONE":
                target = response.get("NextNodeID", -1)
                if target and target > 0 and target not in ids:
                    issues.append(
                        "%s points at node %s, which doesn't exist."
                        % (label, target))
            if action == "OPEN_TRADER" and kind != "TRADER":
                warnings.append(
                    "%s uses OPEN_TRADER but this isn't a trader tree."
                    % label)
            if action in ADVANCED_ACTION_TYPES:
                warnings.append(
                    "%s uses %s, which only works inside the live "
                    "quest-detail step the mod builds itself."
                    % (label, action))
            # NB: not `x or -1` here - that quietly turns 0 into -1, and
            # 0 is precisely the value this check exists to catch.
            gate = response.get("RequiredQuestID", -1)
            if gate is None:
                gate = -1
            if gate == 0:
                issues.append(
                    "%s has RequiredQuestID 0. Use -1 for 'no gate' - 0 is "
                    "treated as a real quest ID and hides the option."
                    % label)
            if gate > 0 and quest_index:
                if not any(q["id"] == gate for q in quest_index):
                    warnings.append(
                        "%s is gated on quest %d, which isn't in your quest "
                        "folder." % (label, gate))
        if node.get("Type", "STANDARD") != "STANDARD":
            warnings.append(
                "%s is type %s - those are built live by the mod and "
                "shouldn't be authored." % (label, node.get("Type")))

    reachable = set()
    frontier = [root]
    while frontier:
        current = frontier.pop()
        if current in reachable:
            continue
        reachable.add(current)
        for node in nodes:
            if node.get("ID") != current:
                continue
            for response in node.get("Responses", []):
                if response.get("ActionType", "NONE") == "NONE":
                    target = response.get("NextNodeID", -1)
                    if target and target > 0:
                        frontier.append(target)
    for node_id in ids:
        if node_id not in reachable:
            warnings.append(
                "Node %s can't be reached from the root node." % node_id)

    if kind == "TRADER":
        keys = sum([
            1 if data.get("TraderIDs") else 0,
            1 if data.get("TraderClassNames") else 0,
            1 if data.get("TraderPositions") else 0,
        ])
        wanted = safe_int(data.get("TraderMinKeyMatches", 2), 2)
        if wanted > keys:
            issues.append(
                "TraderMinKeyMatches is %s but only %d trader key(s) are "
                "filled in - this tree will never match." % (wanted, keys))
        if not any(r.get("ActionType") == "OPEN_TRADER"
                   for nd in nodes for r in nd.get("Responses", [])):
            warnings.append(
                "No option uses OPEN_TRADER, so players can't reach the "
                "shop from this conversation.")

    return issues, warnings


def validate_quest_dict(data):
    issues = []
    warnings = []
    quests = data.get("Quests")
    if quests is None:
        issues.append("No 'Quests' list in this file.")
        return issues, warnings
    ids = [q.get("QuestID") for q in quests]
    for quest_id in set(ids):
        if ids.count(quest_id) > 1:
            issues.append(
                "Quest ID %s appears more than once in this file."
                % quest_id)
    fields = ["AcceptTexts", "DeclineTexts", "TurnInTexts",
              "NotYetTexts", "InProgressTexts",
              "QuestListTexts", "NoQuestsTexts",
              "NoQuestsBackTexts", "NoQuestsLeaveTexts",
              "QuestListBackTexts", "OfferBackTexts",
              "InProgressBackTexts", "TurnInBackTexts"]
    for quest in quests:
        if not any(quest.get(f) for f in fields) \
                and not quest.get("RewardSelectText"):
            warnings.append(
                "Quest %s has no wording at all - it will use the built-in "
                "defaults." % quest.get("QuestID"))
        # The mod only reaches a quest's no-quests wording when that quest
        # supplies a spoken line, so buttons on their own never appear.
        has_buttons = quest.get("NoQuestsBackTexts") \
            or quest.get("NoQuestsLeaveTexts")
        if has_buttons and not quest.get("NoQuestsTexts"):
            warnings.append(
                "Quest %s has 'nothing left' buttons but nothing for the NPC "
                "to say. The mod only uses a quest's buttons when that same "
                "quest also has a line, so these will never show - add one, "
                "or move the buttons onto the dialogue tree."
                % quest.get("QuestID"))
    return issues, warnings


def override_uses_custom_layout(cfg):
    return bool((cfg.get("LayoutOverride") or "").strip())


def validate_menu_dict(cfg, resolved=None):
    issues = []
    warnings = []
    for key, label, _default in COLOR_FIELDS:
        value = cfg.get(key)
        if not isinstance(value, list) or len(value) < 4:
            issues.append("%s isn't a 4-number [A, R, G, B] list." % label)
        elif value[0] == 0:
            warnings.append(
                "%s has alpha 0, so it will be completely invisible." % label)
    width = safe_float(cfg.get("PanelWidth", 0.6), 0.6)
    height = safe_float(cfg.get("PanelHeight", 0.5), 0.5)
    if not 0.05 < width <= 1.0:
        issues.append("Panel width must be between 0.05 and 1.0.")
    if not 0.05 < height <= 1.0:
        issues.append("Panel height must be between 0.05 and 1.0.")
    if cfg.get("Position") not in POSITIONS:
        issues.append("Position '%s' isn't one of the nine presets."
                      % cfg.get("Position"))
    style = cfg.get("FontStyle")
    if style is None:
        warnings.append(
            "No FontStyle set. The mod defaults to DEFAULT, but writing it "
            "explicitly keeps the file readable.")
    elif style not in dict(FONT_STYLES):
        issues.append(
            "FontStyle '%s' isn't one of %s."
            % (style, ", ".join(key for key, _d in FONT_STYLES)))

    version = cfg.get("ConfigVersion")
    if isinstance(version, int) and version < 3:
        warnings.append(
            "ConfigVersion is %s. FontStyle arrived in version 2 and "
            "ShowResponseIcons in version 3 - saving from here updates it."
            % version)

    if cfg.get("ShowResponseIcons") and override_uses_custom_layout(cfg):
        warnings.append(
            "Hint icons are on but LayoutOverride is set. A custom layout "
            "needs its own icon widget, so the icons won't appear.")

    override = (cfg.get("LayoutOverride") or "").strip()
    if override and not override.endswith(".layout"):
        warnings.append(
            "LayoutOverride doesn't end in .layout - the mod will fall back "
            "to the built-in window.")
    if override and style and style != "DEFAULT":
        warnings.append(
            "FontStyle is %s but LayoutOverride is set. A custom layout "
            "brings its own fonts, so the style is ignored." % style)
    if resolved:
        x, y = resolved
        if x < -0.05 or y < -0.05 or x + width > 1.05 or y + height > 1.05:
            issues.append(
                "With these offsets the window ends up partly off-screen. "
                "Offsets aren't clamped by the mod.")
    return issues, warnings


# ---------------------------------------------------------------- chooser

class ChooserDialog(tk.Toplevel):
    """Searchable picker over the scanned Expansion configs."""

    def __init__(self, app, title, entries, hint=""):
        tk.Toplevel.__init__(self, app)
        self.app = app
        self.entries = entries
        self.chosen = None

        self.title(title)
        self.geometry("520x460")
        self.transient(app)
        self.grab_set()

        if hint:
            ttk.Label(self, text=hint, wraplength=480,
                      style="Hint.TLabel").pack(anchor="w", padx=12,
                                                pady=(12, 4))

        search_row = ttk.Frame(self)
        search_row.pack(fill="x", padx=12, pady=(4, 6))
        ttk.Label(search_row, text="Search").pack(side="left")
        self.search = ttk.Entry(search_row)
        self.search.pack(side="left", fill="x", expand=True, padx=6)
        self.search.bind("<KeyRelease>", lambda _e: self.refresh())

        self.list = ttk.Treeview(self, columns=("id", "name"),
                                 show="headings", selectmode="browse")
        self.list.heading("id", text="ID")
        self.list.heading("name", text="Name")
        self.list.column("id", width=70, anchor="w", stretch=False)
        self.list.column("name", width=400, anchor="w")
        self.list.pack(fill="both", expand=True, padx=12)
        self.list.bind("<Double-Button-1>", lambda _e: self.confirm())

        buttons = ttk.Frame(self)
        buttons.pack(fill="x", padx=12, pady=10)
        ttk.Button(buttons, text="Use this",
                   command=self.confirm).pack(side="right")
        ttk.Button(buttons, text="Cancel",
                   command=self.destroy).pack(side="right", padx=6)

        self.refresh()
        app.skin_window(self)
        self.search.focus_set()

    def refresh(self):
        needle = self.search.get().strip().lower()
        self.list.delete(*self.list.get_children())
        for entry in self.entries:
            haystack = "%s %s" % (entry["id"], entry["title"])
            if needle and needle not in haystack.lower():
                continue
            self.list.insert("", "end", iid=str(entry["id"]),
                             values=(entry["id"], entry["title"]))

    def confirm(self):
        selection = self.list.selection()
        if not selection:
            return
        self.chosen = safe_int(selection[0], None)
        self.destroy()


# ---------------------------------------------------------------- dialogue tab

class DialogueTab(ttk.Frame):
    """Three panes: an outline of the whole conversation, the editor for
    whatever is selected, and a branch map showing where you are."""

    BOX_W = 132
    BOX_H = 46
    GAP_X = 62
    GAP_Y = 26
    MARGIN = 18

    def __init__(self, master, app):
        ttk.Frame.__init__(self, master)
        self.app = app
        self.tree = new_tree()
        self.current_node = None
        self.current_response = None
        self.loading = False
        self.source_path = None
        self.map_boxes = {}
        # which outline row the editors are currently showing; used to
        # ignore the selection event a programmatic rebuild fires
        self._loaded_iid = None

        self.target_kind = tk.StringVar(value="NPC")
        self.folder_key = tk.StringVar(value="")
        self.file_name = tk.StringVar(value="Dialogue.json")
        self.show_advanced = tk.BooleanVar(value=False)

        strip = ttk.Frame(self)
        strip.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(strip, text="Editing", width=8).pack(side="left")
        self.summary = ttk.Label(strip, text="", style="Accent.TLabel")
        self.summary.pack(side="left")

        self.inner = ttk.Notebook(self)
        self.inner.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        self.flow_page = ttk.Frame(self.inner)
        self.setup_page = ttk.Frame(self.inner)
        self.quest_talk_page = ttk.Frame(self.inner)
        self.inner.add(self.flow_page, text="  Flow  ")
        self.inner.add(self.setup_page, text="  Who it's for & voice lines  ")
        self.inner.add(self.quest_talk_page, text="  Quest talk  ")

        self._build_setup(self.setup_page)
        self._build_quest_talk(self.quest_talk_page)
        self._build_flow(self.flow_page)
        self.refresh_all()

    # --- setup page

    def _build_setup(self, parent):
        scroll = ScrollFrame(parent)
        scroll.pack(fill="both", expand=True)
        columns = ttk.Frame(scroll.inner)
        columns.pack(fill="both", expand=True, padx=6, pady=6)
        left = ttk.Frame(columns)
        right = ttk.Frame(columns)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        right.pack(side="left", fill="both", expand=True)

        who = ttk.LabelFrame(left, text="Who is this conversation for?",
                             style="Section.TLabelframe")
        who.pack(fill="x")

        for index, (label, value) in enumerate([
                ("A single quest NPC", "NPC"),
                ("A trader", "TRADER"),
                ("Shared by several NPCs", "SHARED"),
        ]):
            ttk.Radiobutton(who, text=label, value=value,
                            variable=self.target_kind,
                            command=self.on_target_change).grid(
                row=index, column=0, columnspan=2, sticky="w", padx=6)

        self.key_label = ttk.Label(who, text="Quest NPC ID")
        self.key_label.grid(row=3, column=0, sticky="w", padx=6, pady=(8, 2))
        key_row = ttk.Frame(who)
        key_row.grid(row=3, column=1, sticky="w", pady=(8, 2))
        key_entry = ttk.Entry(key_row, textvariable=self.folder_key, width=24)
        key_entry.pack(side="left")
        key_entry.bind("<KeyRelease>", lambda _e: self.mark_dirty())
        self.pick_npc_button = ttk.Button(key_row, text="Pick NPC...",
                                          width=12, command=self.browse_npcs)
        self.pick_npc_button.pack(side="left", padx=6)
        # Shows whose conversation this is once an ID is typed, e.g. "Steve",
        # so you don't have to cross-check the NPC config to know who you're on.
        self.npc_name_label = ttk.Label(key_row, text="",
                                        style="Accent.TLabel")
        self.npc_name_label.pack(side="left", padx=(8, 0))

        self.key_hint = ttk.Label(who, text="", wraplength=340,
                                  style="Hint.TLabel")
        self.key_hint.grid(row=4, column=0, columnspan=2,
                           sticky="w", padx=6, pady=(0, 6))

        ttk.Label(who, text="File name").grid(row=5, column=0,
                                              sticky="w", padx=6)
        name_entry = ttk.Entry(who, textvariable=self.file_name, width=24)
        name_entry.grid(row=5, column=1, sticky="w")
        name_entry.bind("<KeyRelease>", lambda _e: self.mark_dirty())

        self.path_preview = ttk.Label(who, text="", wraplength=340,
                                      style="Accent.TLabel")
        self.path_preview.grid(row=6, column=0, columnspan=2,
                               sticky="w", padx=6, pady=(6, 8))

        self.trader_frame = ttk.LabelFrame(
            left, text="Narrow down which trader (optional)",
            style="Section.TLabelframe")
        self.trader_extra = StringListEditor(
            self.trader_frame, "Entity class names",
            "e.g. ExpansionTraderAIDenis - matches every trader using "
            "that class.", height=3, on_change=self.mark_dirty)
        self.trader_extra.pack(fill="x", padx=4, pady=2)

        self.trader_positions = StringListEditor(
            self.trader_frame, "World positions",
            "One specific trader, e.g. 1234.50 300.00 5678.90",
            height=3, on_change=self.mark_dirty)
        self.trader_positions.pack(fill="x", padx=4, pady=2)

        row = ttk.Frame(self.trader_frame)
        row.pack(fill="x", padx=6, pady=(2, 6))
        ttk.Label(row, text="Match radius (m)").pack(side="left")
        self.radius = ttk.Spinbox(row, from_=0.0, to=500.0, increment=1.0,
                                  width=8, command=self.mark_dirty)
        self.radius.pack(side="left", padx=(4, 12))
        ttk.Label(row, text="Keys that must agree").pack(side="left")
        self.min_keys = ttk.Combobox(row, values=["1", "2", "3"], width=4,
                                     state="readonly")
        self.min_keys.pack(side="left", padx=4)
        self.min_keys.bind("<<ComboboxSelected>>",
                           lambda _e: self.mark_dirty())

        self.greeting = StringListEditor(
            right, "Greeting voice lines (optional)",
            "Played when the conversation opens. One picked at random. "
            "Leave empty for a silent greeting.", height=5,
            on_change=self.mark_dirty)
        self.greeting.pack(fill="both", expand=True, pady=(0, 6))

        self.farewell = StringListEditor(
            right, "Farewell voice lines (optional)",
            "Played when the conversation ends.", height=5,
            on_change=self.mark_dirty)
        self.farewell.pack(fill="both", expand=True)

    # --- quest talk page

    def _build_quest_talk(self, parent):
        """What this NPC says around their quest list. Lives in the dialogue
        file, so it belongs beside the conversation rather than on the
        Quest wording tab, which writes a different file entirely."""
        scroll = ScrollFrame(parent)
        scroll.pack(fill="both", expand=True)
        parent = scroll.inner

        ttk.Label(parent,
                  text="The NPC-wide defaults for every quest they have, "
                       "grouped by the in-game screen each shows on. A finished "
                       "quest can override any of these per quest on the Quest "
                       "wording tab. All optional - leave a box empty and the "
                       "mod uses its built-in wording.",
                  wraplength=700, style="Hint.TLabel").pack(
            anchor="w", padx=6, pady=(6, 2))

        back_hint = ("One button per line, each returns to the conversation. "
                     "Blank shows no back button on this screen.")

        list_section = CollapsibleSection(
            parent, "Quest list screen  (optional)", expanded=True)
        list_section.pack(fill="x", padx=4, pady=(4, 4))
        list_box = list_section.content()
        self.quest_prompt = StringListEditor(
            list_box, "Line above their quest list  (NPC says)",
            "One line picked at random. Blank uses \"What do you need "
            "done?\"", height=4, on_change=self.mark_dirty)
        self.quest_prompt.pack(fill="x", padx=6, pady=(6, 4))
        self.quest_list_back = StringListEditor(
            list_box, "Back to the conversation  (Player says)",
            back_hint, height=3, on_change=self.mark_dirty)
        self.quest_list_back.pack(fill="x", padx=6, pady=(0, 6))

        # The offer / in-progress / turn-in wording itself is written per quest
        # on the Quest wording tab; only the back buttons are NPC-wide here.
        offer_section = CollapsibleSection(parent, "Offer screen  (optional)")
        offer_section.pack(fill="x", padx=4, pady=(0, 4))
        offer_box = offer_section.content()
        self.offer_back = StringListEditor(
            offer_box, "Back to the conversation  (Player says)",
            back_hint, height=3, on_change=self.mark_dirty)
        self.offer_back.pack(fill="x", padx=6, pady=(6, 6))

        progress_section = CollapsibleSection(
            parent, "In-progress screen  (optional)")
        progress_section.pack(fill="x", padx=4, pady=(0, 4))
        progress_box = progress_section.content()
        self.in_progress_back = StringListEditor(
            progress_box, "Back to the conversation  (Player says)",
            back_hint, height=3, on_change=self.mark_dirty)
        self.in_progress_back.pack(fill="x", padx=6, pady=(6, 6))

        turnin_section = CollapsibleSection(
            parent, "Turn-in screen  (optional)")
        turnin_section.pack(fill="x", padx=4, pady=(0, 4))
        turnin_box = turnin_section.content()
        self.turn_in_back = StringListEditor(
            turnin_box, "Back to the conversation  (Player says)",
            back_hint, height=3, on_change=self.mark_dirty)
        self.turn_in_back.pack(fill="x", padx=6, pady=(6, 6))

        none_section = CollapsibleSection(
            parent, "No-quests screen  (optional)")
        none_section.pack(fill="x", padx=4, pady=(0, 4))
        none_box = none_section.content()

        self.no_quests_text = StringListEditor(
            none_box, "Line they say  (NPC says)",
            "One line picked at random.", height=4,
            on_change=self.mark_dirty)
        self.no_quests_text.pack(fill="x", padx=6, pady=(6, 0))

        self.no_quests_back = StringListEditor(
            none_box, "Back to the conversation  (Player says)",
            "One button per line. Blank still gives players a Back button.",
            height=3, on_change=self.mark_dirty)
        self.no_quests_back.pack(fill="x", padx=6, pady=(6, 0))

        self.no_quests_leave = StringListEditor(
            none_box, "Buttons that end the chat  (Player says)",
            "One button per line.", height=3, on_change=self.mark_dirty)
        self.no_quests_leave.pack(fill="x", padx=6, pady=(6, 0))

        self.no_quests_voice = StringListEditor(
            none_box, "Voice lines (optional)",
            "One picked at random.", height=3,
            on_change=self.mark_dirty)
        self.no_quests_voice.pack(fill="x", padx=6, pady=(6, 6))

    # --- flow page

    def _build_flow(self, parent):
        panes = ttk.PanedWindow(parent, orient="horizontal")
        panes.pack(fill="both", expand=True, padx=4, pady=4)

        outline_pane = ttk.Frame(panes)
        editor_pane = ttk.Frame(panes)
        map_pane = ttk.Frame(panes)
        panes.add(outline_pane, weight=2)
        panes.add(editor_pane, weight=3)
        panes.add(map_pane, weight=3)

        self._build_outline(outline_pane)
        self._build_editors(editor_pane)
        self._build_map(map_pane)

    def _build_outline(self, parent):
        box = ttk.LabelFrame(parent, text="Conversation outline",
                             style="Section.TLabelframe")
        box.pack(fill="both", expand=True)

        self.outline = ttk.Treeview(box, columns=("target",),
                                    show="tree headings", selectmode="browse")
        self.outline.heading("#0", text="Node / player option")
        self.outline.heading("target", text="Leads to")
        self.outline.column("#0", width=250, stretch=True)
        self.outline.column("target", width=120, stretch=False, anchor="w")
        self.outline.pack(fill="both", expand=True, side="left",
                          padx=(6, 0), pady=6)
        scroll = ttk.Scrollbar(box, orient="vertical",
                               command=self.outline.yview)
        scroll.pack(side="left", fill="y", pady=6, padx=(0, 6))
        self.outline.configure(yscrollcommand=scroll.set)
        self.outline.bind("<<TreeviewSelect>>", self.on_outline_select)
        self.outline.bind("<Button-3>", self._outline_right_click)

        tools = ttk.Frame(parent)
        tools.pack(fill="x", pady=(4, 0))
        ttk.Button(tools, text="Add node", width=11,
                   command=self.add_node).pack(side="left")
        ttk.Button(tools, text="Duplicate", width=11,
                   command=self.duplicate_node).pack(side="left", padx=3)
        ttk.Button(tools, text="Delete node", width=12,
                   command=self.delete_node).pack(side="left")

        root_row = ttk.Frame(parent)
        root_row.pack(fill="x", pady=(6, 0))
        ttk.Label(root_row, text="Conversation opens on node").pack(
            side="left")
        self.root_node = ttk.Combobox(root_row, width=8, state="readonly")
        self.root_node.pack(side="left", padx=6)
        self.root_node.bind("<<ComboboxSelected>>", self.on_root_changed)

    def _build_editors(self, parent):
        scroll = ScrollFrame(parent)
        scroll.pack(fill="both", expand=True)
        parent = scroll.inner

        node_box = ttk.LabelFrame(parent, text="This node",
                                  style="Section.TLabelframe")
        node_box.pack(fill="x")

        row = ttk.Frame(node_box)
        row.pack(fill="x", padx=6, pady=4)
        ttk.Label(row, text="Node ID").pack(side="left")
        self.node_id = ttk.Entry(row, width=7)
        self.node_id.pack(side="left", padx=(4, 14))
        self.node_id.bind("<FocusOut>", lambda _e: self.commit_node_id())
        self.node_id.bind("<Return>", lambda _e: self.commit_node_id())

        ttk.Label(row, text="Type").pack(side="left")
        self.node_type = ttk.Combobox(row, values=NODE_TYPES, width=13,
                                      state="readonly")
        self.node_type.pack(side="left", padx=4)
        self.node_type.bind("<<ComboboxSelected>>", self.on_node_type)

        ttk.Label(node_box, text="What the NPC says here:").pack(
            anchor="w", padx=6)
        self.speaker_text = tk.Text(node_box, height=4, wrap="word",
                                    undo=True, autoseparators=True,
                                    maxundo=-1)
        self.speaker_text.pack(fill="x", padx=6, pady=(2, 6))
        self.speaker_text.bind("<KeyRelease>", lambda _e: self.commit_speaker())
        attach_text_spellcheck(self.speaker_text)

        # Optional / advanced node bits stay folded so a basic node is just an
        # ID, a type and a line of speech.
        voice_section = CollapsibleSection(
            node_box, "Voice lines for this node  (optional)")
        voice_section.pack(fill="x", padx=6, pady=(0, 4))
        self.node_voice = StringListEditor(
            voice_section.content(), "",
            "One picked at random when this node is shown. Used with the main "
            "line above, or as a fallback for any extra line without its own.",
            height=3, on_change=self.commit_node_voice)
        self.node_voice.pack(fill="x", padx=4, pady=(2, 6))

        extra_section = CollapsibleSection(
            node_box, "Extra spoken lines with quest locking  (optional)")
        extra_section.pack(fill="x", padx=6, pady=(0, 6))
        self.speaker_lines = SpeakerLinesEditor(
            extra_section.content(), self.app,
            on_change=self.commit_speaker_lines)
        self.speaker_lines.configure(text="")
        self.speaker_lines.pack(fill="x", padx=4, pady=(2, 6))

        editor = ttk.LabelFrame(parent, text="Selected player option",
                                style="Section.TLabelframe")
        editor.pack(fill="both", expand=True, pady=(6, 0))

        tools = ttk.Frame(editor)
        tools.pack(fill="x", padx=6, pady=(6, 2))
        ttk.Button(tools, text="Add option", width=11,
                   command=self.add_response).pack(side="left")
        ttk.Button(tools, text="Duplicate", width=10,
                   command=self.duplicate_response).pack(side="left", padx=3)
        ttk.Button(tools, text="Delete", width=8,
                   command=self.delete_response).pack(side="left")
        ttk.Button(tools, text="\u2191", width=3,
                   command=lambda: self.move_response(-1)).pack(
            side="left", padx=(10, 2))
        ttk.Button(tools, text="\u2193", width=3,
                   command=lambda: self.move_response(1)).pack(side="left")

        # Every control sits in column 1 next to its own label, so nothing
        # gets flung to the far edge on a wide window.
        fields = ttk.Frame(editor)
        fields.pack(fill="x", padx=6, pady=4)
        fields.columnconfigure(1, weight=1)

        ttk.Label(fields, text="Button text").grid(row=0, column=0,
                                                   sticky="w", pady=3)
        self.response_text = ttk.Entry(fields)
        self.response_text.grid(row=0, column=1, sticky="ew", padx=4, pady=3)
        self.response_text.bind("<KeyRelease>",
                                lambda _e: self.commit_response())
        add_entry_undo(self.response_text)
        attach_entry_spellcheck(self.response_text)

        ttk.Label(fields, text="What it does").grid(row=1, column=0,
                                                    sticky="w", pady=3)
        action_row = ttk.Frame(fields)
        action_row.grid(row=1, column=1, sticky="w", padx=4, pady=3)
        self.action_type = ttk.Combobox(action_row, values=ACTION_TYPES,
                                        width=19, state="readonly")
        self.action_type.pack(side="left")
        self.action_type.bind("<<ComboboxSelected>>", self.on_action_changed)
        ttk.Checkbutton(action_row, text="advanced",
                        variable=self.show_advanced,
                        command=self.refresh_action_values).pack(
            side="left", padx=10)

        self.action_hint = ttk.Label(fields, text="", wraplength=430,
                                     style="Hint.TLabel")
        self.action_hint.grid(row=2, column=1, sticky="w", padx=4)

        ttk.Label(fields, text="Next node").grid(row=3, column=0,
                                                 sticky="w", pady=3)
        next_row = ttk.Frame(fields)
        next_row.grid(row=3, column=1, sticky="w", padx=4, pady=3)
        self.next_node = ttk.Combobox(next_row, width=19, state="readonly")
        self.next_node.pack(side="left")
        self.next_node.bind("<<ComboboxSelected>>",
                            lambda _e: self.commit_response())
        ttk.Button(next_row, text="Jump to", width=9,
                   command=self.jump_to_next).pack(side="left", padx=6)

        # Gating is advanced and rarely used, so it folds away under the core
        # button text / action / next-node fields.
        gate_section = CollapsibleSection(
            editor, "Show only after a quest completes  (optional)")
        gate_section.pack(fill="x", padx=6, pady=(2, 6))
        gate_box = gate_section.content()
        gate_row = ttk.Frame(gate_box)
        gate_row.pack(fill="x", padx=6, pady=(4, 2))
        ttk.Label(gate_row, text="Quest lock").pack(side="left")
        self.gate_quest = ttk.Combobox(gate_row, width=34)
        self.gate_quest.pack(side="left", padx=(4, 0))
        self.gate_quest.bind("<<ComboboxSelected>>", self.on_gate_changed)
        self.gate_quest.bind("<KeyRelease>", self.on_gate_changed)
        ttk.Button(gate_row, text="Browse quests...", width=16,
                   command=self.browse_quests).pack(side="left", padx=6)

        self.gate_note = ttk.Label(gate_box, text="", wraplength=430,
                                   style="Hint.TLabel")
        self.gate_note.pack(anchor="w", padx=6, pady=(0, 4))

    def _build_map(self, parent):
        box = ttk.LabelFrame(parent, text="Branch map",
                             style="Section.TLabelframe")
        box.pack(fill="both", expand=True)

        wrap = ttk.Frame(box)
        wrap.pack(fill="both", expand=True, padx=6, pady=(6, 0))

        self.map_canvas = tk.Canvas(wrap, highlightthickness=0)
        vbar = ttk.Scrollbar(wrap, orient="vertical",
                             command=self.map_canvas.yview)
        hbar = ttk.Scrollbar(box, orient="horizontal",
                             command=self.map_canvas.xview)
        self.map_canvas.configure(yscrollcommand=vbar.set,
                                  xscrollcommand=hbar.set)
        self.map_canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="left", fill="y")
        hbar.pack(fill="x", padx=6)

        self.map_canvas.bind("<Button-1>", self.on_map_click)
        self.map_canvas.bind("<Configure>", lambda _e: self.refresh_map())

        self.map_legend = ttk.Label(
            box,
            text="Click any box to jump to it. Gold = where you are.",
            style="Hint.TLabel")
        self.map_legend.pack(anchor="w", padx=8, pady=(2, 6))

    # --- state plumbing

    def mark_dirty(self, *_args):
        if self.loading:
            return
        self.pull_tree_header()
        self.app.mark_editor_dirty("Dialogue")

    def preview_scene(self):
        speaker = self.speaker_label()
        node = self.current_node
        if not node:
            return PreviewScene(
                "Conversation", speaker, "", [],
                "Pick a node in the outline to see it here.")

        buttons = []
        for response in (node.get("Responses") or []):
            kind = "normal"
            if response is self.current_response:
                kind = "hover"
            buttons.append((response.get("Text") or "(no button text)",
                            kind, icon_for_response(response)))

        note = ""
        if node.get("Type") and node.get("Type") != "STANDARD":
            note = "Node type: %s" % node.get("Type")

        # Show the main line, or the first extra line if there's no main one,
        # and flag that the mod picks one of several at random.
        line = node.get("SpeakerText") or ""
        extra = node.get("SpeakerLines") or []
        if extra:
            if not line:
                line = (extra[0].get("Text") or "")
            pool = (1 if node.get("SpeakerText") else 0) + len(extra)
            variation = "Varies: one of %d lines picked at random" % pool
            gated = sum(1 for ln in extra
                        if (ln.get("RequiredQuestID", -1) or 0) > 0)
            if gated:
                variation += " (%d quest-locked)" % gated
            overrides = sum(1 for ln in extra
                            if (ln.get("OverrideQuestID", -1) or 0) > 0)
            if overrides:
                variation += (", %d take over as the greeting once their "
                              "quest is done" % overrides)
            note = (note + "   •   " + variation) if note else variation
        return PreviewScene(
            "Conversation - node %s" % node.get("ID"), speaker,
            line, buttons, note)

    def speaker_label(self):
        """Who is talking, for the preview header - the NPC's name when we can
        resolve it, so it reads 'NPC 2 "Steve"' instead of a file name."""
        kind = self.target_kind.get()
        key = self.folder_key.get().strip()
        if kind == "NPC" and key:
            return self.app.npc_speaker_label(safe_int(key, 0)) \
                or ("NPC %s" % key)
        if kind == "TRADER" and key:
            return "Trader %s" % key
        return (self.file_name.get() or "NPC").replace(".json", "")

    def browse_npcs(self):
        """Pick a quest NPC by name instead of by ID."""
        if not self.app.ensure_quest_folder():
            return
        if not self.app.npc_index:
            messagebox.showinfo(
                APP_TITLE,
                "No quest NPC configs found. These usually live in the "
                "NPCs folder next to your Expansion quests.", parent=self)
            return
        dialog = ChooserDialog(self.app, "Pick a quest NPC",
                               self.app.npc_index,
                               "Fills in the NPC ID for the folder name.")
        self.wait_window(dialog)
        if dialog.chosen is None:
            return
        if self.target_kind.get() == "SHARED":
            existing = [p.strip() for p in self.folder_key.get().split(",")
                        if p.strip()]
            if str(dialog.chosen) not in existing:
                existing.append(str(dialog.chosen))
            self.folder_key.set(", ".join(existing))
        else:
            self.folder_key.set(str(dialog.chosen))
        self.on_target_change()

    def on_target_change(self):
        kind = self.target_kind.get()
        if kind == "NPC":
            self.key_label.configure(text="Quest NPC ID")
            self.key_hint.configure(
                text="The 'ID' field from your QuestNPC_X.json. NPCIDs stays "
                     "empty in the file - the mod infers it from the folder.")
            self.trader_frame.pack_forget()
            self.pick_npc_button.state(["!disabled"])
        elif kind == "TRADER":
            self.key_label.configure(text="Trader definition name")
            self.key_hint.configure(
                text="The trader's file name, e.g. Weapons. Open the trader "
                     "in game and the client log prints fileName=...")
            self.trader_frame.pack(fill="x", pady=(6, 0))
            self.pick_npc_button.state(["disabled"])
        else:
            self.key_label.configure(text="NPC IDs (comma separated)")
            self.key_hint.configure(
                text="Shared trees MUST list every NPC ID explicitly, "
                     "e.g. 12, 13, 14")
            self.trader_frame.pack_forget()
            self.pick_npc_button.state(["!disabled"])
        self.update_path_preview()
        self.mark_dirty()

    def update_path_preview(self):
        root = self.app.profile_path.get() or "<profile folder>"
        kind = self.target_kind.get()
        key = self.folder_key.get().strip()
        if kind == "NPC":
            folder = "NPC_%s" % (key or "?")
            label = self.app.npc_speaker_label(safe_int(key, 0)) if key else ""
            who = label or ("quest NPC %s" % (key or "?"))
        elif kind == "TRADER":
            folder = "Trader_%s" % (key or "?")
            who = "trader %s" % (key or "?")
        else:
            folder = "Shared"
            who = "shared (%s)" % (key or "no IDs yet")
        name = self.file_name.get().strip() or "Dialogue.json"
        if not name.lower().endswith(".json"):
            name += ".json"
        self.preview_path = os.path.join(root, "Dialogues", folder, name)
        self.path_preview.configure(text="Saves to: " + self.preview_path)
        self.summary.configure(
            text="%s   \u2192   Dialogues\\%s\\%s" % (who, folder, name))

        if hasattr(self, "npc_name_label"):
            npc_name = ""
            if kind == "NPC" and key:
                npc_name = self.app.npc_name(safe_int(key, 0))
            if npc_name:
                self.npc_name_label.configure(text='\u2190 "%s"' % npc_name)
            elif kind == "NPC" and key and safe_int(key, 0) > 0:
                self.npc_name_label.configure(text="(name not in quest folder)")
            else:
                self.npc_name_label.configure(text="")

    def output_path(self):
        self.update_path_preview()
        return self.preview_path

    def pull_tree_header(self):
        kind = self.target_kind.get()
        key = self.folder_key.get().strip()
        self.tree["NPCIDs"] = []
        self.tree["TraderIDs"] = []
        if kind == "SHARED":
            ids = []
            for part in key.replace(";", ",").split(","):
                part = part.strip()
                if part:
                    ids.append(safe_int(part, 0))
            self.tree["NPCIDs"] = [i for i in ids if i > 0]
        elif kind == "TRADER":
            if key:
                self.tree["TraderIDs"] = [key]
            self.tree["TraderClassNames"] = self.trader_extra.get_items()
            self.tree["TraderPositions"] = self.trader_positions.get_items()
            self.tree["TraderPositionRadius"] = safe_float(
                self.radius.get(), 8.0)
            self.tree["TraderMinKeyMatches"] = safe_int(self.min_keys.get(), 2)
        if kind != "TRADER":
            self.tree["TraderClassNames"] = []
            self.tree["TraderPositions"] = []
        self.tree["GreetingVoiceLineIDs"] = self.greeting.get_items()
        self.tree["FarewellVoiceLineIDs"] = self.farewell.get_items()
        self.tree["QuestListTexts"] = self.quest_prompt.get_items()
        self.tree["NoQuestsTexts"] = self.no_quests_text.get_items()
        self.tree["NoQuestsBackTexts"] = self.no_quests_back.get_items()
        self.tree["NoQuestsLeaveTexts"] = self.no_quests_leave.get_items()
        self.tree["NoQuestsVoiceLineIDs"] = self.no_quests_voice.get_items()
        self.tree["QuestListBackTexts"] = self.quest_list_back.get_items()
        self.tree["OfferBackTexts"] = self.offer_back.get_items()
        self.tree["InProgressBackTexts"] = self.in_progress_back.get_items()
        self.tree["TurnInBackTexts"] = self.turn_in_back.get_items()
        self.update_path_preview()

    def refresh_all(self):
        self.loading = True
        self.greeting.set_items(self.tree.get("GreetingVoiceLineIDs"))
        self.farewell.set_items(self.tree.get("FarewellVoiceLineIDs"))
        self.quest_prompt.set_items(self.tree.get("QuestListTexts"))
        self.no_quests_text.set_items(self.tree.get("NoQuestsTexts"))
        self.no_quests_back.set_items(self.tree.get("NoQuestsBackTexts"))
        self.no_quests_leave.set_items(self.tree.get("NoQuestsLeaveTexts"))
        self.no_quests_voice.set_items(self.tree.get("NoQuestsVoiceLineIDs"))
        self.quest_list_back.set_items(self.tree.get("QuestListBackTexts"))
        self.offer_back.set_items(self.tree.get("OfferBackTexts"))
        self.in_progress_back.set_items(self.tree.get("InProgressBackTexts"))
        self.turn_in_back.set_items(self.tree.get("TurnInBackTexts"))
        self.trader_extra.set_items(self.tree.get("TraderClassNames"))
        self.trader_positions.set_items(self.tree.get("TraderPositions"))
        self.radius.delete(0, tk.END)
        self.radius.insert(0, str(self.tree.get("TraderPositionRadius", 8.0)))
        self.min_keys.set(str(self.tree.get("TraderMinKeyMatches", 2)))
        self.loading = False
        self.on_target_change()
        self.refresh_outline()

    # --- outline

    def node_index(self, node):
        return self.tree["Nodes"].index(node)

    @staticmethod
    def short(text, limit=40):
        text = (text or "").replace("\n", " ").strip()
        if not text:
            return "(nothing said yet)"
        return text if len(text) <= limit else text[:limit] + "..."

    def response_target_label(self, response):
        action = response.get("ActionType", "NONE")
        if action != "NONE":
            return {"SHOW_QUEST_LIST": "quest list",
                    "END_CONVERSATION": "ends chat",
                    "OPEN_TRADER": "opens shop"}.get(action, action.lower())
        target = response.get("NextNodeID", -1)
        return "node %d" % target if target and target > 0 else "ends chat"

    def refresh_outline(self, keep_node=None, keep_response=None,
                        reload_editors=True):
        """Rebuild the outline tree, then reselect what was being edited."""
        if keep_node is None and self.current_node is not None:
            keep_node = self.current_node.get("ID")
        if keep_response is None and self.current_response is not None \
                and self.current_node is not None:
            try:
                keep_response = self.current_node["Responses"].index(
                    self.current_response)
            except ValueError:
                keep_response = None

        self.outline.delete(*self.outline.get_children())
        root_id = self.tree.get("RootNodeID")

        for n_index, node in enumerate(self.tree["Nodes"]):
            marker = "\u25b6 " if node.get("ID") == root_id else ""
            flag = "" if node.get("Type") == "STANDARD" else \
                "  [%s]" % node.get("Type")
            label = "%sNode %s - %s%s" % (
                marker, node.get("ID"), self.short(node.get("SpeakerText")),
                flag)
            self.outline.insert(
                "", "end", iid="n%d" % n_index, text=label,
                values=("start" if node.get("ID") == root_id else "",),
                open=True, tags=("node",))

            for r_index, response in enumerate(node.get("Responses", [])):
                gate = response.get("RequiredQuestID", -1)
                lock = "\U0001f512 " if gate and gate > 0 else ""
                self.outline.insert(
                    "n%d" % n_index, "end",
                    iid="r%d_%d" % (n_index, r_index),
                    text="    %s%s" % (lock, self.short(
                        response.get("Text"), 34)),
                    values=(self.response_target_label(response),),
                    tags=("response",))

        ids = [str(n.get("ID", 0)) for n in self.tree["Nodes"]]
        self.root_node["values"] = ids
        self.root_node.set(str(self.tree.get("RootNodeID", 1)))

        if not self.tree["Nodes"]:
            self.current_node = None
            self.current_response = None
            self.refresh_map()
            return

        index = 0
        for position, node in enumerate(self.tree["Nodes"]):
            if node.get("ID") == keep_node:
                index = position
                break

        iid = "n%d" % index
        if keep_response is not None:
            candidate = "r%d_%d" % (index, keep_response)
            if self.outline.exists(candidate):
                iid = candidate
        self._loaded_iid = iid
        self.outline.selection_set(iid)
        self.outline.see(iid)
        if reload_editors:
            self.load_from_iid(iid)

    def load_from_iid(self, iid):
        """Point the editor panels at whatever this outline row is."""
        if iid.startswith("n"):
            self.select_node(int(iid[1:]))
            self.current_response = None
            self.clear_response_editor()
        else:
            n_index, r_index = iid[1:].split("_")
            self.select_node(int(n_index))
            self.select_response(int(r_index))

    def on_outline_select(self, _event=None):
        selection = self.outline.selection()
        if not selection:
            return
        iid = selection[0]
        # A rebuild re-selects the same row and fires this event again.
        # Reloading there would yank the caret out of whatever the user is
        # mid-way through typing, so ignore it.
        if iid == self._loaded_iid:
            return
        self._loaded_iid = iid
        self.load_from_iid(iid)
        self.refresh_map()

    def _outline_right_click(self, event):
        """Edit or delete whatever outline row was right-clicked, so deleting a
        node vs an option is one menu on the thing itself - not two buttons in
        different corners that are easy to mix up."""
        iid = self.outline.identify_row(event.y)
        if not iid:
            return
        # Select and load the clicked row first, so the menu's actions and the
        # editor both operate on it.
        self.outline.selection_set(iid)
        if iid != self._loaded_iid:
            self._loaded_iid = iid
            self.load_from_iid(iid)
            self.refresh_map()

        menu = tk.Menu(self, tearoff=0)
        if iid.startswith("n"):
            menu.add_command(label="Edit this node",
                             command=lambda: self._outline_edit(iid))
            menu.add_separator()
            menu.add_command(label="Delete this node", command=self.delete_node)
        else:
            menu.add_command(label="Edit this option",
                             command=lambda: self._outline_edit(iid))
            menu.add_separator()
            menu.add_command(label="Delete this option",
                             command=self.delete_response)
        _popup_menu(menu, event)

    def _outline_edit(self, iid):
        """The row is already loaded into the editor; drop the cursor into the
        main field for that row so 'Edit' goes straight to typing."""
        if iid.startswith("n"):
            self.speaker_text.focus_set()
        else:
            self.response_text.focus_set()
            self.response_text.icursor(tk.END)

    # --- node editing

    def select_node(self, index):
        self.current_node = self.tree["Nodes"][index]
        self.loading = True
        self.node_id.delete(0, tk.END)
        self.node_id.insert(0, str(self.current_node.get("ID", 0)))
        self.node_type.set(self.current_node.get("Type", "STANDARD"))
        self.speaker_text.delete("1.0", tk.END)
        self.speaker_text.insert("1.0", self.current_node.get(
            "SpeakerText", ""))
        self.node_voice.set_items(self.current_node.get("VoiceLineIDs"))
        self.speaker_lines.set_lines(self.current_node.get("SpeakerLines"))
        self.loading = False

    def commit_speaker_lines(self):
        if self.loading or not self.current_node:
            return
        self.current_node["SpeakerLines"] = self.speaker_lines.get_lines()
        self.refresh_map()
        self.mark_dirty()

    def on_root_changed(self, _event=None):
        self.tree["RootNodeID"] = safe_int(self.root_node.get(), 1)
        self.refresh_outline()
        self.refresh_map()
        self.mark_dirty()

    def next_free_node_id(self):
        used = {n.get("ID", 0) for n in self.tree["Nodes"]}
        candidate = 1
        while candidate in used:
            candidate += 1
        return candidate

    def add_node(self):
        node = new_node(self.next_free_node_id())
        self.tree["Nodes"].append(node)
        self.current_response = None
        self.refresh_outline(keep_node=node["ID"], keep_response=None)
        self.refresh_map()
        self.mark_dirty()

    def duplicate_node(self):
        if not self.current_node:
            return
        clone = copy.deepcopy(self.current_node)
        clone["ID"] = self.next_free_node_id()
        self.tree["Nodes"].append(clone)
        self.current_response = None
        self.refresh_outline(keep_node=clone["ID"], keep_response=None)
        self.refresh_map()
        self.mark_dirty()

    def delete_node(self):
        if not self.current_node:
            return
        if len(self.tree["Nodes"]) == 1:
            messagebox.showinfo(
                APP_TITLE, "A tree needs at least one node.", parent=self)
            return
        node_id = self.current_node.get("ID")
        incoming = sum(
            1 for n in self.tree["Nodes"] for r in n.get("Responses", [])
            if r.get("ActionType", "NONE") == "NONE"
            and r.get("NextNodeID") == node_id)
        message = "Delete node %s?" % node_id
        if incoming:
            message += ("\n\n%d option(s) point at it. They'll be left "
                        "pointing at a node that no longer exists, and "
                        "'Check for problems' will flag them." % incoming)
        if not messagebox.askyesno(APP_TITLE, message, parent=self):
            return
        self.tree["Nodes"].remove(self.current_node)
        self.current_node = None
        self.current_response = None
        self.refresh_outline(keep_node=None, keep_response=None)
        self.refresh_map()
        self.mark_dirty()

    def commit_node_id(self):
        if self.loading or not self.current_node:
            return
        new_id = safe_int(self.node_id.get(), self.current_node.get("ID", 1))
        if new_id == self.current_node.get("ID"):
            return
        if new_id < 1:
            messagebox.showwarning(
                APP_TITLE, "Node IDs start at 1 - 0 is treated as 'unset'.",
                parent=self)
            new_id = 1
        clash = [n for n in self.tree["Nodes"]
                 if n is not self.current_node and n.get("ID") == new_id]
        if clash:
            messagebox.showwarning(
                APP_TITLE,
                "Node ID %d is already used. Duplicate IDs silently break "
                "navigation." % new_id, parent=self)
            self.loading = True
            self.node_id.delete(0, tk.END)
            self.node_id.insert(0, str(self.current_node.get("ID")))
            self.loading = False
            return
        old_id = self.current_node.get("ID")
        self.current_node["ID"] = new_id
        for node in self.tree["Nodes"]:
            for response in node.get("Responses", []):
                if response.get("NextNodeID") == old_id:
                    response["NextNodeID"] = new_id
        if self.tree.get("RootNodeID") == old_id:
            self.tree["RootNodeID"] = new_id
        self.refresh_outline(keep_node=new_id)
        self.refresh_map()
        self.mark_dirty()

    def on_node_type(self, _event=None):
        if self.loading or not self.current_node:
            return
        value = self.node_type.get()
        if value != "STANDARD":
            messagebox.showwarning(
                APP_TITLE,
                "QUEST_LIST and QUEST_DETAIL nodes are built live by the mod "
                "from real Expansion quest data. Authoring them by hand is "
                "not supported - use STANDARD.", parent=self)
        self.current_node["Type"] = value
        self.refresh_outline(reload_editors=False)
        self.mark_dirty()

    def commit_speaker(self):
        if self.loading or not self.current_node:
            return
        self.current_node["SpeakerText"] = \
            self.speaker_text.get("1.0", "end-1c")
        self.refresh_outline(reload_editors=False)
        self.refresh_map()
        self.mark_dirty()

    def commit_node_voice(self):
        if self.loading or not self.current_node:
            return
        self.current_node["VoiceLineIDs"] = self.node_voice.get_items()
        self.mark_dirty()

    # --- response editing

    def refresh_action_values(self):
        values = list(ACTION_TYPES)
        if self.show_advanced.get():
            values += ADVANCED_ACTION_TYPES
        self.action_type["values"] = values

    def clear_response_editor(self):
        self.loading = True
        self.response_text.delete(0, tk.END)
        self.action_type.set("")
        self.next_node.set("")
        self.gate_quest.set(NOT_LOCKED_LABEL)
        self.gate_note.configure(text="")
        self.action_hint.configure(
            text="Pick an option in the outline, or add one.")
        self.next_node.configure(state="disabled")
        self.gate_quest.configure(state="disabled")
        self.loading = False

    def select_response(self, index):
        responses = self.current_node.get("Responses", [])
        if index >= len(responses):
            self.current_response = None
            self.clear_response_editor()
            return
        self.current_response = responses[index]
        response = self.current_response
        self.loading = True
        self.refresh_action_values()
        self.response_text.delete(0, tk.END)
        self.response_text.insert(0, response.get("Text", ""))
        action = response.get("ActionType", "NONE")
        if action in ADVANCED_ACTION_TYPES:
            self.show_advanced.set(True)
            self.refresh_action_values()
        self.action_type.set(action)

        options = ["(end conversation)"] + \
            [str(n.get("ID")) for n in self.tree["Nodes"]]
        self.next_node["values"] = options
        target = response.get("NextNodeID", -1)
        self.next_node.set(str(target) if target and target > 0
                           else "(end conversation)")

        gate = response.get("RequiredQuestID", -1)
        self.refresh_quest_choices()
        self.set_gate_value(gate)
        self.loading = False
        self.update_action_state()

    def refresh_quest_choices(self):
        self.gate_quest["values"] = [NOT_LOCKED_LABEL] + self.app.quest_labels()
        self.update_gate_note()
        if hasattr(self, "speaker_lines"):
            self.speaker_lines.refresh_quest_choices()

    def update_gate_note(self):
        if not self.current_response:
            self.gate_note.configure(text="")
            return
        text = self.gate_quest.get().strip()
        if not text or text == NOT_LOCKED_LABEL:
            self.gate_note.configure(
                text="This option is always available.")
            return
        quest_id = quest_id_from_label(text, 0)
        if quest_id <= 0:
            self.gate_note.configure(
                text="Not a quest yet - pick one from the list, or choose "
                     "\"%s\"." % NOT_LOCKED_LABEL)
            return
        if not self.app.quest_index:
            self.gate_note.configure(
                text="No quest folder set - using raw quest ID %d. Point "
                     "Settings at your Expansion quests to pick by name."
                     % quest_id)
            return
        if self.app.quest_lookup(quest_id) is None:
            self.gate_note.configure(
                text="Quest %d isn't in your quest folder - double-check it."
                     % quest_id)
        else:
            self.gate_note.configure(
                text="Option stays hidden until this quest is COMPLETED.")

    def browse_quests(self):
        """Pick a quest by name rather than remembering its number."""
        if not self.app.ensure_quest_folder():
            return
        if not self.app.quest_index:
            messagebox.showinfo(
                APP_TITLE,
                "No quest configs found in that folder. Point it at the "
                "folder holding your Expansion quest .json files.",
                parent=self)
            return
        dialog = ChooserDialog(
            self.app, "Pick a quest", self.app.quest_index,
            "The option will only appear once the player has COMPLETED "
            "the quest you pick.")
        self.wait_window(dialog)
        if dialog.chosen is None:
            return
        self.set_gate_value(dialog.chosen)
        self.update_gate_note()
        self.commit_response()

    def set_gate_value(self, quest_id):
        if quest_id and quest_id > 0:
            self.gate_quest.set(self.app.quest_label(quest_id))
        else:
            self.gate_quest.set(NOT_LOCKED_LABEL)

    def update_action_state(self):
        action = self.action_type.get()
        self.action_hint.configure(text=ACTION_HELP.get(action, ""))
        self.next_node.configure(
            state="readonly" if action == "NONE" else "disabled")
        self.gate_quest.configure(state="normal")
        self.update_gate_note()

    def on_action_changed(self, _event=None):
        self.update_action_state()
        self.commit_response()

    def on_gate_changed(self, _event=None):
        self.update_gate_note()
        self.commit_response()

    def commit_response(self):
        if self.loading or not self.current_response:
            return
        response = self.current_response
        response["Text"] = self.response_text.get()
        response["ActionType"] = self.action_type.get() or "NONE"
        if response["ActionType"] == "NONE":
            target = self.next_node.get()
            response["NextNodeID"] = -1 if target.startswith("(") \
                else safe_int(target, -1)
        else:
            response["NextNodeID"] = -1
        gate_text = self.gate_quest.get().strip()
        if not gate_text or gate_text == NOT_LOCKED_LABEL:
            response["RequiredQuestID"] = -1
        else:
            response["RequiredQuestID"] = max(
                1, quest_id_from_label(gate_text, 1))
        self.refresh_outline(reload_editors=False)
        self.refresh_map()
        self.mark_dirty()

    def add_response(self):
        if not self.current_node:
            messagebox.showinfo(
                APP_TITLE, "Select a node first.", parent=self)
            return
        response = new_response()
        # With no option selected the Button text box is a staging field for a
        # new option, so a label typed there names it. (With an option selected
        # the box is editing that option, so Add just makes a fresh default.)
        typed = self.response_text.get().strip()
        if typed and self.current_response is None:
            response["Text"] = typed
        self.current_node.setdefault("Responses", []).append(response)
        # Deselect and clear so the box is ready to stage the NEXT option. If we
        # left the new option selected, the box would stay bound to it and the
        # next thing typed would overwrite it instead of starting a new one.
        # Click the option in the outline to set its action or next node.
        self.current_response = None
        self.refresh_outline(keep_response=None)
        self.refresh_map()
        self.mark_dirty()
        self.response_text.focus_set()

    def duplicate_response(self):
        if not self.current_response:
            return
        clone = copy.deepcopy(self.current_response)
        self.current_node["Responses"].append(clone)
        index = len(self.current_node["Responses"]) - 1
        self.current_response = clone
        self.refresh_outline(keep_response=index)
        self.refresh_map()
        self.mark_dirty()

    def delete_response(self):
        if not self.current_response:
            return
        self.current_node["Responses"].remove(self.current_response)
        self.current_response = None
        self.refresh_outline(keep_response=None)
        self.refresh_map()
        self.mark_dirty()

    def move_response(self, delta):
        if not self.current_response:
            return
        responses = self.current_node["Responses"]
        index = responses.index(self.current_response)
        target = index + delta
        if target < 0 or target >= len(responses):
            return
        responses[index], responses[target] = responses[target], responses[index]
        self.refresh_outline(keep_response=target)
        self.refresh_map()
        self.mark_dirty()

    def jump_to_next(self):
        """Select whatever node the current option leads to."""
        if not self.current_response:
            return
        if self.current_response.get("ActionType", "NONE") != "NONE":
            return
        target = self.current_response.get("NextNodeID", -1)
        if not target or target < 1:
            return
        for index, node in enumerate(self.tree["Nodes"]):
            if node.get("ID") == target:
                self.current_response = None
                self.refresh_outline(keep_node=target, keep_response=None)
                self.refresh_map()
                return
        messagebox.showinfo(
            APP_TITLE, "Node %d doesn't exist yet." % target, parent=self)

    # --- branch map

    def layout_map(self):
        """Assign every node a (column, row) using breadth-first depth."""
        nodes_by_id = {n.get("ID"): n for n in self.tree["Nodes"]}
        root = self.tree.get("RootNodeID")

        depth = {}
        if root in nodes_by_id:
            depth[root] = 0
            queue = [root]
            while queue:
                current = queue.pop(0)
                for response in nodes_by_id[current].get("Responses", []):
                    if response.get("ActionType", "NONE") != "NONE":
                        continue
                    target = response.get("NextNodeID", -1)
                    if target in nodes_by_id and target not in depth:
                        depth[target] = depth[current] + 1
                        queue.append(target)

        reachable = set(depth)
        orphan_column = (max(depth.values()) + 1) if depth else 0
        for node in self.tree["Nodes"]:
            if node.get("ID") not in depth:
                depth[node.get("ID")] = orphan_column

        columns = {}
        placed = {}
        for node in self.tree["Nodes"]:
            column = depth[node.get("ID")]
            row = columns.get(column, 0)
            columns[column] = row + 1
            placed[node.get("ID")] = (column, row)
        return placed, reachable, root in nodes_by_id

    def refresh_map(self):
        canvas = getattr(self, "map_canvas", None)
        if canvas is None:
            return
        canvas.delete("all")
        self.map_boxes = {}

        skin = self.app.palette()
        canvas.configure(background=skin["field"])

        placed, reachable, has_root = self.layout_map()
        nodes_by_id = {n.get("ID"): n for n in self.tree["Nodes"]}
        current_id = self.current_node.get("ID") if self.current_node else None
        root_id = self.tree.get("RootNodeID")

        def box_at(node_id):
            column, row = placed[node_id]
            x = self.MARGIN + column * (self.BOX_W + self.GAP_X)
            y = self.MARGIN + row * (self.BOX_H + self.GAP_Y)
            return x, y, x + self.BOX_W, y + self.BOX_H

        # --- edges first so boxes sit on top
        highlight_target = None
        if self.current_response is not None \
                and self.current_response.get("ActionType", "NONE") == "NONE":
            highlight_target = self.current_response.get("NextNodeID", -1)

        for node in self.tree["Nodes"]:
            source_id = node.get("ID")
            if source_id not in placed:
                continue
            sx0, sy0, sx1, sy1 = box_at(source_id)
            for response in node.get("Responses", []):
                if response.get("ActionType", "NONE") != "NONE":
                    continue
                target = response.get("NextNodeID", -1)
                if target not in nodes_by_id or target not in placed:
                    continue
                tx0, ty0, _tx1, ty1 = box_at(target)
                start = (sx1, (sy0 + sy1) / 2)
                end = (tx0, (ty0 + ty1) / 2)
                mid = (start[0] + end[0]) / 2

                live = (source_id == current_id
                        and target == highlight_target)
                gated = (response.get("RequiredQuestID", -1) or 0) > 0
                canvas.create_line(
                    start[0], start[1], mid, start[1], mid, end[1],
                    end[0], end[1],
                    fill=skin["accent"] if live else skin["border"],
                    width=3 if live else 2,
                    smooth=True, arrow="last",
                    dash=() if not gated else (5, 3))

        for node in self.tree["Nodes"]:
            node_id = node.get("ID")
            if node_id not in placed:
                continue
            x0, y0, x1, y1 = box_at(node_id)
            selected = node_id == current_id
            unreachable = node_id not in reachable

            fill = skin["panel"]
            outline = skin["accent"] if selected else skin["border"]
            width = 3 if selected else 1

            rect = canvas.create_rectangle(
                x0, y0, x1, y1, fill=fill, outline=outline, width=width)
            self.map_boxes[rect] = node_id

            title = "Node %s" % node_id
            if node_id == root_id:
                title = "\u25b6 " + title
            text_id = canvas.create_text(
                x0 + 8, y0 + 6, anchor="nw", text=title,
                fill=skin["accent"] if selected else skin["fg"],
                font=("Segoe UI", 8, "bold"))
            self.map_boxes[text_id] = node_id

            body = self.short(node.get("SpeakerText"), 26)
            line_id = canvas.create_text(
                x0 + 8, y0 + 22, anchor="nw", text=body,
                width=self.BOX_W - 16,
                fill=skin["hint"] if not selected else skin["fg"],
                font=("Segoe UI", 7))
            self.map_boxes[line_id] = node_id

            if unreachable:
                mark = canvas.create_text(
                    x1 - 8, y0 + 6, anchor="ne", text="!",
                    fill=skin["warn"], font=("Segoe UI", 9, "bold"))
                self.map_boxes[mark] = node_id

            # terminal actions hang off the right edge as small pills
            offset = 0
            for response in node.get("Responses", []):
                action = response.get("ActionType", "NONE")
                if action == "NONE":
                    if not (response.get("NextNodeID", -1) or -1) > 0:
                        label = "end"
                    else:
                        continue
                else:
                    label = {"SHOW_QUEST_LIST": "quests",
                             "END_CONVERSATION": "end",
                             "OPEN_TRADER": "shop"}.get(action, "quest")
                canvas.create_text(
                    x1 + 8, y0 + 10 + offset, anchor="w", text="\u2192 " + label,
                    fill=skin["warn"], font=("Segoe UI", 7))
                offset += 12

        bounds = canvas.bbox("all")
        if bounds:
            canvas.configure(scrollregion=(
                bounds[0] - 10, bounds[1] - 10,
                bounds[2] + 60, bounds[3] + 10))

        if not has_root:
            canvas.create_text(
                self.MARGIN, 4, anchor="nw",
                text="Root node doesn't exist - nothing is reachable.",
                fill=skin["warn"], font=("Segoe UI", 8, "bold"))

    def on_map_click(self, event):
        canvas = self.map_canvas
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        for item in canvas.find_overlapping(x - 2, y - 2, x + 2, y + 2):
            if item in self.map_boxes:
                node_id = self.map_boxes[item]
                self.current_response = None
                self.refresh_outline(keep_node=node_id, keep_response=None)
                self.refresh_map()
                return

    # --- load / save

    def build_output(self):
        self.pull_tree_header()
        kind = self.target_kind.get()
        out = {
            "ID": safe_int(self.tree.get("ID", 1), 1),
            "NPCIDs": list(self.tree.get("NPCIDs", [])),
            "RootNodeID": safe_int(self.tree.get("RootNodeID", 1), 1),
        }
        if kind == "TRADER":
            out["TraderIDs"] = list(self.tree.get("TraderIDs", []))
            out["TraderClassNames"] = list(self.tree.get("TraderClassNames", []))
            out["TraderPositions"] = list(self.tree.get("TraderPositions", []))
            out["TraderPositionRadius"] = float(
                self.tree.get("TraderPositionRadius", 8.0))
            out["TraderMinKeyMatches"] = safe_int(
                self.tree.get("TraderMinKeyMatches", 2), 2)
        out["GreetingVoiceLineIDs"] = list(
            self.tree.get("GreetingVoiceLineIDs", []))
        out["FarewellVoiceLineIDs"] = list(
            self.tree.get("FarewellVoiceLineIDs", []))
        out["QuestListTexts"] = list(self.tree.get("QuestListTexts", []))
        out["NoQuestsTexts"] = list(self.tree.get("NoQuestsTexts", []))
        out["NoQuestsBackTexts"] = list(
            self.tree.get("NoQuestsBackTexts", []))
        out["NoQuestsLeaveTexts"] = list(
            self.tree.get("NoQuestsLeaveTexts", []))
        out["NoQuestsVoiceLineIDs"] = list(
            self.tree.get("NoQuestsVoiceLineIDs", []))
        out["QuestListBackTexts"] = list(
            self.tree.get("QuestListBackTexts", []))
        out["OfferBackTexts"] = list(self.tree.get("OfferBackTexts", []))
        out["InProgressBackTexts"] = list(
            self.tree.get("InProgressBackTexts", []))
        out["TurnInBackTexts"] = list(self.tree.get("TurnInBackTexts", []))

        nodes = []
        for node in self.tree["Nodes"]:
            entry = {
                "ID": safe_int(node.get("ID", 1), 1),
                "Type": node.get("Type", "STANDARD") or "STANDARD",
                "SpeakerText": node.get("SpeakerText", ""),
                "VoiceLineIDs": list(node.get("VoiceLineIDs", [])),
                "Responses": [],
            }
            speaker_lines = []
            for line in (node.get("SpeakerLines") or []):
                text = line.get("Text", "")
                gate = line.get("RequiredQuestID", -1)
                override = line.get("OverrideQuestID", -1)
                speaker_lines.append({
                    "Text": text,
                    "RequiredQuestID": gate if gate and gate > 0 else -1,
                    "OverrideQuestID": override if override and override > 0
                    else -1,
                    "VoiceLineIDs": list(line.get("VoiceLineIDs") or []),
                })
            # Only written when present, so untouched files stay byte-identical
            # and older mod builds ignore what they never see.
            if speaker_lines:
                entry["SpeakerLines"] = speaker_lines
            for response in node.get("Responses", []):
                action = response.get("ActionType", "NONE") or "NONE"
                gate = response.get("RequiredQuestID", -1)
                # every field written explicitly - omitted fields do NOT
                # give you the documented default on load
                entry["Responses"].append({
                    "Text": response.get("Text", ""),
                    "NextNodeID": safe_int(response.get("NextNodeID", -1), -1)
                    if action == "NONE" else -1,
                    "RequiredQuestID": gate if gate and gate > 0 else -1,
                    "ActionType": action,
                })
            nodes.append(entry)
        out["Nodes"] = nodes
        return out

    def load_tree(self, data, path=None):
        self.tree = new_tree()
        self.tree.update({k: v for k, v in data.items() if k != "Nodes"})
        nodes = data.get("Nodes") or []
        self.tree["Nodes"] = [
            {
                "ID": safe_int(n.get("ID", 1), 1),
                "Type": n.get("Type", "STANDARD") or "STANDARD",
                "SpeakerText": n.get("SpeakerText", ""),
                "VoiceLineIDs": list(n.get("VoiceLineIDs") or []),
                "Responses": [dict(r) for r in (n.get("Responses") or [])],
                "SpeakerLines": [
                    {
                        "Text": line.get("Text", ""),
                        "RequiredQuestID": safe_int(
                            line.get("RequiredQuestID", -1), -1),
                        "OverrideQuestID": safe_int(
                            line.get("OverrideQuestID", -1), -1),
                        "VoiceLineIDs": list(line.get("VoiceLineIDs") or []),
                    }
                    for line in (n.get("SpeakerLines") or [])
                ],
            }
            for n in nodes
        ] or [new_node(1)]
        self.source_path = path
        self.current_node = None
        self.current_response = None

        if path:
            folder = os.path.basename(os.path.dirname(path))
            self.file_name.set(os.path.basename(path))
            if folder.startswith("NPC_"):
                self.target_kind.set("NPC")
                self.folder_key.set(folder[4:])
            elif folder.startswith("Trader_"):
                self.target_kind.set("TRADER")
                self.folder_key.set(folder[7:])
            elif folder == "Shared":
                self.target_kind.set("SHARED")
                self.folder_key.set(", ".join(
                    str(i) for i in (data.get("NPCIDs") or [])))
        elif data.get("TraderIDs"):
            self.target_kind.set("TRADER")
            self.folder_key.set(data["TraderIDs"][0])
        self.refresh_all()
        self.refresh_map()

    # --- validation

    def validate(self):
        self.pull_tree_header()
        return validate_tree_dict(
            self.build_output(), self.target_kind.get(),
            self.folder_key.get(), self.app.quest_index)


# ---------------------------------------------------------------- quest text

class QuestTextTab(ttk.Frame):

    BACK_HINT = ("One button per line, each returns to the conversation. "
                 "Blank shows no back button on this screen.")

    # Player-facing screens, grouped so one box = one in-game screen. Each
    # screen carries its own "back to the conversation" wording.
    SCREEN_GROUPS = [
        ("Offer screen  —  quest not started", [
            ("AcceptTexts", "Accept  (Player says)",
             "One button per line."),
            ("DeclineTexts", "Turn it down  (Player says)",
             "One button per line."),
            ("OfferBackTexts", "Back to the conversation  (Player says)",
             BACK_HINT),
        ]),
        ("In-progress screen  —  quest running", [
            ("InProgressTexts", "While it's running  (Player says)",
             "One button per line."),
            ("InProgressBackTexts", "Back to the conversation  (Player says)",
             BACK_HINT),
        ]),
        ("Turn-in screen  —  ready to hand in", [
            ("TurnInTexts", "Hand it in  (Player says)",
             "One button per line."),
            ("NotYetTexts", "Not finished yet  (Player says)",
             "One button per line."),
            ("TurnInBackTexts", "Back to the conversation  (Player says)",
             BACK_HINT),
        ]),
    ]

    # Screens shown once this quest is completed - these override the NPC's
    # Quest talk defaults.
    COMPLETED_GROUPS = [
        ("Quest list greeting  —  once this quest is completed", [
            ("QuestListTexts", "Line above their quest list  (NPC says)",
             "One line picked at random."),
            ("QuestListBackTexts", "Back to the conversation  (Player says)",
             BACK_HINT),
        ]),
        ("Nothing-left screen  —  once this quest is completed", [
            ("NoQuestsTexts", "What they say with nothing left  (NPC says)",
             "One line picked at random."),
            ("NoQuestsLeaveTexts", "Buttons that end the chat  (Player says)",
             "One button per line."),
            ("NoQuestsBackTexts", "Back to the conversation  (Player says)",
             "One button per line. Blank still gives a Back button."),
        ]),
    ]

    @property
    def all_list_fields(self):
        fields = []
        for _title, specs in self.SCREEN_GROUPS + self.COMPLETED_GROUPS:
            fields.extend(specs)
        return fields

    def __init__(self, master, app):
        ttk.Frame.__init__(self, master)
        self.app = app
        self.quests = []
        self.current = None
        self.loading = False
        self.config_version = 0
        # which field the cursor is in, so the live preview can show the
        # matching in-game screen rather than guessing
        self.focus_key = "AcceptTexts"
        self.file_name = tk.StringVar(value="ServerQuests.json")

        header = ttk.Frame(self)
        header.pack(fill="x", padx=6, pady=(6, 0))
        ttk.Label(header,
                  text="Everything on this tab is optional. Anything you "
                       "leave empty falls back to the mod's built-in text, "
                       "so a partial file - or no file at all - works fine.",
                  wraplength=900, style="Hint.TLabel").pack(anchor="w")

        row = ttk.Frame(self)
        row.pack(fill="x", padx=6, pady=4)
        ttk.Label(row, text="Save as QuestText\\").pack(side="left")
        ttk.Entry(row, textvariable=self.file_name, width=28).pack(side="left")

        body = ttk.PanedWindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=6, pady=6)

        left = ttk.Frame(body)
        right_scroll = ScrollFrame(body)
        right = right_scroll.inner
        body.add(left, weight=1)
        body.add(right_scroll, weight=3)

        ttk.Label(left, text="Quests in this file").pack(anchor="w")
        self.quest_list = tk.Listbox(left, exportselection=False)
        self.quest_list.pack(fill="both", expand=True, pady=4)
        self.quest_list.bind("<<ListboxSelect>>", self.on_selected)

        buttons = ttk.Frame(left)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Add quest",
                   command=self.add_quest).pack(side="left")
        ttk.Button(buttons, text="Duplicate",
                   command=self.duplicate_quest).pack(side="left", padx=3)
        ttk.Button(buttons, text="Delete",
                   command=self.delete_quest).pack(side="left")

        id_row = ttk.Frame(right)
        id_row.pack(fill="x", pady=(0, 4))
        ttk.Label(id_row, text="Expansion quest").pack(side="left")
        self.quest_id = ttk.Combobox(id_row, width=36)
        self.quest_id.pack(side="left", padx=6)
        self.quest_id.bind("<<ComboboxSelected>>", lambda _e: self.commit())
        self.quest_id.bind("<KeyRelease>", lambda _e: self.commit())
        ttk.Button(id_row, text="Browse quests...", width=16,
                   command=self.browse_quests).pack(side="left")

        # Whose quest this wording is for, so you can tell at a glance which
        # NPC you're writing lines for.
        self.quest_npc = ttk.Label(right, text="", style="Accent.TLabel")
        self.quest_npc.pack(anchor="w", pady=(0, 4))

        # The two description lines the mod actually shows to players: line 1
        # on offer (the giver) and line 3 on turn-in (the turn-in NPC). Line 2
        # is only shown mid-quest and the mod overrides it, so it's left out.
        # Both live in the Expansion quest file and are editable in place.
        self._desc_entry = None
        self.desc_box = ttk.LabelFrame(
            right, text="Preview from Expansion quest file",
            style="Section.TLabelframe")
        self.desc_box.pack(fill="x", padx=2, pady=(0, 8))
        self.desc_editors = [
            self._build_desc_editor(
                self.desc_box, "On offer", 0, "giver", "desc"),
            self._build_desc_editor(
                self.desc_box, "On turn-in", 2, "turnin", "desc_turnin"),
        ]

        self.editors = {}

        # One collapsible section per in-game screen, in the order a quest
        # moves through them. The first (offer) opens by default; the rest stay
        # tucked away so the tab isn't a wall of fields.
        for i, (title, specs) in enumerate(self.SCREEN_GROUPS):
            self._build_screen_box(right, title, specs, expanded=(i == 0))

        reward_section = CollapsibleSection(
            right, "Reward picker  (NPC says, optional)", expanded=False)
        reward_section.pack(fill="x", padx=2, pady=(0, 4))
        reward = reward_section.content()
        ttk.Label(reward,
                  text="Only used by quests that let the player pick a "
                       "reward.",
                  wraplength=600, style="Hint.TLabel").pack(
            anchor="w", padx=6, pady=(4, 0))
        self.reward_text = ttk.Entry(reward)
        self.reward_text.pack(fill="x", padx=6, pady=6)
        self.reward_text.bind("<KeyRelease>", lambda _e: self.commit())
        add_entry_undo(self.reward_text)
        attach_entry_spellcheck(self.reward_text)
        self.reward_text.bind(
            "<FocusIn>", lambda _e: self.set_focus_key("RewardSelectText"),
            add="+")

        # Screens shown after this quest is completed. Their shared explanation
        # and the impact line live inside the first completed section (quest
        # list greeting) so nothing floats loose between the dropdowns.
        def completed_intro(box):
            ttk.Label(box,
                      text="After this quest is completed  —  overrides the "
                           "NPC's Quest talk tab. These start the moment it is "
                           "turned in and last until the player finishes a "
                           "higher-numbered quest for the same NPC.",
                      wraplength=560, style="Hint.TLabel").pack(
                anchor="w", padx=6, pady=(4, 2))
            self.completed_impact = ttk.Label(
                box, text="", wraplength=560, justify="left",
                style="Accent.TLabel")
            self.completed_impact.pack(anchor="w", padx=6, pady=(0, 6))

        for i, (title, specs) in enumerate(self.COMPLETED_GROUPS):
            self._build_screen_box(
                right, title, specs,
                intro=completed_intro if i == 0 else None)

    def _build_screen_box(self, parent, title, specs, expanded=False,
                          intro=None):
        """One collapsible section holding the StringListEditors for a single
        in-game screen. Registers each editor in self.editors by its field
        key. intro(box), if given, adds leading widgets inside the section
        before the fields."""
        section = CollapsibleSection(parent, title, expanded=expanded)
        section.pack(fill="x", padx=2, pady=(0, 4))
        box = section.content()
        if intro:
            intro(box)
        for key, label, hint in specs:
            editor = StringListEditor(
                box, label, hint, height=3, on_change=self.commit,
                on_focus=lambda k=key: self.set_focus_key(k))
            editor.pack(fill="x", padx=6, pady=(4, 4))
            self.editors[key] = editor
        return section

    def refresh_quest_choices(self):
        self.quest_id["values"] = self.app.quest_labels()
        self.update_quest_desc()

    def current_desc(self):
        quest_id = quest_id_from_label(self.quest_id.get(), 0)
        entry = self.app.quest_lookup(quest_id) if quest_id > 0 else None
        return entry.get("desc", "") if entry else ""

    def _build_desc_editor(self, parent, base_title, index, role, cache_key):
        """One read-only-until-Edit box for a single Descriptions[] line.

        role picks whose name is shown ('giver' or 'turnin'); index is which
        Descriptions slot Save writes; cache_key is where the value is kept on
        the quest_index entry."""
        box = ttk.LabelFrame(parent, text=base_title)
        box.pack(fill="x", pady=(0, 4))
        text = tk.Text(box, height=3, wrap="word", state="disabled", undo=True)
        text.pack(fill="x", padx=6, pady=(6, 2))
        attach_text_spellcheck(text)
        tools = ttk.Frame(box)
        tools.pack(fill="x", padx=6, pady=(0, 6))
        editor = {"box": box, "text": text, "index": index, "role": role,
                  "cache_key": cache_key, "base_title": base_title,
                  "editing": False}
        editor["edit"] = ttk.Button(tools, text="Edit", width=8,
                                    command=lambda e=editor: self.edit_desc(e))
        editor["edit"].pack(side="left")
        editor["save"] = ttk.Button(tools, text="Save", width=8,
                                    state="disabled",
                                    command=lambda e=editor: self.save_desc(e))
        editor["save"].pack(side="left", padx=4)
        editor["note"] = ttk.Label(tools, text="", style="Hint.TLabel")
        editor["note"].pack(side="left", padx=8)
        return editor

    def _set_editor_text(self, editor, text):
        widget = editor["text"]
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.edit_reset()
        widget.configure(state="disabled")

    def _cancel_editor_edit(self, editor):
        if not editor.get("editing"):
            return
        editor["editing"] = False
        editor["save"].configure(state="disabled")
        editor["edit"].configure(state="normal")
        editor["note"].configure(text="")

    def update_quest_desc(self):
        if not hasattr(self, "desc_editors"):
            return
        quest_id = quest_id_from_label(self.quest_id.get(), 0)
        entry = self.app.quest_lookup(quest_id) if quest_id > 0 else None
        self._desc_entry = entry
        if hasattr(self, "desc_box"):
            title = "Preview from Expansion quest file"
            if quest_id > 0:
                title = title + "   —  quest " + self.app.quest_label(quest_id)
            self.desc_box.configure(text=title)
        if hasattr(self, "quest_npc"):
            givers = self.app.npc_givers_label(quest_id) if quest_id > 0 else ""
            self.quest_npc.configure(
                text=("Quest given by  " + givers) if givers else "")
        # Name the turn-in NPC on the Hand it in box so a quest whose giver and
        # turn-in differ can be told apart while you write its wording.
        if hasattr(self, "editors") and "TurnInTexts" in self.editors:
            base = next(lbl for key, lbl, _hint in self.all_list_fields
                        if key == "TurnInTexts")
            turnins = self.app.npc_turnins_label(quest_id) if quest_id > 0 \
                else ""
            self.editors["TurnInTexts"].configure(
                text=(base + "   —  to " + turnins) if turnins else base)
        if hasattr(self, "completed_impact"):
            self.completed_impact.configure(
                text=self._completed_impact_text(quest_id))

        can_edit = bool(entry and entry.get("file")
                        and os.path.isfile(entry.get("file")))
        for editor in self.desc_editors:
            self._cancel_editor_edit(editor)
            editor["box"].configure(text=self._desc_title(editor, quest_id))
            if entry:
                self._set_editor_text(editor, entry.get(editor["cache_key"], ""))
                editor["note"].configure(
                    text="" if entry.get(editor["cache_key"])
                    else ("Empty - Edit to write one." if can_edit
                          else "Empty."))
            else:
                self._set_editor_text(
                    editor,
                    "Pick an Expansion quest above to see this line. Set a "
                    "quest folder in Settings if the list is empty.")
                editor["note"].configure(text="")
            editor["edit"].configure(
                state="normal" if can_edit else "disabled")
            editor["save"].configure(state="disabled")

    def _completed_impact_text(self, quest_id):
        """Whose quest list this quest's 'once completed' wording appears on,
        and where it sits in each NPC's override chain."""
        entry = self.app.quest_lookup(quest_id) if quest_id > 0 else None
        if not entry:
            return ""
        givers = entry.get("givers") or []
        turnins = entry.get("turnins") or []
        order = []
        for npc in list(givers) + list(turnins):
            if npc not in order:
                order.append(npc)
        if not order:
            return ("Shown on the quest list of whichever NPC gives or takes "
                    "in this quest, once it's completed - but this quest's "
                    "Expansion config lists no giver or turn-in NPC yet.")
        lines = ["Shown once completed on:"]
        for npc in order:
            roles = []
            if npc in givers:
                roles.append("giver")
            if npc in turnins:
                roles.append("turn-in")
            chain = self.app.npc_quest_chain(npc)
            lower = [q for q in chain if q < quest_id]
            higher = [q for q in chain if q > quest_id]
            prev_bit = ("replaces quest %d's wording" % lower[-1]) if lower \
                else "first for this NPC"
            next_bit = ("until quest %d is completed" % higher[0]) if higher \
                else "stays until a higher quest for this NPC is completed"
            lines.append("• %s (%s): %s, %s"
                         % (self.app.npc_speaker_label(npc),
                            " & ".join(roles), prev_bit, next_bit))
        return "\n".join(lines)

    def _desc_title(self, editor, quest_id):
        """Box heading with whoever says the line, e.g.
        'On offer  —  NPC 2 "Steve" says'."""
        who = ""
        if quest_id > 0:
            if editor["role"] == "giver":
                who = self.app.npc_givers_label(quest_id)
            else:
                who = self.app.npc_turnins_label(quest_id)
        if who:
            return "%s   —  %s says" % (editor["base_title"], who)
        return "%s  (from the Expansion quest file)" % editor["base_title"]

    def edit_desc(self, editor):
        entry = self._desc_entry
        if not entry:
            return
        path = entry.get("file")
        if not path or not os.path.isfile(path):
            messagebox.showinfo(
                APP_TITLE,
                "Can't find this quest's config file on disk, so this line "
                "can't be edited here.", parent=self)
            return
        editor["editing"] = True
        editor["text"].configure(state="normal")
        editor["text"].focus_set()
        editor["edit"].configure(state="disabled")
        editor["save"].configure(state="normal")
        editor["note"].configure(
            text="Editing - Save writes this line back to the quest file.")

    def save_desc(self, editor):
        entry = self._desc_entry
        if not entry:
            return
        path = entry.get("file")
        index = editor["index"]
        new_text = editor["text"].get("1.0", "end-1c").strip()
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception as exc:
            messagebox.showerror(
                APP_TITLE, "Couldn't read the quest file:\n\n%s" % exc,
                parent=self)
            return
        descriptions = data.get("Descriptions")
        if not isinstance(descriptions, list):
            descriptions = []
        # The mod expects three lines; pad so writing line 3 never leaves gaps.
        while len(descriptions) <= index:
            descriptions.append("")
        descriptions[index] = new_text
        data["Descriptions"] = descriptions
        try:
            write_json(path, data)
        except Exception as exc:
            messagebox.showerror(
                APP_TITLE, "Couldn't save the quest file:\n\n%s" % exc,
                parent=self)
            return
        entry[editor["cache_key"]] = new_text
        editor["editing"] = False
        self._set_editor_text(editor, new_text)
        editor["save"].configure(state="disabled")
        editor["edit"].configure(state="normal")
        editor["note"].configure(text="Saved to %s" % os.path.basename(path))

    def browse_quests(self):
        if not self.app.ensure_quest_folder():
            return
        if not self.app.quest_index:
            messagebox.showinfo(
                APP_TITLE, "No quest configs found in that folder.",
                parent=self)
            return
        dialog = ChooserDialog(self.app, "Pick a quest", self.app.quest_index,
                               "Sets which quest this wording belongs to.")
        self.wait_window(dialog)
        if dialog.chosen is None:
            return
        self.quest_id.delete(0, tk.END)
        self.quest_id.insert(0, self.app.quest_label(dialog.chosen))
        self.commit()

    def label_for(self, quest):
        return "Quest %s" % self.app.quest_label(quest.get("QuestID", 0))

    def refresh_list(self, keep_index=None):
        self.quest_list.delete(0, tk.END)
        for quest in self.quests:
            self.quest_list.insert(tk.END, self.label_for(quest))
        if self.quests:
            index = keep_index if keep_index is not None else 0
            index = max(0, min(index, len(self.quests) - 1))
            self.quest_list.selection_clear(0, tk.END)
            self.quest_list.selection_set(index)
            self.select(index)
        else:
            self.current = None
            self.loading = True
            self.quest_id.delete(0, tk.END)
            for editor in self.editors.values():
                editor.set_items([])
            self.reward_text.delete(0, tk.END)
            self.loading = False

    def select(self, index):
        self.current = self.quests[index]
        self.loading = True
        self.refresh_quest_choices()
        self.quest_id.delete(0, tk.END)
        self.quest_id.insert(
            0, self.app.quest_label(self.current.get("QuestID", 1)))
        self.update_quest_desc()
        for key, editor in self.editors.items():
            editor.set_items(self.current.get(key) or [])
        self.reward_text.delete(0, tk.END)
        self.reward_text.insert(0, self.current.get("RewardSelectText", ""))
        self.loading = False

    def on_selected(self, _event=None):
        selection = self.quest_list.curselection()
        if selection:
            self.select(selection[0])

    def commit(self):
        if self.loading or not self.current:
            return
        self.current["QuestID"] = max(
            1, quest_id_from_label(self.quest_id.get(), 1))
        for key, editor in self.editors.items():
            self.current[key] = editor.get_items()
        self.current["RewardSelectText"] = self.reward_text.get()
        index = self.quests.index(self.current)
        self.quest_list.delete(index)
        self.quest_list.insert(index, self.label_for(self.current))
        self.quest_list.selection_set(index)
        self.update_quest_desc()
        self.app.mark_editor_dirty("Quest wording")

    def add_quest(self):
        used = {q.get("QuestID", 0) for q in self.quests}
        candidate = 1
        while candidate in used:
            candidate += 1
        self.quests.append(new_quest_entry(candidate))
        self.refresh_list(keep_index=len(self.quests) - 1)

    def duplicate_quest(self):
        if not self.current:
            return
        clone = copy.deepcopy(self.current)
        used = {q.get("QuestID", 0) for q in self.quests}
        candidate = 1
        while candidate in used:
            candidate += 1
        clone["QuestID"] = candidate
        self.quests.append(clone)
        self.refresh_list(keep_index=len(self.quests) - 1)

    def delete_quest(self):
        if not self.current:
            return
        self.quests.remove(self.current)
        self.current = None
        self.refresh_list()

    QUEST_TEXT_CONFIG_VERSION = 2

    # which in-game screen each field appears on
    SCREENS = {
        "AcceptTexts": "offer",
        "DeclineTexts": "offer",
        "OfferBackTexts": "offer",
        "InProgressTexts": "progress",
        "InProgressBackTexts": "progress",
        "TurnInTexts": "turnin",
        "NotYetTexts": "turnin",
        "TurnInBackTexts": "turnin",
        "RewardSelectText": "reward",
        "QuestListTexts": "questlist",
        "QuestListBackTexts": "questlist",
        "NoQuestsTexts": "noquests",
        "NoQuestsBackTexts": "noquests",
        "NoQuestsLeaveTexts": "noquests",
    }

    def set_focus_key(self, key):
        self.focus_key = key

    def field(self, key):
        if not self.current:
            return []
        return list(self.current.get(key) or [])

    def preview_scene(self):
        if not self.current:
            return PreviewScene(
                "Quest wording", "NPC", "", [],
                "Add or pick a quest on the left.")

        quest_id = self.current.get("QuestID", 1)
        entry = self.app.quest_lookup(quest_id)
        givers = (entry.get("givers") if entry else None) or []
        speaker = ""
        if givers:
            speaker = self.app.npc_speaker_label(givers[0])
        if not speaker:
            speaker = "Quest %s" % quest_id
        screen = self.SCREENS.get(self.focus_key, "offer")
        active = self.focus_key

        # which icon each field's buttons carry in game
        icons = {"AcceptTexts": "chat", "DeclineTexts": "chat",
                 "TurnInTexts": "chat", "NotYetTexts": "exit",
                 "InProgressTexts": "exit",
                 "OfferBackTexts": "chat", "InProgressBackTexts": "chat",
                 "TurnInBackTexts": "chat", "QuestListBackTexts": "chat",
                 "NoQuestsBackTexts": "chat", "NoQuestsLeaveTexts": "exit"}

        def rows(key, kind="normal"):
            out = []
            for text in self.field(key):
                mark = kind
                if key == active:
                    mark = "hover"
                out.append((text, mark, icons.get(key, "chat")))
            return out

        if screen == "offer":
            return PreviewScene(
                "Quest offered", speaker,
                self.current_desc()
                or "(the quest's own description shows here)",
                rows("AcceptTexts") + rows("DeclineTexts")
                + rows("OfferBackTexts"),
                "Accept first, then decline, then any back buttons.")

        if screen == "progress":
            return PreviewScene(
                "Quest in progress", speaker,
                "(the quest's own progress text shows here)",
                rows("InProgressTexts") + rows("InProgressBackTexts"))

        if screen == "turnin":
            # Handed in to the turn-in NPC, who may not be the giver.
            turnin_speaker = speaker
            turnins = entry.get("turnins") if entry else None
            if turnins:
                turnin_speaker = self.app.npc_speaker_label(turnins[0]) \
                    or speaker
            turnin_line = (entry.get("desc_turnin") if entry else "") \
                or "(the quest's own turn-in text shows here)"
            return PreviewScene(
                "Ready to hand in", turnin_speaker, turnin_line,
                rows("TurnInTexts") + rows("NotYetTexts")
                + rows("TurnInBackTexts"),
                "Hand-in first, then not-yet, then any back buttons.")

        if screen == "reward":
            reward = self.reward_text.get()
            return PreviewScene(
                "Reward picker", speaker, reward,
                [("Canned Beans x4", "normal", "chat"),
                 ("Ammo Box", "normal", "chat"),
                 ("Field Bandage x2", "normal", "chat")],
                "Rewards come from the quest itself - shown here as examples.")

        if screen == "questlist":
            lines = self.field("QuestListTexts")
            first = ""
            if lines:
                first = lines[0]
            return PreviewScene(
                "Their quest list", speaker, first,
                [("Clear the barn", "normal", "chat"),
                 ("Haul timber from the mill", "normal", "chat")]
                + rows("QuestListBackTexts"),
                "Shown once this quest is completed. One line picked at "
                "random; the first is shown here. Quest titles are examples.")

        lines = self.field("NoQuestsTexts")
        first = ""
        if lines:
            first = lines[0]
        return PreviewScene(
            "No quests available", speaker, first,
            rows("NoQuestsBackTexts") + rows("NoQuestsLeaveTexts"),
            "Shown once this quest is completed and the NPC has nothing "
            "left. Blank buttons still give the player a Back button.")

    def build_output(self):
        self.commit()
        entries = []
        for quest in self.quests:
            entry = {"QuestID": safe_int(quest.get("QuestID", 1), 1)}
            for key, _label, _hint in self.all_list_fields:
                entry[key] = list(quest.get(key) or [])
            entry["RewardSelectText"] = quest.get("RewardSelectText", "")
            entries.append(entry)
        # Stamp the version the mod uses to decide whether a file needs its
        # new fields written in. Never lower one we loaded - a newer mod may
        # have bumped it past what this build knows about.
        version = max(self.config_version, self.QUEST_TEXT_CONFIG_VERSION)
        return {"ConfigVersion": version, "Quests": entries}

    def load(self, data, path=None):
        self.quests = []
        self.config_version = safe_int(
            data.get("ConfigVersion", 0), 0)
        for quest in (data.get("Quests") or []):
            entry = new_quest_entry(safe_int(quest.get("QuestID", 1), 1))
            for key, _label, _hint in self.all_list_fields:
                entry[key] = list(quest.get(key) or [])
            entry["RewardSelectText"] = quest.get("RewardSelectText", "")
            self.quests.append(entry)
        if path:
            self.file_name.set(os.path.basename(path))
        self.refresh_list()

    def output_path(self):
        root = self.app.profile_path.get() or ""
        name = self.file_name.get().strip() or "ServerQuests.json"
        if not name.lower().endswith(".json"):
            name += ".json"
        return os.path.join(root, "QuestText", name)

    def validate(self):
        return validate_quest_dict(self.build_output())


# ---------------------------------------------------------------- menu tab

class MenuConfigTab(ttk.Frame):

    def __init__(self, master, app):
        ttk.Frame.__init__(self, master)
        self.app = app
        self.config = default_menu_config()

        body = ttk.PanedWindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=6, pady=6)
        left_scroll = ScrollFrame(body)
        left = left_scroll.inner
        right = ttk.Frame(body)
        body.add(left_scroll, weight=2)
        body.add(right, weight=3)

        place_section = CollapsibleSection(left, "Placement", expanded=True)
        place_section.pack(fill="x")
        place = place_section.content()

        ttk.Label(place, text="Screen position").grid(
            row=0, column=0, sticky="w", padx=6, pady=4)
        self.position = ttk.Combobox(place, values=POSITIONS, width=16,
                                     state="readonly")
        self.position.set(self.config["Position"])
        self.position.grid(row=0, column=1, sticky="w", pady=4)
        self.position.bind("<<ComboboxSelected>>", lambda _e: self.on_change())

        ttk.Label(place,
                  text="BOTTOM_CENTER keeps the NPC's face visible. CENTER "
                       "covers whoever you're talking to.",
                  wraplength=380, style="Hint.TLabel").grid(
            row=1, column=0, columnspan=3, sticky="w", padx=6)

        self.sliders = {}
        slider_specs = [
            ("PanelWidth", "Panel width", 0.1, 1.0, 0.01,
             "Fraction of the screen. 0.6 = 60% wide."),
            ("PanelHeight", "Panel height", 0.1, 1.0, 0.01, ""),
            ("OffsetX", "Nudge left / right", -0.5, 0.5, 0.01,
             "Applied after the preset. Not clamped - big values push it "
             "off-screen."),
            ("OffsetY", "Nudge up / down", -0.5, 0.5, 0.01, ""),
            ("EdgeMargin", "Edge margin", 0.0, 0.4, 0.005,
             "How far edge-hugging presets sit from the screen edge."),
            ("VisitedResponseOpacity", "Already-picked fade", 0.0, 1.0, 0.05,
             "Dims options the player already chose. 1.0 = no fading."),
        ]
        row_index = 2
        for key, label, low, high, step, hint in slider_specs:
            ttk.Label(place, text=label).grid(row=row_index, column=0,
                                              sticky="w", padx=6, pady=2)
            var = tk.DoubleVar(value=self.config[key])
            scale = ttk.Scale(place, from_=low, to=high, orient="horizontal",
                              variable=var, length=180,
                              command=lambda _v, k=key: self.on_slider(k))
            scale.grid(row=row_index, column=1, sticky="w", pady=2)
            value_label = ttk.Label(place, width=6,
                                    text="%.2f" % self.config[key])
            value_label.grid(row=row_index, column=2, sticky="w")
            self.sliders[key] = (var, value_label, step)
            row_index += 1
            if hint:
                ttk.Label(place, text=hint, wraplength=380,
                          style="Hint.TLabel").grid(
                    row=row_index, column=0, columnspan=3,
                    sticky="w", padx=6)
                row_index += 1

        border = ttk.Frame(place)
        border.grid(row=row_index, column=0, columnspan=3,
                    sticky="w", padx=6, pady=6)
        ttk.Label(border, text="Border thickness (px)").pack(side="left")
        self.border_thickness = ttk.Spinbox(border, from_=0, to=20, width=5,
                                            command=self.on_change)
        self.border_thickness.set(self.config["WindowBorderThickness"])
        self.border_thickness.pack(side="left", padx=6)
        ttk.Label(border, text="0 removes it entirely.",
                  style="Hint.TLabel").pack(side="left")

        colours_section = CollapsibleSection(left, "Colours", expanded=True)
        colours_section.pack(fill="x", pady=6)
        colours = colours_section.content()

        preset_row = ttk.Frame(colours)
        preset_row.pack(fill="x", padx=6, pady=4)
        ttk.Label(preset_row, text="Preset").pack(side="left")
        self.preset = ttk.Combobox(preset_row, values=list(MENU_PRESETS),
                                   width=18, state="readonly")
        self.preset.set("Default (dark)")
        self.preset.pack(side="left", padx=6)
        ttk.Button(preset_row, text="Apply",
                   command=self.apply_preset).pack(side="left")

        self.color_rows = {}
        for key, label, default in COLOR_FIELDS:
            row = ColorRow(colours, label, self.config[key],
                           on_change=self.on_change)
            row.pack(fill="x", padx=6, pady=1)
            self.color_rows[key] = row

        ttk.Label(colours,
                  text="Stored as [Alpha, Red, Green, Blue]. Getting that "
                       "order backwards is the classic mistake - it shows up "
                       "as an invisible or black element.",
                  wraplength=420, style="Hint.TLabel").pack(
            anchor="w", padx=6, pady=(2, 6))

        fonts_section = CollapsibleSection(left, "Text")
        fonts_section.pack(fill="x", pady=(0, 6))
        fonts = fonts_section.content()

        row = ttk.Frame(fonts)
        row.pack(fill="x", padx=6, pady=6)
        ttk.Label(row, text="Font style").pack(side="left")
        self.font_style = ttk.Combobox(
            row, values=[key for key, _desc in FONT_STYLES],
            width=12, state="readonly")
        self.font_style.set("DEFAULT")
        self.font_style.pack(side="left", padx=6)
        self.font_style.bind("<<ComboboxSelected>>",
                             lambda _e: self.on_font_style())

        self.show_icons = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            row, text="Hint icons on buttons",
            variable=self.show_icons,
            command=self.on_change).pack(side="left", padx=(14, 0))
        self.font_note = ttk.Label(row, text="", style="Hint.TLabel")
        self.font_note.pack(side="left", padx=(4, 0))

        ttk.Label(fonts,
                  text="Built into the mod, so no repacking needed. A custom "
                       "layout below overrides whatever is picked here.",
                  wraplength=420, style="Hint.TLabel").pack(
            anchor="w", padx=6, pady=(0, 6))

        override_section = CollapsibleSection(left, "Custom layout (advanced)")
        override_section.pack(fill="x")
        override = override_section.content()
        ttk.Label(override,
                  text="Fonts can't be set here - DayZ only reads a font "
                       "from a .layout file. Point this at your own layout "
                       "to change fonts or structure. Leave empty for the "
                       "built-in window.",
                  wraplength=420, style="Hint.TLabel").pack(
            anchor="w", padx=6, pady=(4, 2))
        self.layout_override = ttk.Entry(override)
        self.layout_override.pack(fill="x", padx=6, pady=(0, 6))
        self.layout_override.bind("<KeyRelease>", lambda _e: self.on_change())

        preview_box = ttk.LabelFrame(right, text="Preview (approximate)",
                                     style="Section.TLabelframe")
        preview_box.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(
            preview_box, background=self.app.palette()["preview_bg"],
            highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.canvas.bind("<Configure>", lambda _e: self.draw_preview())
        ttk.Label(preview_box,
                  text="Rough guide only - it shows placement, sizing and "
                       "colour balance, not the real in-game fonts.",
                  style="Hint.TLabel").pack(anchor="w", padx=8, pady=(0, 6))

        self.draw_preview()

    def on_slider(self, key):
        var, label, step = self.sliders[key]
        value = var.get()
        if step >= 0.01:
            value = round(value / step) * step
        label.configure(text="%.2f" % value)
        self.on_change()

    def on_font_style(self):
        descriptions = dict(FONT_STYLES)
        self.font_note.configure(
            text=descriptions.get(self.font_style.get(), ""))
        self.on_change()

    def on_change(self, *_args):
        self.draw_preview()
        self.app.mark_editor_dirty("Menu appearance")

    def preview_scene(self):
        cfg = self.gather()
        return PreviewScene(
            "Menu appearance", "Trader Denis",
            "Cash or trade, I don't much care which.",
            [("Let's see what you've got.", "hover", "cart"),
             ("Where does your stock come from?", "normal", "chat"),
             ("Already asked this one.", "visited", "chat"),
             ("Nothing right now.", "normal", "exit")],
            "Sample text - this tab sets colours, size and font, not "
            "wording. Style: %s%s" % (
                cfg.get("FontStyle", "DEFAULT"),
                ", hint icons on" if cfg.get("ShowResponseIcons") else ""))

    def apply_preset(self):
        preset = MENU_PRESETS.get(self.preset.get(), {})
        for key, _label, default in COLOR_FIELDS:
            self.color_rows[key].set_value(preset.get(key, default))
        self.on_change()

    def gather(self):
        cfg = {"ConfigVersion": 3, "Position": self.position.get()}
        for key, (var, _label, step) in self.sliders.items():
            value = var.get()
            if step >= 0.01:
                value = round(value / step) * step
            cfg[key] = round(value, 4)
        for key, _label, _default in COLOR_FIELDS:
            cfg[key] = self.color_rows[key].get_value()
        cfg["WindowBorderThickness"] = max(0, min(20, safe_int(
            self.border_thickness.get(), 2)))
        cfg["FontStyle"] = self.font_style.get() or "DEFAULT"
        cfg["ShowResponseIcons"] = bool(self.show_icons.get())
        cfg["LayoutOverride"] = self.layout_override.get().strip()
        return cfg

    def build_output(self):
        cfg = self.gather()
        ordered = {
            "ConfigVersion": 3,
            "Position": cfg["Position"],
            "PanelWidth": cfg["PanelWidth"],
            "PanelHeight": cfg["PanelHeight"],
            "OffsetX": cfg["OffsetX"],
            "OffsetY": cfg["OffsetY"],
            "EdgeMargin": cfg["EdgeMargin"],
        }
        for key, _label, _default in COLOR_FIELDS:
            ordered[key] = cfg[key]
        ordered["WindowBorderThickness"] = cfg["WindowBorderThickness"]
        ordered["VisitedResponseOpacity"] = cfg["VisitedResponseOpacity"]
        ordered["FontStyle"] = cfg["FontStyle"]
        ordered["ShowResponseIcons"] = cfg["ShowResponseIcons"]
        ordered["LayoutOverride"] = cfg["LayoutOverride"]
        return ordered

    def load(self, data):
        defaults = default_menu_config()
        self.position.set(data.get("Position", defaults["Position"]))
        for key, (var, label, step) in self.sliders.items():
            value = safe_float(data.get(key, defaults[key]), defaults[key])
            var.set(value)
            label.configure(text="%.2f" % value)
        for key, _label, default in COLOR_FIELDS:
            value = data.get(key) or default
            if len(value) < 4:
                value = default
            self.color_rows[key].set_value(value)
        self.border_thickness.delete(0, tk.END)
        self.border_thickness.insert(0, str(
            data.get("WindowBorderThickness", 2)))
        self.show_icons.set(bool(data.get("ShowResponseIcons", False)))
        style = str(data.get("FontStyle", "DEFAULT") or "DEFAULT").upper()
        if style not in dict(FONT_STYLES):
            style = "DEFAULT"
        self.font_style.set(style)
        self.on_font_style()
        self.layout_override.delete(0, tk.END)
        self.layout_override.insert(0, data.get("LayoutOverride", ""))
        self.draw_preview()

    def output_path(self):
        return os.path.join(self.app.profile_path.get() or "",
                            "MenuConfig.json")

    def resolved_xy(self, cfg):
        width, height = cfg["PanelWidth"], cfg["PanelHeight"]
        margin = cfg["EdgeMargin"]
        center_x = (1.0 - width) / 2.0
        center_y = (1.0 - height) / 2.0
        right_x = 1.0 - width - margin
        bottom_y = 1.0 - height - margin
        position = cfg["Position"]
        x, y = center_x, center_y
        if position == "TOP_LEFT":
            x, y = margin, margin
        elif position == "TOP_CENTER":
            x, y = center_x, margin
        elif position == "TOP_RIGHT":
            x, y = right_x, margin
        elif position == "CENTER_LEFT":
            x, y = margin, center_y
        elif position == "CENTER_RIGHT":
            x, y = right_x, center_y
        elif position == "BOTTOM_LEFT":
            x, y = margin, bottom_y
        elif position == "BOTTOM_CENTER":
            x, y = center_x, bottom_y
        elif position == "BOTTOM_RIGHT":
            x, y = right_x, bottom_y
        return x + cfg["OffsetX"], y + cfg["OffsetY"]

    def draw_preview(self):
        canvas = self.canvas
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 50 or height < 50:
            return

        # 16:9 screen rectangle centred in the canvas
        screen_w = width - 20
        screen_h = int(screen_w * 9 / 16)
        if screen_h > height - 20:
            screen_h = height - 20
            screen_w = int(screen_h * 16 / 9)
        ox = (width - screen_w) // 2
        oy = (height - screen_h) // 2
        skin = self.app.palette()
        canvas.configure(background=skin["preview_bg"])
        canvas.create_rectangle(ox, oy, ox + screen_w, oy + screen_h,
                                fill=skin["preview_screen"],
                                outline=skin["preview_edge"])
        canvas.create_text(ox + screen_w // 2, oy + 14,
                           text="game screen", fill=skin["preview_text"])

        cfg = self.gather()
        x, y = self.resolved_xy(cfg)
        px = ox + x * screen_w
        py = oy + y * screen_h
        pw = cfg["PanelWidth"] * screen_w
        ph = cfg["PanelHeight"] * screen_h

        bg = blend_over(cfg["BackgroundColor"], skin["preview_screen"])
        border = blend_over(cfg["WindowBorderColor"], bg)
        thickness = max(1, cfg["WindowBorderThickness"])
        canvas.create_rectangle(px, py, px + pw, py + ph, fill=bg,
                                outline=border, width=thickness)

        pad = 10
        text_scale, name_bold = FONT_STYLE_PREVIEW.get(
            cfg.get("FontStyle", "DEFAULT"), (1.0, True))
        name_size = max(6, int(round(10 * text_scale)))
        body_size = max(6, int(round(9 * text_scale)))

        canvas.create_text(px + pad, py + pad, anchor="nw",
                           text="Trader Denis",
                           fill=blend_over(cfg["SpeakerNameColor"], bg),
                           font=("Segoe UI", name_size,
                                 "bold" if name_bold else "normal"))
        canvas.create_text(px + pad, py + pad + 20, anchor="nw",
                           width=max(40, pw - pad * 2),
                           text="Cash or trade, I don't much care which.",
                           fill=blend_over(cfg["SpeakerTextColor"], bg),
                           font=("Segoe UI", body_size))

        option_bg = blend_over(cfg["ResponseBackgroundColor"], bg)
        option_fg = blend_over(cfg["ResponseTextColor"], option_bg)
        faded = blend_over(
            [int(cfg["ResponseTextColor"][0]
                 * cfg["VisitedResponseOpacity"])] +
            list(cfg["ResponseTextColor"][1:4]), option_bg)
        hover = blend_over(cfg["HoverBorderColor"], option_bg)

        labels = [("Let's see what you've got.", "cart"),
                  ("Where does your stock come from?", "chat"),
                  ("Already asked this one.", "chat"),
                  ("Nothing right now.", "exit")]
        show_icons = bool(cfg.get("ShowResponseIcons"))
        top = py + pad + 56
        row_h = max(16 * text_scale, min(30 * text_scale,
                    (ph - (top - py) - pad) / len(labels)))
        for index, (label, icon) in enumerate(labels):
            ry = top + index * row_h
            if ry + row_h - 3 > py + ph - 4:
                break
            outline = hover if index == 0 else option_bg
            right = px + pw - pad
            canvas.create_rectangle(px + pad, ry, right,
                                    ry + row_h - 4, fill=option_bg,
                                    outline=outline, width=2)
            fill_text = option_fg
            if index == 2:
                fill_text = faded
            text_width = right - (px + pad) - 16
            if show_icons:
                size = max(7, row_h * 0.48)
                draw_hint_icon(canvas, right - 7 - size / 2,
                               ry + (row_h - 4) / 2, size, icon, fill_text)
                text_width -= size + 9
            canvas.create_text(px + pad + 8, ry + (row_h - 4) / 2,
                               anchor="w", text=label, fill=fill_text,
                               width=max(28, text_width),
                               font=("Segoe UI", body_size))

    def validate(self):
        cfg = self.gather()
        return validate_menu_dict(cfg, resolved=self.resolved_xy(cfg))


def icon_for_response(response):
    """Same rule the mod uses: a NONE response with no next node closes the
    menu too, so it earns the exit icon rather than the speech bubble."""
    action = response.get("ActionType") or "NONE"
    if action == "OPEN_TRADER":
        return "cart"
    if action == "END_CONVERSATION":
        return "exit"
    if action == "NONE" and safe_int(response.get("NextNodeID", -1), -1) == -1:
        return "exit"
    return "chat"


def draw_hint_icon(canvas, cx, cy, size, kind, colour):
    """Small vector stand-in for the mod's response-button icons. Drawn with
    canvas primitives rather than bitmaps so it tints with the theme and stays
    legible at preview size."""
    if not kind:
        return
    half = size / 2.0
    w = max(1, int(round(size / 7.0)))

    if kind == "exit":
        # door: three sides of a rectangle, open on the right
        left = cx - half
        right = cx - half * 0.15
        canvas.create_line(right, cy - half, left, cy - half,
                           fill=colour, width=w)
        canvas.create_line(left, cy - half, left, cy + half,
                           fill=colour, width=w)
        canvas.create_line(left, cy + half, right, cy + half,
                           fill=colour, width=w)
        # arrow leaving through the gap
        canvas.create_line(cx - half * 0.35, cy, cx + half, cy,
                           fill=colour, width=w)
        canvas.create_line(cx + half * 0.35, cy - half * 0.45,
                           cx + half, cy, fill=colour, width=w)
        canvas.create_line(cx + half * 0.35, cy + half * 0.45,
                           cx + half, cy, fill=colour, width=w)
        return

    if kind == "cart":
        canvas.create_line(cx - half, cy - half * 0.75,
                           cx - half * 0.65, cy - half * 0.75,
                           fill=colour, width=w)
        canvas.create_line(cx - half * 0.65, cy - half * 0.75,
                           cx - half * 0.2, cy + half * 0.35,
                           fill=colour, width=w)
        canvas.create_line(cx - half * 0.5, cy - half * 0.2,
                           cx + half, cy - half * 0.2,
                           fill=colour, width=w)
        canvas.create_line(cx + half, cy - half * 0.2,
                           cx + half * 0.6, cy + half * 0.35,
                           fill=colour, width=w)
        canvas.create_line(cx - half * 0.2, cy + half * 0.35,
                           cx + half * 0.6, cy + half * 0.35,
                           fill=colour, width=w)
        r = max(1.0, size * 0.11)
        for wx in (cx - half * 0.05, cx + half * 0.45):
            canvas.create_oval(wx - r, cy + half * 0.62 - r,
                               wx + r, cy + half * 0.62 + r,
                               fill=colour, outline=colour)
        return

    # chat bubble
    canvas.create_rectangle(cx - half, cy - half * 0.85,
                            cx + half, cy + half * 0.25,
                            outline=colour, width=w)
    canvas.create_polygon(cx - half * 0.55, cy + half * 0.2,
                          cx - half * 0.55, cy + half * 0.95,
                          cx - half * 0.05, cy + half * 0.2,
                          fill=colour, outline=colour)


# ------------------------------------------------------------ live preview

class PreviewScene:
    """One in-game screen, described plainly enough for the preview window to
    draw it. `buttons` are (text, kind[, icon]); kind is
    normal/hover/visited and icon is exit/chat/cart or blank."""

    def __init__(self, title, speaker, line, buttons, note=""):
        self.title = title
        self.speaker = speaker
        self.line = line
        self.buttons = [self.normalise(b) for b in buttons]
        self.note = note

    @staticmethod
    def normalise(button):
        if len(button) >= 3:
            return (button[0], button[1], button[2])
        return (button[0], button[1], "chat")

    def signature(self):
        return (self.title, self.speaker, self.line,
                tuple(self.buttons), self.note)


class LivePreviewWindow(tk.Toplevel):
    """Separate always-available window showing where the text you are typing
    ends up on the in-game menu. Polls rather than hooking every widget, so
    nothing has to remember to notify it."""

    POLL_MS = 250

    def __init__(self, app):
        tk.Toplevel.__init__(self, app)
        self.app = app
        self.title("Live preview - " + APP_TITLE)
        self.geometry("520x420")
        self.minsize(360, 300)

        self.heading = ttk.Label(self, text="", padding=(10, 8, 10, 0),
                                 font=("Segoe UI", 10, "bold"))
        self.heading.pack(fill="x")
        self.note = ttk.Label(self, text="", padding=(10, 0, 10, 4),
                              wraplength=480, style="Hint.TLabel")
        self.note.pack(fill="x")

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        self.canvas.bind("<Configure>", lambda _e: self.redraw(force=True))

        ttk.Label(self,
                  text="Approximate: real fonts and spacing come from the "
                       "game. Colours follow your Menu appearance tab.",
                  wraplength=480, style="Hint.TLabel").pack(
            anchor="w", padx=10, pady=(0, 8))

        self.last_signature = None
        self.scene = None
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(self.POLL_MS, self.tick)
        self.redraw(force=True)

    def close(self):
        self.app.preview_window = None
        self.destroy()

    def tick(self):
        if not self.winfo_exists():
            return
        self.redraw()
        self.after(self.POLL_MS, self.tick)

    def redraw(self, force=False):
        try:
            scene = self.app.preview_scene()
        except Exception:
            scene = PreviewScene("Preview", "", "", [])
        signature = scene.signature()
        if not force and signature == self.last_signature:
            return
        self.last_signature = signature
        self.scene = scene
        self.heading.configure(text=scene.title)
        self.note.configure(text=scene.note)
        self.draw(scene)

    def draw(self, scene):
        canvas = self.canvas
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 60 or height < 60:
            return

        skin = self.app.palette()
        canvas.configure(background=skin["preview_bg"])

        try:
            cfg = self.app.menu_tab.gather()
        except Exception:
            cfg = None

        if cfg:
            bg = blend_over(cfg["BackgroundColor"], skin["preview_screen"])
            border = blend_over(cfg["WindowBorderColor"], bg)
            thickness = max(1, cfg["WindowBorderThickness"])
            name_fill = blend_over(cfg["SpeakerNameColor"], bg)
            line_fill = blend_over(cfg["SpeakerTextColor"], bg)
            option_bg = blend_over(cfg["ResponseBackgroundColor"], bg)
            option_fg = blend_over(cfg["ResponseTextColor"], option_bg)
            hover = blend_over(cfg["HoverBorderColor"], option_bg)
            faded = blend_over(
                [int(cfg["ResponseTextColor"][0]
                     * cfg["VisitedResponseOpacity"])] +
                list(cfg["ResponseTextColor"][1:4]), option_bg)
            scale, name_bold = FONT_STYLE_PREVIEW.get(
                cfg.get("FontStyle", "DEFAULT"), (1.0, True))
        else:
            bg = skin["preview_screen"]
            border = skin["preview_edge"]
            thickness = 2
            name_fill = skin["preview_text"]
            line_fill = skin["preview_text"]
            option_bg = skin["preview_bg"]
            option_fg = skin["preview_text"]
            hover = skin["preview_edge"]
            faded = skin["preview_edge"]
            scale, name_bold = 1.0, True

        pad = 12
        px, py = pad, pad
        pw, ph = width - pad * 2, height - pad * 2
        canvas.create_rectangle(px, py, px + pw, py + ph, fill=bg,
                                outline=border, width=thickness)

        name_size = max(7, int(round(11 * scale)))
        body_size = max(7, int(round(10 * scale)))
        inner = 12
        y = py + inner

        weight = "normal"
        if name_bold:
            weight = "bold"
        canvas.create_text(px + inner, y, anchor="nw", text=scene.speaker,
                           fill=name_fill,
                           font=("Segoe UI", name_size, weight))
        y += name_size + 12

        if scene.line:
            line_id = canvas.create_text(
                px + inner, y, anchor="nw", text=scene.line,
                width=max(60, pw - inner * 2), fill=line_fill,
                font=("Segoe UI", body_size))
        else:
            line_id = canvas.create_text(
                px + inner, y, anchor="nw",
                text="(no line - the mod's built-in text shows here)",
                width=max(60, pw - inner * 2), fill=skin["preview_edge"],
                font=("Segoe UI", body_size, "italic"))
        # Measure what the text actually wrapped to rather than guessing, so
        # the buttons below always start clear of it.
        line_box = canvas.bbox(line_id)
        y = (line_box[3] if line_box else y + body_size) + 14

        show_icons = bool(cfg and cfg.get("ShowResponseIcons"))

        row_h = max(20, int(round(24 * scale)))
        vpad = max(3, int(round(4 * scale)))
        gap = 4
        bottom_limit = py + ph - inner
        for text, kind, icon in scene.buttons:
            if y + row_h > bottom_limit:
                canvas.create_text(px + inner, y, anchor="nw",
                                   text="...", fill=option_fg,
                                   font=("Segoe UI", body_size))
                break
            outline = hover if kind == "hover" else option_bg
            fill_text = faded if kind == "visited" else option_fg
            left = px + inner
            right = px + pw - inner
            text_x = left + 8
            text_width = right - text_x - 8
            icon_size = 0
            if show_icons:
                icon_size = max(8, row_h * 0.5)
                text_width -= icon_size + 10
            # Draw the text first so we can measure how tall it wrapped, then
            # size the highlight box to fit it - a fixed-height box clips long
            # options into the row below.
            txt_id = canvas.create_text(
                text_x, y + vpad, anchor="nw", text=text, fill=fill_text,
                width=max(30, text_width), font=("Segoe UI", body_size))
            text_box = canvas.bbox(txt_id)
            text_h = (text_box[3] - text_box[1]) if text_box else body_size
            box_h = max(row_h - 4, text_h + vpad * 2)
            rect = canvas.create_rectangle(
                left, y, right, y + box_h, fill=option_bg,
                outline=outline, width=2)
            canvas.tag_raise(txt_id, rect)
            if show_icons:
                draw_hint_icon(canvas, right - 8 - icon_size / 2,
                               y + box_h / 2, icon_size, icon, fill_text)
            y += box_h + gap

        if not scene.buttons:
            canvas.create_text(px + pw / 2, y + 20, anchor="n",
                               text="(no buttons yet)",
                               fill=skin["preview_edge"],
                               font=("Segoe UI", body_size, "italic"))


# ---------------------------------------------------------------- save as

class SaveAsDialog(tk.Toplevel):
    """Pick a new destination for the current dialogue tree.

    This is how you take an existing conversation and drop a copy on a
    different NPC or trader without touching the original file.
    """

    def __init__(self, app, dialogue_tab):
        tk.Toplevel.__init__(self, app)
        self.app = app
        self.tab = dialogue_tab
        self.confirmed = False
        self.kind = dialogue_tab.target_kind.get()
        self.key = ""
        self.file_name = dialogue_tab.file_name.get()

        self.title("Save as / copy to")
        self.resizable(False, False)
        self.transient(app)
        self.grab_set()

        self.kind_var = tk.StringVar(value=self.kind)
        self.key_var = tk.StringVar(value="")
        self.name_var = tk.StringVar(value=self.file_name)

        ttk.Label(self,
                  text="Where should this conversation be saved?",
                  style="Accent.TLabel").pack(anchor="w", padx=12, pady=(12, 2))
        ttk.Label(self,
                  text="The file you opened is left alone, so this is the "
                       "safe way to reuse a tree you already like on another "
                       "NPC or trader.",
                  wraplength=420, style="Hint.TLabel").pack(
            anchor="w", padx=12, pady=(0, 8))

        box = ttk.LabelFrame(self, text="Target")
        box.pack(fill="x", padx=12)
        for label, value in [("A single quest NPC", "NPC"),
                             ("A trader", "TRADER"),
                             ("Shared by several NPCs", "SHARED")]:
            ttk.Radiobutton(box, text=label, value=value,
                            variable=self.kind_var,
                            command=self.refresh).pack(anchor="w", padx=8,
                                                       pady=1)

        entry_row = ttk.Frame(self)
        entry_row.pack(fill="x", padx=12, pady=(8, 0))
        self.key_label = ttk.Label(entry_row, text="Quest NPC ID", width=22)
        self.key_label.pack(side="left")
        ttk.Entry(entry_row, textvariable=self.key_var, width=24).pack(
            side="left")

        name_row = ttk.Frame(self)
        name_row.pack(fill="x", padx=12, pady=6)
        ttk.Label(name_row, text="File name", width=22).pack(side="left")
        ttk.Entry(name_row, textvariable=self.name_var, width=24).pack(
            side="left")

        self.preview = ttk.Label(self, text="", wraplength=420,
                                 style="Accent.TLabel")
        self.preview.pack(anchor="w", padx=12, pady=(2, 8))

        buttons = ttk.Frame(self)
        buttons.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(buttons, text="Save here",
                   command=self.confirm).pack(side="right")
        ttk.Button(buttons, text="Cancel",
                   command=self.destroy).pack(side="right", padx=6)

        self.key_var.trace_add("write", lambda *_a: self.refresh())
        self.name_var.trace_add("write", lambda *_a: self.refresh())
        self.refresh()
        app.skin_window(self)

    def refresh(self, *_args):
        kind = self.kind_var.get()
        if kind == "NPC":
            self.key_label.configure(text="Quest NPC ID")
        elif kind == "TRADER":
            self.key_label.configure(text="Trader definition name")
        else:
            self.key_label.configure(text="NPC IDs (comma separated)")

        key = self.key_var.get().strip()
        if kind == "NPC":
            folder = "NPC_%s" % (key or "?")
        elif kind == "TRADER":
            folder = "Trader_%s" % (key or "?")
        else:
            folder = "Shared"
        name = self.name_var.get().strip() or "Dialogue.json"
        if not name.lower().endswith(".json"):
            name += ".json"
        self.target_path = os.path.join(
            self.app.profile_path.get() or "<profile folder>",
            "Dialogues", folder, name)
        self.preview.configure(text="Saves to: " + self.target_path)

    def confirm(self):
        kind = self.kind_var.get()
        key = self.key_var.get().strip()
        if kind == "NPC" and safe_int(key, 0) <= 0:
            messagebox.showwarning(
                APP_TITLE, "Enter the quest NPC ID for the new folder.",
                parent=self)
            return
        if kind == "TRADER" and not key:
            messagebox.showwarning(
                APP_TITLE, "Enter the trader definition name.", parent=self)
            return
        if kind == "SHARED" and not key:
            messagebox.showwarning(
                APP_TITLE,
                "Shared trees must list every NPC ID that uses them.",
                parent=self)
            return

        name = self.name_var.get().strip() or "Dialogue.json"
        if not name.lower().endswith(".json"):
            name += ".json"

        self.kind = kind
        self.key = key
        self.file_name = name
        self.confirmed = True
        self.destroy()


# ---------------------------------------------------------------- main app

class App(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.title(APP_TITLE)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = max(960, min(1360, screen_w - 120))
        height = max(600, min(900, screen_h - 140))
        self.geometry("%dx%d+%d+%d" % (
            width, height,
            max(0, (screen_w - width) // 2),
            max(0, (screen_h - height) // 3)))
        self.minsize(940, 560)

        self.profile_path = tk.StringVar(value="")
        self.quest_folder = tk.StringVar(value="")
        self.quest_index = []   # [{"id": int, "title": str, "file": str}]
        self.npc_index = []
        self.theme_name = "dark"   # matches the mod: gold on near-black
        # editors with changes that have not been written to disk
        self.dirty_editors = set()
        self.preview_window = None
        # tabs report changes while they build themselves; ignore until the
        # window is actually up, or it starts life claiming unsaved work
        self.ready = False
        self.load_settings()

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self._build_header()

        # Built BEFORE the tabs: the editors report status while they
        # construct themselves, so this has to already exist.
        self.status = ttk.Label(self, text="Ready", anchor="w",
                                relief="sunken", padding=4)
        self.status.pack(fill="x", side="bottom")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        self.dialogue_tab = DialogueTab(self.notebook, self)
        self.quest_tab = QuestTextTab(self.notebook, self)
        self.menu_tab = MenuConfigTab(self.notebook, self)
        self.files_tab = ttk.Frame(self.notebook)
        self._build_files_tab(self.files_tab)

        self.notebook.add(self.dialogue_tab, text="  Dialogue  ")
        self.notebook.add(self.quest_tab, text="  Quest wording  ")
        self.notebook.add(self.menu_tab, text="  Menu appearance  ")
        self.notebook.add(self.files_tab, text="  Server files  ")

        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_all(sequence, self.on_mouse_wheel)

        self.dialogue_tab.update_path_preview()
        self.apply_theme()
        self.scan_quests(announce=False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.dirty_editors.clear()
        self.refresh_title()
        self.ready = True
        self.set_status("Ready")

    def _build_header(self):
        brand = ttk.Frame(self)
        brand.pack(fill="x", padx=10, pady=(7, 0))

        self.logo_image = load_logo(self, subsample=5)
        if self.logo_image is not None:
            self.logo_label = tk.Label(brand, image=self.logo_image, bd=0)
            self.logo_label._skip_theme = True
            self.logo_label.pack(side="left", padx=(0, 10))
            try:
                self.icon_image = load_logo(self)
                self.iconphoto(True, self.icon_image)
            except Exception:
                pass

        words = ttk.Frame(brand)
        words.pack(side="left")
        self.wordmark = ttk.Label(words, text="DialogueForge",
                                  font=("Segoe UI", 16, "bold"))
        self.wordmark.pack(anchor="w")
        ttk.Label(words,
                  text="config editor for the DayZ Dialogue Framework",
                  style="Hint.TLabel").pack(anchor="w")

        links = ttk.Frame(brand)
        links.pack(side="right")
        self.github_image = load_png(self, GITHUB_PNG_B64)
        self.workshop_image = load_png(self, WORKSHOP_PNG_B64)
        ttk.Button(links, text=" GitHub", image=self.github_image,
                   compound="left",
                   command=lambda: self.open_url(GITHUB_URL)).pack(
            side="left", padx=4)
        ttk.Button(links, text=" Steam Workshop",
                   image=self.workshop_image, compound="left",
                   command=lambda: self.open_url(WORKSHOP_URL)).pack(
            side="left")

        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=(6, 2))

        self.theme_button = ttk.Button(top, text="Dark mode", width=12,
                                       command=self.toggle_theme)
        self.theme_button.pack(side="right")

        ttk.Button(top, text="Live preview", width=13,
                   command=self.toggle_preview).pack(side="right", padx=6)

        folders = ttk.Frame(top)
        folders.pack(side="left", fill="x", expand=True)
        folders.columnconfigure(1, weight=1)

        ttk.Label(folders, text="Server profile folder").grid(
            row=0, column=0, sticky="w")
        ttk.Entry(folders, textvariable=self.profile_path).grid(
            row=0, column=1, sticky="ew", padx=6)
        ttk.Button(folders, text="Browse...", width=12,
                   command=self.pick_profile).grid(row=0, column=2)

        ttk.Label(folders, text="Expansion quests (optional)").grid(
            row=1, column=0, sticky="w", pady=(3, 0))
        ttk.Entry(folders, textvariable=self.quest_folder).grid(
            row=1, column=1, sticky="ew", padx=6, pady=(3, 0))
        ttk.Button(folders, text="Browse...", width=12,
                   command=self.pick_quest_folder).grid(row=1, column=2,
                                                        pady=(3, 0))
        self.quest_count = ttk.Label(folders, text="", style="Hint.TLabel")
        self.quest_count.grid(row=2, column=1, sticky="w", padx=6)

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8, pady=(0, 2))

        ttk.Button(bar, text="New (blank)",
                   command=self.new_blank).pack(side="left")
        ttk.Button(bar, text="Open file...",
                   command=self.open_file).pack(side="left", padx=6)
        ttk.Button(bar, text="Save",
                   command=self.save_current).pack(side="left")
        ttk.Button(bar, text="Save as / copy to...",
                   command=self.save_as).pack(side="left", padx=6)
        ttk.Button(bar, text="Check this tab",
                   command=self.run_validation).pack(side="left")
        ttk.Button(bar, text="Check ALL config files",
                   command=self.check_all_files).pack(side="left", padx=6)

        ttk.Label(self,
                  text="Point this at the DialogFramework folder in your "
                       "server profile - the one with MenuConfig.json in it. "
                       "Start the server once if it isn't there yet.",
                  wraplength=1200, style="Hint.TLabel").pack(
            anchor="w", padx=10, pady=(1, 4))

    def on_mouse_wheel(self, event):
        """Send the wheel to whatever is under the pointer.

        Tk delivers wheel events by focus, not position, so without this the
        wrong panel scrolls. Widgets that scroll themselves keep the event.
        """
        widget = self.winfo_containing(event.x_root, event.y_root)
        while widget is not None:
            if isinstance(widget, (tk.Listbox, tk.Text)):
                return None
            if widget.winfo_class() in ("Treeview", "TCombobox"):
                return None
            if isinstance(widget, tk.Canvas):
                holder = getattr(widget, "_scrollframe", None)
                if holder is None:
                    return None
                holder.scroll_by(event)
                return "break"
            widget = getattr(widget, "master", None)
        return None

    def open_url(self, url):
        try:
            webbrowser.open_new_tab(url)
            self.set_status("Opened %s in your browser" % url)
        except Exception:
            self.clipboard_clear()
            self.clipboard_append(url)
            messagebox.showinfo(
                APP_TITLE,
                "Couldn't open a browser, so the link is on your "
                "clipboard instead:\n\n%s" % url)

    # ---------------- expansion quest index

    def quest_lookup(self, quest_id):
        for entry in self.quest_index:
            if entry["id"] == quest_id:
                return entry
        return None

    def quest_label(self, quest_id):
        entry = self.quest_lookup(quest_id)
        return "%d - %s" % (quest_id, entry["title"]) if entry \
            else str(quest_id)

    def quest_labels(self):
        return ["%d - %s" % (e["id"], e["title"]) for e in self.quest_index]

    def npc_lookup(self, npc_id):
        for entry in self.npc_index:
            if entry["id"] == npc_id:
                return entry
        return None

    def npc_name(self, npc_id):
        entry = self.npc_lookup(npc_id)
        return entry["title"] if entry else ""

    def npc_speaker_label(self, npc_id):
        """Format an NPC for context: 'NPC 2 "Steve"', or 'NPC 2' when the
        name hasn't been scanned in yet."""
        if not isinstance(npc_id, int) or npc_id <= 0:
            return ""
        name = self.npc_name(npc_id)
        return 'NPC %d "%s"' % (npc_id, name) if name else "NPC %d" % npc_id

    def npc_givers_label(self, quest_id):
        """'NPC 2 "Steve"' for the NPC(s) that hand out a quest, comma-joined
        when several do. Empty when the quest or its givers aren't known."""
        entry = self.quest_lookup(quest_id)
        if not entry:
            return ""
        parts = [self.npc_speaker_label(g) for g in (entry.get("givers") or [])]
        return ", ".join(part for part in parts if part)

    def npc_turnins_label(self, quest_id):
        """'NPC 3 "Bob"' for the NPC(s) a quest is turned in to. Lets a quest
        with a different giver and turn-in be told apart at a glance."""
        entry = self.quest_lookup(quest_id)
        if not entry:
            return ""
        parts = [self.npc_speaker_label(t)
                 for t in (entry.get("turnins") or [])]
        return ", ".join(part for part in parts if part)

    def npc_quest_chain(self, npc_id):
        """Sorted quest IDs an NPC gives OR takes in - the chain the mod walks
        for that NPC's 'once completed' wording (highest completed one wins)."""
        ids = set()
        for entry in self.quest_index:
            if npc_id in (entry.get("givers") or []) \
                    or npc_id in (entry.get("turnins") or []):
                ids.add(entry["id"])
        return sorted(ids)

    def pick_quest_folder(self):
        folder = filedialog.askdirectory(
            title="Select the folder holding your Expansion quest configs")
        if not folder:
            return False
        self.quest_folder.set(folder)
        self.save_settings()
        self.scan_quests(announce=True)
        return True

    def ensure_quest_folder(self):
        """Returns True once a quest folder is set (asking if it isn't)."""
        if self.quest_folder.get() and os.path.isdir(self.quest_folder.get()):
            if not self.quest_index and not self.npc_index:
                self.scan_quests(announce=False)
            return True
        if not messagebox.askyesno(
                APP_TITLE,
                "No Expansion quest folder is set yet.\n\nPick the folder "
                "holding your quest .json files and DialogueForge can list "
                "them by name instead of making you remember ID numbers.\n\n"
                "Choose it now?"):
            return False
        return self.pick_quest_folder()

    def guess_quest_folder(self):
        """Expansion usually sits beside DialogFramework in the profile."""
        if self.quest_folder.get():
            return
        base = self.profile_path.get()
        if not base:
            return
        parent = os.path.dirname(base.rstrip("\\/"))
        for candidate in (
                os.path.join(parent, "ExpansionMod", "Quests"),
                os.path.join(parent, "ExpansionMod", "Quests", "Quests"),
                os.path.join(base, "ExpansionMod", "Quests")):
            if os.path.isdir(candidate):
                self.quest_folder.set(os.path.normpath(candidate))
                self.scan_quests(announce=False)
                return

    @staticmethod
    def quest_scan_roots(root):
        """Expansion splits quests and NPCs into sibling folders, so picking
        the Quests folder alone would otherwise find no NPCs at all."""
        if not root or not os.path.isdir(root):
            return []
        roots = [root]
        parent = os.path.dirname(root.rstrip("/\\"))
        if parent and os.path.isdir(parent):
            for sibling in ("NPCs", "Quests", "Objectives"):
                candidate = os.path.join(parent, sibling)
                if not os.path.isdir(candidate):
                    continue
                if os.path.normcase(os.path.abspath(candidate)) == \
                        os.path.normcase(os.path.abspath(root)):
                    continue
                roots.append(candidate)
        return roots

    def scan_quests(self, announce=False):
        """Index Expansion quest and NPC configs so they can be picked by
        name. Objective configs share the ID field but carry ObjectiveType,
        so they're skipped."""
        self.quest_index = []
        self.npc_index = []
        root = self.quest_folder.get()
        seen = set()

        for base in self.quest_scan_roots(root):
            for current, _dirs, files in os.walk(base):
                for name in sorted(files):
                    if not name.lower().endswith(".json"):
                        continue
                    path = os.path.join(current, name)
                    key = os.path.normcase(os.path.abspath(path))
                    if key in seen:
                        continue
                    seen.add(key)
                    try:
                        with open(path, "r", encoding="utf-8") as handle:
                            data = json.load(handle)
                    except Exception:
                        continue
                    if not isinstance(data, dict) or "ObjectiveType" in data:
                        continue
                    ident = data.get("ID")
                    if not isinstance(ident, int) or isinstance(ident, bool):
                        continue
                    if "NPCName" in data:
                        self.npc_index.append({
                            "id": ident,
                            "title": data.get("NPCName") or name,
                            "file": path})
                    elif "Title" in data:
                        descs = data.get("Descriptions") or []

                        def desc_at(pos, lines=descs):
                            if len(lines) > pos and isinstance(lines[pos], str):
                                return lines[pos].strip()
                            return ""
                        # Line 1 (offer) and line 3 (turn-in) are the two the
                        # mod shows verbatim; line 2 is overridden mid-quest.
                        first_desc = desc_at(0)
                        turnin_desc = desc_at(2)
                        givers = [g for g in (data.get("QuestGiverIDs") or [])
                                  if isinstance(g, int)
                                  and not isinstance(g, bool)]
                        turnins = [t for t in (data.get("QuestTurnInIDs") or [])
                                   if isinstance(t, int)
                                   and not isinstance(t, bool)]
                        self.quest_index.append({
                            "id": ident,
                            "title": data.get("Title") or name,
                            "desc": first_desc,
                            "desc_turnin": turnin_desc,
                            "givers": givers,
                            "turnins": turnins,
                            "file": path})

        self.quest_index.sort(key=lambda e: e["id"])
        self.npc_index.sort(key=lambda e: e["id"])

        summary = "%d quest(s), %d NPC(s) found" % (
            len(self.quest_index), len(self.npc_index))
        if hasattr(self, "quest_count"):
            self.quest_count.configure(text=summary if root else "")
        for tab in ("dialogue_tab", "quest_tab"):
            widget = getattr(self, tab, None)
            if widget is not None:
                widget.refresh_quest_choices()
        if announce:
            self.set_status(summary)
            if not self.quest_index and not self.npc_index:
                messagebox.showinfo(
                    APP_TITLE,
                    "Nothing readable found in that folder.\n\nPoint it at "
                    "the folder containing your Expansion quest .json files "
                    "(the one with Title and ID in each file). Subfolders "
                    "are searched too.")

    # ---------------- theming

    def palette(self):
        return PALETTES[self.theme_name]

    def toggle_theme(self):
        self.theme_name = "dark" if self.theme_name == "light" else "light"
        self.apply_theme()
        self.save_settings()

    def apply_theme(self):
        colors = self.palette()
        style = self.style

        self.configure(background=colors["bg"])
        self.theme_button.configure(
            text="Light mode" if self.theme_name == "dark" else "Dark mode")

        style.configure(".", background=colors["bg"],
                        foreground=colors["fg"],
                        fieldbackground=colors["field"],
                        bordercolor=colors["border"],
                        lightcolor=colors["panel"],
                        darkcolor=colors["panel"],
                        troughcolor=colors["trough"],
                        focuscolor=colors["accent"])

        for name in ("TFrame", "TPanedwindow", "TLabelframe"):
            style.configure(name, background=colors["bg"])
        style.configure("TLabelframe", bordercolor=colors["border"])
        style.configure("TLabelframe.Label", background=colors["bg"],
                        foreground=colors["fg"])
        # Screen-box titles: bold and accent-coloured so each in-game screen
        # reads as its own section and doesn't blend into the field labels.
        style.configure("Section.TLabelframe", background=colors["bg"],
                        bordercolor=colors["border"])
        style.configure("Section.TLabelframe.Label", background=colors["bg"],
                        foreground=colors["accent"],
                        font=("Segoe UI", 10, "bold"))
        # Collapsible section: a clickable header bar over a hideable body.
        style.configure("Section.TFrame", background=colors["bg"])
        style.configure("SectionBody.TFrame", background=colors["bg"])
        style.configure("SectionHeader.TFrame", background=colors["panel"])
        style.configure("SectionTitle.TLabel", background=colors["panel"],
                        foreground=colors["accent"],
                        font=("Segoe UI", 10, "bold"))
        style.configure("SectionSub.TLabel", background=colors["panel"],
                        foreground=colors["hint"])
        style.configure("TLabel", background=colors["bg"],
                        foreground=colors["fg"])
        style.configure("Hint.TLabel", background=colors["bg"],
                        foreground=colors["hint"])
        style.configure("Accent.TLabel", background=colors["bg"],
                        foreground=colors["accent"])
        style.configure("Warn.TLabel", background=colors["bg"],
                        foreground=colors["warn"])

        style.configure("TButton", background=colors["panel"],
                        foreground=colors["fg"], bordercolor=colors["border"])
        style.map("TButton",
                  background=[("active", colors["active"]),
                              ("pressed", colors["active"])],
                  foreground=[("disabled", colors["hint"])])

        for name in ("TCheckbutton", "TRadiobutton"):
            style.configure(name, background=colors["bg"],
                            foreground=colors["fg"])
            style.map(name, background=[("active", colors["bg"])],
                      foreground=[("disabled", colors["hint"])])
        style.configure("TCheckbutton", indicatorcolor=colors["field"])
        style.configure("TRadiobutton", indicatorcolor=colors["field"])

        for name in ("TEntry", "TSpinbox", "TCombobox"):
            style.configure(name, fieldbackground=colors["field"],
                            background=colors["panel"],
                            foreground=colors["fg"],
                            insertcolor=colors["fg"],
                            arrowcolor=colors["fg"],
                            bordercolor=colors["border"])
            style.map(name,
                      fieldbackground=[("readonly", colors["field"]),
                                       ("disabled", colors["panel"])],
                      foreground=[("disabled", colors["hint"])])
        # the combobox popup is a plain tk listbox owned by Tk itself
        self.option_add("*TCombobox*Listbox.background", colors["field"])
        self.option_add("*TCombobox*Listbox.foreground", colors["fg"])
        self.option_add("*TCombobox*Listbox.selectBackground",
                        colors["select_bg"])
        self.option_add("*TCombobox*Listbox.selectForeground",
                        colors["select_fg"])

        style.configure("TNotebook", background=colors["bg"],
                        bordercolor=colors["border"])
        style.configure("TNotebook.Tab", background=colors["panel"],
                        foreground=colors["hint"], padding=(10, 5))
        style.map("TNotebook.Tab",
                  background=[("selected", colors["bg"])],
                  foreground=[("selected", colors["fg"])])

        style.configure("Treeview",
                        background=colors["field"],
                        fieldbackground=colors["field"],
                        foreground=colors["fg"],
                        bordercolor=colors["border"],
                        rowheight=22)
        style.map("Treeview",
                  background=[("selected", colors["select_bg"])],
                  foreground=[("selected", colors["select_fg"])])
        style.configure("Treeview.Heading",
                        background=colors["panel"],
                        foreground=colors["hint"],
                        bordercolor=colors["border"])
        style.map("Treeview.Heading",
                  background=[("active", colors["active"])])

        style.configure("TScale", background=colors["bg"],
                        troughcolor=colors["trough"])
        style.configure("TScrollbar", background=colors["panel"],
                        troughcolor=colors["trough"],
                        arrowcolor=colors["fg"],
                        bordercolor=colors["border"])

        self.skin_children(self)
        if self.logo_image is not None:
            self.logo_label.configure(background=colors["bg"])
        self.wordmark.configure(style="Gold.TLabel")
        style.configure("Gold.TLabel", background=colors["bg"],
                        foreground=colors["gold"],
                        font=("Segoe UI", 16, "bold"))

        self.menu_tab.draw_preview()
        for row in self.menu_tab.color_rows.values():
            row.refresh()
        self.dialogue_tab.refresh_map()

    def skin_children(self, widget):
        """Classic tk widgets ignore ttk styles, so colour them by hand."""
        colors = self.palette()
        for child in widget.winfo_children():
            if getattr(child, "_skip_theme", False):
                self.skin_children(child)
                continue
            if isinstance(child, tk.Listbox):
                child.configure(background=colors["field"],
                                foreground=colors["fg"],
                                selectbackground=colors["select_bg"],
                                selectforeground=colors["select_fg"],
                                highlightthickness=1,
                                highlightbackground=colors["border"],
                                borderwidth=0)
            elif isinstance(child, tk.Text):
                child.configure(background=colors["field"],
                                foreground=colors["fg"],
                                insertbackground=colors["fg"],
                                selectbackground=colors["select_bg"],
                                selectforeground=colors["select_fg"],
                                highlightthickness=1,
                                highlightbackground=colors["border"],
                                borderwidth=0)
            elif isinstance(child, tk.Canvas):
                child.configure(
                    background=colors[getattr(child, "_theme_bg",
                                              "preview_bg")])
            elif isinstance(child, tk.Label):
                child.configure(background=colors["bg"],
                                foreground=colors["fg"])
            self.skin_children(child)

    def skin_window(self, window):
        """Apply the current theme to a pop-up window."""
        window.configure(background=self.palette()["bg"])
        self.skin_children(window)

    def _build_files_tab(self, parent):
        ttk.Label(parent,
                  text="Everything found in the profile folder. Double-click "
                       "a file to open it in the right editor.",
                  style="Hint.TLabel").pack(anchor="w", padx=8, pady=8)

        row = ttk.Frame(parent)
        row.pack(fill="x", padx=8)
        ttk.Button(row, text="Rescan folder",
                   command=self.scan_files).pack(side="left")
        ttk.Button(row, text="Create folder structure",
                   command=self.create_structure).pack(side="left", padx=6)
        ttk.Button(row, text="Open LoadLog.txt",
                   command=self.open_loadlog).pack(side="left")

        self.file_list = tk.Listbox(parent, exportselection=False)
        self.file_list.pack(fill="both", expand=True, padx=8, pady=8)
        self.file_list.bind("<Double-Button-1>",
                            lambda _e: self.open_selected_file())
        self.found_files = []

        ttk.Label(parent,
                  text="Reminder: dialogue and appearance changes need a "
                       "server restart AND a full client restart - not just "
                       "a reconnect. Check Dialogues\\LoadLog.txt afterwards.",
                  wraplength=1100, style="Warn.TLabel").pack(
            anchor="w", padx=8, pady=(0, 8))

    # ---------------- settings

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            self.profile_path.set(data.get("profile_path", ""))
            self.quest_folder.set(data.get("quest_folder", ""))
            if data.get("theme") in PALETTES:
                self.theme_name = data["theme"]
        except Exception:
            pass

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as handle:
                json.dump({"profile_path": self.profile_path.get(),
                           "quest_folder": self.quest_folder.get(),
                           "theme": self.theme_name}, handle)
        except Exception:
            pass

    # ---------------- unsaved changes

    def mark_editor_dirty(self, name):
        if not self.ready:
            return
        self.dirty_editors.add(name)
        self.refresh_title()
        self.set_status("Unsaved changes in %s" % name)

    def clear_editor_dirty(self, name):
        self.dirty_editors.discard(name)
        self.refresh_title()

    def refresh_title(self):
        if self.dirty_editors:
            self.title(APP_TITLE + " *")
        else:
            self.title(APP_TITLE)

    def editor_name(self, editor):
        names = {id(self.dialogue_tab): "Dialogue",
                 id(self.quest_tab): "Quest wording",
                 id(self.menu_tab): "Menu appearance"}
        return names.get(id(editor), "")

    def on_close(self):
        """Never let a closed window be the reason someone loses an hour of
        writing. Save / Don't save / Cancel, with Cancel as the safe escape."""
        if not self.dirty_editors:
            self.destroy()
            return

        pending = ", ".join(sorted(self.dirty_editors))
        answer = messagebox.askyesnocancel(
            APP_TITLE,
            "Unsaved changes in: %s\n\nSave before closing?\n\n"
            "Yes - save, then close\n"
            "No - close and lose the changes\n"
            "Cancel - go back" % pending)

        if answer is None:
            return
        if not answer:
            self.destroy()
            return

        tabs = {"Dialogue": self.dialogue_tab,
                "Quest wording": self.quest_tab,
                "Menu appearance": self.menu_tab}
        for name in sorted(list(self.dirty_editors)):
            tab = tabs.get(name)
            if not tab:
                continue
            self.notebook.select(tab)
            self.save_current(quiet=True)

        if self.dirty_editors:
            # a save was cancelled or failed - stay open rather than lose it
            self.set_status("Still unsaved: %s"
                            % ", ".join(sorted(self.dirty_editors)))
            return

        self.destroy()

    # ---------------- live preview

    def toggle_preview(self):
        if self.preview_window is not None:
            try:
                self.preview_window.close()
            except Exception:
                self.preview_window = None
            return
        self.preview_window = LivePreviewWindow(self)

    def preview_scene(self):
        editor = self.current_editor()
        if editor is not None and hasattr(editor, "preview_scene"):
            return editor.preview_scene()
        return PreviewScene(
            "Live preview", "", "", [],
            "Switch to Dialogue, Quest wording or Menu appearance.")

    def set_status(self, text):
        # Guarded: a status message during start-up should never be able to
        # take the whole program down.
        status = getattr(self, "status", None)
        if status is not None:
            status.configure(text=text)

    # ---------------- profile / files

    def pick_profile(self):
        folder = filedialog.askdirectory(
            title="Select your DialogFramework folder")
        if not folder:
            return
        self.profile_path.set(folder)
        self.save_settings()
        self.dialogue_tab.update_path_preview()
        self.scan_files()
        self.guess_quest_folder()
        self.auto_load_menu_config()

    def auto_load_menu_config(self):
        path = os.path.join(self.profile_path.get(), "MenuConfig.json")
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    self.menu_tab.load(json.load(handle))
                self.set_status("Loaded existing MenuConfig.json")
            except Exception as error:
                self.set_status("MenuConfig.json could not be read: %s" % error)

    def create_structure(self):
        root = self.profile_path.get()
        if not root:
            messagebox.showinfo(APP_TITLE, "Pick a profile folder first.")
            return
        for folder in ["Dialogues", os.path.join("Dialogues", "Shared"),
                       "QuestText"]:
            target = os.path.join(root, folder)
            if not os.path.isdir(target):
                os.makedirs(target)
        self.scan_files()
        self.set_status("Folder structure created under %s" % root)

    def scan_files(self):
        self.file_list.delete(0, tk.END)
        self.found_files = []
        root = self.profile_path.get()
        if not root or not os.path.isdir(root):
            self.file_list.insert(tk.END, "(no profile folder selected)")
            return
        candidates = []
        menu_config = os.path.join(root, "MenuConfig.json")
        if os.path.isfile(menu_config):
            candidates.append(menu_config)
        for sub in ["Dialogues", "QuestText"]:
            base = os.path.join(root, sub)
            for current, _dirs, files in os.walk(base):
                for name in sorted(files):
                    if name.lower().endswith(".json"):
                        candidates.append(os.path.join(current, name))
        for path in candidates:
            self.found_files.append(path)
            self.file_list.insert(tk.END, os.path.relpath(path, root))
        if not candidates:
            self.file_list.insert(tk.END, "(no config files found yet)")

    def open_loadlog(self):
        path = os.path.join(self.profile_path.get(), "Dialogues",
                            "LoadLog.txt")
        if not os.path.isfile(path):
            messagebox.showinfo(
                APP_TITLE,
                "No LoadLog.txt yet - it's written on server start.")
            return
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            content = handle.read()
        window = tk.Toplevel(self)
        window.title("LoadLog.txt")
        window.geometry("900x600")
        text = tk.Text(window, wrap="none")
        text.pack(fill="both", expand=True)
        text.insert("1.0", content)
        text.configure(state="disabled")
        self.skin_window(window)

    def open_selected_file(self):
        selection = self.file_list.curselection()
        if not selection or selection[0] >= len(self.found_files):
            return
        self.load_path(self.found_files[selection[0]])

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Open a config file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if path:
            self.load_path(path)

    def load_path(self, path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception as error:
            messagebox.showerror(
                APP_TITLE,
                "Couldn't read that file:\n\n%s\n\nIf you edited it by hand, "
                "check for a trailing comma or a leftover comment - JSON "
                "doesn't allow either." % error)
            return

        name = os.path.basename(path).lower()
        if "Quests" in data:
            self.quest_tab.load(data, path)
            self.notebook.select(self.quest_tab)
            self.clear_editor_dirty("Quest wording")
            self.set_status("Loaded quest wording from %s" % path)
        elif "Position" in data or name == "menuconfig.json":
            self.menu_tab.load(data)
            self.notebook.select(self.menu_tab)
            self.clear_editor_dirty("Menu appearance")
            self.set_status("Loaded menu config from %s" % path)
        elif "Nodes" in data:
            self.dialogue_tab.load_tree(data, path)
            self.notebook.select(self.dialogue_tab)
            self.clear_editor_dirty("Dialogue")
            self.set_status("Loaded dialogue tree from %s" % path)
        else:
            messagebox.showwarning(
                APP_TITLE,
                "That doesn't look like a Dialogue Framework config - no "
                "Nodes, Quests or Position field found.")

    # ---------------- save & validate

    def current_editor(self):
        current = self.notebook.select()
        widget = self.nametowidget(current)
        if widget in (self.dialogue_tab, self.quest_tab, self.menu_tab):
            return widget
        return None

    def run_validation(self, silent=False):
        editor = self.current_editor()
        if not editor:
            messagebox.showinfo(
                APP_TITLE,
                "This tab has nothing to validate. Switch to Dialogue, "
                "Quest wording or Menu appearance, or use "
                "'Check ALL config files'.")
            return True
        issues, warnings = editor.validate()
        if not issues and not warnings:
            if not silent:
                messagebox.showinfo(APP_TITLE, "No problems found.")
            return True

        window = tk.Toplevel(self)
        window.title("Check results")
        window.geometry("720x480")
        text = tk.Text(window, wrap="word", padx=10, pady=10)
        text.pack(fill="both", expand=True)
        text.tag_configure("head", font=("Segoe UI", 10, "bold"))
        if issues:
            text.insert(tk.END, "Will break in game (%d)\n" % len(issues),
                        "head")
            for issue in issues:
                text.insert(tk.END, "  - %s\n" % issue)
            text.insert(tk.END, "\n")
        if warnings:
            text.insert(tk.END, "Worth a look (%d)\n" % len(warnings), "head")
            for warning in warnings:
                text.insert(tk.END, "  - %s\n" % warning)
        text.configure(state="disabled")
        ttk.Button(window, text="Close",
                   command=window.destroy).pack(pady=6)
        self.skin_window(window)
        text.tag_configure("head", foreground=self.palette()["accent"],
                           font=("Segoe UI", 10, "bold"))
        return not issues

    def new_blank(self):
        editor = self.current_editor()
        if not editor:
            messagebox.showinfo(
                APP_TITLE, "Switch to an editor tab to start something new.")
            return

        labels = {
            self.dialogue_tab: "dialogue tree",
            self.quest_tab: "quest wording file",
            self.menu_tab: "menu appearance (back to defaults)",
        }
        if not messagebox.askyesno(
                APP_TITLE,
                "Start a blank %s?\n\nAnything unsaved in this tab is lost. "
                "Files already on disk are untouched."
                % labels[editor]):
            return

        if editor is self.dialogue_tab:
            self.dialogue_tab.load_tree(new_tree())
            self.dialogue_tab.source_path = None
            self.dialogue_tab.folder_key.set("")
            self.dialogue_tab.file_name.set("Dialogue.json")
            self.dialogue_tab.target_kind.set("NPC")
            self.dialogue_tab.on_target_change()
        elif editor is self.quest_tab:
            self.quest_tab.load({"Quests": []})
            self.quest_tab.file_name.set("ServerQuests.json")
        else:
            self.menu_tab.load(default_menu_config())

        self.apply_theme()
        self.clear_editor_dirty(self.editor_name(editor))
        self.set_status("Blank %s ready" % labels[editor])

    def save_as(self):
        editor = self.current_editor()
        if not editor:
            messagebox.showinfo(
                APP_TITLE, "Switch to an editor tab to save something.")
            return
        if not self.profile_path.get():
            messagebox.showinfo(APP_TITLE, "Pick a profile folder first.")
            return

        if editor is self.dialogue_tab:
            dialog = SaveAsDialog(self, self.dialogue_tab)
            self.wait_window(dialog)
            if not dialog.confirmed:
                return
            self.dialogue_tab.target_kind.set(dialog.kind)
            self.dialogue_tab.folder_key.set(dialog.key)
            self.dialogue_tab.file_name.set(dialog.file_name)
            self.dialogue_tab.on_target_change()
            self.dialogue_tab.source_path = None
            self.save_current()
            return

        if editor is self.quest_tab:
            name = simpledialog.askstring(
                "Save as",
                "File name inside QuestText\\ :",
                initialvalue=self.quest_tab.file_name.get(), parent=self)
            if not name:
                return
            self.quest_tab.file_name.set(name)
            self.save_current()
            return

        # menu config: the mod only ever reads MenuConfig.json, so Save As
        # here is for keeping a copy of a palette you like
        path = filedialog.asksaveasfilename(
            title="Save a copy of this menu config",
            defaultextension=".json",
            initialfile="MenuConfig.json",
            filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            write_json(path, self.menu_tab.build_output())
        except Exception as error:
            messagebox.showerror(APP_TITLE, "Couldn't save:\n\n%s" % error)
            return
        self.scan_files()
        self.set_status("Saved a copy to %s" % path)
        if os.path.basename(path).lower() != "menuconfig.json":
            messagebox.showinfo(
                APP_TITLE,
                "Saved.\n\nNote the mod only ever reads MenuConfig.json in "
                "the root of the profile folder - this copy is for your own "
                "reference.")

    def check_all_files(self):
        """Validate every config in the profile folder, plus the conflicts
        that only show up when you look at the files together."""
        root = self.profile_path.get()
        if not root or not os.path.isdir(root):
            messagebox.showinfo(APP_TITLE, "Pick a profile folder first.")
            return

        self.scan_files()
        if not self.found_files:
            messagebox.showinfo(
                APP_TITLE, "No config files found under:\n%s" % root)
            return

        results = []            # (relative path, issues, warnings)
        npc_claims = {}         # npc id  -> [files claiming it]
        trader_claims = {}      # trader  -> [files]
        quest_claims = {}       # questid -> [files]
        counts = {"dialogue": 0, "quest": 0, "menu": 0, "unknown": 0}

        for path in self.found_files:
            rel = os.path.relpath(path, root)
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
            except Exception as error:
                results.append((rel, ["Won't parse as JSON: %s" % error], []))
                continue
            if not isinstance(data, dict):
                results.append((rel, ["Top level isn't a JSON object."], []))
                continue

            name = os.path.basename(path).lower()
            if "Nodes" in data:
                counts["dialogue"] += 1
                kind, key = kind_and_key_from_path(path)
                issues, warnings = validate_tree_dict(
                    data, kind, key, self.quest_index)
                if kind == "NPC":
                    npc_claims.setdefault(safe_int(key, 0), []).append(rel)
                elif kind == "SHARED":
                    for npc_id in (data.get("NPCIDs") or []):
                        npc_claims.setdefault(npc_id, []).append(rel)
                elif kind == "TRADER":
                    trader_claims.setdefault(key.lower(), []).append(rel)
            elif "Quests" in data:
                counts["quest"] += 1
                issues, warnings = validate_quest_dict(data)
                for quest in (data.get("Quests") or []):
                    quest_claims.setdefault(
                        quest.get("QuestID"), []).append(rel)
            elif "Position" in data or name == "menuconfig.json":
                counts["menu"] += 1
                issues, warnings = validate_menu_dict(data)
                if name != "menuconfig.json":
                    warnings.append(
                        "Only MenuConfig.json in the profile root is read by "
                        "the mod - this copy is ignored.")
            else:
                counts["unknown"] += 1
                issues, warnings = [], [
                    "Not a recognised config - no Nodes, Quests or Position."]
            results.append((rel, issues, warnings))

        cross_issues = []
        cross_warnings = []
        for npc_id, files in sorted(npc_claims.items()):
            if len(files) > 1:
                cross_issues.append(
                    "NPC %s is claimed by %d files: %s. The mod loads one "
                    "tree per NPC, so the others are ignored - check "
                    "LoadLog.txt to see which won."
                    % (npc_id, len(files), ", ".join(sorted(set(files)))))
        for trader, files in sorted(trader_claims.items()):
            if len(set(files)) > 1:
                cross_warnings.append(
                    "Trader '%s' has trees in %d files: %s. Whichever "
                    "matches on more keys wins."
                    % (trader, len(set(files)), ", ".join(sorted(set(files)))))
        for quest_id, files in sorted(
                quest_claims.items(), key=lambda kv: (kv[0] is None, kv[0])):
            if len(set(files)) > 1:
                cross_issues.append(
                    "Quest %s has wording in %d files: %s. All QuestText "
                    "files are merged, so which one wins is not defined."
                    % (quest_id, len(set(files)), ", ".join(sorted(set(files)))))
        if counts["menu"] == 0:
            cross_warnings.append(
                "No MenuConfig.json found - the mod will use its built-in "
                "appearance.")
        if counts["dialogue"] == 0:
            cross_warnings.append(
                "No dialogue trees found under Dialogues\\.")

        self.show_sweep_report(root, results, cross_issues,
                               cross_warnings, counts)

    def show_sweep_report(self, root, results, cross_issues,
                          cross_warnings, counts):
        total_issues = sum(len(r[1]) for r in results) + len(cross_issues)
        total_warnings = sum(len(r[2]) for r in results) + len(cross_warnings)
        clean = [r[0] for r in results if not r[1] and not r[2]]

        window = tk.Toplevel(self)
        window.title("Check all config files")
        window.geometry("880x620")

        head = ttk.Frame(window)
        head.pack(fill="x", padx=12, pady=(12, 4))
        ttk.Label(
            head,
            text="%d file(s) checked - %d will break in game, %d worth a look"
                 % (len(results), total_issues, total_warnings),
            style="Accent.TLabel" if total_issues else "Hint.TLabel").pack(
            anchor="w")
        ttk.Label(
            head,
            text="%d dialogue, %d quest wording, %d menu, %d unrecognised"
                 % (counts["dialogue"], counts["quest"], counts["menu"],
                    counts["unknown"]),
            style="Hint.TLabel").pack(anchor="w")

        body = ttk.Frame(window)
        body.pack(fill="both", expand=True, padx=12, pady=6)
        text = tk.Text(body, wrap="word", padx=10, pady=10)
        scroll = ttk.Scrollbar(body, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="left", fill="y")

        skin = self.palette()
        text.tag_configure("file", foreground=skin["fg"],
                           font=("Segoe UI", 10, "bold"))
        text.tag_configure("bad", foreground=skin["warn"])
        text.tag_configure("head", foreground=skin["accent"],
                           font=("Segoe UI", 10, "bold"))
        text.tag_configure("dim", foreground=skin["hint"])

        lines = []
        if cross_issues or cross_warnings:
            text.insert(tk.END, "Across your whole setup\n", "head")
            lines.append("Across your whole setup")
            for item in cross_issues:
                text.insert(tk.END, "   [breaks] %s\n" % item, "bad")
                lines.append("   [breaks] " + item)
            for item in cross_warnings:
                text.insert(tk.END, "   [check]  %s\n" % item)
                lines.append("   [check]  " + item)
            text.insert(tk.END, "\n")
            lines.append("")

        for rel, issues, warnings in results:
            if not issues and not warnings:
                continue
            text.insert(tk.END, "%s\n" % rel, "file")
            lines.append(rel)
            for item in issues:
                text.insert(tk.END, "   [breaks] %s\n" % item, "bad")
                lines.append("   [breaks] " + item)
            for item in warnings:
                text.insert(tk.END, "   [check]  %s\n" % item)
                lines.append("   [check]  " + item)
            text.insert(tk.END, "\n")
            lines.append("")

        if clean:
            text.insert(tk.END, "Nothing to report in %d file(s)\n"
                        % len(clean), "head")
            lines.append("Nothing to report in %d file(s)" % len(clean))
            for rel in clean:
                text.insert(tk.END, "   %s\n" % rel, "dim")
                lines.append("   " + rel)

        if not total_issues and not total_warnings:
            text.insert(tk.END, "\nEverything checks out.\n", "head")

        text.configure(state="disabled")

        footer = ttk.Frame(window)
        footer.pack(fill="x", padx=12, pady=(0, 12))
        report = "\n".join(lines)

        def copy_report():
            self.clipboard_clear()
            self.clipboard_append(report)
            self.set_status("Report copied to clipboard")

        ttk.Button(footer, text="Copy report",
                   command=copy_report).pack(side="left")
        ttk.Button(footer, text="Close",
                   command=window.destroy).pack(side="right")

        self.skin_window(window)
        text.tag_configure("file", foreground=skin["fg"],
                           font=("Segoe UI", 10, "bold"))
        text.tag_configure("bad", foreground=skin["warn"])
        text.tag_configure("head", foreground=skin["accent"],
                           font=("Segoe UI", 10, "bold"))
        text.tag_configure("dim", foreground=skin["hint"])

    def save_current(self, quiet=False):
        editor = self.current_editor()
        if not editor:
            messagebox.showinfo(
                APP_TITLE, "Switch to an editor tab to save something.")
            return
        if not self.profile_path.get():
            messagebox.showinfo(APP_TITLE, "Pick a profile folder first.")
            return

        issues, _warnings = editor.validate()
        if issues:
            if not messagebox.askyesno(
                    APP_TITLE,
                    "%d problem(s) found that will break this file in game.\n\n"
                    "Save anyway?" % len(issues)):
                self.run_validation()
                return

        path = editor.output_path()
        if os.path.isfile(path):
            if not messagebox.askyesno(
                    APP_TITLE, "Overwrite:\n%s ?" % path):
                return
            try:
                backup = path + ".bak"
                with open(path, "r", encoding="utf-8") as source:
                    content = source.read()
                with open(backup, "w", encoding="utf-8") as target:
                    target.write(content)
            except Exception:
                pass

        try:
            write_json(path, editor.build_output())
        except Exception as error:
            messagebox.showerror(APP_TITLE, "Couldn't save:\n\n%s" % error)
            return

        self.scan_files()
        self.clear_editor_dirty(self.editor_name(editor))
        self.set_status("Saved %s" % path)
        if quiet:
            return
        messagebox.showinfo(
            APP_TITLE,
            "Saved:\n%s\n\nRestart the server, then restart your game client "
            "fully (a reconnect isn't enough), then check "
            "Dialogues\\LoadLog.txt." % path)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
