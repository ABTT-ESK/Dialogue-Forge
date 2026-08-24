import json
import os
import re
import copy
import uuid
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog

try:
    from spellchecker import SpellChecker
except Exception:
    SpellChecker = None

APP_VERSION = "1.3.0"
APP_TITLE = "DialogueForge - DayZ Dialogue Framework config editor"
SETTINGS_FILE = os.path.join(
    os.path.expanduser("~"), ".dialogueforge_settings.json")

# ---------------------------------------------------------------- constants

ACTION_TYPES = [
    "NONE",
    "SHOW_QUEST_LIST",
    "OFFER_QUEST",
    "END_CONVERSATION",
    "OPEN_TRADER",
    "RECRUIT_AI",
    "GO_HOSTILE",
]

ADVANCED_ACTION_TYPES = [
    "ACCEPT_QUEST",
    "DECLINE_QUEST",
    "TURN_IN_QUEST",
]

ACTION_HELP = {
    "NONE": "Go to the node picked in 'Next node'. Set it to (end) to finish.",
    "SHOW_QUEST_LIST": "Opens the live quest list for this NPC.",
    "OFFER_QUEST": "Opens one specific quest's offer screen - its description, what it needs, what it pays, and accept/decline buttons. Pick the quest in 'Quest to use'.",
    "END_CONVERSATION": "Plays a random farewell line, then closes the window.",
    "OPEN_TRADER": "Traders only. Closes dialogue and opens the market menu.",
    "RECRUIT_AI": "AI trees only. Recruits the AI into the player's group, then closes. Respects Expansion's recruit settings; add a RequiredQuestID to lock it behind a quest.",
    "GO_HOSTILE": "AI trees only. The AI's whole patrol turns hostile and attacks the player, then the window closes. For conversations that can go sideways.",
    "ACCEPT_QUEST": "Hands the player a quest immediately, with no offer screen. Pick it in 'Quest to use'. Left empty, it only works inside the live quest-detail step.",
    "DECLINE_QUEST": "Advanced - only meaningful inside the live quest-detail step.",
    "TURN_IN_QUEST": "Advanced - only meaningful inside the live quest-detail step.",
}

NODE_TYPES = ["STANDARD", "QUEST_LIST", "QUEST_DETAIL"]

NOT_LOCKED_LABEL = "Not locked"

NEVER_HIDDEN_LABEL = "Never hidden"

NO_ACTION_QUEST_LABEL = "(none)"

OVERRIDE_NONE_LABEL = "No override"

FONT_STYLES = [
    ("DEFAULT", "Metron Book, standard sizes"),
    ("LIGHT", "Metron Light - thinner, less shouty"),
    ("LARGE", "Metron Book at 120% - easier at distance or on a TV"),
    ("COMPACT", "Metron Book at 85% - more options without scrolling"),
]

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

# ---------------------------------------------------------------- languages

#! Must stay in step with DialogueFWLanguages.All() in the mod and with the
#! column order of the mod's stringtable.csv -- the folder name under
#! Localization\ is what the server matches on.
TRANSLATION_LANGUAGES = [
    ("english", "English"),
    ("czech", "Čeština"),
    ("german", "Deutsch"),
    ("russian", "Русский"),
    ("polish", "Polski"),
    ("hungarian", "Magyar"),
    ("italian", "Italiano"),
    ("spanish", "Español"),
    ("french", "Français"),
    ("chinese", "繁體中文"),
    ("japanese", "日本語"),
    ("portuguese", "Português"),
    ("chinesesimp", "简体中文"),
]

LANGUAGE_CODES = [code for code, _label in TRANSLATION_LANGUAGES]

LANGUAGE_LABELS = dict(TRANSLATION_LANGUAGES)

LOC_FILE_VERSION = 1

#! Tree-level lists the player can see. Field name -> what it is, in the
#! wording the Translations tab shows above each group.
TREE_TEXT_LISTS = [
    ("QuestListTexts", "Line above the quest list"),
    ("NoQuestsTexts", "Line when there is nothing available"),
    ("NoQuestsBackTexts", "Back button, nothing-available screen"),
    ("NoQuestsLeaveTexts", "Leave button, nothing-available screen"),
    ("QuestListBackTexts", "Back button, quest list"),
    ("OfferBackTexts", "Back button, quest offer"),
    ("InProgressBackTexts", "Back button, quest in progress"),
    ("TurnInBackTexts", "Back button, quest turn-in"),
]

QUEST_TEXT_LISTS = [
    ("AcceptTexts", "Accept button"),
    ("DeclineTexts", "Decline button"),
    ("TurnInTexts", "Turn-in button"),
    ("NotYetTexts", "Not-yet button"),
    ("InProgressTexts", "Still-working-on-it button"),
    ("QuestListTexts", "Line above the quest list"),
    ("NoQuestsTexts", "Line when there is nothing available"),
    ("NoQuestsBackTexts", "Back button, nothing-available screen"),
    ("NoQuestsLeaveTexts", "Leave button, nothing-available screen"),
    ("QuestListBackTexts", "Back button, quest list"),
    ("OfferBackTexts", "Back button, quest offer"),
    ("InProgressBackTexts", "Back button, quest in progress"),
    ("TurnInBackTexts", "Back button, quest turn-in"),
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
    match = re.match(r"\s*(\d+)", text or "")
    return int(match.group(1)) if match else fallback


def default_ai_settings():
    return {
        "ResetOnDeath": 1,
        "ResetOnWeaponStowed": 1,
        "ResetOnLeaveArea": 1,
        "LeaveAreaDistance": 60.0,
        "ResetOnSurrender": 1,
        "PersistentAggroThreshold": 0,
        "PersistenceMode": "FACTION",
        "CheckInterval": 2.0,
    }


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
    cfg["ShowLanguageButton"] = True
    cfg["ScaleTextWithPanel"] = False
    cfg["ShowErrorNotifications"] = True
    cfg["LayoutOverride"] = ""
    return cfg


def new_response():
    return {
        "Text": "New option",
        "NextNodeID": -1,
        "RequiredQuestID": -1,
        "ActionType": "NONE",
        "RequiredVars": [],
        "SetVars": [],
        "MaxUses": 0,
        "UsesKey": "",
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
        "AIPatrolID": 0,
        "AIPatrolSubID": 0,
        "ReputationVar": "",
        "ReputationTiers": [],
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
        "Stages": [],
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
    try:
        _a, r, g, b = [max(0, min(255, int(v))) for v in argb[:4]]
    except Exception:
        r, g, b = 255, 255, 255
    return "#%02x%02x%02x" % (r, g, b)


def blend_over(argb, bg_hex="#202020"):
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


def rep_key_from_name(name):
    slug = re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")
    if not slug:
        return ""
    return slug if slug.startswith("rep_") else "rep_" + slug


def rep_label_from_key(key):
    key = str(key or "")
    base = key[4:] if key.startswith("rep_") else key
    base = base.replace("_", " ").strip()
    return base.title() if base else key


VAR_CONDITION_OPS = ("EQUALS", "NOT_EQUAL", "AT_LEAST", "AT_MOST",
                     "MORE_THAN", "BELOW")
VAR_SET_OPS = ("SET", "INCREASE", "DECREASE")


def clean_var_ops(raw):
    ops = []
    for entry in (raw or []):
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("Name", "")).strip()
        if not name:
            continue
        ops.append({
            "Name": name,
            "Op": (str(entry.get("Op", "SET")).strip().upper() or "SET"),
            "Value": safe_int(entry.get("Value", 0), 0),
        })
    return ops




# ------------------------------------------------- translation key builders

#! These key strings are a contract with the mod: DialogueLocKeys in
#! Scripts/3_Game/Dialogue/DialogueLocalization.c builds the exact same
#! strings at runtime. Change one side and translations silently stop
#! matching, so change both together.

def _stage_prefix(stage_index):
    if stage_index is None or stage_index < 0:
        return ""
    return "stage.%d." % stage_index


def loc_node_entries(nodes, stage_index, where_prefix):
    """(key, original, where) for every visible string in a list of nodes."""
    entries = []
    prefix = _stage_prefix(stage_index)
    for node in nodes or []:
        node_id = safe_int(node.get("ID", 1), 1)
        where = "%sNode %d" % (where_prefix, node_id)

        speaker = node.get("SpeakerText", "") or ""
        if speaker.strip():
            entries.append((prefix + "node.%d.SpeakerText" % node_id,
                            speaker, where + "  -  spoken line"))

        for index, line in enumerate(node.get("SpeakerLines") or []):
            text = line.get("Text", "") or ""
            if text.strip():
                entries.append(
                    (prefix + "node.%d.SpeakerLines.%d" % (node_id, index),
                     text, where + "  -  alternate line %d" % (index + 1)))

        for index, response in enumerate(node.get("Responses") or []):
            text = response.get("Text", "") or ""
            if text.strip():
                entries.append(
                    (prefix + "node.%d.Responses.%d" % (node_id, index),
                     text, where + "  -  option %d" % (index + 1)))

    return entries


def loc_tree_entries(data):
    """Every player-visible string in a dialogue tree, in reading order."""
    entries = []

    for field, label in TREE_TEXT_LISTS:
        for index, text in enumerate(data.get(field) or []):
            if str(text).strip():
                entries.append(("tree.%s.%d" % (field, index), str(text),
                                "%s %d" % (label, index + 1)))

    for index, tier in enumerate(data.get("ReputationTiers") or []):
        label = str(tier.get("Label", ""))
        if label.strip():
            entries.append(("tree.ReputationTiers.%d" % index, label,
                            "Reputation tier %d" % (index + 1)))

    entries.extend(loc_node_entries(data.get("Nodes"), -1, ""))

    for stage_index, stage in enumerate(data.get("Stages") or []):
        entries.extend(loc_node_entries(
            stage.get("Nodes"), stage_index,
            "Story tree %d  -  " % (stage_index + 1)))

    return entries


def loc_quest_entries(quest):
    """Every player-visible string in one QuestText entry."""
    entries = []

    for field, label in QUEST_TEXT_LISTS:
        for index, text in enumerate(quest.get(field) or []):
            if str(text).strip():
                entries.append(("quest.%s.%d" % (field, index), str(text),
                                "%s %d" % (label, index + 1)))

    reward = str(quest.get("RewardSelectText", "") or "")
    if reward.strip():
        entries.append(("quest.RewardSelectText", reward,
                        "Line above the reward choice"))

    return entries


def loc_relative_tree_path(profile_root, tree_path):
    """The TreeFile value the mod matches on: the tree's path under
    Dialogues\\, lowercased, forward slashes."""
    if not profile_root or not tree_path:
        return ""
    base = os.path.join(profile_root, "Dialogues")
    try:
        relative = os.path.relpath(tree_path, base)
    except ValueError:
        return ""
    if relative.startswith(".."):
        return ""
    #! An unsaved tree's path still has the "?" placeholder in it. That is not
    #! a real file, so report it as unmatchable rather than writing a TreeFile
    #! the server could never line up with anything.
    if re.search(r'[<>:"|?*]', relative):
        return ""
    return relative.replace("\\", "/").lower()


# ------------------------------------------------------- editor's own language

#! The editor's interface is translated by walking the widget tree and
#! swapping any text we have a translation for, keyed by the English string
#! itself. Nothing in the layout code has to know about languages, and an
#! untranslated string simply stays English.

#! Keyed by the English string exactly as it appears in the layout code.
#! This covers the chrome -- tabs, toolbar, folder pickers. Everything else
#! falls back to English until someone fills in the template written by
#! "Export interface template..." on the Translations tab.
UI_TRANSLATIONS = {
    "czech": {
        "  Dialogue  ": "  Dialog  ",
        "  Quest wording  ": "  Text úkolů  ",
        "  Translations  ": "  Překlady  ",
        "  Menu appearance  ": "  Vzhled okna  ",
        "  Global AI settings  ": "  Globální AI  ",
        "  Factions  ": "  Frakce  ",
        "  AI patrols  ": "  AI hlídky  ",
        "  Server files  ": "  Soubory serveru  ",
        "New (blank)": "Nový (prázdný)",
        "Open file...": "Otevřít soubor...",
        "Save": "Uložit",
        "Save as / copy to...": "Uložit jako / kopírovat...",
        "Check this tab": "Zkontrolovat záložku",
        "Check ALL config files": "Zkontrolovat VŠE",
        "Browse...": "Procházet...",
        "Live preview": "Živý náhled",
        "Dark mode": "Tmavý režim",
        "Light mode": "Světlý režim",
        "Ready": "Připraveno",
        "Translate into": "Přeložit do",
        "Load what's on disk": "Načíst z disku",
        "Pull latest text": "Načíst aktuální text",
        "Original": "Originál",
        "Translation": "Překlad",
        "Apply": "Použít",
        "Copy the original across": "Zkopírovat originál",
        "Next one missing": "Další chybějící",
        "Only show lines still missing": "Zobrazit jen chybějící",
        "Export interface template...": "Exportovat šablonu rozhraní...",
    },
    "german": {
        "  Dialogue  ": "  Dialog  ",
        "  Quest wording  ": "  Quest-Texte  ",
        "  Translations  ": "  Übersetzungen  ",
        "  Menu appearance  ": "  Fenster-Design  ",
        "  Global AI settings  ": "  Globale KI  ",
        "  Factions  ": "  Fraktionen  ",
        "  AI patrols  ": "  KI-Patrouillen  ",
        "  Server files  ": "  Server-Dateien  ",
        "New (blank)": "Neu (leer)",
        "Open file...": "Datei öffnen...",
        "Save": "Speichern",
        "Save as / copy to...": "Speichern unter / kopieren...",
        "Check this tab": "Diesen Tab prüfen",
        "Check ALL config files": "ALLE Dateien prüfen",
        "Browse...": "Durchsuchen...",
        "Live preview": "Live-Vorschau",
        "Dark mode": "Dunkler Modus",
        "Light mode": "Heller Modus",
        "Ready": "Bereit",
        "Translate into": "Übersetzen nach",
        "Load what's on disk": "Von der Festplatte laden",
        "Pull latest text": "Aktuellen Text holen",
        "Original": "Original",
        "Translation": "Übersetzung",
        "Apply": "Übernehmen",
        "Copy the original across": "Original übernehmen",
        "Next one missing": "Nächste fehlende",
        "Only show lines still missing": "Nur fehlende anzeigen",
        "Export interface template...": "Oberflächen-Vorlage exportieren...",
    },
    "russian": {
        "  Dialogue  ": "  Диалог  ",
        "  Quest wording  ": "  Тексты заданий  ",
        "  Translations  ": "  Переводы  ",
        "  Menu appearance  ": "  Вид окна  ",
        "  Global AI settings  ": "  Общие настройки ИИ  ",
        "  Factions  ": "  Фракции  ",
        "  AI patrols  ": "  Патрули ИИ  ",
        "  Server files  ": "  Файлы сервера  ",
        "New (blank)": "Создать (пустой)",
        "Open file...": "Открыть файл...",
        "Save": "Сохранить",
        "Save as / copy to...": "Сохранить как / копировать...",
        "Check this tab": "Проверить вкладку",
        "Check ALL config files": "Проверить ВСЁ",
        "Browse...": "Обзор...",
        "Live preview": "Живой просмотр",
        "Dark mode": "Тёмная тема",
        "Light mode": "Светлая тема",
        "Ready": "Готово",
        "Translate into": "Перевести на",
        "Load what's on disk": "Загрузить с диска",
        "Pull latest text": "Обновить текст",
        "Original": "Оригинал",
        "Translation": "Перевод",
        "Apply": "Применить",
        "Copy the original across": "Скопировать оригинал",
        "Next one missing": "Следующая непереведённая",
        "Only show lines still missing": "Только непереведённые",
        "Export interface template...": "Экспорт шаблона интерфейса...",
    },
    "polish": {
        "  Dialogue  ": "  Dialog  ",
        "  Quest wording  ": "  Teksty zadań  ",
        "  Translations  ": "  Tłumaczenia  ",
        "  Menu appearance  ": "  Wygląd okna  ",
        "  Global AI settings  ": "  Globalne AI  ",
        "  Factions  ": "  Frakcje  ",
        "  AI patrols  ": "  Patrole AI  ",
        "  Server files  ": "  Pliki serwera  ",
        "New (blank)": "Nowy (pusty)",
        "Open file...": "Otwórz plik...",
        "Save": "Zapisz",
        "Save as / copy to...": "Zapisz jako / kopiuj...",
        "Check this tab": "Sprawdź tę kartę",
        "Check ALL config files": "Sprawdź WSZYSTKO",
        "Browse...": "Przeglądaj...",
        "Live preview": "Podgląd na żywo",
        "Dark mode": "Tryb ciemny",
        "Light mode": "Tryb jasny",
        "Ready": "Gotowe",
        "Translate into": "Przetłumacz na",
        "Load what's on disk": "Wczytaj z dysku",
        "Pull latest text": "Pobierz aktualny tekst",
        "Original": "Oryginał",
        "Translation": "Tłumaczenie",
        "Apply": "Zastosuj",
        "Copy the original across": "Skopiuj oryginał",
        "Next one missing": "Następne brakujące",
        "Only show lines still missing": "Pokaż tylko brakujące",
        "Export interface template...": "Eksportuj szablon interfejsu...",
    },
    "hungarian": {
        "  Dialogue  ": "  Párbeszéd  ",
        "  Quest wording  ": "  Küldetésszöveg  ",
        "  Translations  ": "  Fordítások  ",
        "  Menu appearance  ": "  Ablak megjelenés  ",
        "  Global AI settings  ": "  Globális MI  ",
        "  Factions  ": "  Frakciók  ",
        "  AI patrols  ": "  MI járőrök  ",
        "  Server files  ": "  Szerverfájlok  ",
        "New (blank)": "Új (üres)",
        "Open file...": "Fájl megnyitása...",
        "Save": "Mentés",
        "Save as / copy to...": "Mentés másként / másolás...",
        "Check this tab": "Fül ellenőrzése",
        "Check ALL config files": "MINDEN fájl ellenőrzése",
        "Browse...": "Tallózás...",
        "Live preview": "Élő előnézet",
        "Dark mode": "Sötét mód",
        "Light mode": "Világos mód",
        "Ready": "Kész",
        "Translate into": "Fordítás erre",
        "Load what's on disk": "Betöltés lemezről",
        "Pull latest text": "Friss szöveg betöltése",
        "Original": "Eredeti",
        "Translation": "Fordítás",
        "Apply": "Alkalmaz",
        "Copy the original across": "Eredeti átmásolása",
        "Next one missing": "Következő hiányzó",
        "Only show lines still missing": "Csak a hiányzók",
        "Export interface template...": "Felület-sablon exportálása...",
    },
    "italian": {
        "  Dialogue  ": "  Dialogo  ",
        "  Quest wording  ": "  Testi missioni  ",
        "  Translations  ": "  Traduzioni  ",
        "  Menu appearance  ": "  Aspetto finestra  ",
        "  Global AI settings  ": "  IA globale  ",
        "  Factions  ": "  Fazioni  ",
        "  AI patrols  ": "  Pattuglie IA  ",
        "  Server files  ": "  File del server  ",
        "New (blank)": "Nuovo (vuoto)",
        "Open file...": "Apri file...",
        "Save": "Salva",
        "Save as / copy to...": "Salva come / copia in...",
        "Check this tab": "Controlla questa scheda",
        "Check ALL config files": "Controlla TUTTO",
        "Browse...": "Sfoglia...",
        "Live preview": "Anteprima dal vivo",
        "Dark mode": "Tema scuro",
        "Light mode": "Tema chiaro",
        "Ready": "Pronto",
        "Translate into": "Traduci in",
        "Load what's on disk": "Carica dal disco",
        "Pull latest text": "Aggiorna il testo",
        "Original": "Originale",
        "Translation": "Traduzione",
        "Apply": "Applica",
        "Copy the original across": "Copia l'originale",
        "Next one missing": "Prossima mancante",
        "Only show lines still missing": "Mostra solo le mancanti",
        "Export interface template...": "Esporta modello interfaccia...",
    },
    "spanish": {
        "  Dialogue  ": "  Diálogo  ",
        "  Quest wording  ": "  Textos de misión  ",
        "  Translations  ": "  Traducciones  ",
        "  Menu appearance  ": "  Aspecto de ventana  ",
        "  Global AI settings  ": "  IA global  ",
        "  Factions  ": "  Facciones  ",
        "  AI patrols  ": "  Patrullas IA  ",
        "  Server files  ": "  Archivos del servidor  ",
        "New (blank)": "Nuevo (vacío)",
        "Open file...": "Abrir archivo...",
        "Save": "Guardar",
        "Save as / copy to...": "Guardar como / copiar a...",
        "Check this tab": "Revisar esta pestaña",
        "Check ALL config files": "Revisar TODO",
        "Browse...": "Examinar...",
        "Live preview": "Vista previa",
        "Dark mode": "Modo oscuro",
        "Light mode": "Modo claro",
        "Ready": "Listo",
        "Translate into": "Traducir a",
        "Load what's on disk": "Cargar desde el disco",
        "Pull latest text": "Traer el texto actual",
        "Original": "Original",
        "Translation": "Traducción",
        "Apply": "Aplicar",
        "Copy the original across": "Copiar el original",
        "Next one missing": "Siguiente sin traducir",
        "Only show lines still missing": "Solo las que faltan",
        "Export interface template...": "Exportar plantilla de interfaz...",
    },
    "french": {
        "  Dialogue  ": "  Dialogue  ",
        "  Quest wording  ": "  Textes de quête  ",
        "  Translations  ": "  Traductions  ",
        "  Menu appearance  ": "  Apparence  ",
        "  Global AI settings  ": "  IA globale  ",
        "  Factions  ": "  Factions  ",
        "  AI patrols  ": "  Patrouilles IA  ",
        "  Server files  ": "  Fichiers serveur  ",
        "New (blank)": "Nouveau (vide)",
        "Open file...": "Ouvrir un fichier...",
        "Save": "Enregistrer",
        "Save as / copy to...": "Enregistrer sous / copier...",
        "Check this tab": "Vérifier cet onglet",
        "Check ALL config files": "TOUT vérifier",
        "Browse...": "Parcourir...",
        "Live preview": "Aperçu en direct",
        "Dark mode": "Mode sombre",
        "Light mode": "Mode clair",
        "Ready": "Prêt",
        "Translate into": "Traduire vers",
        "Load what's on disk": "Charger depuis le disque",
        "Pull latest text": "Récupérer le texte",
        "Original": "Original",
        "Translation": "Traduction",
        "Apply": "Appliquer",
        "Copy the original across": "Copier l'original",
        "Next one missing": "Suivante non traduite",
        "Only show lines still missing": "Afficher seulement les manquantes",
        "Export interface template...": "Exporter le modèle d'interface...",
    },
    "chinese": {
        "  Dialogue  ": "  對話  ",
        "  Quest wording  ": "  任務文字  ",
        "  Translations  ": "  翻譯  ",
        "  Menu appearance  ": "  視窗外觀  ",
        "  Global AI settings  ": "  全域 AI  ",
        "  Factions  ": "  陣營  ",
        "  AI patrols  ": "  AI 巡邏  ",
        "  Server files  ": "  伺服器檔案  ",
        "New (blank)": "新建（空白）",
        "Open file...": "開啟檔案...",
        "Save": "儲存",
        "Save as / copy to...": "另存為 / 複製到...",
        "Check this tab": "檢查此分頁",
        "Check ALL config files": "檢查全部設定檔",
        "Browse...": "瀏覽...",
        "Live preview": "即時預覽",
        "Dark mode": "深色模式",
        "Light mode": "淺色模式",
        "Ready": "就緒",
        "Translate into": "翻譯成",
        "Load what's on disk": "從磁碟載入",
        "Pull latest text": "取得最新文字",
        "Original": "原文",
        "Translation": "翻譯",
        "Apply": "套用",
        "Copy the original across": "複製原文",
        "Next one missing": "下一個未翻譯",
        "Only show lines still missing": "只顯示未翻譯",
        "Export interface template...": "匯出介面範本...",
    },
    "japanese": {
        "  Dialogue  ": "  会話  ",
        "  Quest wording  ": "  クエスト文  ",
        "  Translations  ": "  翻訳  ",
        "  Menu appearance  ": "  ウィンドウ外観  ",
        "  Global AI settings  ": "  AI 全体設定  ",
        "  Factions  ": "  勢力  ",
        "  AI patrols  ": "  AI パトロール  ",
        "  Server files  ": "  サーバーファイル  ",
        "New (blank)": "新規（空）",
        "Open file...": "ファイルを開く...",
        "Save": "保存",
        "Save as / copy to...": "名前を付けて保存 / コピー...",
        "Check this tab": "このタブを確認",
        "Check ALL config files": "すべての設定を確認",
        "Browse...": "参照...",
        "Live preview": "ライブプレビュー",
        "Dark mode": "ダークモード",
        "Light mode": "ライトモード",
        "Ready": "準備完了",
        "Translate into": "翻訳先",
        "Load what's on disk": "ディスクから読み込む",
        "Pull latest text": "最新のテキストを取得",
        "Original": "原文",
        "Translation": "翻訳",
        "Apply": "適用",
        "Copy the original across": "原文をコピー",
        "Next one missing": "次の未翻訳",
        "Only show lines still missing": "未翻訳のみ表示",
        "Export interface template...": "UI テンプレートを書き出す...",
    },
    "portuguese": {
        "  Dialogue  ": "  Diálogo  ",
        "  Quest wording  ": "  Textos de missão  ",
        "  Translations  ": "  Traduções  ",
        "  Menu appearance  ": "  Aparência da janela  ",
        "  Global AI settings  ": "  IA global  ",
        "  Factions  ": "  Facções  ",
        "  AI patrols  ": "  Patrulhas de IA  ",
        "  Server files  ": "  Ficheiros do servidor  ",
        "New (blank)": "Novo (vazio)",
        "Open file...": "Abrir ficheiro...",
        "Save": "Guardar",
        "Save as / copy to...": "Guardar como / copiar para...",
        "Check this tab": "Verificar este separador",
        "Check ALL config files": "Verificar TUDO",
        "Browse...": "Procurar...",
        "Live preview": "Pré-visualização",
        "Dark mode": "Modo escuro",
        "Light mode": "Modo claro",
        "Ready": "Pronto",
        "Translate into": "Traduzir para",
        "Load what's on disk": "Carregar do disco",
        "Pull latest text": "Obter o texto atual",
        "Original": "Original",
        "Translation": "Tradução",
        "Apply": "Aplicar",
        "Copy the original across": "Copiar o original",
        "Next one missing": "Próxima em falta",
        "Only show lines still missing": "Mostrar só as que faltam",
        "Export interface template...": "Exportar modelo da interface...",
    },
    "chinesesimp": {
        "  Dialogue  ": "  对话  ",
        "  Quest wording  ": "  任务文本  ",
        "  Translations  ": "  翻译  ",
        "  Menu appearance  ": "  窗口外观  ",
        "  Global AI settings  ": "  全局 AI  ",
        "  Factions  ": "  阵营  ",
        "  AI patrols  ": "  AI 巡逻  ",
        "  Server files  ": "  服务器文件  ",
        "New (blank)": "新建（空白）",
        "Open file...": "打开文件...",
        "Save": "保存",
        "Save as / copy to...": "另存为 / 复制到...",
        "Check this tab": "检查此标签页",
        "Check ALL config files": "检查全部配置文件",
        "Browse...": "浏览...",
        "Live preview": "实时预览",
        "Dark mode": "深色模式",
        "Light mode": "浅色模式",
        "Ready": "就绪",
        "Translate into": "翻译为",
        "Load what's on disk": "从磁盘加载",
        "Pull latest text": "获取最新文本",
        "Original": "原文",
        "Translation": "翻译",
        "Apply": "应用",
        "Copy the original across": "复制原文",
        "Next one missing": "下一个未翻译",
        "Only show lines still missing": "仅显示未翻译",
        "Export interface template...": "导出界面模板...",
    },
}

_UI_STATE = {"code": "english", "map": {}, "seen": set()}


def tr(text):
    """Translate one interface string. Unknown strings pass straight through."""
    if not text:
        return text
    _UI_STATE["seen"].add(text)
    return _UI_STATE["map"].get(text, text)


def ui_language_code():
    return _UI_STATE["code"]


def external_locale_path():
    """Optional override file sitting next to the .exe (or the script), so a
    translator can ship a language without rebuilding anything."""
    import sys
    if getattr(sys, "frozen", False):
        folder = os.path.dirname(sys.executable)
    else:
        folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, "DialogueForge_locales.json")


def load_ui_language(code):
    code = (code or "english").lower()
    if code not in LANGUAGE_LABELS:
        code = "english"

    merged = dict(UI_TRANSLATIONS.get(code) or {})
    try:
        with open(external_locale_path(), "r", encoding="utf-8") as handle:
            external = json.load(handle)
        for key, value in (external.get(code) or {}).items():
            if str(value).strip():
                merged[key] = value
    except Exception:
        pass

    _UI_STATE["code"] = code
    _UI_STATE["map"] = merged
    return len(merged)


def quest_flow_rows(data, rel_path):
    """Every place one conversation mentions a quest, as flat rows.
    Walks the base tree and every story tree."""
    rows = []

    def walk(nodes, where_prefix):
        for node in nodes or []:
            node_id = safe_int(node.get("ID", 1), 1)
            for index, response in enumerate(node.get("Responses") or []):
                text = str(response.get("Text", "") or "")
                where = "%snode %d, option %d" % (where_prefix, node_id,
                                                 index + 1)
                action = str(response.get("ActionType", "NONE") or "NONE")

                shown = safe_int(response.get("RequiredQuestID", -1), -1)
                hidden = safe_int(response.get("HideAfterQuestID", -1), -1)
                used = safe_int(response.get("QuestID", -1), -1)

                if shown > 0:
                    rows.append((shown, "shown after", rel_path, where, text))
                if hidden > 0:
                    rows.append((hidden, "hidden after", rel_path, where, text))
                if used > 0:
                    verb = "offered by" if action == "OFFER_QUEST"                         else "handed over by"
                    rows.append((used, verb, rel_path, where, text))

            for index, line in enumerate(node.get("SpeakerLines") or []):
                gate = safe_int(line.get("RequiredQuestID", -1), -1)
                if gate > 0:
                    rows.append((gate, "shown after", rel_path,
                                 "%snode %d, alternate line %d"
                                 % (where_prefix, node_id, index + 1),
                                 str(line.get("Text", "") or "")))
                override = safe_int(line.get("OverrideQuestID", -1), -1)
                if override > 0:
                    rows.append((override, "takes over after", rel_path,
                                 "%snode %d, alternate line %d"
                                 % (where_prefix, node_id, index + 1),
                                 str(line.get("Text", "") or "")))

    walk(data.get("Nodes"), "")
    for stage_index, stage in enumerate(data.get("Stages") or []):
        walk(stage.get("Nodes"), "story tree %d, " % (stage_index + 1))
        required = safe_int(stage.get("RequiredQuestID", -1), -1)
        if required > 0:
            rows.append((required, "unlocks story tree", rel_path,
                         "story tree %d" % (stage_index + 1), ""))

    return rows


def quest_flow_problems(data, rel_path, known_quest_ids):
    """The mistakes that are invisible in game: a line that can never show,
    an action pointing nowhere, a quest id that doesn't exist."""
    problems = []

    def check(nodes, where_prefix):
        for node in nodes or []:
            node_id = safe_int(node.get("ID", 1), 1)
            for index, response in enumerate(node.get("Responses") or []):
                where = "%s: %snode %d, option %d" % (
                    rel_path, where_prefix, node_id, index + 1)
                action = str(response.get("ActionType", "NONE") or "NONE")
                shown = safe_int(response.get("RequiredQuestID", -1), -1)
                hidden = safe_int(response.get("HideAfterQuestID", -1), -1)
                used = safe_int(response.get("QuestID", -1), -1)

                if shown > 0 and shown == hidden:
                    problems.append(
                        "%s shows after quest %d and hides after the same "
                        "quest, so it can never be seen." % (where, shown))

                if action in ("OFFER_QUEST",) and used <= 0:
                    problems.append(
                        "%s uses OFFER_QUEST but names no quest, so it will "
                        "just close the window." % where)

                for quest_id, label in ((shown, "shows after"),
                                        (hidden, "hides after"),
                                        (used, "acts on")):
                    if quest_id > 0 and known_quest_ids                             and quest_id not in known_quest_ids:
                        problems.append(
                            "%s %s quest %d, which isn't in your quest "
                            "folder." % (where, label, quest_id))

    check(data.get("Nodes"), "")
    for stage_index, stage in enumerate(data.get("Stages") or []):
        check(stage.get("Nodes"), "story tree %d, " % (stage_index + 1))

    return problems


def build_quest_flow_report(rows, problems, quest_namer):
    """The text file itself, written to be read rather than parsed."""
    out = []
    out.append("DIALOGUE QUEST FLOW")
    out.append("=" * 60)
    out.append("")
    out.append("Every place your conversations mention a quest, so you don't")
    out.append("have to hold it all in your head. Regenerate this whenever")
    out.append("you change a quest lock.")
    out.append("")

    if problems:
        out.append("PROBLEMS (%d)" % len(problems))
        out.append("-" * 60)
        for problem in problems:
            out.append("  - " + problem)
        out.append("")
    else:
        out.append("No problems found.")
        out.append("")

    out.append("BY QUEST")
    out.append("-" * 60)
    if not rows:
        out.append("  Nothing in your conversations refers to a quest yet.")
    for quest_id in sorted(set(r[0] for r in rows)):
        out.append("")
        out.append("  Quest %d  %s" % (quest_id, quest_namer(quest_id)))
        for verb in ("offered by", "handed over by", "shown after",
                     "hidden after", "takes over after",
                     "unlocks story tree"):
            for row in [r for r in rows if r[0] == quest_id and r[1] == verb]:
                line = "      %-18s %s  %s" % (verb, row[2], row[3])
                if row[4]:
                    out.append(line + '   "' + short_one_line(row[4], 46) + '"')
                else:
                    out.append(line)
    out.append("")

    out.append("BY CONVERSATION")
    out.append("-" * 60)
    for path in sorted(set(r[2] for r in rows)):
        out.append("")
        out.append("  " + path)
        for row in [r for r in rows if r[2] == path]:
            detail = "%s quest %d (%s)" % (row[1], row[0],
                                           quest_namer(row[0]))
            out.append("      %-34s %s" % (row[3], detail))
    out.append("")

    return chr(10).join(out)


def looks_like_localization(data):
    """A Localization overlay, as opposed to a tree or a quest wording file.
    Told apart by its Entries blocks -- a QuestText file has plain lists."""
    if "Trees" in data:
        return True
    for block in (data.get("Quests") or []):
        if isinstance(block, dict) and "Entries" in block:
            return True
    return False


def short_one_line(text, limit=70):
    """Collapse a possibly multi-line string down to one readable row."""
    flat = " ".join(str(text or "").split())
    if len(flat) <= limit:
        return flat
    return flat[:limit - 3] + "..."


def write_json(path, data):
    folder = os.path.dirname(path)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=4, ensure_ascii=False)


def add_entry_undo(entry):
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

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’]*")

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


class VarOpEditor(ttk.Frame):
    """Plain-English editor for a list of variable operations. mode 'set' shows
    Increase/Decrease/Set to; mode 'condition' shows is at least / is not / etc."""

    SET_LABELS = [("Increase by", "INCREASE"), ("Decrease by", "DECREASE"),
                  ("Set to", "SET")]
    COND_LABELS = [("is at least", "AT_LEAST"), ("is more than", "MORE_THAN"),
                   ("is at most", "AT_MOST"), ("is below", "BELOW"),
                   ("is exactly", "EQUALS"), ("is not", "NOT_EQUAL")]

    def __init__(self, master, mode, on_change=None, name_provider=None):
        ttk.Frame.__init__(self, master)
        self.mode = mode
        self.on_change = on_change
        self.name_provider = name_provider
        self.rows = []
        self._loading = False

        pairs = self.SET_LABELS if mode == "set" else self.COND_LABELS
        self.labels = [p[0] for p in pairs]
        self.label_to_code = {}
        self.code_to_label = {}
        for label, code in pairs:
            self.label_to_code[label] = code
            self.code_to_label[code] = label

        self.rows_frame = ttk.Frame(self)
        self.rows_frame.pack(fill="x")

        ttk.Button(self, text="+ Add", width=8,
                   command=lambda: self.add_row()).pack(anchor="w", pady=(2, 2))

    def _fire(self):
        if self.on_change and not self._loading:
            self.on_change()

    def _name_options(self):
        if not self.name_provider:
            return []
        try:
            return list(self.name_provider())
        except Exception:
            return []

    def _resolve_key(self, text):
        text = str(text).strip()
        if not text:
            return ""
        for label, key in self._name_options():
            if text == label or text == key:
                return key
        return text

    def _display_for(self, key):
        for label, existing in self._name_options():
            if existing == key:
                return label
        return key

    def add_row(self, name="", code="", value=0):
        row = ttk.Frame(self.rows_frame)
        row.pack(fill="x", pady=1)

        ttk.Label(row, text="Reputation" if self.mode == "condition"
                  else "Change").pack(side="left")

        if self.name_provider:
            name_entry = ttk.Combobox(row, width=16)
            name_entry.set(self._display_for(name))

            def refresh_values(entry=name_entry):
                entry["values"] = [label for label, _key in self._name_options()]
            refresh_values()
            name_entry.configure(postcommand=refresh_values)
            name_entry.bind("<<ComboboxSelected>>", lambda _e: self._fire())
        else:
            name_entry = ttk.Entry(row, width=16)
            name_entry.insert(0, name)
        name_entry.pack(side="left", padx=4)
        name_entry.bind("<KeyRelease>", lambda _e: self._fire())

        op = ttk.Combobox(row, values=self.labels, width=12, state="readonly")
        op.set(self.code_to_label.get(str(code).upper(), self.labels[0]))
        op.pack(side="left", padx=4)
        op.bind("<<ComboboxSelected>>", lambda _e: self._fire())

        value_spin = ttk.Spinbox(row, from_=-1000000, to=1000000, width=7,
                                 command=self._fire)
        value_spin.delete(0, tk.END)
        value_spin.insert(0, str(value))
        value_spin.pack(side="left", padx=4)
        value_spin.bind("<KeyRelease>", lambda _e: self._fire())

        if self.mode == "set":
            ttk.Label(row, text="point(s)").pack(side="left", padx=(2, 0))

        entry = {"frame": row, "name": name_entry, "op": op,
                 "value": value_spin}
        ttk.Button(row, text="×", width=3,
                   command=lambda: self._remove(entry)).pack(
            side="left", padx=(4, 0))
        self.rows.append(entry)
        self._fire()

    def _remove(self, entry):
        entry["frame"].destroy()
        if entry in self.rows:
            self.rows.remove(entry)
        self._fire()

    def get_ops(self):
        ops = []
        for row in self.rows:
            name = self._resolve_key(row["name"].get())
            if not name:
                continue
            ops.append({
                "Name": name,
                "Op": self.label_to_code.get(row["op"].get(), self.labels[0]),
                "Value": safe_int(row["value"].get(), 0),
            })
        return ops

    def set_ops(self, ops):
        self._loading = True
        for row in list(self.rows):
            row["frame"].destroy()
        self.rows = []
        for op in (ops or []):
            self.add_row(op.get("Name", ""), op.get("Op", ""),
                         safe_int(op.get("Value", 0), 0))
        self._loading = False


class RepTierEditor(ttk.Frame):
    """Rows of 'at N or more, show <label>' for the reputation marker."""

    def __init__(self, master, on_change=None):
        ttk.Frame.__init__(self, master)
        self.on_change = on_change
        self.rows = []
        self._loading = False
        self.rows_frame = ttk.Frame(self)
        self.rows_frame.pack(fill="x")
        ttk.Button(self, text="+ Add tier", width=10,
                   command=lambda: self.add_row()).pack(anchor="w", pady=(2, 2))

    def _fire(self):
        if self.on_change and not self._loading:
            self.on_change()

    def add_row(self, threshold=0, label=""):
        row = ttk.Frame(self.rows_frame)
        row.pack(fill="x", pady=1)
        ttk.Label(row, text="At").pack(side="left")
        t = ttk.Spinbox(row, from_=-1000000, to=1000000, width=6,
                        command=self._fire)
        t.delete(0, tk.END)
        t.insert(0, str(threshold))
        t.pack(side="left", padx=4)
        t.bind("<KeyRelease>", lambda _e: self._fire())
        ttk.Label(row, text="or more, show").pack(side="left")
        lab = ttk.Entry(row, width=16)
        lab.insert(0, label)
        lab.pack(side="left", padx=4)
        lab.bind("<KeyRelease>", lambda _e: self._fire())
        entry = {"frame": row, "threshold": t, "label": lab}
        ttk.Button(row, text="×", width=3,
                   command=lambda: self._remove(entry)).pack(
            side="left", padx=(4, 0))
        self.rows.append(entry)
        self._fire()

    def _remove(self, entry):
        entry["frame"].destroy()
        if entry in self.rows:
            self.rows.remove(entry)
        self._fire()

    def get_tiers(self):
        out = []
        for row in self.rows:
            label = row["label"].get().strip()
            if not label:
                continue
            out.append({"Threshold": safe_int(row["threshold"].get(), 0),
                        "Label": label})
        return out

    def set_tiers(self, tiers):
        self._loading = True
        for row in list(self.rows):
            row["frame"].destroy()
        self.rows = []
        for tier in (tiers or []):
            self.add_row(safe_int(tier.get("Threshold", 0), 0),
                         str(tier.get("Label", "")))
        self._loading = False


class CollapsibleSection(ttk.Frame):

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
        return self.body


class SpeakerLinesEditor(ttk.LabelFrame):

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

        ttk.Label(self.detail, text="Only use this line if:",
                  style="Accent.TLabel").grid(row=5, column=0, sticky="w",
                                              pady=(6, 0))
        self.require_vars = VarOpEditor(self.detail, "condition",
                                        on_change=self.commit_current,
                                        name_provider=self.app.known_reputations)
        self.require_vars.grid(row=6, column=0, sticky="ew", pady=(0, 4))

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
                "RequiredVars": clean_var_ops(line.get("RequiredVars")),
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
            self.require_vars.set_ops([])
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
        self.require_vars.set_ops(self.current.get("RequiredVars"))
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
        self.current["RequiredVars"] = self.require_vars.get_ops()
        index = self.lines.index(self.current)
        self.listbox.delete(index)
        self.listbox.insert(index, self.label_for(self.current))
        self.listbox.selection_set(index)
        self._fire()


class ScrollFrame(ttk.Frame):

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

    def __init__(self, master, label, value, on_change=None):
        ttk.Frame.__init__(self, master)
        self.value = list(value)
        self.on_change = on_change

        ttk.Label(self, text=label, width=22).grid(row=0, column=0, sticky="w")
        self.swatch = tk.Label(self, width=6, relief="sunken", bd=1)
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

def kind_and_key_from_path(path):
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

    for si, stage in enumerate(data.get("Stages") or []):
        tree_no = si + 2
        st_quest = stage.get("RequiredQuestID", -1)
        st_nodes = stage.get("Nodes") or []
        st_ids = [n.get("ID") for n in st_nodes]
        if not isinstance(st_quest, int) or st_quest <= 0:
            issues.append(
                "Tree %d has no unlock quest set, so it can never open." % tree_no)
        elif quest_index and not any(q["id"] == st_quest for q in quest_index):
            warnings.append(
                "Tree %d's unlock quest %s isn't in your quest folder."
                % (tree_no, st_quest))
        if not st_nodes:
            issues.append("Tree %d has no nodes." % tree_no)
        elif stage.get("RootNodeID") not in st_ids:
            issues.append(
                "Tree %d opens on node %s, which doesn't exist in that tree."
                % (tree_no, stage.get("RootNodeID")))
        for node_id in set(st_ids):
            if st_ids.count(node_id) > 1:
                issues.append(
                    "Tree %d uses node ID %s more than once." % (tree_no, node_id))

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

    if kind == "AI" and safe_int(data.get("AIPatrolID", 0), 0) <= 0:
        issues.append(
            "This is an AI tree but AIPatrolID is 0 - it won't attach to any "
            "AI. Set it to the DialogueID of a patrol in AIPatrol\\AIPatrols.json.")

    has_ai_action = any(r.get("ActionType") in ("RECRUIT_AI", "GO_HOSTILE")
                        for nd in nodes for r in nd.get("Responses", []))
    if has_ai_action and safe_int(data.get("AIPatrolID", 0), 0) <= 0:
        warnings.append(
            "An option uses an AI action (RECRUIT_AI / GO_HOSTILE) but no "
            "AIPatrolID is set, so this tree won't attach to any AI.")

    for nd in nodes:
        for r in nd.get("Responses", []):
            label = str(r.get("Text", ""))[:24]
            for o in (r.get("SetVars") or []):
                if o.get("Op") not in VAR_SET_OPS:
                    warnings.append(
                        "Option '%s' changes reputation '%s' with an unknown "
                        "action '%s' - expected Increase by / Decrease by / "
                        "Set to." % (label, o.get("Name"), o.get("Op")))
            for o in (r.get("RequiredVars") or []):
                if o.get("Op") not in VAR_CONDITION_OPS:
                    warnings.append(
                        "Option '%s' checks reputation '%s' with an unknown "
                        "test '%s' - expected is at least / is at most / is "
                        "more than / is below / is exactly / is not."
                        % (label, o.get("Name"), o.get("Op")))

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
    if isinstance(version, int) and version < 6:
        warnings.append(
            "ConfigVersion is %s. FontStyle arrived in version 2, "
            "ShowResponseIcons in 3, ShowLanguageButton in 4, "
            "ScaleTextWithPanel in 5 and ShowErrorNotifications in 6 - "
            "saving from here updates it." % version)

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

    BOX_W = 132
    BOX_H = 46
    GAP_X = 62
    GAP_Y = 26
    MARGIN = 18

    def __init__(self, master, app):
        ttk.Frame.__init__(self, master)
        self.app = app
        self.tree = new_tree()
        self.current_stage_index = -1
        self.current_node = None
        self.current_response = None
        self.loading = False
        self.source_path = None
        self.map_boxes = {}
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
                ("Talkable AI (Expansion)", "AI"),
        ]):
            ttk.Radiobutton(who, text=label, value=value,
                            variable=self.target_kind,
                            command=self.on_target_change).grid(
                row=index, column=0, columnspan=2, sticky="w", padx=6)

        self.key_label = ttk.Label(who, text="Quest NPC ID")
        self.key_label.grid(row=4, column=0, sticky="w", padx=6, pady=(8, 2))
        key_row = ttk.Frame(who)
        key_row.grid(row=4, column=1, sticky="w", pady=(8, 2))
        self.key_entry = ttk.Entry(key_row, textvariable=self.folder_key, width=24)
        self.key_entry.pack(side="left")
        self.key_entry.bind("<KeyRelease>", lambda _e: self.mark_dirty())
        self.pick_npc_button = ttk.Button(key_row, text="Pick NPC...",
                                          width=12, command=self.browse_npcs)
        self.pick_npc_button.pack(side="left", padx=6)
        self.npc_name_label = ttk.Label(key_row, text="",
                                        style="Accent.TLabel")
        self.npc_name_label.pack(side="left", padx=(8, 0))

        self.key_hint = ttk.Label(who, text="", wraplength=340,
                                  style="Hint.TLabel")
        self.key_hint.grid(row=5, column=0, columnspan=2,
                           sticky="w", padx=6, pady=(0, 6))

        ttk.Label(who, text="File name").grid(row=6, column=0,
                                              sticky="w", padx=6)
        name_entry = ttk.Entry(who, textvariable=self.file_name, width=24)
        name_entry.grid(row=6, column=1, sticky="w")
        name_entry.bind("<KeyRelease>", lambda _e: self.mark_dirty())

        self.path_preview = ttk.Label(who, text="", wraplength=340,
                                      style="Accent.TLabel")
        self.path_preview.grid(row=7, column=0, columnspan=2,
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

        self.ai_frame = ttk.LabelFrame(
            left, text="Which AI (Expansion patrol)",
            style="Section.TLabelframe")
        ttk.Label(
            self.ai_frame,
            text="Spawn the AI via AIPatrol\\AIPatrols.json with a DialogueID, "
                 "then lock this tree onto it here.",
            wraplength=340, style="Hint.TLabel").pack(
            anchor="w", padx=6, pady=(4, 2))
        ai_row = ttk.Frame(self.ai_frame)
        ai_row.pack(fill="x", padx=6, pady=(2, 6))
        ttk.Label(ai_row, text="Patrol DialogueID").pack(side="left")
        self.ai_patrol_id = ttk.Spinbox(ai_row, from_=0, to=1000000, width=8,
                                        command=self.mark_dirty)
        self.ai_patrol_id.pack(side="left", padx=(4, 12))
        self.ai_patrol_id.bind("<KeyRelease>", lambda _e: self.mark_dirty())
        ttk.Label(ai_row, text="Sub-ID (0 = any unit)").pack(side="left")
        self.ai_sub_id = ttk.Spinbox(ai_row, from_=0, to=100000, width=6,
                                     command=self.mark_dirty)
        self.ai_sub_id.pack(side="left", padx=4)
        self.ai_sub_id.bind("<KeyRelease>", lambda _e: self.mark_dirty())

        rep_frame = ttk.LabelFrame(
            left, text="This character's reputation (optional)",
            style="Section.TLabelframe")
        rep_frame.pack(fill="x", pady=(6, 0))
        ttk.Label(
            rep_frame,
            text="Give this character a name to track its own reputation, "
                 "separate from everyone else. Other NPCs can then pick this "
                 "name from a dropdown to raise or lower it — no codes to type.",
            wraplength=340, style="Hint.TLabel").pack(anchor="w", padx=6,
                                                      pady=(4, 2))
        rep_row = ttk.Frame(rep_frame)
        rep_row.pack(fill="x", padx=6, pady=(0, 2))
        ttk.Label(rep_row, text="Character name").pack(side="left")
        self.reputation_var = ttk.Entry(rep_row, width=20)
        self.reputation_var.pack(side="left", padx=(4, 0))
        self.reputation_var.bind("<KeyRelease>",
                                 lambda _e: self._on_reputation_typed())
        self.rep_key_hint = ttk.Label(rep_frame, text="", style="Hint.TLabel")
        self.rep_key_hint.pack(anchor="w", padx=6)
        ttk.Label(rep_frame, text="Marker shows (optional tiers):",
                  style="Hint.TLabel").pack(anchor="w", padx=6, pady=(2, 0))
        self.rep_tiers = RepTierEditor(rep_frame, on_change=self.mark_dirty)
        self.rep_tiers.pack(fill="x", padx=6, pady=(0, 4))

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


    def _build_quest_talk(self, parent):
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
        tree_row = ttk.Frame(parent)
        tree_row.pack(fill="x", pady=(0, 4))
        ttk.Label(tree_row, text="Editing tree",
                  font=("Segoe UI", 10, "bold")).pack(side="left")
        self.tree_selector = ttk.Combobox(tree_row, state="readonly", width=28)
        self.tree_selector.pack(side="left", padx=4)
        self.tree_selector.bind("<<ComboboxSelected>>", self.on_tree_changed)
        ttk.Button(tree_row, text="Add tree", width=9,
                   command=self.add_tree).pack(side="left", padx=(6, 0))
        ttk.Button(tree_row, text="Remove", width=8,
                   command=self.remove_tree).pack(side="left", padx=2)

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

        self.stage_quest_row = ttk.Frame(parent)
        self.stage_quest_row.pack(fill="x", pady=(4, 0))
        ttk.Label(self.stage_quest_row, text="This tree unlocks after quest").pack(
            side="left")
        self.stage_quest = ttk.Combobox(self.stage_quest_row, width=22)
        self.stage_quest.pack(side="left", padx=4)
        self.stage_quest.bind("<<ComboboxSelected>>", self.on_stage_quest_changed)
        self.stage_quest.bind("<KeyRelease>", self.on_stage_quest_changed)

        self.stage_priority_row = ttk.Frame(parent)
        ttk.Label(self.stage_priority_row,
                  text="Priority (if several trees qualify, highest wins)").pack(
            side="left")
        self.stage_priority = ttk.Spinbox(
            self.stage_priority_row, from_=0, to=1000000, width=7,
            command=self.on_stage_priority_changed)
        self.stage_priority.pack(side="left", padx=4)
        self.stage_priority.bind("<KeyRelease>",
                                 self.on_stage_priority_changed)

        self.stage_vars_row = ttk.Frame(parent)
        ttk.Label(self.stage_vars_row,
                  text="…or this tree opens when reputation:",
                  style="Accent.TLabel").pack(anchor="w")
        self.stage_vars = VarOpEditor(self.stage_vars_row, "condition",
                                      on_change=self.on_stage_vars_changed,
                                      name_provider=self.app.known_reputations)
        self.stage_vars.pack(fill="x")

    def container(self):
        if self.current_stage_index >= 0:
            stages = self.tree.get("Stages") or []
            if self.current_stage_index < len(stages):
                return stages[self.current_stage_index]
        return self.tree

    def tree_labels(self):
        labels = ["Tree 1  —  starting tree"]
        for i, stage in enumerate(self.tree.get("Stages") or []):
            quest = stage.get("RequiredQuestID", -1)
            if quest and quest > 0:
                cond = "after quest %s" % quest
            elif clean_var_ops(stage.get("RequiredVars")):
                cond = "by reputation"
            else:
                cond = "(no trigger set)"
            labels.append("Tree %d  —  %s" % (i + 2, cond))
        return labels

    def refresh_tree_selector(self):
        if not hasattr(self, "tree_selector"):
            return
        self.tree_selector["values"] = self.tree_labels()
        stages = self.tree.get("Stages") or []
        if self.current_stage_index >= len(stages):
            self.current_stage_index = -1
        self.tree_selector.current(self.current_stage_index + 1)

        if self.current_stage_index >= 0:
            self.stage_quest.configure(state="normal")
            self.stage_quest["values"] = self.app.quest_labels()
            quest = self.container().get("RequiredQuestID", -1)
            self.stage_quest.set(self.app.quest_label(quest)
                                 if quest and quest > 0 else "")
            self.stage_priority_row.pack(fill="x", pady=(4, 0))
            self.stage_vars_row.pack(fill="x", pady=(4, 0))
            self.stage_priority.delete(0, tk.END)
            self.stage_priority.insert(
                0, str(safe_int(self.container().get("Priority", 0), 0)))
            self.stage_vars.set_ops(self.container().get("RequiredVars"))
        else:
            self.stage_quest.set("")
            self.stage_quest.configure(state="disabled")
            self.stage_priority_row.pack_forget()
            self.stage_vars_row.pack_forget()

    def on_tree_changed(self, _event=None):
        self.current_stage_index = self.tree_selector.current() - 1
        self.current_node = None
        self.current_response = None
        self.refresh_tree_selector()
        self.refresh_outline()
        self.refresh_map()

    def on_stage_quest_changed(self, _event=None):
        if self.current_stage_index < 0:
            return
        self.container()["RequiredQuestID"] = max(
            -1, quest_id_from_label(self.stage_quest.get(), -1))
        self.tree_selector["values"] = self.tree_labels()
        self.tree_selector.current(self.current_stage_index + 1)
        self.mark_dirty()

    def on_stage_priority_changed(self, _event=None):
        if self.current_stage_index < 0:
            return
        self.container()["Priority"] = safe_int(self.stage_priority.get(), 0)
        self.mark_dirty()

    def on_stage_vars_changed(self):
        if self.current_stage_index < 0:
            return
        self.container()["RequiredVars"] = self.stage_vars.get_ops()
        self.mark_dirty()

    def add_tree(self):
        stages = self.tree.setdefault("Stages", [])
        stages.append({
            "RequiredQuestID": -1,
            "RootNodeID": 1,
            "Nodes": [new_node(1)],
        })
        self.current_stage_index = len(stages) - 1
        self.current_node = None
        self.current_response = None
        self.refresh_tree_selector()
        self.refresh_outline()
        self.refresh_map()
        self.mark_dirty()
        self.stage_quest.focus_set()

    def remove_tree(self):
        if self.current_stage_index < 0:
            messagebox.showinfo(
                APP_TITLE, "Tree 1 is the base tree and can't be removed.",
                parent=self)
            return
        stages = self.tree.get("Stages") or []
        idx = self.current_stage_index
        if not (0 <= idx < len(stages)):
            return
        quest = stages[idx].get("RequiredQuestID", -1)
        if not messagebox.askyesno(
                APP_TITLE, "Delete Tree %d (after quest %s) and every node in "
                "it?" % (idx + 2, quest), parent=self):
            return
        del stages[idx]
        self.current_stage_index = -1
        self.current_node = None
        self.current_response = None
        self.refresh_tree_selector()
        self.refresh_outline()
        self.refresh_map()
        self.mark_dirty()

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

        ttk.Label(fields, text="Quest to use").grid(row=3, column=0,
                                                    sticky="w", pady=3)
        action_quest_row = ttk.Frame(fields)
        action_quest_row.grid(row=3, column=1, sticky="w", padx=4, pady=3)
        self.action_quest = ttk.Combobox(action_quest_row, width=28)
        self.action_quest.pack(side="left")
        self.action_quest.bind("<<ComboboxSelected>>", self.on_gate_changed)
        self.action_quest.bind("<KeyRelease>", self.on_gate_changed)
        ttk.Button(action_quest_row, text="Browse quests...", width=16,
                   command=self.browse_action_quest).pack(side="left", padx=6)

        self.action_quest_note = ttk.Label(fields, text="", wraplength=430,
                                           style="Hint.TLabel")
        self.action_quest_note.grid(row=4, column=1, sticky="w", padx=4)

        ttk.Label(fields, text="Next node").grid(row=5, column=0,
                                                 sticky="w", pady=3)
        next_row = ttk.Frame(fields)
        next_row.grid(row=5, column=1, sticky="w", padx=4, pady=3)
        self.next_node = ttk.Combobox(next_row, width=19, state="readonly")
        self.next_node.pack(side="left")
        self.next_node.bind("<<ComboboxSelected>>",
                            lambda _e: self.commit_response())
        ttk.Button(next_row, text="Jump to", width=9,
                   command=self.jump_to_next).pack(side="left", padx=6)

        gate_section = CollapsibleSection(
            editor, "Show / hide based on quest  (optional)")
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

        hide_row = ttk.Frame(gate_box)
        hide_row.pack(fill="x", padx=6, pady=(4, 2))
        ttk.Label(hide_row, text="Hide after").pack(side="left")
        self.hide_quest = ttk.Combobox(hide_row, width=34)
        self.hide_quest.pack(side="left", padx=(4, 0))
        self.hide_quest.bind("<<ComboboxSelected>>", self.on_gate_changed)
        self.hide_quest.bind("<KeyRelease>", self.on_gate_changed)
        ttk.Button(hide_row, text="Browse quests...", width=16,
                   command=self.browse_hide_quest).pack(side="left", padx=6)

        self.hide_note = ttk.Label(gate_box, text="", wraplength=430,
                                   style="Hint.TLabel")
        self.hide_note.pack(anchor="w", padx=6, pady=(0, 4))


        var_section = CollapsibleSection(
            editor, "Reputation & story flags  (optional)")
        var_section.pack(fill="x", padx=6, pady=(2, 6))
        var_box = var_section.content()

        ttk.Label(
            var_box,
            text="Pick a character or faction from the dropdown to change or "
                 "check their reputation - the list fills from your NPCs and "
                 "factions. (You can still type a custom flag if you want one.) "
                 "Points start at 0.",
            wraplength=430, style="Hint.TLabel").pack(anchor="w", padx=6,
                                                      pady=(4, 2))

        ttk.Label(var_box, text="When this option is picked:",
                  style="Accent.TLabel").pack(anchor="w", padx=6, pady=(4, 0))
        self.set_vars = VarOpEditor(var_box, "set",
                                    on_change=self.commit_response,
                                    name_provider=self.app.known_reputations)
        self.set_vars.pack(fill="x", padx=6, pady=(0, 4))

        ttk.Label(var_box, text="Only show this option if:",
                  style="Accent.TLabel").pack(anchor="w", padx=6, pady=(4, 0))
        self.require_vars = VarOpEditor(var_box, "condition",
                                        on_change=self.commit_response,
                                        name_provider=self.app.known_reputations)
        self.require_vars.pack(fill="x", padx=6, pady=(0, 6))

        quick = ttk.Frame(var_box)
        quick.pack(fill="x", padx=6, pady=(0, 6))
        ttk.Button(quick, text="+ change this character's reputation",
                   command=self.add_rep_change).pack(side="left")
        ttk.Button(quick, text="+ require this character's reputation",
                   command=self.add_rep_condition).pack(side="left", padx=6)

        limit = ttk.Frame(var_box)
        limit.pack(fill="x", padx=6, pady=(2, 6))
        ttk.Label(limit, text="Max times a player can pick this "
                  "(0 = unlimited)").pack(side="left")
        self.max_uses = ttk.Spinbox(limit, from_=0, to=100000, width=7,
                                    command=self.commit_response)
        self.max_uses.pack(side="left", padx=(4, 0))
        self.max_uses.bind("<KeyRelease>", lambda _e: self.commit_response())
        ttk.Label(
            var_box,
            text="Stops rep-farming: after this many picks (per player, ever) "
                 "the option disappears. 1 = one-time only.",
            wraplength=430, style="Hint.TLabel").pack(anchor="w", padx=6,
                                                      pady=(0, 4))

    def _on_reputation_typed(self):
        self._refresh_rep_hint()
        self.mark_dirty()

    def _refresh_rep_hint(self):
        if not hasattr(self, "rep_key_hint"):
            return
        key = rep_key_from_name(self.reputation_var.get())
        self.rep_key_hint.configure(text=("saved as: " + key) if key else "")

    def _character_rep_name(self):
        rep = rep_key_from_name(self.reputation_var.get())
        if not rep:
            messagebox.showinfo(
                APP_TITLE,
                "Give this character a name first, in the \"This character's "
                "reputation\" box on the \"Who it's for & voice lines\" tab.",
                parent=self)
        return rep

    def add_rep_change(self):
        if not self.current_response:
            return
        rep = self._character_rep_name()
        if rep:
            self.set_vars.add_row(rep, "INCREASE", 1)

    def add_rep_condition(self):
        if not self.current_response:
            return
        rep = self._character_rep_name()
        if rep:
            self.require_vars.add_row(rep, "AT_LEAST", 1)

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
                "Conversation screen", speaker, "", [],
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
            "Conversation screen  —  node %s" % node.get("ID"), speaker,
            line, buttons, note)

    def speaker_label(self):
        kind = self.target_kind.get()
        key = self.folder_key.get().strip()
        if kind == "NPC" and key:
            return self.app.npc_speaker_label(safe_int(key, 0)) \
                or ("NPC %s" % key)
        if kind == "TRADER" and key:
            return "Trader %s" % key
        return (self.file_name.get() or "NPC").replace(".json", "")

    def browse_npcs(self):
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
            self.ai_frame.pack_forget()
            self.key_entry.state(["!disabled"])
            self.pick_npc_button.state(["!disabled"])
        elif kind == "TRADER":
            self.key_label.configure(text="Trader definition name")
            self.key_hint.configure(
                text="The trader's file name, e.g. Weapons. Open the trader "
                     "in game and the client log prints fileName=...")
            self.trader_frame.pack(fill="x", pady=(6, 0))
            self.ai_frame.pack_forget()
            self.key_entry.state(["!disabled"])
            self.pick_npc_button.state(["disabled"])
        elif kind == "AI":
            self.key_label.configure(text="(matched by DialogueID below)")
            self.key_hint.configure(
                text="Talkable AI are spawned via AIPatrol\\AIPatrols.json and "
                     "matched by DialogueID, not a folder ID. Saved to "
                     "Dialogues\\AI\\.")
            self.trader_frame.pack_forget()
            self.ai_frame.pack(fill="x", pady=(6, 0))
            self.key_entry.state(["disabled"])
            self.pick_npc_button.state(["disabled"])
        else:
            self.key_label.configure(text="NPC IDs (comma separated)")
            self.key_hint.configure(
                text="Shared trees MUST list every NPC ID explicitly, "
                     "e.g. 12, 13, 14")
            self.trader_frame.pack_forget()
            self.ai_frame.pack_forget()
            self.key_entry.state(["!disabled"])
            self.pick_npc_button.state(["!disabled"])

        self.refresh_action_values()
        is_ai = kind == "AI"
        try:
            if is_ai and self.inner.select() == str(self.quest_talk_page):
                self.inner.select(self.flow_page)
            self.inner.tab(
                self.quest_talk_page,
                state=("disabled" if is_ai else "normal"))
        except Exception:
            pass

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
        elif kind == "AI":
            folder = "AI"
            pid = safe_int(self.ai_patrol_id.get(), 0) if hasattr(
                self, "ai_patrol_id") else 0
            sid = safe_int(self.ai_sub_id.get(), 0) if hasattr(
                self, "ai_sub_id") else 0
            who = "AI patrol %s" % (pid or "?")
            if sid > 0:
                who += " unit %s" % sid
        else:
            folder = "Shared"
            who = "shared (%s)" % (key or "no IDs yet")
        name = self.file_name.get().strip() or "Dialogue.json"
        if not name.lower().endswith(".json"):
            name += ".json"
        self.preview_path = os.path.join(root, "Dialogues", folder, name)
        if getattr(self, "source_path", None):
            self.preview_path = self.source_path
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
        if kind == "AI":
            self.tree["AIPatrolID"] = safe_int(self.ai_patrol_id.get(), 0)
            self.tree["AIPatrolSubID"] = safe_int(self.ai_sub_id.get(), 0)
        else:
            self.tree["AIPatrolID"] = 0
            self.tree["AIPatrolSubID"] = 0
        if hasattr(self, "reputation_var"):
            self.tree["ReputationVar"] = rep_key_from_name(
                self.reputation_var.get())
            self.tree["ReputationTiers"] = self.rep_tiers.get_tiers()
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
        self.ai_patrol_id.delete(0, tk.END)
        self.ai_patrol_id.insert(0, str(safe_int(self.tree.get("AIPatrolID", 0), 0)))
        self.ai_sub_id.delete(0, tk.END)
        self.ai_sub_id.insert(0, str(safe_int(self.tree.get("AIPatrolSubID", 0), 0)))
        self.reputation_var.delete(0, tk.END)
        self.reputation_var.insert(
            0, rep_label_from_key(self.tree.get("ReputationVar", "") or ""))
        self._refresh_rep_hint()
        self.rep_tiers.set_tiers(self.tree.get("ReputationTiers"))
        self.loading = False
        self.on_target_change()
        self.refresh_tree_selector()
        self.refresh_outline()


    def node_index(self, node):
        return self.container()["Nodes"].index(node)

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
        nodes = self.container()["Nodes"]
        root_id = self.container().get("RootNodeID")

        for n_index, node in enumerate(nodes):
            node_id = node.get("ID")
            marker = "\u25b6 " if node_id == root_id else ""
            flag = "" if node.get("Type") == "STANDARD" else \
                "  [%s]" % node.get("Type")
            label = "%sNode %s - %s%s" % (
                marker, node_id, self.short(node.get("SpeakerText")), flag)
            self.outline.insert(
                "", "end", iid="n%d" % n_index, text=label,
                values=("start" if node_id == root_id else "",),
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

        ids = [str(n.get("ID", 0)) for n in nodes]
        self.root_node["values"] = ids
        self.root_node.set(str(root_id if root_id is not None else 1))

        if not nodes:
            self.current_node = None
            self.current_response = None
            self.refresh_map()
            return

        index = 0
        for position, node in enumerate(nodes):
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
        if iid == self._loaded_iid:
            return
        self._loaded_iid = iid
        self.load_from_iid(iid)
        self.refresh_map()

    def _outline_right_click(self, event):
        iid = self.outline.identify_row(event.y)
        if not iid:
            return
        self.outline.selection_set(iid)
        if iid != self._loaded_iid:
            self._loaded_iid = iid
            self.load_from_iid(iid)
            self.refresh_map()

        menu = tk.Menu(self, tearoff=0)
        if iid.startswith("n"):
            n_index = int(iid[1:])
            menu.add_command(label="Edit this node",
                             command=lambda: self._outline_edit(iid))
            menu.add_separator()
            self._add_copy_to_tree_menu(menu, n_index)
            menu.add_separator()
            menu.add_command(label="Delete this node", command=self.delete_node)
        else:
            menu.add_command(label="Edit this option",
                             command=lambda: self._outline_edit(iid))
            menu.add_separator()
            menu.add_command(label="Delete this option",
                             command=self.delete_response)
        _popup_menu(menu, event)

    def _add_copy_to_tree_menu(self, menu, n_index):
        others = [i for i in range(-1, len(self.tree.get("Stages") or []))
                  if i != self.current_stage_index]
        if not others:
            return

        def tree_name(idx):
            return "Tree 1" if idx < 0 else "Tree %d" % (idx + 2)

        node_menu = tk.Menu(menu, tearoff=0)
        branch_menu = tk.Menu(menu, tearoff=0)
        for idx in others:
            node_menu.add_command(
                label=tree_name(idx),
                command=lambda t=idx: self.copy_node_to_tree(n_index, t, False))
            branch_menu.add_command(
                label=tree_name(idx),
                command=lambda t=idx: self.copy_node_to_tree(n_index, t, True))
        menu.add_cascade(label="Copy node to", menu=node_menu)
        menu.add_cascade(label="Copy node + its branch to", menu=branch_menu)

    def copy_node_to_tree(self, n_index, target_index, with_branch):
        src_nodes = self.container()["Nodes"]
        if not (0 <= n_index < len(src_nodes)):
            return
        target = (self.tree if target_index < 0
                  else self.tree["Stages"][target_index])
        target_nodes = target.setdefault("Nodes", [])

        to_copy = [src_nodes[n_index]]
        if with_branch:
            by_id = {n.get("ID"): n for n in src_nodes}
            seen = {src_nodes[n_index].get("ID")}
            queue = [src_nodes[n_index]]
            while queue:
                node = queue.pop()
                for resp in node.get("Responses", []):
                    if resp.get("ActionType", "NONE") != "NONE":
                        continue
                    nxt = resp.get("NextNodeID", -1)
                    if nxt and nxt > 0 and nxt not in seen and nxt in by_id:
                        seen.add(nxt)
                        child = by_id[nxt]
                        to_copy.append(child)
                        queue.append(child)

        used = {n.get("ID", 0) for n in target_nodes}
        next_id = (max(used) + 1) if used else 1
        id_map = {}
        for node in to_copy:
            id_map[node.get("ID")] = next_id
            next_id += 1

        for node in to_copy:
            clone = copy.deepcopy(node)
            clone["ID"] = id_map[node.get("ID")]
            for resp in clone.get("Responses", []):
                if resp.get("ActionType", "NONE") == "NONE":
                    old = resp.get("NextNodeID", -1)
                    if old in id_map:
                        resp["NextNodeID"] = id_map[old]
            target_nodes.append(clone)

        self.mark_dirty()
        messagebox.showinfo(
            APP_TITLE, "Copied %d node(s) into %s." % (
                len(to_copy),
                "Tree 1" if target_index < 0 else "Tree %d" % (target_index + 2)),
            parent=self)

    def _outline_edit(self, iid):
        if iid.startswith("n"):
            self.speaker_text.focus_set()
        else:
            self.response_text.focus_set()
            self.response_text.icursor(tk.END)


    def select_node(self, index):
        self.current_node = self.container()["Nodes"][index]
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
        self.container()["RootNodeID"] =safe_int(self.root_node.get(), 1)
        self.refresh_outline()
        self.refresh_map()
        self.mark_dirty()

    def next_free_node_id(self):
        used = {n.get("ID", 0) for n in self.container()["Nodes"]}
        candidate = 1
        while candidate in used:
            candidate += 1
        return candidate

    def add_node(self):
        node = new_node(self.next_free_node_id())
        self.container()["Nodes"].append(node)
        self.current_response = None
        self.refresh_outline(keep_node=node["ID"], keep_response=None)
        self.refresh_map()
        self.mark_dirty()

    def duplicate_node(self):
        if not self.current_node:
            return
        clone = copy.deepcopy(self.current_node)
        clone["ID"] = self.next_free_node_id()
        self.container()["Nodes"].append(clone)
        self.current_response = None
        self.refresh_outline(keep_node=clone["ID"], keep_response=None)
        self.refresh_map()
        self.mark_dirty()

    def delete_node(self):
        if not self.current_node:
            return
        if len(self.container()["Nodes"]) == 1:
            messagebox.showinfo(
                APP_TITLE, "A tree needs at least one node.", parent=self)
            return
        node_id = self.current_node.get("ID")
        incoming = sum(
            1 for n in self.container()["Nodes"] for r in n.get("Responses", [])
            if r.get("ActionType", "NONE") == "NONE"
            and r.get("NextNodeID") == node_id)
        message = "Delete node %s?" % node_id
        if incoming:
            message += ("\n\n%d option(s) point at it. They'll be left "
                        "pointing at a node that no longer exists, and "
                        "'Check for problems' will flag them." % incoming)
        if not messagebox.askyesno(APP_TITLE, message, parent=self):
            return
        self.container()["Nodes"].remove(self.current_node)
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
        clash = [n for n in self.container()["Nodes"]
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
        for node in self.container()["Nodes"]:
            for response in node.get("Responses", []):
                if response.get("NextNodeID") == old_id:
                    response["NextNodeID"] = new_id
        if self.container().get("RootNodeID") == old_id:
            self.container()["RootNodeID"] =new_id
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


    def refresh_action_values(self):
        if self.target_kind.get() == "AI":
            self.action_type["values"] = [
                "NONE", "END_CONVERSATION", "RECRUIT_AI", "GO_HOSTILE"]
            return
        values = [a for a in ACTION_TYPES
                  if a not in ("RECRUIT_AI", "GO_HOSTILE")]
        if self.show_advanced.get():
            values += ADVANCED_ACTION_TYPES
        self.action_type["values"] = values

    def clear_response_editor(self):
        self.loading = True
        self.response_text.delete(0, tk.END)
        self.action_type.set("")
        self.next_node.set("")
        self.gate_quest.set(NOT_LOCKED_LABEL)
        self.hide_quest.set(NEVER_HIDDEN_LABEL)
        self.action_quest.set(NO_ACTION_QUEST_LABEL)
        self.gate_note.configure(text="")
        self.hide_note.configure(text="")
        self.action_quest_note.configure(text="")
        self.action_hint.configure(
            text="Pick an option in the outline, or add one.")
        self.next_node.configure(state="disabled")
        self.gate_quest.configure(state="disabled")
        self.hide_quest.configure(state="disabled")
        self.action_quest.configure(state="disabled")
        if hasattr(self, "require_vars"):
            self.set_vars.set_ops([])
            self.require_vars.set_ops([])
        if hasattr(self, "max_uses"):
            self.max_uses.delete(0, tk.END)
            self.max_uses.insert(0, "0")
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
            [str(n.get("ID")) for n in self.container()["Nodes"]]
        self.next_node["values"] = options
        target = response.get("NextNodeID", -1)
        self.next_node.set(str(target) if target and target > 0
                           else "(end conversation)")

        gate = response.get("RequiredQuestID", -1)
        self.refresh_quest_choices()
        self.set_gate_value(gate)

        hide = safe_int(response.get("HideAfterQuestID", -1), -1)
        self.hide_quest.set(self.app.quest_label(hide) if hide > 0
                            else NEVER_HIDDEN_LABEL)
        action_quest = safe_int(response.get("QuestID", -1), -1)
        self.action_quest.set(self.app.quest_label(action_quest)
                              if action_quest > 0 else NO_ACTION_QUEST_LABEL)
        self.update_action_state()
        if hasattr(self, "require_vars"):
            self.set_vars.set_ops(response.get("SetVars"))
            self.require_vars.set_ops(response.get("RequiredVars"))
        if hasattr(self, "max_uses"):
            self.max_uses.delete(0, tk.END)
            self.max_uses.insert(0, str(safe_int(response.get("MaxUses", 0), 0)))
        self.loading = False
        self.update_action_state()

    def refresh_quest_choices(self):
        labels = self.app.quest_labels()
        self.gate_quest["values"] = [NOT_LOCKED_LABEL] + labels
        self.hide_quest["values"] = [NEVER_HIDDEN_LABEL] + labels
        self.action_quest["values"] = [NO_ACTION_QUEST_LABEL] + labels
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

        self.update_extra_quest_notes()

    def _pick_quest(self, title, hint):
        if not self.app.ensure_quest_folder():
            return None
        if not self.app.quest_index:
            messagebox.showinfo(
                APP_TITLE,
                "No quest configs found in that folder. Point it at the "
                "folder holding your Expansion quest .json files.",
                parent=self)
            return None
        dialog = ChooserDialog(self.app, title, self.app.quest_index, hint)
        self.wait_window(dialog)
        return dialog.chosen

    def browse_hide_quest(self):
        chosen = self._pick_quest(
            "Pick a quest",
            "The option DISAPPEARS once the player has completed the quest "
            "you pick. Use it to retire a line that no longer makes sense.")
        if chosen is None:
            return
        self.hide_quest.set(self.app.quest_label(chosen) if chosen > 0
                            else NEVER_HIDDEN_LABEL)
        self.update_gate_note()
        self.commit_response()

    def browse_action_quest(self):
        chosen = self._pick_quest(
            "Pick a quest",
            "The quest this option offers or hands over when clicked.")
        if chosen is None:
            return
        self.action_quest.set(self.app.quest_label(chosen) if chosen > 0
                              else NO_ACTION_QUEST_LABEL)
        self.update_gate_note()
        self.commit_response()

    def update_extra_quest_notes(self):
        hide_text = self.hide_quest.get().strip()
        if not hide_text or hide_text == NEVER_HIDDEN_LABEL:
            self.hide_note.configure(text="")
        else:
            self.hide_note.configure(
                text="Disappears once the player has completed “%s”."
                     % hide_text)

        action = self.action_type.get()
        quest_text = self.action_quest.get().strip()
        blank = not quest_text or quest_text == NO_ACTION_QUEST_LABEL

        if action == "OFFER_QUEST":
            if blank:
                self.action_quest_note.configure(
                    text="Pick a quest - without one this option does "
                         "nothing but close the window.")
            else:
                self.action_quest_note.configure(
                    text="Opens the offer screen for “%s”, where the "
                         "player can read it and accept or decline."
                         % quest_text)
        elif action == "ACCEPT_QUEST":
            if blank:
                self.action_quest_note.configure(
                    text="No quest picked, so this only works inside the "
                         "live quest-detail step the mod builds itself.")
            else:
                self.action_quest_note.configure(
                    text="Hands “%s” straight over, with no offer "
                         "screen." % quest_text)
        else:
            self.action_quest_note.configure(text="")

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
        self.hide_quest.configure(state="normal")

        uses_quest = action in ("OFFER_QUEST", "ACCEPT_QUEST")
        self.action_quest.configure(state="normal" if uses_quest else "disabled")
        if not uses_quest:
            self.action_quest.set(NO_ACTION_QUEST_LABEL)

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
        hide_text = self.hide_quest.get().strip()
        if not hide_text or hide_text == NEVER_HIDDEN_LABEL:
            response["HideAfterQuestID"] = -1
        else:
            response["HideAfterQuestID"] = max(
                1, quest_id_from_label(hide_text, 1))
        action_quest_text = self.action_quest.get().strip()
        if not action_quest_text                 or action_quest_text == NO_ACTION_QUEST_LABEL:
            response["QuestID"] = -1
        else:
            response["QuestID"] = max(
                1, quest_id_from_label(action_quest_text, 1))
        if hasattr(self, "require_vars"):
            response["SetVars"] = self.set_vars.get_ops()
            response["RequiredVars"] = self.require_vars.get_ops()
        if hasattr(self, "max_uses"):
            uses = safe_int(self.max_uses.get(), 0)
            response["MaxUses"] = uses
            if uses > 0 and not response.get("UsesKey"):
                response["UsesKey"] = "uses_" + uuid.uuid4().hex[:8]
        self.refresh_outline(reload_editors=False)
        self.refresh_map()
        self.mark_dirty()

    def add_response(self):
        if not self.current_node:
            messagebox.showinfo(
                APP_TITLE, "Select a node first.", parent=self)
            return
        response = new_response()
        typed = self.response_text.get().strip()
        if typed and self.current_response is None:
            response["Text"] = typed
        self.current_node.setdefault("Responses", []).append(response)
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
        if not self.current_response:
            return
        if self.current_response.get("ActionType", "NONE") != "NONE":
            return
        target = self.current_response.get("NextNodeID", -1)
        if not target or target < 1:
            return
        for index, node in enumerate(self.container()["Nodes"]):
            if node.get("ID") == target:
                self.current_response = None
                self.refresh_outline(keep_node=target, keep_response=None)
                self.refresh_map()
                return
        messagebox.showinfo(
            APP_TITLE, "Node %d doesn't exist yet." % target, parent=self)


    def layout_map(self):
        nodes_by_id = {n.get("ID"): n for n in self.container()["Nodes"]}
        root = self.container().get("RootNodeID")

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
        for node in self.container()["Nodes"]:
            if node.get("ID") not in depth:
                depth[node.get("ID")] = orphan_column

        columns = {}
        placed = {}
        for node in self.container()["Nodes"]:
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
        nodes_by_id = {n.get("ID"): n for n in self.container()["Nodes"]}
        current_id = self.current_node.get("ID") if self.current_node else None
        root_id = self.container().get("RootNodeID")

        def box_at(node_id):
            column, row = placed[node_id]
            x = self.MARGIN + column * (self.BOX_W + self.GAP_X)
            y = self.MARGIN + row * (self.BOX_H + self.GAP_Y)
            return x, y, x + self.BOX_W, y + self.BOX_H

        highlight_target = None
        if self.current_response is not None \
                and self.current_response.get("ActionType", "NONE") == "NONE":
            highlight_target = self.current_response.get("NextNodeID", -1)

        for node in self.container()["Nodes"]:
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

        for node in self.container()["Nodes"]:
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
        if safe_int(self.tree.get("AIPatrolID", 0), 0) > 0:
            out["AIPatrolID"] = safe_int(self.tree.get("AIPatrolID", 0), 0)
            out["AIPatrolSubID"] = safe_int(self.tree.get("AIPatrolSubID", 0), 0)
        if (self.tree.get("ReputationVar") or "").strip():
            out["ReputationVar"] = self.tree.get("ReputationVar", "").strip()
            out["ReputationTiers"] = [
                {"Threshold": safe_int(t.get("Threshold", 0), 0),
                 "Label": str(t.get("Label", ""))}
                for t in (self.tree.get("ReputationTiers") or [])
                if str(t.get("Label", "")).strip()
            ]
        out["GreetingVoiceLineIDs"] = list(
            self.tree.get("GreetingVoiceLineIDs", []))
        out["FarewellVoiceLineIDs"] = list(
            self.tree.get("FarewellVoiceLineIDs", []))
        if kind != "AI":
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
        out["Stages"] = [
            {
                "RequiredQuestID": safe_int(s.get("RequiredQuestID", -1), -1),
                "RootNodeID": safe_int(s.get("RootNodeID", 1), 1),
                "Priority": safe_int(s.get("Priority", 0), 0),
                "RequiredVars": clean_var_ops(s.get("RequiredVars")),
                "Nodes": self._serialize_nodes(s.get("Nodes") or []),
            }
            for s in self.tree.get("Stages", [])
        ]
        out["Nodes"] = self._serialize_nodes(self.tree["Nodes"])
        return out

    def _serialize_nodes(self, nodes):
        out_nodes = []
        for node in nodes:
            entry = {
                "ID": safe_int(node.get("ID", 1), 1),
                "Type": node.get("Type", "STANDARD") or "STANDARD",
                "SpeakerText": node.get("SpeakerText", ""),
                "VoiceLineIDs": list(node.get("VoiceLineIDs", [])),
                "Responses": [],
            }
            speaker_lines = []
            for line in (node.get("SpeakerLines") or []):
                gate = line.get("RequiredQuestID", -1)
                override = line.get("OverrideQuestID", -1)
                line_entry = {
                    "Text": line.get("Text", ""),
                    "RequiredQuestID": gate if gate and gate > 0 else -1,
                    "OverrideQuestID": override if override and override > 0
                    else -1,
                    "VoiceLineIDs": list(line.get("VoiceLineIDs") or []),
                }
                req = clean_var_ops(line.get("RequiredVars"))
                if req:
                    line_entry["RequiredVars"] = req
                speaker_lines.append(line_entry)
            if speaker_lines:
                entry["SpeakerLines"] = speaker_lines
            for response in node.get("Responses", []):
                action = response.get("ActionType", "NONE") or "NONE"
                gate = response.get("RequiredQuestID", -1)
                resp_entry = {
                    "Text": response.get("Text", ""),
                    "NextNodeID": safe_int(response.get("NextNodeID", -1), -1)
                    if action == "NONE" else -1,
                    "RequiredQuestID": gate if gate and gate > 0 else -1,
                    "ActionType": action,
                }
                req_vars = clean_var_ops(response.get("RequiredVars"))
                if req_vars:
                    resp_entry["RequiredVars"] = req_vars
                set_vars = clean_var_ops(response.get("SetVars"))
                if set_vars:
                    resp_entry["SetVars"] = set_vars
                hide_after = safe_int(response.get("HideAfterQuestID", -1), -1)
                if hide_after > 0:
                    resp_entry["HideAfterQuestID"] = hide_after
                action_quest = safe_int(response.get("QuestID", -1), -1)
                if action_quest > 0:
                    resp_entry["QuestID"] = action_quest
                max_uses = safe_int(response.get("MaxUses", 0), 0)
                if max_uses > 0:
                    resp_entry["MaxUses"] = max_uses
                    resp_entry["UsesKey"] = (response.get("UsesKey", "")
                                             or "uses_" + uuid.uuid4().hex[:8])
                entry["Responses"].append(resp_entry)
            out_nodes.append(entry)
        return out_nodes

    def _load_nodes(self, raw):
        return [
            {
                "ID": safe_int(n.get("ID", 1), 1),
                "Type": n.get("Type", "STANDARD") or "STANDARD",
                "SpeakerText": n.get("SpeakerText", ""),
                "VoiceLineIDs": list(n.get("VoiceLineIDs") or []),
                "Responses": [self._load_response(r)
                              for r in (n.get("Responses") or [])],
                "SpeakerLines": [
                    {
                        "Text": line.get("Text", ""),
                        "RequiredQuestID": safe_int(
                            line.get("RequiredQuestID", -1), -1),
                        "OverrideQuestID": safe_int(
                            line.get("OverrideQuestID", -1), -1),
                        "VoiceLineIDs": list(line.get("VoiceLineIDs") or []),
                        "RequiredVars": clean_var_ops(line.get("RequiredVars")),
                    }
                    for line in (n.get("SpeakerLines") or [])
                ],
            }
            for n in (raw or [])
        ]

    def _load_response(self, r):
        entry = dict(r)
        entry["RequiredVars"] = clean_var_ops(r.get("RequiredVars"))
        entry["SetVars"] = clean_var_ops(r.get("SetVars"))
        return entry

    def load_tree(self, data, path=None):
        self.tree = new_tree()
        self.tree.update(
            {k: v for k, v in data.items() if k not in ("Nodes", "Stages")})
        self.tree["Nodes"] = self._load_nodes(data.get("Nodes")) or [new_node(1)]
        self.tree["Stages"] = [
            {
                "RequiredQuestID": safe_int(s.get("RequiredQuestID", -1), -1),
                "RootNodeID": safe_int(s.get("RootNodeID", 1), 1),
                "Priority": safe_int(s.get("Priority", 0), 0),
                "RequiredVars": clean_var_ops(s.get("RequiredVars")),
                "Nodes": self._load_nodes(s.get("Nodes")) or [new_node(1)],
            }
            for s in (data.get("Stages") or [])
        ]
        self.current_stage_index = -1
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
        if safe_int(data.get("AIPatrolID", 0), 0) > 0:
            self.target_kind.set("AI")
        self.refresh_all()
        self.refresh_map()


    def validate(self):
        self.pull_tree_header()
        return validate_tree_dict(
            self.build_output(), self.target_kind.get(),
            self.folder_key.get(), self.app.quest_index)


# ---------------------------------------------------------------- quest text

class QuestTextTab(ttk.Frame):

    BACK_HINT = ("One button per line, each returns to the conversation. "
                 "Blank shows no back button on this screen.")

    SCREEN_GROUPS = [
        ("Quest offer screen  —  not started yet", [
            ("AcceptTexts", "Accept  (Player says)",
             "One button per line."),
            ("DeclineTexts", "Turn it down  (Player says)",
             "One button per line."),
            ("OfferBackTexts", "Back to the conversation  (Player says)",
             BACK_HINT),
        ]),
        ("Quest in-progress screen  —  accepted, not finished", [
            ("InProgressTexts", "While it's running  (Player says)",
             "One button per line."),
            ("InProgressBackTexts", "Back to the conversation  (Player says)",
             BACK_HINT),
        ]),
        ("Quest turn-in screen  —  ready to hand in", [
            ("TurnInTexts", "Hand it in  (Player says)",
             "One button per line."),
            ("NotYetTexts", "Not finished yet  (Player says)",
             "One button per line."),
            ("TurnInBackTexts", "Back to the conversation  (Player says)",
             BACK_HINT),
        ]),
    ]

    COMPLETED_GROUPS = [
        ("Quest list screen  —  once this quest is completed", [
            ("QuestListTexts", "Line above their quest list  (NPC says)",
             "One line picked at random."),
            ("QuestListBackTexts", "Back to the conversation  (Player says)",
             BACK_HINT),
        ]),
        ("No-quests screen  —  once this quest is completed", [
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

        self.quest_npc = ttk.Label(right, text="", style="Accent.TLabel")
        self.quest_npc.pack(anchor="w", pady=(0, 4))

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

        for i, (title, specs) in enumerate(self.SCREEN_GROUPS):
            self._build_screen_box(right, title, specs, expanded=(i == 0))

        reward_section = CollapsibleSection(
            right, "Reward choice screen  (NPC says, optional)", expanded=False)
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
                "Quest offer screen", speaker,
                self.current_desc()
                or "(the quest's own description shows here)",
                rows("AcceptTexts") + rows("DeclineTexts")
                + rows("OfferBackTexts"),
                "Accept first, then decline, then any back buttons.")

        if screen == "progress":
            return PreviewScene(
                "Quest in-progress screen", speaker,
                "(the quest's own progress text shows here)",
                rows("InProgressTexts") + rows("InProgressBackTexts"))

        if screen == "turnin":
            turnin_speaker = speaker
            turnins = entry.get("turnins") if entry else None
            if turnins:
                turnin_speaker = self.app.npc_speaker_label(turnins[0]) \
                    or speaker
            turnin_line = (entry.get("desc_turnin") if entry else "") \
                or "(the quest's own turn-in text shows here)"
            return PreviewScene(
                "Quest turn-in screen", turnin_speaker, turnin_line,
                rows("TurnInTexts") + rows("NotYetTexts")
                + rows("TurnInBackTexts"),
                "Hand-in first, then not-yet, then any back buttons.")

        if screen == "reward":
            reward = self.reward_text.get()
            return PreviewScene(
                "Reward choice screen", speaker, reward,
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
                "Quest list screen", speaker, first,
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
            "No-quests screen", speaker, first,
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
        #! Never write a version older than the file came in as - a newer mod
        #! may have bumped it past what this build knows about.
        self.config_version = 0

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

        language_row = ttk.Frame(fonts)
        language_row.pack(fill="x", padx=6, pady=(2, 0))
        self.show_language = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            language_row, text="Let players pick their language",
            variable=self.show_language,
            command=self.on_change).pack(side="left")

        self.scale_text = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            language_row, text="Option text scales with panel size",
            variable=self.scale_text,
            command=self.on_change).pack(side="left", padx=(14, 0))

        notify_row = ttk.Frame(fonts)
        notify_row.pack(fill="x", padx=6, pady=(2, 0))
        self.error_notifications = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            notify_row,
            text="Tell players on screen when an option is misconfigured",
            variable=self.error_notifications,
            command=self.on_change).pack(side="left")

        ttk.Label(fonts,
                  text="A short pop-up so a player isn't left staring at a "
                       "window that closed for no reason. The full reason "
                       "always goes to your log either way.",
                  wraplength=420, style="Hint.TLabel").pack(
            anchor="w", padx=6, pady=(0, 4))

        ttk.Label(fonts,
                  text="The language option only ever appears if you have "
                       "translations in Localization\\ - a single-language "
                       "server never sees it either way.",
                  wraplength=420, style="Hint.TLabel").pack(
            anchor="w", padx=6, pady=(0, 2))

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
        cfg["ShowLanguageButton"] = bool(self.show_language.get())
        cfg["ScaleTextWithPanel"] = bool(self.scale_text.get())
        cfg["ShowErrorNotifications"] = bool(self.error_notifications.get())
        cfg["LayoutOverride"] = self.layout_override.get().strip()
        return cfg

    def build_output(self):
        cfg = self.gather()
        ordered = {
            "ConfigVersion": max(self.config_version, 6),
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
        ordered["ShowLanguageButton"] = cfg["ShowLanguageButton"]
        ordered["ScaleTextWithPanel"] = cfg["ScaleTextWithPanel"]
        ordered["ShowErrorNotifications"] = cfg["ShowErrorNotifications"]
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
        self.show_language.set(bool(data.get("ShowLanguageButton", True)))
        self.scale_text.set(bool(data.get("ScaleTextWithPanel", False)))
        self.error_notifications.set(
            bool(data.get("ShowErrorNotifications", True)))
        self.config_version = safe_int(data.get("ConfigVersion", 0), 0)
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
    action = response.get("ActionType") or "NONE"
    if action == "OPEN_TRADER":
        return "cart"
    if action == "END_CONVERSATION":
        return "exit"
    if action == "NONE" and safe_int(response.get("NextNodeID", -1), -1) == -1:
        return "exit"
    return "chat"


def draw_hint_icon(canvas, cx, cy, size, kind, colour):
    if not kind:
        return
    half = size / 2.0
    w = max(1, int(round(size / 7.0)))

    if kind == "exit":
        left = cx - half
        right = cx - half * 0.15
        canvas.create_line(right, cy - half, left, cy - half,
                           fill=colour, width=w)
        canvas.create_line(left, cy - half, left, cy + half,
                           fill=colour, width=w)
        canvas.create_line(left, cy + half, right, cy + half,
                           fill=colour, width=w)
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

    canvas.create_rectangle(cx - half, cy - half * 0.85,
                            cx + half, cy + half * 0.25,
                            outline=colour, width=w)
    canvas.create_polygon(cx - half * 0.55, cy + half * 0.2,
                          cx - half * 0.55, cy + half * 0.95,
                          cx - half * 0.05, cy + half * 0.2,
                          fill=colour, outline=colour)


# ------------------------------------------------------------ live preview

class AISettingsTab(ttk.Frame):

    def __init__(self, master, app):
        ttk.Frame.__init__(self, master)
        self.app = app
        self.loading = False

        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(
            wrap,
            text="What a talkable AI does after a GO_HOSTILE dialogue choice "
                 "turns them on the player. Saved to AISettings.json. Only "
                 "affects AI angered through dialogue.",
            wraplength=560, style="Hint.TLabel").pack(anchor="w", pady=(0, 8))

        box = ttk.LabelFrame(wrap, text="Let them calm down when the player…",
                             style="Section.TLabelframe")
        box.pack(fill="x")
        self.reset_death = tk.BooleanVar(value=True)
        self.reset_weapon = tk.BooleanVar(value=True)
        self.reset_surrender = tk.BooleanVar(value=True)
        self.reset_leave = tk.BooleanVar(value=True)
        for var, label in [
                (self.reset_death, "dies"),
                (self.reset_weapon, "puts their weapon away"),
                (self.reset_surrender, "puts their hands up (surrender)"),
                (self.reset_leave, "leaves the area")]:
            ttk.Checkbutton(box, text=label, variable=var,
                            command=self._dirty).pack(anchor="w", padx=8, pady=1)

        row = ttk.Frame(wrap)
        row.pack(fill="x", pady=(8, 0))
        ttk.Label(row, text="Leave-area distance (m)").pack(side="left")
        self.leave_distance = ttk.Spinbox(row, from_=0, to=2000, increment=5,
                                          width=8, command=self._dirty)
        self.leave_distance.pack(side="left", padx=6)
        ttk.Label(row, text="     Check every (seconds)").pack(side="left")
        self.check_interval = ttk.Spinbox(row, from_=0.5, to=30, increment=0.5,
                                          width=8, command=self._dirty)
        self.check_interval.pack(side="left", padx=6)

        perm = ttk.LabelFrame(
            wrap, text="Permanent hostility (stops repeat offenders)",
            style="Section.TLabelframe")
        perm.pack(fill="x", pady=(10, 0))
        ttk.Label(
            perm,
            text="After angering them this many times, that player is hostile "
                 "for good and won't be forgiven. 0 = never permanent.",
            wraplength=540, style="Hint.TLabel").pack(anchor="w", padx=8,
                                                      pady=(4, 2))
        prow = ttk.Frame(perm)
        prow.pack(fill="x", padx=8, pady=(0, 6))
        ttk.Label(prow, text="Threshold").pack(side="left")
        self.threshold = ttk.Spinbox(prow, from_=0, to=100, width=6,
                                     command=self._dirty)
        self.threshold.pack(side="left", padx=(4, 12))
        ttk.Label(prow, text="Remembered by").pack(side="left")
        self.mode = ttk.Combobox(prow, values=["FACTION", "PATROL", "BOTH"],
                                 width=10, state="readonly")
        self.mode.pack(side="left", padx=4)
        self.mode.bind("<<ComboboxSelected>>", lambda _e: self._dirty())

        ttk.Button(wrap, text="Save global AI settings",
                   command=lambda: self.app.save_current()).pack(
            anchor="w", pady=(12, 0))

        self.load(default_ai_settings())

    def _dirty(self, *_args):
        if self.loading:
            return
        self.app.mark_editor_dirty("Global AI settings")

    def load(self, data):
        self.loading = True
        d = default_ai_settings()
        self.reset_death.set(bool(data.get("ResetOnDeath", d["ResetOnDeath"])))
        self.reset_weapon.set(
            bool(data.get("ResetOnWeaponStowed", d["ResetOnWeaponStowed"])))
        self.reset_surrender.set(
            bool(data.get("ResetOnSurrender", d["ResetOnSurrender"])))
        self.reset_leave.set(
            bool(data.get("ResetOnLeaveArea", d["ResetOnLeaveArea"])))
        self.leave_distance.delete(0, tk.END)
        self.leave_distance.insert(0, str(safe_float(
            data.get("LeaveAreaDistance", d["LeaveAreaDistance"]),
            d["LeaveAreaDistance"])))
        self.check_interval.delete(0, tk.END)
        self.check_interval.insert(0, str(safe_float(
            data.get("CheckInterval", d["CheckInterval"]), d["CheckInterval"])))
        self.threshold.delete(0, tk.END)
        self.threshold.insert(0, str(safe_int(
            data.get("PersistentAggroThreshold", 0), 0)))
        mode = str(data.get("PersistenceMode", "FACTION") or "FACTION").upper()
        if mode not in ("FACTION", "PATROL", "BOTH"):
            mode = "FACTION"
        self.mode.set(mode)
        self.loading = False

    def build_output(self):
        return {
            "ResetOnDeath": 1 if self.reset_death.get() else 0,
            "ResetOnWeaponStowed": 1 if self.reset_weapon.get() else 0,
            "ResetOnLeaveArea": 1 if self.reset_leave.get() else 0,
            "LeaveAreaDistance": safe_float(self.leave_distance.get(), 60.0),
            "ResetOnSurrender": 1 if self.reset_surrender.get() else 0,
            "PersistentAggroThreshold": safe_int(self.threshold.get(), 0),
            "PersistenceMode": self.mode.get() or "FACTION",
            "CheckInterval": safe_float(self.check_interval.get(), 2.0),
        }

    def output_path(self):
        return os.path.join(self.app.profile_path.get() or "",
                            "AISettings.json")

    def validate(self):
        return [], []


PATROL_FACTIONS = ("Raiders", "Mercenaries", "West", "East", "Guards",
                   "Civilian", "Passive")
PATROL_FORMATIONS = ("RANDOM", "Column", "File", "Vee", "Wall", "Circle",
                     "CircleDot", "InvColumn", "InvFile", "InvVee", "Star",
                     "StarDot")
PATROL_BEHAVIOURS = ("HALT", "LOOP", "ALTERNATE", "ONCE", "HALT_OR_LOOP",
                     "HALT_OR_ALTERNATE", "LOOP_OR_ALTERNATE", "ROAMING",
                     "ROAMING_LOCAL", "MIXED")
PATROL_SPEEDS = ("STATIC", "WALK", "JOG", "SPRINT", "RANDOM",
                 "RANDOM_NONSTATIC")
PATROL_STANCES = ("STANDING", "CROUCHED", "PRONE")


def default_patrol():
    return {
        "DialogueID": 0,
        "PersistentAggroThreshold": -1,
        "PersistenceMode": "",
        "Name": "New talkable patrol",
        "Persist": 0,
        "Faction": "Guards",
        "Formation": "Vee",
        "FormationScale": 1.5,
        "FormationLooseness": 0.1,
        "Loadout": "",
        "Units": [],
        "NumberOfAI": 1,
        "NumberOfAIMax": 0,
        "Behaviour": "LOOP",
        "LootingBehaviour": "",
        "Speed": "WALK",
        "UnderThreatSpeed": "SPRINT",
        "DefaultStance": "STANDING",
        "DefaultLookAngle": 0.0,
        "CanBeLooted": 1,
        "LootDropOnDeath": "",
        "UnlimitedReload": 0,
        "SniperProneDistanceThreshold": 0.0,
        "AccuracyMin": -1.0,
        "AccuracyMax": -1.0,
        "ThreatDistanceLimit": -1.0,
        "NoiseInvestigationDistanceLimit": -1.0,
        "MaxFlankingDistance": -1.0,
        "EnableFlankingOutsideCombat": -1,
        "DamageMultiplier": -1.0,
        "DamageReceivedMultiplier": -1.0,
        "HeadshotResistance": 0.0,
        "ShoryukenChance": 0.0,
        "ShoryukenDamageMultiplier": 0.0,
        "CanSpawnInContaminatedArea": 0,
        "CanBeTriggeredByAI": 0,
        "MinDistRadius": -1.0,
        "MaxDistRadius": -1.0,
        "DespawnRadius": -1.0,
        "MinSpreadRadius": 0.0,
        "MaxSpreadRadius": 0.0,
        "Chance": 1.0,
        "DespawnTime": -1.0,
        "RespawnTime": -2.0,
        "LoadBalancingCategory": "",
        "ObjectClassName": "",
        "WaypointInterpolation": "",
        "UseRandomWaypointAsStartPoint": 1,
        "Waypoints": [],
    }


class AIPatrolsTab(ttk.Frame):

    PERM_CHOICES = ("Use server default", "Never permanent", "After a set number")
    MODE_CHOICES = ("Use server default", "FACTION", "PATROL", "BOTH")

    def __init__(self, master, app):
        ttk.Frame.__init__(self, master)
        self.app = app
        self.loading = False
        self.patrols = []
        self.selected = -1
        self.fields = {}
        self._inputs = []

        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(
            wrap,
            text="Build talkable AI patrols (AIPatrol\\AIPatrols.json). This is "
                 "a full patrol generator - the normal Expansion patrol fields "
                 "plus the two links this mod adds (the dialogue tree it uses "
                 "and how permanently it holds a grudge). Dropdowns are filled "
                 "from Expansion's own script values.",
            wraplength=620, style="Hint.TLabel").pack(anchor="w", pady=(0, 8))

        body = ttk.Frame(wrap)
        body.pack(fill="both", expand=True)

        left = ttk.LabelFrame(body, text="Patrols", style="Section.TLabelframe")
        left.pack(side="left", fill="y", padx=(0, 10))
        self.listbox = tk.Listbox(left, width=32, height=18,
                                  exportselection=False, activestyle="none")
        self.listbox.pack(fill="y", expand=True, padx=6, pady=6)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        row = ttk.Frame(left)
        row.pack(fill="x", padx=6, pady=(0, 6))
        ttk.Button(row, text="New patrol", width=11,
                   command=self._new_patrol).pack(side="left")
        ttk.Button(row, text="Duplicate", width=10,
                   command=self._duplicate).pack(side="left", padx=4)
        row2 = ttk.Frame(left)
        row2.pack(fill="x", padx=6, pady=(0, 6))
        ttk.Button(row2, text="Remove", width=11,
                   command=self._remove).pack(side="left")

        scroll = ScrollFrame(body)
        scroll.pack(side="left", fill="both", expand=True)
        self.detail = scroll.inner

        # ---- Identity & dialogue link
        sec = self._section("Identity & dialogue link")
        self._field(sec, "Name", "Name", "text", hint="just a label for you")
        self._field(sec, "DialogueID", "Dialogue ID", "int",
                    hint="match a dialogue tree's \"AIPatrolID\"")

        # ---- Spawning
        sec = self._section("Spawning")
        self._field(sec, "Faction", "Faction", "combo", PATROL_FACTIONS,
                    "or any faction your server defines")
        self._field(sec, "Loadout", "Loadout", "text",
                    "loadout json name; blank = faction default")
        self._units_entry = self._simple(sec, "Units (classnames)",
                                         "comma-separated; blank = faction default")
        self._field(sec, "NumberOfAI", "Number of AI", "int")
        self._field(sec, "NumberOfAIMax", "Number of AI (max)", "int",
                    hint="0 = exactly the number above; >0 = random range")
        self._field(sec, "Chance", "Spawn chance", "float", hint="0.0 - 1.0")
        self._field(sec, "Persist", "Persist across restarts", "bool",
                    hint="leave off for talkable patrols")
        self._field(sec, "RespawnTime", "Respawn time (s)", "float",
                    hint="-2 = Expansion default, -1 = never")
        self._field(sec, "DespawnTime", "Despawn time (s)", "float",
                    hint="-1 = never")
        self._field(sec, "CanBeLooted", "Can be looted", "bool")
        self._field(sec, "LootDropOnDeath", "Loot drop on death", "text")
        self._field(sec, "CanSpawnInContaminatedArea",
                    "Spawn in contaminated area", "bool")
        self._field(sec, "CanBeTriggeredByAI", "Can be triggered by AI", "bool")

        # ---- Movement & formation
        sec = self._section("Movement & formation")
        self._field(sec, "Behaviour", "Behaviour", "enum", PATROL_BEHAVIOURS)
        self._field(sec, "Speed", "Speed", "enum", PATROL_SPEEDS)
        self._field(sec, "UnderThreatSpeed", "Under-threat speed", "enum",
                    PATROL_SPEEDS)
        self._field(sec, "Formation", "Formation", "enum", PATROL_FORMATIONS)
        self._field(sec, "FormationScale", "Formation scale", "float")
        self._field(sec, "FormationLooseness", "Formation looseness", "float")
        self._field(sec, "DefaultStance", "Default stance", "enum",
                    PATROL_STANCES)
        self._field(sec, "DefaultLookAngle", "Default look angle", "float")
        self._field(sec, "UnlimitedReload", "Unlimited reload", "bool")
        self._field(sec, "LootingBehaviour", "Looting behaviour", "text")

        # ---- Spawn area & waypoints
        sec = self._section("Spawn area")
        self._field(sec, "MinDistRadius", "Min distance radius", "float",
                    hint="-1 = Expansion default")
        self._field(sec, "MaxDistRadius", "Max distance radius", "float")
        self._field(sec, "DespawnRadius", "Despawn radius", "float")
        self._field(sec, "MinSpreadRadius", "Min spread radius", "float")
        self._field(sec, "MaxSpreadRadius", "Max spread radius", "float")
        self._field(sec, "UseRandomWaypointAsStartPoint",
                    "Random start waypoint", "bool")
        self._field(sec, "WaypointInterpolation", "Waypoint interpolation",
                    "text")
        self._build_waypoints(self._section("Waypoints"))

        # ---- Permanent hostility (this mod)
        sec = self._section("Permanent hostility for this patrol")
        ttk.Label(sec,
                  text="Overrides the Global AI settings tab for this patrol "
                       "only.", wraplength=460, style="Hint.TLabel").pack(
            anchor="w", padx=8, pady=(0, 4))
        prow = ttk.Frame(sec)
        prow.pack(fill="x", padx=8)
        self.perm = ttk.Combobox(prow, values=self.PERM_CHOICES, width=20,
                                 state="readonly")
        self.perm.pack(side="left")
        self.perm.bind("<<ComboboxSelected>>", self._on_perm_change)
        self.perm_count = ttk.Spinbox(prow, from_=1, to=100, width=5,
                                      command=self._commit)
        self.perm_count.pack(side="left", padx=(8, 2))
        self.perm_count.bind("<KeyRelease>", self._commit)
        ttk.Label(prow, text="bad runs").pack(side="left")
        self._inputs.append((self.perm, "readonly"))

        mrow = ttk.Frame(sec)
        mrow.pack(fill="x", padx=8, pady=(6, 6))
        ttk.Label(mrow, text="Remembered by", width=24, anchor="w").pack(
            side="left")
        self.mode = ttk.Combobox(mrow, values=self.MODE_CHOICES, width=18,
                                 state="readonly")
        self.mode.pack(side="left")
        self.mode.bind("<<ComboboxSelected>>", self._commit)
        self._inputs.append((self.mode, "readonly"))

        ttk.Button(wrap, text="Save AI patrols",
                   command=lambda: self.app.save_current()).pack(
            anchor="w", pady=(10, 0))

        self.load({"Patrols": []})

    # ---- construction helpers

    def _section(self, title):
        frame = ttk.LabelFrame(self.detail, text=title,
                               style="Section.TLabelframe")
        frame.pack(fill="x", expand=True, padx=6, pady=(0, 8))
        return frame

    def _field(self, parent, key, label, kind, values=None, hint=None):
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=8, pady=1)
        ttk.Label(row, text=label, width=24, anchor="w").pack(side="left")
        if kind == "bool":
            var = tk.BooleanVar()
            widget = ttk.Checkbutton(row, variable=var, command=self._commit)
            widget.pack(side="left")
            self.fields[key] = ("bool", var)
            self._inputs.append((widget, "normal"))
        elif kind in ("enum", "combo"):
            state = "readonly" if kind == "enum" else "normal"
            widget = ttk.Combobox(row, values=values, width=18, state=state)
            widget.pack(side="left")
            widget.bind("<<ComboboxSelected>>", self._commit)
            if kind == "combo":
                widget.bind("<KeyRelease>", self._commit)
            self.fields[key] = (kind, widget)
            self._inputs.append((widget, state))
        else:
            widget = ttk.Entry(row, width=16)
            widget.pack(side="left")
            widget.bind("<KeyRelease>", self._commit)
            self.fields[key] = (kind, widget)
            self._inputs.append((widget, "normal"))
        if hint:
            ttk.Label(row, text=hint, style="Hint.TLabel").pack(
                side="left", padx=8)
        return widget

    def _simple(self, parent, label, hint=None):
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=8, pady=1)
        ttk.Label(row, text=label, width=24, anchor="w").pack(side="left")
        widget = ttk.Entry(row, width=28)
        widget.pack(side="left")
        widget.bind("<KeyRelease>", self._commit)
        self._inputs.append((widget, "normal"))
        if hint:
            ttk.Label(row, text=hint, style="Hint.TLabel").pack(
                side="left", padx=8)
        return widget

    def _build_waypoints(self, parent):
        ttk.Label(parent,
                  text="Where the patrol lives. At least ONE waypoint is "
                       "required - with none, the patrol does not spawn at all. "
                       "One waypoint = spawns there and holds position. Extra "
                       "waypoints = a route it walks. The first is the spawn "
                       "point.",
                  wraplength=460, style="Hint.TLabel").pack(
            anchor="w", padx=8, pady=(0, 4))
        mid = ttk.Frame(parent)
        mid.pack(fill="x", padx=8)
        self.wp_list = tk.Listbox(mid, height=6, exportselection=False,
                                  activestyle="none")
        self.wp_list.pack(side="left", fill="x", expand=True)
        self.wp_list.bind("<<ListboxSelect>>", self._wp_on_select)
        self._inputs.append((self.wp_list, "normal"))

        entry = ttk.Frame(parent)
        entry.pack(fill="x", padx=8, pady=(4, 2))
        self.wp_x = ttk.Entry(entry, width=10)
        self.wp_y = ttk.Entry(entry, width=10)
        self.wp_z = ttk.Entry(entry, width=10)
        for label, widget in (("X", self.wp_x), ("Y", self.wp_y),
                              ("Z", self.wp_z)):
            ttk.Label(entry, text=label).pack(side="left")
            widget.pack(side="left", padx=(2, 8))
            self._inputs.append((widget, "normal"))

        buttons = ttk.Frame(parent)
        buttons.pack(fill="x", padx=8, pady=(0, 6))
        for text, cmd in (("Add", self._wp_add),
                          ("Update selected", self._wp_update),
                          ("Remove", self._wp_remove),
                          ("Paste coords...", self._wp_paste)):
            button = ttk.Button(buttons, text=text, command=cmd)
            button.pack(side="left", padx=(0, 4))
            self._inputs.append((button, "normal"))

    # ---- state

    def _dirty(self):
        if self.loading:
            return
        self.app.mark_editor_dirty("AI patrols")

    @staticmethod
    def _label_for(index, patrol):
        name = str(patrol.get("Name", "") or "").strip()
        if not name:
            name = "(patrol %d)" % (index + 1)
        return "%s  [ID %s]" % (name, patrol.get("DialogueID", 0))

    def _set_detail_state(self, on):
        for widget, enabled in self._inputs:
            widget.configure(state=(enabled if on else "disabled"))

    def _sync_perm_count_state(self):
        on = self.selected >= 0 and self.perm.get() == "After a set number"
        self.perm_count.configure(state=("normal" if on else "disabled"))

    def _set_entry(self, widget, text):
        widget.delete(0, tk.END)
        widget.insert(0, text)

    def _refresh_list(self, keep):
        self.listbox.delete(0, tk.END)
        for i, patrol in enumerate(self.patrols):
            self.listbox.insert(tk.END, self._label_for(i, patrol))
        if 0 <= keep < len(self.patrols):
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(keep)
            self.selected = keep
        else:
            self.selected = -1

    def _clear_detail(self):
        self.loading = True
        self._set_detail_state(True)
        self._apply_to_widgets(default_patrol())
        self._set_detail_state(False)
        self.loading = False

    # ---- events

    def _on_select(self, _event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        self.selected = sel[0]
        self._populate(self.patrols[self.selected])

    def _on_perm_change(self, _event=None):
        self._sync_perm_count_state()
        self._commit()

    def _apply_to_widgets(self, patrol):
        faction_kind, faction_widget = self.fields.get("Faction", (None, None))
        if faction_widget is not None:
            values = list(PATROL_FACTIONS)
            for name in self.app.custom_faction_names():
                if name and name not in values:
                    values.append(name)
            faction_widget.configure(values=values)

        for key, (kind, holder) in self.fields.items():
            if kind == "bool":
                holder.set(bool(safe_int(patrol.get(key, 0), 0)))
            elif kind in ("enum", "combo"):
                holder.set(str(patrol.get(key, "") or ""))
            elif kind == "int":
                self._set_entry(holder, str(safe_int(patrol.get(key, 0), 0)))
            elif kind == "float":
                self._set_entry(holder,
                                str(safe_float(patrol.get(key, 0.0), 0.0)))
            else:
                self._set_entry(holder, str(patrol.get(key, "") or ""))

        units = patrol.get("Units") or []
        self._set_entry(self._units_entry,
                        ", ".join(str(u) for u in units))

        threshold = safe_int(patrol.get("PersistentAggroThreshold", -1), -1)
        self._set_entry(self.perm_count, "2")
        if threshold < 0:
            self.perm.set("Use server default")
        elif threshold == 0:
            self.perm.set("Never permanent")
        else:
            self.perm.set("After a set number")
            self._set_entry(self.perm_count, str(threshold))

        mode = str(patrol.get("PersistenceMode", "") or "").upper()
        self.mode.set(mode if mode in ("FACTION", "PATROL", "BOTH")
                      else "Use server default")

        self._wp_refresh(patrol.get("Waypoints"))
        self._set_entry(self.wp_x, "")
        self._set_entry(self.wp_y, "")
        self._set_entry(self.wp_z, "")

    def _populate(self, patrol):
        self.loading = True
        self._set_detail_state(True)
        self._apply_to_widgets(patrol)
        self._sync_perm_count_state()
        self.loading = False

    def _commit(self, *_args):
        if self.loading or self.selected < 0:
            return
        patrol = self.patrols[self.selected]
        for key, (kind, holder) in self.fields.items():
            if kind == "bool":
                patrol[key] = 1 if holder.get() else 0
            elif kind in ("enum", "combo"):
                patrol[key] = holder.get()
            elif kind == "int":
                patrol[key] = safe_int(holder.get(), 0)
            elif kind == "float":
                patrol[key] = safe_float(holder.get(), 0.0)
            else:
                patrol[key] = holder.get()

        units = [u.strip() for u in self._units_entry.get().split(",")
                 if u.strip()]
        patrol["Units"] = units

        choice = self.perm.get()
        if choice == "Never permanent":
            patrol["PersistentAggroThreshold"] = 0
        elif choice == "After a set number":
            patrol["PersistentAggroThreshold"] = max(
                1, safe_int(self.perm_count.get(), 1))
        else:
            patrol["PersistentAggroThreshold"] = -1

        mode = self.mode.get()
        patrol["PersistenceMode"] = mode if mode in ("FACTION", "PATROL",
                                                     "BOTH") else ""

        self.listbox.delete(self.selected)
        self.listbox.insert(self.selected,
                            self._label_for(self.selected, patrol))
        self.listbox.selection_set(self.selected)
        self._dirty()

    # ---- waypoints

    def _current_waypoints(self):
        if self.selected < 0:
            return None
        patrol = self.patrols[self.selected]
        if not isinstance(patrol.get("Waypoints"), list):
            patrol["Waypoints"] = []
        return patrol["Waypoints"]

    def _wp_refresh(self, waypoints):
        self.wp_list.delete(0, tk.END)
        for point in (waypoints or []):
            try:
                self.wp_list.insert(
                    tk.END, "%s,  %s,  %s" % (point[0], point[1], point[2]))
            except Exception:
                self.wp_list.insert(tk.END, str(point))

    def _wp_on_select(self, _event=None):
        waypoints = self._current_waypoints()
        sel = self.wp_list.curselection()
        if waypoints is None or not sel or sel[0] >= len(waypoints):
            return
        point = waypoints[sel[0]]
        self._set_entry(self.wp_x, str(point[0]))
        self._set_entry(self.wp_y, str(point[1]))
        self._set_entry(self.wp_z, str(point[2]))

    def _wp_read_entries(self):
        return [safe_float(self.wp_x.get(), 0.0),
                safe_float(self.wp_y.get(), 0.0),
                safe_float(self.wp_z.get(), 0.0)]

    def _wp_add(self):
        waypoints = self._current_waypoints()
        if waypoints is None:
            return
        waypoints.append(self._wp_read_entries())
        self._wp_refresh(waypoints)
        self._dirty()

    def _wp_update(self):
        waypoints = self._current_waypoints()
        sel = self.wp_list.curselection()
        if waypoints is None or not sel or sel[0] >= len(waypoints):
            return
        index = sel[0]
        waypoints[index] = self._wp_read_entries()
        self._wp_refresh(waypoints)
        self.wp_list.selection_set(index)
        self._dirty()

    def _wp_remove(self):
        waypoints = self._current_waypoints()
        sel = self.wp_list.curselection()
        if waypoints is None or not sel or sel[0] >= len(waypoints):
            return
        del waypoints[sel[0]]
        self._wp_refresh(waypoints)
        self._dirty()

    def _wp_paste(self):
        waypoints = self._current_waypoints()
        if waypoints is None:
            messagebox.showinfo(APP_TITLE, "Select or make a patrol first.")
            return
        window = tk.Toplevel(self)
        window.title("Paste waypoint coordinates")
        window.geometry("420x360")
        ttk.Label(window,
                  text="One waypoint per line - any format with three numbers "
                       "works, e.g. 6424.15 18.33 2299.4 or "
                       "[6424.15, 18.33, 2299.4].",
                  wraplength=390, style="Hint.TLabel").pack(
            anchor="w", padx=10, pady=8)
        text = tk.Text(window, wrap="word", height=12)
        text.pack(fill="both", expand=True, padx=10)

        def do_add():
            added = 0
            for line in text.get("1.0", tk.END).splitlines():
                nums = re.findall(r"-?\d+\.?\d*", line)
                if len(nums) >= 3:
                    waypoints.append([float(nums[0]), float(nums[1]),
                                      float(nums[2])])
                    added += 1
            self._wp_refresh(waypoints)
            if added:
                self._dirty()
            window.destroy()
            self.set_status_safe("Added %d waypoint(s)." % added)

        bar = ttk.Frame(window)
        bar.pack(fill="x", padx=10, pady=8)
        ttk.Button(bar, text="Add these", command=do_add).pack(side="left")
        ttk.Button(bar, text="Cancel",
                   command=window.destroy).pack(side="left", padx=6)
        self.app.skin_window(window)

    def set_status_safe(self, text):
        try:
            self.app.set_status(text)
        except Exception:
            pass

    # ---- list actions

    def _new_patrol(self):
        patrol = default_patrol()
        self.patrols.append(patrol)
        self._refresh_list(keep=len(self.patrols) - 1)
        self._populate(patrol)
        self._dirty()

    def _duplicate(self):
        if self.selected < 0:
            return
        clone = copy.deepcopy(self.patrols[self.selected])
        name = str(clone.get("Name", "") or "")
        clone["Name"] = (name + " (copy)") if name else "(copy)"
        self.patrols.insert(self.selected + 1, clone)
        self._refresh_list(keep=self.selected + 1)
        self._populate(clone)
        self._dirty()

    def _remove(self):
        if self.selected < 0:
            return
        if not messagebox.askyesno(
                APP_TITLE, "Remove this patrol from the file?"):
            return
        del self.patrols[self.selected]
        keep = min(self.selected, len(self.patrols) - 1)
        self._refresh_list(keep=keep)
        if keep >= 0:
            self._populate(self.patrols[keep])
        else:
            self._clear_detail()
        self._dirty()

    # ---- app hooks

    def load(self, data):
        self.loading = True
        patrols = []
        if isinstance(data, dict) and isinstance(data.get("Patrols"), list):
            patrols = [p for p in data["Patrols"] if isinstance(p, dict)]
        self.patrols = patrols
        self._refresh_list(keep=0 if patrols else -1)
        if patrols:
            self._populate(patrols[0])
        else:
            self._clear_detail()
        self.loading = False

    def build_output(self):
        return {"Patrols": self.patrols}

    def output_path(self):
        return os.path.join(self.app.profile_path.get() or "",
                            "AIPatrol", "AIPatrols.json")

    def validate(self):
        issues = []
        warnings = []
        for i, patrol in enumerate(self.patrols):
            label = self._label_for(i, patrol)
            if safe_int(patrol.get("DialogueID", 0), 0) <= 0:
                issues.append(
                    "%s has no Dialogue ID - set it to 1 or higher, or the "
                    "patrol has no tree to talk with." % label)
            if not str(patrol.get("Faction", "") or "").strip():
                warnings.append("%s has no Faction set." % label)
            if safe_int(patrol.get("NumberOfAI", 0), 0) < 1:
                warnings.append("%s spawns 0 AI (Number of AI is under 1)."
                                % label)
            waypoints = patrol.get("Waypoints")
            if not isinstance(waypoints, list) or len(waypoints) == 0:
                issues.append(
                    "%s has no waypoints - it will NOT spawn. Add at least one "
                    "(the first is the spawn point)." % label)
        return issues, warnings


FACTION_MAX_SLOTS = 32
FACTION_STANCES = ("Friendly", "Guard", "Hostile")


def default_faction():
    return {
        "Name": "New Faction",
        "Loadout": "",
        "PlayerStance": "FRIENDLY",
        "FriendlyFactions": [],
    }


class FactionsTab(ttk.Frame):

    def __init__(self, master, app):
        ttk.Frame.__init__(self, master)
        self.app = app
        self.loading = False
        self.factions = []
        self.selected = -1

        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(
            wrap,
            text="Make your own AI factions (Factions\\Factions.json) and give "
                 "them to talkable patrols on the AI patrols tab. Each gets a "
                 "name, a loadout, how it treats players, and which other "
                 "factions it won't fight. Up to %d factions." % FACTION_MAX_SLOTS,
            wraplength=620, style="Hint.TLabel").pack(anchor="w", pady=(0, 8))

        body = ttk.Frame(wrap)
        body.pack(fill="both", expand=True)

        left = ttk.LabelFrame(body, text="Factions",
                              style="Section.TLabelframe")
        left.pack(side="left", fill="y", padx=(0, 10))
        self.listbox = tk.Listbox(left, width=28, height=18,
                                  exportselection=False, activestyle="none")
        self.listbox.pack(fill="y", expand=True, padx=6, pady=6)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        row = ttk.Frame(left)
        row.pack(fill="x", padx=6, pady=(0, 6))
        ttk.Button(row, text="New", width=8,
                   command=self._new).pack(side="left")
        ttk.Button(row, text="Duplicate", width=10,
                   command=self._duplicate).pack(side="left", padx=4)
        ttk.Button(row, text="Remove", width=8,
                   command=self._remove).pack(side="left")

        detail = ttk.LabelFrame(body, text="Selected faction",
                                style="Section.TLabelframe")
        detail.pack(side="left", fill="both", expand=True)

        namerow = ttk.Frame(detail)
        namerow.pack(fill="x", padx=8, pady=(8, 2))
        ttk.Label(namerow, text="Name", width=14, anchor="w").pack(side="left")
        self.name = ttk.Entry(namerow, width=26)
        self.name.pack(side="left")
        self.name.bind("<KeyRelease>", self._commit)

        loadrow = ttk.Frame(detail)
        loadrow.pack(fill="x", padx=8, pady=2)
        ttk.Label(loadrow, text="Loadout", width=14, anchor="w").pack(
            side="left")
        self.loadout = ttk.Entry(loadrow, width=26)
        self.loadout.pack(side="left")
        self.loadout.bind("<KeyRelease>", self._commit)
        ttk.Label(loadrow, text="blank = default human loadout",
                  style="Hint.TLabel").pack(side="left", padx=8)

        stancerow = ttk.Frame(detail)
        stancerow.pack(fill="x", padx=8, pady=2)
        ttk.Label(stancerow, text="Toward players", width=14,
                  anchor="w").pack(side="left")
        self.stance = ttk.Combobox(stancerow, values=FACTION_STANCES, width=12,
                                   state="readonly")
        self.stance.pack(side="left")
        self.stance.bind("<<ComboboxSelected>>", self._commit)
        self.stance_hint = ttk.Label(detail, text="", wraplength=440,
                                     style="Hint.TLabel")
        self.stance_hint.pack(anchor="w", padx=8, pady=(0, 4))

        fbox = ttk.LabelFrame(detail, text="Won't fight these factions",
                              style="Section.TLabelframe")
        fbox.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        ttk.Label(fbox,
                  text="Tick allies. For two custom factions to truly ignore "
                       "each other, tick it on BOTH. Built-in Expansion "
                       "factions only befriend you back if their own rules "
                       "allow it (guards/passive).",
                  wraplength=440, style="Hint.TLabel").pack(anchor="w", padx=6,
                                                            pady=(2, 4))
        self.friendly_holder = ttk.Frame(fbox)
        self.friendly_holder.pack(fill="both", expand=True, padx=6)
        self.friendly_vars = {}

        ttk.Button(wrap, text="Save factions",
                   command=lambda: self.app.save_current()).pack(
            anchor="w", pady=(4, 0))

        self._inputs = [self.name, self.loadout, self.stance]
        self.load({"Factions": []})

    # ---- helpers

    def _dirty(self):
        if self.loading:
            return
        self.app.mark_editor_dirty("Factions")

    def _stance_display(self, stored):
        stored = str(stored or "FRIENDLY").upper()
        if stored == "GUARD":
            return "Guard"
        if stored == "HOSTILE":
            return "Hostile"
        return "Friendly"

    def _stance_store(self, display):
        return str(display or "Friendly").upper()

    def _set_stance_hint(self):
        text = {
            "Friendly": "Players can walk up and talk; never attacks unless a "
                        "dialogue choice turns them hostile.",
            "Guard": "Tolerates players until one raises a weapon at them, then "
                     "defends.",
            "Hostile": "Attacks players on sight.",
        }
        self.stance_hint.configure(text=text.get(self.stance.get(), ""))

    def _names(self):
        return [str(f.get("Name", "") or "") for f in self.factions]

    def _set_entry(self, widget, text):
        widget.delete(0, tk.END)
        widget.insert(0, text)

    def _set_detail_state(self, on):
        state = "normal" if on else "disabled"
        self.name.configure(state=state)
        self.loadout.configure(state=state)
        self.stance.configure(state=("readonly" if on else "disabled"))

    def _refresh_list(self, keep):
        self.listbox.delete(0, tk.END)
        for i, faction in enumerate(self.factions):
            name = str(faction.get("Name", "") or "").strip() or "(faction %d)" \
                % (i + 1)
            self.listbox.insert(tk.END, name)
        if 0 <= keep < len(self.factions):
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(keep)
            self.selected = keep
        else:
            self.selected = -1

    def _build_friendly_checks(self, faction):
        for child in self.friendly_holder.winfo_children():
            child.destroy()
        self.friendly_vars = {}
        chosen = [str(x) for x in (faction.get("FriendlyFactions") or [])]
        available = list(PATROL_FACTIONS)
        for other in self._names():
            if other and other != faction.get("Name") and other not in available:
                available.append(other)
        for name in chosen:
            if name not in available:
                available.append(name)
        columns = 2
        for index, name in enumerate(available):
            var = tk.BooleanVar(value=(name in chosen))
            chk = ttk.Checkbutton(self.friendly_holder, text=name, variable=var,
                                  command=self._commit)
            chk.grid(row=index // columns, column=index % columns, sticky="w",
                     padx=4, pady=1)
            self.friendly_vars[name] = var

    # ---- events

    def _on_select(self, _event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        self.selected = sel[0]
        self._populate(self.factions[self.selected])

    def _populate(self, faction):
        self.loading = True
        self._set_detail_state(True)
        self._set_entry(self.name, str(faction.get("Name", "") or ""))
        self._set_entry(self.loadout, str(faction.get("Loadout", "") or ""))
        self.stance.set(self._stance_display(faction.get("PlayerStance")))
        self._set_stance_hint()
        self._build_friendly_checks(faction)
        self.loading = False

    def _clear_detail(self):
        self.loading = True
        self._set_entry(self.name, "")
        self._set_entry(self.loadout, "")
        self.stance.set("Friendly")
        self.stance_hint.configure(text="")
        for child in self.friendly_holder.winfo_children():
            child.destroy()
        self.friendly_vars = {}
        self._set_detail_state(False)
        self.loading = False

    def _commit(self, *_args):
        if self.loading or self.selected < 0:
            return
        faction = self.factions[self.selected]
        faction["Name"] = self.name.get().strip()
        faction["Loadout"] = self.loadout.get().strip()
        faction["PlayerStance"] = self._stance_store(self.stance.get())
        faction["FriendlyFactions"] = [name for name, var
                                       in self.friendly_vars.items()
                                       if var.get()]
        self._set_stance_hint()
        name = faction["Name"] or "(faction %d)" % (self.selected + 1)
        self.listbox.delete(self.selected)
        self.listbox.insert(self.selected, name)
        self.listbox.selection_set(self.selected)
        self._dirty()

    def _new(self):
        if len(self.factions) >= FACTION_MAX_SLOTS:
            messagebox.showinfo(
                APP_TITLE,
                "You've hit the %d-faction limit built into the mod."
                % FACTION_MAX_SLOTS)
            return
        faction = default_faction()
        self.factions.append(faction)
        self._refresh_list(keep=len(self.factions) - 1)
        self._populate(faction)
        self._dirty()

    def _duplicate(self):
        if self.selected < 0:
            return
        if len(self.factions) >= FACTION_MAX_SLOTS:
            messagebox.showinfo(
                APP_TITLE,
                "You've hit the %d-faction limit built into the mod."
                % FACTION_MAX_SLOTS)
            return
        clone = copy.deepcopy(self.factions[self.selected])
        name = str(clone.get("Name", "") or "")
        clone["Name"] = (name + " (copy)") if name else "(copy)"
        self.factions.insert(self.selected + 1, clone)
        self._refresh_list(keep=self.selected + 1)
        self._populate(clone)
        self._dirty()

    def _remove(self):
        if self.selected < 0:
            return
        if not messagebox.askyesno(APP_TITLE, "Remove this faction?"):
            return
        del self.factions[self.selected]
        keep = min(self.selected, len(self.factions) - 1)
        self._refresh_list(keep=keep)
        if keep >= 0:
            self._populate(self.factions[keep])
        else:
            self._clear_detail()
        self._dirty()

    # ---- app hooks

    def load(self, data):
        self.loading = True
        factions = []
        if isinstance(data, dict) and isinstance(data.get("Factions"), list):
            factions = [f for f in data["Factions"] if isinstance(f, dict)]
        self.factions = factions
        self._refresh_list(keep=0 if factions else -1)
        if factions:
            self._populate(factions[0])
        else:
            self._clear_detail()
        self.loading = False

    def build_output(self):
        return {"Factions": self.factions}

    def output_path(self):
        return os.path.join(self.app.profile_path.get() or "",
                            "Factions", "Factions.json")

    def names(self):
        return [n for n in self._names() if n]

    def validate(self):
        issues = []
        warnings = []
        seen = {}
        for i, faction in enumerate(self.factions):
            name = str(faction.get("Name", "") or "").strip()
            if not name:
                issues.append("Faction %d has no name." % (i + 1))
                continue
            key = name.lower()
            if key in seen:
                issues.append("Two factions are both named '%s' - names must be "
                              "unique." % name)
            seen[key] = True
        if len(self.factions) > FACTION_MAX_SLOTS:
            issues.append("%d factions defined; only the first %d will load."
                          % (len(self.factions), FACTION_MAX_SLOTS))
        return issues, warnings


class TranslationsTab(ttk.Frame):

    SOURCE_TREE = "TREE"
    SOURCE_QUEST = "QUEST"

    def __init__(self, master, app):
        ttk.Frame.__init__(self, master)
        self.app = app

        #! Each entry is a dict: scope ("tree"/"quest"), quest_id, key,
        #! text (the original) and where (what the translator is looking at).
        self.entries = []
        #! language code -> {cache key: translation}. Kept in memory so
        #! flicking between languages never loses a half-finished pass.
        self.by_language = {}
        self.current_index = None
        self.source_path = None

        self.source_kind = tk.StringVar(value=self.SOURCE_TREE)
        self.language_label = tk.StringVar(value=LANGUAGE_LABELS["german"])
        self.only_missing = tk.BooleanVar(value=False)
        self.progress = tk.StringVar(value="")
        self.source_note = tk.StringVar(value="")

        head = ttk.Frame(self)
        head.pack(fill="x", padx=8, pady=(8, 2))

        ttk.Label(head, text="Translate into").pack(side="left")
        self.language_box = ttk.Combobox(
            head, textvariable=self.language_label, state="readonly", width=14,
            values=[label for _code, label in TRANSLATION_LANGUAGES])
        self.language_box.pack(side="left", padx=6)
        self.language_box.bind("<<ComboboxSelected>>",
                               lambda _e: self.on_language_change())

        ttk.Button(head, text="Load what's on disk",
                   command=self.load_existing).pack(side="left", padx=(4, 0))
        ttk.Button(head, text="Pull latest text",
                   command=self.refresh_source).pack(side="left", padx=6)

        ttk.Label(head, textvariable=self.progress,
                  style="Hint.TLabel").pack(side="right")

        source = ttk.Frame(self)
        source.pack(fill="x", padx=8, pady=(0, 2))
        ttk.Radiobutton(source, text="The dialogue tree in the Dialogue tab",
                        variable=self.source_kind, value=self.SOURCE_TREE,
                        command=self.refresh_source).pack(side="left")
        ttk.Radiobutton(source,
                        text="The file in the Quest wording tab",
                        variable=self.source_kind, value=self.SOURCE_QUEST,
                        command=self.refresh_source).pack(side="left", padx=10)
        ttk.Checkbutton(source, text="Only show lines still missing",
                        variable=self.only_missing,
                        command=self.refresh_list).pack(side="left", padx=10)

        ttk.Label(self, textvariable=self.source_note,
                  style="Hint.TLabel").pack(anchor="w", padx=8)

        body = ttk.PanedWindow(self, orient="vertical")
        body.pack(fill="both", expand=True, padx=8, pady=6)

        list_frame = ttk.Frame(body)
        body.add(list_frame, weight=3)

        self.tree_view = ttk.Treeview(
            list_frame, columns=("where", "original", "translation"),
            show="headings", selectmode="browse")
        self.tree_view.heading("where", text="Where it shows")
        self.tree_view.heading("original", text="Original")
        self.tree_view.heading("translation", text="Translation")
        self.tree_view.column("where", width=250, stretch=False)
        self.tree_view.column("original", width=340)
        self.tree_view.column("translation", width=340)
        self.tree_view.pack(side="left", fill="both", expand=True)
        self.tree_view.bind("<<TreeviewSelect>>", self.on_row_select)

        bar = ttk.Scrollbar(list_frame, orient="vertical",
                            command=self.tree_view.yview)
        bar.pack(side="right", fill="y")
        self.tree_view.configure(yscrollcommand=bar.set)

        detail = ttk.Frame(body)
        body.add(detail, weight=2)
        detail.columnconfigure(0, weight=1)
        detail.columnconfigure(1, weight=1)
        detail.rowconfigure(1, weight=1)

        ttk.Label(detail, text="Original").grid(row=0, column=0, sticky="w")
        self.original_box = tk.Text(detail, height=5, wrap="word")
        self.original_box.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        self.original_box.configure(state="disabled")

        ttk.Label(detail, text="Translation").grid(row=0, column=1, sticky="w")
        self.translation_box = tk.Text(detail, height=5, wrap="word",
                                       undo=True)
        self.translation_box.grid(row=1, column=1, sticky="nsew")

        buttons = ttk.Frame(detail)
        buttons.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Button(buttons, text="Apply", command=self.apply_current).pack(
            side="left")
        ttk.Button(buttons, text="Copy the original across",
                   command=self.copy_original).pack(side="left", padx=6)
        ttk.Button(buttons, text="Next one missing",
                   command=self.jump_to_missing).pack(side="left")
        ttk.Button(buttons, text="Export interface template...",
                   command=self.app.export_ui_template).pack(side="left",
                                                             padx=(20, 0))

        ttk.Label(self,
                  text="Your tree files never change - translations are saved "
                       "next to them in Localization\\<language>\\. Anything "
                       "you leave blank falls back to the original wording in "
                       "game, so a half-finished language is safe to ship.",
                  wraplength=1100, style="Hint.TLabel").pack(
            anchor="w", padx=8, pady=(0, 8))

        self.refresh_source()

    # ---------------- state

    def language_code(self):
        label = self.language_label.get()
        for code, text in TRANSLATION_LANGUAGES:
            if text == label:
                return code
        return "german"

    def store(self):
        return self.by_language.setdefault(self.language_code(), {})

    @staticmethod
    def cache_key(entry):
        if entry["scope"] == "quest":
            return "q%d|%s" % (entry["quest_id"], entry["key"])
        return "t|%s" % entry["key"]

    def dirty(self):
        self.app.mark_editor_dirty("Translations")

    # ---------------- source

    def refresh_source(self):
        self.entries = []

        if self.source_kind.get() == self.SOURCE_QUEST:
            self._pull_quests()
        else:
            self._pull_tree()

        self.current_index = None
        self.refresh_list()

    def _pull_tree(self):
        tab = self.app.dialogue_tab
        data = tab.build_output()

        for key, text, where in loc_tree_entries(data):
            self.entries.append({"scope": "tree", "quest_id": 0,
                                 "key": key, "text": text, "where": where})

        self.source_path = tab.source_path
        relative = loc_relative_tree_path(self.app.profile_path.get(),
                                          tab.output_path())
        if relative:
            self.source_note.set(
                "From the dialogue tree %s (tree ID %s)."
                % (relative, data.get("ID", "?")))
        else:
            self.source_note.set(
                "From the dialogue tree open in the Dialogue tab (tree ID %s). "
                "Pick your profile folder so the file can be matched by name "
                "as well as by ID." % data.get("ID", "?"))

    def _pull_quests(self):
        tab = self.app.quest_tab
        data = tab.build_output()

        for quest in data.get("Quests") or []:
            quest_id = safe_int(quest.get("QuestID", 0), 0)
            if quest_id <= 0:
                continue
            label = self.app.quest_label(quest_id) or ("Quest %d" % quest_id)
            for key, text, where in loc_quest_entries(quest):
                self.entries.append(
                    {"scope": "quest", "quest_id": quest_id, "key": key,
                     "text": text, "where": "%s  -  %s" % (label, where)})

        self.source_path = None
        self.source_note.set(
            "From the quest wording file open in the Quest wording tab (%d "
            "quest(s))." % len(data.get("Quests") or []))

    # ---------------- list

    def visible_entries(self):
        store = self.store()
        if not self.only_missing.get():
            return list(enumerate(self.entries))
        return [(index, entry) for index, entry in enumerate(self.entries)
                if not (store.get(self.cache_key(entry)) or "").strip()]

    def refresh_list(self):
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)

        store = self.store()
        for index, entry in self.visible_entries():
            translation = store.get(self.cache_key(entry), "")
            self.tree_view.insert(
                "", "end", iid=str(index),
                values=(entry["where"], short_one_line(entry["text"]),
                        short_one_line(translation)))

        done = 0
        for entry in self.entries:
            if (store.get(self.cache_key(entry)) or "").strip():
                done += 1
        total = len(self.entries)
        if total:
            self.progress.set("%d of %d translated" % (done, total))
        else:
            self.progress.set("nothing to translate yet")

        self._show_entry(None)

    def on_row_select(self, _event=None):
        selection = self.tree_view.selection()
        if not selection:
            return
        self.apply_current(refresh=False)
        self._show_entry(int(selection[0]))

    def _show_entry(self, index):
        self.current_index = index

        self.original_box.configure(state="normal")
        self.original_box.delete("1.0", tk.END)
        self.translation_box.delete("1.0", tk.END)

        if index is None or index >= len(self.entries):
            self.original_box.configure(state="disabled")
            self.translation_box.configure(state="disabled")
            return

        entry = self.entries[index]
        self.original_box.insert("1.0", entry["text"])
        self.original_box.configure(state="disabled")
        self.translation_box.configure(state="normal")
        self.translation_box.insert(
            "1.0", self.store().get(self.cache_key(entry), ""))

    def apply_current(self, refresh=True):
        if self.current_index is None:
            return
        if self.current_index >= len(self.entries):
            return

        entry = self.entries[self.current_index]
        text = self.translation_box.get("1.0", tk.END).strip()
        key = self.cache_key(entry)

        previous = self.store().get(key, "")
        if text == previous:
            return

        if text:
            self.store()[key] = text
        else:
            self.store().pop(key, None)

        self.dirty()

        if refresh:
            keep = self.current_index
            self.refresh_list()
            if str(keep) in self.tree_view.get_children():
                self.tree_view.selection_set(str(keep))
                self._show_entry(keep)
        else:
            values = self.tree_view.item(str(self.current_index), "values")
            if values:
                self.tree_view.item(
                    str(self.current_index),
                    values=(values[0], values[1], short_one_line(text)))

    def copy_original(self):
        if self.current_index is None:
            return
        self.translation_box.delete("1.0", tk.END)
        self.translation_box.insert(
            "1.0", self.entries[self.current_index]["text"])
        self.apply_current()

    def jump_to_missing(self):
        self.apply_current(refresh=False)
        store = self.store()
        start = 0
        if self.current_index is not None:
            start = self.current_index + 1
        order = list(range(start, len(self.entries))) + list(range(0, start))
        for index in order:
            entry = self.entries[index]
            if (store.get(self.cache_key(entry)) or "").strip():
                continue
            if str(index) not in self.tree_view.get_children():
                self.only_missing.set(False)
                self.refresh_list()
            self.tree_view.selection_set(str(index))
            self.tree_view.see(str(index))
            self._show_entry(index)
            return
        messagebox.showinfo(APP_TITLE, tr("Every line has a translation."))

    def on_language_change(self):
        self.apply_current(refresh=False)
        self.current_index = None
        self.refresh_list()

    # ---------------- disk

    @staticmethod
    def safe_stub(text):
        cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")
        return cleaned or "translation"

    def source_file_stub(self):
        if self.source_kind.get() == self.SOURCE_QUEST:
            name = self.app.quest_tab.file_name.get().strip() \
                or "ServerQuests.json"
            return self.safe_stub("questtext_"
                                  + os.path.splitext(name)[0].lower())

        relative = loc_relative_tree_path(self.app.profile_path.get(),
                                          self.app.dialogue_tab.output_path())
        if relative:
            return self.safe_stub(os.path.splitext(relative)[0].replace(
                "/", "_"))

        tree_id = safe_int(self.app.dialogue_tab.tree.get("ID", 1), 1)
        return "tree_%d" % tree_id

    def output_path(self):
        root = self.app.profile_path.get() or ""
        return os.path.join(root, "Localization", self.language_code(),
                            self.source_file_stub() + ".json")

    def build_output(self):
        self.apply_current(refresh=False)
        store = self.store()

        tree_entries = []
        quest_entries = {}

        for entry in self.entries:
            text = (store.get(self.cache_key(entry)) or "").strip()
            if not text:
                continue
            record = {"Key": entry["key"], "Text": text}
            if entry["scope"] == "quest":
                quest_entries.setdefault(entry["quest_id"], []).append(record)
            else:
                tree_entries.append(record)

        out = {
            "ConfigVersion": LOC_FILE_VERSION,
            "Language": self.language_code(),
            "Trees": [],
            "Quests": [],
        }

        if tree_entries:
            out["Trees"].append({
                "TreeID": safe_int(self.app.dialogue_tab.tree.get("ID", 1), 1),
                "TreeFile": loc_relative_tree_path(
                    self.app.profile_path.get(),
                    self.app.dialogue_tab.output_path()),
                "Entries": tree_entries,
            })

        for quest_id in sorted(quest_entries):
            out["Quests"].append({"QuestID": quest_id,
                                  "Entries": quest_entries[quest_id]})

        return out

    def load(self, data, path=None):
        """Pull an existing Localization file into the language it declares."""
        code = str(data.get("Language", "") or "").lower()
        if code not in LANGUAGE_LABELS and path:
            code = os.path.basename(os.path.dirname(path)).lower()
        if code not in LANGUAGE_LABELS:
            code = self.language_code()

        store = self.by_language.setdefault(code, {})
        count = 0

        for block in data.get("Trees") or []:
            for record in block.get("Entries") or []:
                key = str(record.get("Key", ""))
                text = str(record.get("Text", ""))
                if key and text:
                    store["t|" + key] = text
                    count += 1

        for block in data.get("Quests") or []:
            quest_id = safe_int(block.get("QuestID", 0), 0)
            for record in block.get("Entries") or []:
                key = str(record.get("Key", ""))
                text = str(record.get("Text", ""))
                if key and text:
                    store["q%d|%s" % (quest_id, key)] = text
                    count += 1

        self.language_label.set(LANGUAGE_LABELS[code])
        self.current_index = None
        self.refresh_list()
        return count

    def load_existing(self):
        path = self.output_path()
        if not os.path.isfile(path):
            messagebox.showinfo(
                APP_TITLE,
                tr("Nothing saved for this language yet:\n\n%s") % path)
            return
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception as error:
            messagebox.showerror(
                APP_TITLE, tr("Couldn't read that file:\n\n%s") % error)
            return
        count = self.load(data, path)
        self.app.clear_editor_dirty("Translations")
        self.app.set_status(tr("Loaded %d translated line(s) from %s")
                            % (count, path))

    def validate(self):
        issues = []
        warnings = []

        if not self.entries:
            issues.append(
                "There is nothing to translate - open a dialogue tree or a "
                "quest wording file first, then press 'Pull latest text'.")
            return issues, warnings

        store = self.store()
        missing = 0
        for entry in self.entries:
            if not (store.get(self.cache_key(entry)) or "").strip():
                missing += 1

        if missing:
            warnings.append(
                "%d of %d line(s) have no translation yet. Those show the "
                "original wording in game, which is fine - this is only a "
                "reminder of what is left."
                % (missing, len(self.entries)))

        if self.source_kind.get() == self.SOURCE_TREE:
            if not loc_relative_tree_path(self.app.profile_path.get(),
                                          self.app.dialogue_tab.output_path()):
                warnings.append(
                    "This tree isn't inside your profile's Dialogues folder "
                    "yet, so the translation can only be matched by tree ID. "
                    "Save the tree into the profile first if two trees share "
                    "an ID.")

        return issues, warnings


class PreviewScene:

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

    #! Kept in step with RESPONSE_GROW_LINES / RESPONSE_MIN_FONT_PX in
    #! DialogueWindowMenu.c. The preview's pixel scale isn't the game's, so
    #! the floor is the same fraction of the base rather than the same number.
    GROW_LINES = 3
    MIN_OPTION_SIZE = 6

    def option_lines(self, canvas, text, text_width, size):
        """How many lines this option wraps onto at this size. Measured off a
        one-line sample rather than assumed, so it holds at any font size."""
        probe = canvas.create_text(0, -3000, anchor="nw", text=text,
                                   width=max(30, text_width),
                                   font=("Segoe UI", size))
        box = canvas.bbox(probe)
        canvas.delete(probe)

        sample = canvas.create_text(0, -3000, anchor="nw", text="Ag",
                                    font=("Segoe UI", size))
        sample_box = canvas.bbox(sample)
        canvas.delete(sample)

        if not box or not sample_box:
            return 1

        line_height = max(1, sample_box[3] - sample_box[1])
        return max(1, int(round((box[3] - box[1]) / float(line_height))))

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
        line_box = canvas.bbox(line_id)
        y = (line_box[3] if line_box else y + body_size) + 14

        show_icons = bool(cfg and cfg.get("ShowResponseIcons"))

        #! Mirrors the mod: an option wraps and the button grows, but only so
        #! far - past GROW_LINES the text shrinks instead. Getting this wrong
        #! here is what let a truncated option look fine in the preview.
        option_size = body_size
        if cfg and cfg.get("ScaleTextWithPanel"):
            panel_scale = min(1.8, max(
                0.6, safe_float(cfg.get("PanelWidth", 0.6), 0.6) / 0.6))
            option_size = max(6, int(round(body_size * panel_scale)))

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

            size = option_size
            lines = self.option_lines(canvas, text, text_width, size)
            while lines > self.GROW_LINES and size > self.MIN_OPTION_SIZE:
                size -= 1
                lines = self.option_lines(canvas, text, text_width, size)

            txt_id = canvas.create_text(
                text_x, y + vpad, anchor="nw", text=text, fill=fill_text,
                width=max(30, text_width), font=("Segoe UI", size))
            text_box = canvas.bbox(txt_id)
            text_h = (text_box[3] - text_box[1]) if text_box else size
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
        self.quest_index = []
        self.npc_index = []
        self.theme_name = "dark"
        self.ui_language = "english"
        self.dirty_editors = set()
        self.preview_window = None
        self.ready = False
        self.load_settings()
        load_ui_language(self.ui_language)

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self._build_header()

        self.status = ttk.Label(self, text="Ready", anchor="w",
                                relief="sunken", padding=4)
        self.status.pack(fill="x", side="bottom")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        self.dialogue_tab = DialogueTab(self.notebook, self)
        self.quest_tab = QuestTextTab(self.notebook, self)
        self.menu_tab = MenuConfigTab(self.notebook, self)
        self.ai_settings_tab = AISettingsTab(self.notebook, self)
        self.factions_tab = FactionsTab(self.notebook, self)
        self.ai_patrols_tab = AIPatrolsTab(self.notebook, self)
        self.translations_tab = TranslationsTab(self.notebook, self)
        self.files_tab = ttk.Frame(self.notebook)
        self._build_files_tab(self.files_tab)

        self.notebook.add(self.dialogue_tab, text="  Dialogue  ")
        self.notebook.add(self.quest_tab, text="  Quest wording  ")
        self.notebook.add(self.translations_tab, text="  Translations  ")
        self.notebook.add(self.menu_tab, text="  Menu appearance  ")
        self.notebook.add(self.ai_settings_tab, text="  Global AI settings  ")
        self.notebook.add(self.factions_tab, text="  Factions  ")
        self.notebook.add(self.ai_patrols_tab, text="  AI patrols  ")
        self.notebook.add(self.files_tab, text="  Server files  ")

        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_all(sequence, self.on_mouse_wheel)

        self.bind_all("<Control-KeyPress>", self.on_control_key)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.tab_titles = [self.notebook.tab(index, "text")
                           for index in range(len(self.notebook.tabs()))]

        self.dialogue_tab.update_path_preview()
        self.apply_theme()
        self.apply_language()
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
        title_row = ttk.Frame(words)
        title_row.pack(anchor="w")
        self.wordmark = ttk.Label(title_row, text="DialogueForge",
                                  font=("Segoe UI", 16, "bold"))
        self.wordmark.pack(side="left")
        ttk.Label(title_row, text="v" + APP_VERSION,
                  style="Hint.TLabel").pack(side="left", anchor="s",
                                            padx=(6, 0), pady=(0, 3))
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

        self.ui_language_box = ttk.Combobox(
            top, state="readonly", width=12,
            values=[label for _code, label in TRANSLATION_LANGUAGES])
        self.ui_language_box.set(
            LANGUAGE_LABELS.get(self.ui_language, "English"))
        self.ui_language_box.pack(side="right", padx=6)
        self.ui_language_box.bind("<<ComboboxSelected>>",
                                  lambda _e: self.on_ui_language_change())

        ttk.Button(top, text="Live preview", width=13,
                   command=self.toggle_preview).pack(side="right", padx=6)

        folders = ttk.Frame(top)
        folders.pack(side="left", fill="x", expand=True)
        folders.columnconfigure(1, weight=1)

        ttk.Label(folders,
                  text="Mod folder in /profiles - eg: "
                       "DayZServer/Profiles/DialogFramework").grid(
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

    def on_tab_changed(self, _event=None):
        """Keep the Translations tab in step with whatever is being edited -
        already-typed translations are kept, they are keyed, not positional."""
        if not self.ready:
            return
        try:
            widget = self.nametowidget(self.notebook.select())
        except Exception:
            return
        if widget is self.translations_tab:
            self.translations_tab.refresh_source()

    def on_mouse_wheel(self, event):
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

    def on_control_key(self, event):
        # Ctrl+C/V/X/A by physical key, so copy/paste still work on non-Latin
        # keyboard layouts where the keysym isn't the Latin letter (Tk's default
        # bindings only fire on <Control-c> etc. and never trigger there).
        actions = {67: "<<Copy>>", 86: "<<Paste>>", 88: "<<Cut>>",
                   65: "<<SelectAll>>"}
        virtual = actions.get(event.keycode)
        if not virtual:
            return None
        widget = event.widget
        if not isinstance(widget, (tk.Entry, ttk.Entry, tk.Text,
                                   ttk.Combobox, tk.Spinbox, ttk.Spinbox)):
            return None
        widget.event_generate(virtual)
        return "break"

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
        if not isinstance(npc_id, int) or npc_id <= 0:
            return ""
        name = self.npc_name(npc_id)
        return 'NPC %d "%s"' % (npc_id, name) if name else "NPC %d" % npc_id

    def npc_givers_label(self, quest_id):
        entry = self.quest_lookup(quest_id)
        if not entry:
            return ""
        parts = [self.npc_speaker_label(g) for g in (entry.get("givers") or [])]
        return ", ".join(part for part in parts if part)

    def npc_turnins_label(self, quest_id):
        entry = self.quest_lookup(quest_id)
        if not entry:
            return ""
        parts = [self.npc_speaker_label(t)
                 for t in (entry.get("turnins") or [])]
        return ", ".join(part for part in parts if part)

    def npc_quest_chain(self, npc_id):
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
        style.configure("Section.TLabelframe", background=colors["bg"],
                        bordercolor=colors["border"])
        style.configure("Section.TLabelframe.Label", background=colors["bg"],
                        foreground=colors["accent"],
                        font=("Segoe UI", 10, "bold"))
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
        window.configure(background=self.palette()["bg"])
        self.skin_children(window)
        self.translate_children(window)

    # ---------------- the editor's own language

    def on_ui_language_change(self):
        label = self.ui_language_box.get()
        for code, text in TRANSLATION_LANGUAGES:
            if text == label:
                self.ui_language = code
                break
        load_ui_language(self.ui_language)
        self.apply_language()
        self.save_settings()
        self.set_status(tr("Interface language set to %s") % label)

    def translate_children(self, widget):
        """Swap every static label/button caption for its translation. The
        English original is stashed on first pass so switching language a
        second time still translates from English, not from itself."""
        for child in widget.winfo_children():
            try:
                original = getattr(child, "_source_text", None)
                if original is None and "text" in child.keys():
                    original = child.cget("text")
                    child._source_text = original
                if original:
                    child.configure(text=tr(original))
            except Exception:
                pass
            self.translate_children(child)

    def apply_language(self):
        self.translate_children(self)
        for index, title in enumerate(getattr(self, "tab_titles", [])):
            try:
                self.notebook.tab(index, text=tr(title))
            except Exception:
                pass

    def export_ui_template(self):
        """Write every interface string this session has shown into the
        override file, so a translator can fill it in without a rebuild."""
        path = external_locale_path()

        existing = {}
        try:
            with open(path, "r", encoding="utf-8") as handle:
                existing = json.load(handle)
        except Exception:
            pass

        strings = sorted(_UI_STATE["seen"])
        for code, _label in TRANSLATION_LANGUAGES:
            if code == "english":
                continue
            block = existing.setdefault(code, {})
            for text in strings:
                block.setdefault(text, "")

        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(existing, handle, indent=2, ensure_ascii=False,
                          sort_keys=True)
        except Exception as error:
            messagebox.showerror(
                APP_TITLE,
                tr("Couldn't write the template: %s")
                % error)
            return

        messagebox.showinfo(
            APP_TITLE,
            tr("Interface translation template written to:\n\n%s\n\nFill in "
               "the blanks for any language and restart DialogueForge - it is "
               "picked up automatically, no rebuild needed. Visit every tab "
               "before exporting to catch every string.") % path)

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
        ttk.Button(row, text="Quest flow report",
                   command=self.write_quest_flow).pack(side="left", padx=6)

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
            if data.get("ui_language") in LANGUAGE_LABELS:
                self.ui_language = data["ui_language"]
        except Exception:
            pass

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as handle:
                json.dump({"profile_path": self.profile_path.get(),
                           "quest_folder": self.quest_folder.get(),
                           "theme": self.theme_name,
                           "ui_language": self.ui_language}, handle)
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
                 id(self.menu_tab): "Menu appearance",
                 id(self.ai_settings_tab): "Global AI settings",
                 id(self.factions_tab): "Factions",
                 id(self.ai_patrols_tab): "AI patrols",
                 id(self.translations_tab): "Translations"}
        return names.get(id(editor), "")

    def custom_faction_names(self):
        tab = getattr(self, "factions_tab", None)
        if tab is None:
            return []
        return tab.names()

    def known_reputations(self):
        result = {}
        for key, label in getattr(self, "_rep_scan", {}).items():
            if key:
                result[key] = label
        for name in self.custom_faction_names():
            key = rep_key_from_name(name)
            if key:
                result[key] = name
        try:
            own = (self.dialogue_tab.reputation_var.get() or "").strip()
        except Exception:
            own = ""
        own_key = rep_key_from_name(own)
        if own_key:
            result.setdefault(own_key, own or rep_label_from_key(own_key))
        pairs = [(label, key) for key, label in result.items()]
        pairs.sort(key=lambda pair: pair[0].lower())
        return pairs

    def _scan_reputations(self):
        found = {}

        def note(key):
            key = str(key or "").strip()
            if key:
                found.setdefault(key, rep_label_from_key(key))

        for path in getattr(self, "found_files", []):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            note(data.get("ReputationVar"))
            trees = [data] + list(data.get("Stages") or [])
            for tree in trees:
                if not isinstance(tree, dict):
                    continue
                note(tree.get("ReputationVar"))
                for op in (tree.get("RequiredVars") or []):
                    if isinstance(op, dict):
                        note(op.get("Name"))
                for node in (tree.get("Nodes") or []):
                    if not isinstance(node, dict):
                        continue
                    for line in (node.get("SpeakerLines") or []):
                        for op in (line.get("RequiredVars") or []):
                            if isinstance(op, dict):
                                note(op.get("Name"))
                    for resp in (node.get("Responses") or []):
                        if not isinstance(resp, dict):
                            continue
                        for field in ("SetVars", "RequiredVars"):
                            for op in (resp.get(field) or []):
                                if isinstance(op, dict):
                                    note(op.get("Name"))
        self._rep_scan = found

    def on_close(self):
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
        status = getattr(self, "status", None)
        if status is not None:
            status.configure(text=text)

    # ---------------- profile / files

    def pick_profile(self):
        folder = filedialog.askdirectory(
            title="Select your DialogFramework folder")
        if not folder:
            return
        folder = self._resolve_profile_folder(folder)
        self.profile_path.set(folder)
        self.save_settings()
        self.dialogue_tab.update_path_preview()
        self.scan_files()
        self.guess_quest_folder()
        self.auto_load_menu_config()

    def _resolve_profile_folder(self, folder):
        def looks_like_framework(path):
            return (os.path.isfile(os.path.join(path, "MenuConfig.json"))
                    or os.path.isdir(os.path.join(path, "Dialogues")))

        if looks_like_framework(folder):
            return folder

        try:
            for name in os.listdir(folder):
                sub = os.path.join(folder, name)
                if (os.path.isdir(sub) and name.lower() == "dialogframework"
                        and looks_like_framework(sub)):
                    if messagebox.askyesno(
                            APP_TITLE,
                            "That looks like the profile root.\n\nThe mod's "
                            "files are in the \"%s\" folder inside it. Use that "
                            "instead? (recommended)" % name):
                        return sub
                    break
        except Exception:
            pass

        return folder

    def auto_load_menu_config(self):
        path = os.path.join(self.profile_path.get(), "MenuConfig.json")
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    self.menu_tab.load(json.load(handle))
                self.set_status("Loaded existing MenuConfig.json")
            except Exception as error:
                self.set_status("MenuConfig.json could not be read: %s" % error)

        ai_path = os.path.join(self.profile_path.get(), "AISettings.json")
        if os.path.isfile(ai_path):
            try:
                with open(ai_path, "r", encoding="utf-8") as handle:
                    self.ai_settings_tab.load(json.load(handle))
            except Exception:
                pass

        faction_path = os.path.join(self.profile_path.get(), "Factions",
                                    "Factions.json")
        if os.path.isfile(faction_path):
            try:
                with open(faction_path, "r", encoding="utf-8") as handle:
                    self.factions_tab.load(json.load(handle))
            except Exception:
                pass

        patrol_path = os.path.join(self.profile_path.get(), "AIPatrol",
                                   "AIPatrols.json")
        if os.path.isfile(patrol_path):
            try:
                with open(patrol_path, "r", encoding="utf-8") as handle:
                    self.ai_patrols_tab.load(json.load(handle))
            except Exception:
                pass

    def create_structure(self):
        root = self.profile_path.get()
        if not root:
            messagebox.showinfo(APP_TITLE, "Pick a profile folder first.")
            return
        for folder in ["Dialogues", os.path.join("Dialogues", "Shared"),
                       "QuestText", "Localization"]:
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
        for top in ["MenuConfig.json", "AISettings.json"]:
            path = os.path.join(root, top)
            if os.path.isfile(path):
                candidates.append(path)
        for sub in ["Dialogues", "QuestText", "AIPatrol", "Factions",
                    "Localization"]:
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
        self._scan_reputations()

    def write_quest_flow(self):
        """Writes a plain-text map of every quest lock across every
        conversation, so an owner can look it up instead of remembering it."""
        root = self.profile_path.get()
        if not root or not os.path.isdir(root):
            messagebox.showinfo(APP_TITLE, "Pick a profile folder first.")
            return

        known = set(q.get("id") for q in self.quest_index
                    if isinstance(q.get("id"), int))

        rows = []
        problems = []
        scanned = 0

        base = os.path.join(root, "Dialogues")
        for current, _dirs, files in os.walk(base):
            for name in sorted(files):
                if not name.lower().endswith(".json"):
                    continue
                path = os.path.join(current, name)
                try:
                    with open(path, "r", encoding="utf-8") as handle:
                        data = json.load(handle)
                except Exception as error:
                    problems.append("%s won't parse as JSON: %s"
                                    % (os.path.relpath(path, root), error))
                    continue
                if not isinstance(data, dict) or "Nodes" not in data:
                    continue

                rel = os.path.relpath(path, root)
                scanned += 1
                rows.extend(quest_flow_rows(data, rel))
                problems.extend(quest_flow_problems(data, rel, known))

        if not scanned:
            messagebox.showinfo(
                APP_TITLE,
                "No conversations found under the Dialogues folder.")
            return

        report = build_quest_flow_report(
            rows, problems,
            self.quest_title_only)

        out_path = os.path.join(root, "QuestFlow.txt")
        try:
            with open(out_path, "w", encoding="utf-8") as handle:
                handle.write(report)
        except Exception as error:
            messagebox.showerror(
                APP_TITLE,
                "Couldn't write the report: %s" % error)
            return

        self.scan_files()
        self.set_status("Quest flow report written to %s" % out_path)
        self.show_text_window("QuestFlow.txt", report)

    def quest_title_only(self, quest_id):
        """Just the name. quest_label() prefixes the id, which reads badly
        under a heading that already says the id."""
        entry = self.quest_lookup(quest_id)
        if entry and entry.get("title"):
            return entry["title"]
        return "name unknown - not in your quest folder"

    def show_text_window(self, title, content):
        window = tk.Toplevel(self)
        window.title(title)
        window.geometry("900x600")
        text = tk.Text(window, wrap="none")
        text.pack(fill="both", expand=True)
        text.insert("1.0", content)
        text.configure(state="disabled")
        self.skin_window(window)

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
        if looks_like_localization(data):
            count = self.translations_tab.load(data, path)
            self.notebook.select(self.translations_tab)
            self.clear_editor_dirty("Translations")
            self.set_status("Loaded %d translated line(s) from %s"
                            % (count, path))
        elif "Factions" in data or name == "factions.json":
            self.factions_tab.load(data)
            self.notebook.select(self.factions_tab)
            self.clear_editor_dirty("Factions")
            self.set_status("Loaded factions from %s" % path)
        elif "Patrols" in data or name == "aipatrols.json":
            self.ai_patrols_tab.load(data)
            self.notebook.select(self.ai_patrols_tab)
            self.clear_editor_dirty("AI patrols")
            self.set_status("Loaded AI patrols from %s" % path)
        elif "ResetOnDeath" in data or name == "aisettings.json":
            self.ai_settings_tab.load(data)
            self.notebook.select(self.ai_settings_tab)
            self.clear_editor_dirty("Global AI settings")
            self.set_status("Loaded global AI settings from %s" % path)
        elif "Quests" in data:
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
                "Nodes, Quests, Position, Patrols or AI settings field found.")

    # ---------------- save & validate

    def current_editor(self):
        current = self.notebook.select()
        widget = self.nametowidget(current)
        if widget in (self.dialogue_tab, self.quest_tab, self.menu_tab,
                      self.ai_settings_tab, self.factions_tab,
                      self.ai_patrols_tab, self.translations_tab):
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
        if editor not in labels:
            messagebox.showinfo(
                APP_TITLE,
                "This tab edits a single server file - open or edit it "
                "directly rather than starting a blank one.")
            return
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
        root = self.profile_path.get()
        if not root or not os.path.isdir(root):
            messagebox.showinfo(APP_TITLE, "Pick a profile folder first.")
            return

        self.scan_files()
        if not self.found_files:
            messagebox.showinfo(
                APP_TITLE, "No config files found under:\n%s" % root)
            return

        results = []
        npc_claims = {}
        trader_claims = {}
        quest_claims = {}
        counts = {"dialogue": 0, "quest": 0, "menu": 0, "localization": 0,
                  "unknown": 0}

        #! Collected on the way past so translations can be checked against
        #! the trees they claim to translate, once every file has been read.
        loc_files = []
        tree_keys_by_file = {}
        tree_keys_by_id = {}
        quest_keys_by_id = {}

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
            if looks_like_localization(data):
                #! Checked after the loop - the trees it refers to may not
                #! have been read yet.
                counts["localization"] += 1
                loc_files.append((rel, path, data))
                continue
            if "Nodes" in data:
                counts["dialogue"] += 1
                keys = set(key for key, _text, _where in loc_tree_entries(data))
                loc_key = loc_relative_tree_path(root, path)
                if loc_key:
                    tree_keys_by_file[loc_key] = keys
                tree_id = safe_int(data.get("ID", 0), 0)
                if tree_id > 0:
                    tree_keys_by_id.setdefault(tree_id, set()).update(keys)
                kind, key = kind_and_key_from_path(path)
                if safe_int(data.get("AIPatrolID", 0), 0) > 0:
                    kind = "AI"
                issues, warnings = validate_tree_dict(
                    data, kind, key, self.quest_index)
                #! Same checks the quest flow report runs, so a broken quest
                #! lock shows up here too rather than only in the report.
                known_ids = set(q.get("id") for q in self.quest_index
                                if isinstance(q.get("id"), int))
                issues.extend(quest_flow_problems(data, rel, known_ids))
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
                    quest_id = safe_int(quest.get("QuestID", 0), 0)
                    if quest_id > 0:
                        quest_keys_by_id.setdefault(quest_id, set()).update(
                            key for key, _t, _w in loc_quest_entries(quest))
            elif "Position" in data or name == "menuconfig.json":
                counts["menu"] += 1
                issues, warnings = validate_menu_dict(data)
                if name != "menuconfig.json":
                    warnings.append(
                        "Only MenuConfig.json in the profile root is read by "
                        "the mod - this copy is ignored.")
            elif "Patrols" in data or name == "aipatrols.json":
                issues, warnings = [], []
                plist = data.get("Patrols")
                if not isinstance(plist, list):
                    plist = []
                for i, patrol in enumerate(plist):
                    if not isinstance(patrol, dict):
                        continue
                    pname = (str(patrol.get("Name", "") or "").strip()
                             or "patrol %d" % (i + 1))
                    if safe_int(patrol.get("DialogueID", 0), 0) <= 0:
                        issues.append(
                            "%s has no Dialogue ID (must be 1 or higher)."
                            % pname)
            elif "ResetOnDeath" in data or name == "aisettings.json":
                issues, warnings = [], []
            elif "Factions" in data or name == "factions.json":
                issues, warnings = [], []
                for i, faction in enumerate(data.get("Factions") or []):
                    if isinstance(faction, dict) and not str(
                            faction.get("Name", "") or "").strip():
                        issues.append("Faction %d has no name." % (i + 1))
            else:
                counts["unknown"] += 1
                issues, warnings = [], [
                    "Not a recognised config - no Nodes, Quests, Position, "
                    "Patrols, Factions or AI settings."]
            results.append((rel, issues, warnings))

        results.extend(self.check_localization_files(
            loc_files, tree_keys_by_file, tree_keys_by_id, quest_keys_by_id))

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

    def check_localization_files(self, loc_files, tree_keys_by_file,
                                 tree_keys_by_id, quest_keys_by_id):
        """Translations point at a line by position, so editing a tree after
        translating it can leave an overlay aimed at the wrong line - or at a
        line that no longer exists. Nothing errors in game when that happens,
        the text just quietly comes out wrong, so it gets caught here."""
        results = []

        for rel, path, data in loc_files:
            issues = []
            warnings = []

            language = str(data.get("Language", "") or "").lower()
            folder = os.path.basename(os.path.dirname(path)).lower()
            if folder not in LANGUAGE_LABELS:
                issues.append(
                    "'%s' isn't a language the mod reads, so nothing in this "
                    "file is used. The folder must be one of: %s."
                    % (folder, ", ".join(LANGUAGE_CODES)))
            elif language and language != folder:
                warnings.append(
                    "Says Language '%s' but sits in the '%s' folder. The "
                    "folder wins - players get %s."
                    % (language, folder, folder))

            for block in (data.get("Trees") or []):
                tree_file = str(block.get("TreeFile", "") or "").lower()
                tree_id = safe_int(block.get("TreeID", 0), 0)

                known = None
                matched_by = ""
                if tree_file and tree_file in tree_keys_by_file:
                    known = tree_keys_by_file[tree_file]
                    matched_by = tree_file
                elif tree_id > 0 and tree_id in tree_keys_by_id:
                    known = tree_keys_by_id[tree_id]
                    matched_by = "tree ID %d" % tree_id
                    if tree_file:
                        warnings.append(
                            "No tree at '%s' any more - falling back to "
                            "matching on tree ID %d. Re-save this translation "
                            "from the Translations tab if you moved or "
                            "renamed the conversation."
                            % (tree_file, tree_id))

                if known is None:
                    issues.append(
                        "Nothing this translates to. No tree at '%s' and no "
                        "tree with ID %d - these lines never reach a player."
                        % (tree_file or "(no TreeFile)", tree_id))
                    continue

                self._report_stale_keys(block, known, matched_by, issues,
                                        warnings)

            for block in (data.get("Quests") or []):
                quest_id = safe_int(block.get("QuestID", 0), 0)
                known = quest_keys_by_id.get(quest_id)
                if known is None:
                    issues.append(
                        "Translates quest %d, but no QuestText file has "
                        "wording for that quest - these lines never reach a "
                        "player." % quest_id)
                    continue
                self._report_stale_keys(block, known, "quest %d" % quest_id,
                                        issues, warnings)

            results.append((rel, issues, warnings))

        return results

    @staticmethod
    def _report_stale_keys(block, known, matched_by, issues, warnings):
        entries = block.get("Entries") or []
        stale = [str(record.get("Key", "")) for record in entries
                 if str(record.get("Key", "")) not in known]

        if stale:
            issues.append(
                "%d translated line(s) point at text that isn't in %s any "
                "more (%s%s). That usually means the conversation was edited "
                "after it was translated - open the tree, go to the "
                "Translations tab and save it again."
                % (len(stale), matched_by, ", ".join(sorted(stale)[:4]),
                   ", ..." if len(stale) > 4 else ""))

        done = len(entries) - len(stale)
        if known and done < len(known):
            warnings.append(
                "%d of %d line(s) translated in %s - the rest show the "
                "original wording, which is fine if that's what you want."
                % (done, len(known), matched_by))

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
