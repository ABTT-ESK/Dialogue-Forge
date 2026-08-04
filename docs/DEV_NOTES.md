# Developer notes

Only relevant if you're modifying DialogueForge itself. Users don't need any
of this — see [`GUIDE.md`](GUIDE.md).

The app is a single file, `src/DialogueForge.py`, laid out top to bottom:
constants → theme/artwork → helpers → spellcheck → shared widgets →
validation → the tabs (Dialogue, Quest wording, Menu appearance, Global AI
settings, Factions, AI patrols) → live preview → main app. `# ----` banners mark
each section.

Every tab implements the same contract the main app calls: `load(data)`,
`build_output()`, `output_path()`, and `validate()` (returns `(issues,
warnings)`). New file types are wired in five places: the notebook, `editor_name`,
`current_editor`, `load_path` (open-file type detection), `scan_files` /
`check_all_files` (Server files list + sweep), and `auto_load_menu_config`
(load on profile pick).

## AI patrols / factions tabs

- **`AIPatrolsTab` round-trips unknown fields.** It keeps each patrol as a raw
  dict and only rebinds the keys the UI shows (via the generic `self.fields`
  table), so any Expansion field the editor doesn't surface survives a save.
- **`PATROL_FACTIONS/FORMATIONS/BEHAVIOURS/SPEEDS/STANCES` and `PATROL_STANCES`
  are copied verbatim from the Expansion AI scripts** (`eAIWaypointBehavior`,
  `eAIMovementSpeed`, `eAIStance`, the `Formations/` classes, and the faction
  hint in `ExpansionAISpawnBase`) — not invented. Re-check them against the
  reference if Expansion adds more.
- **A patrol with no waypoints does not spawn** (the mod skips it), so that's a
  hard validation error, not a warning.
- **`FactionsTab` feeds custom names into the patrol Faction dropdown** through
  `App.custom_faction_names()`; the mod caps factions at
  `FACTION_MAX_SLOTS` (32), mirrored here.

## Data model

- **`current_stage_index`**: `-1` = the base tree (Tree 1); `0+` = an index
  into `self.tree["Stages"]`. `container()` returns the node dict currently
  being edited, and all node / outline / branch-map editing runs on it, so
  the base tree and each quest-locked stage are edited the same way.
- **Serialization writes every field explicitly.** Omitted fields do *not*
  inherit the mod's documented defaults (JSON loading skips constructors
  mod-side), so `_serialize_nodes` always writes them out.
- **Only genuinely optional fields are written conditionally** (e.g.
  `Stages`), so a file that never used them stays byte-identical and older mod
  builds ignore what they never see.

## Config versioning

Stamp the `ConfigVersion` the mod uses to decide whether a file needs new
fields written in, but **never lower a version already loaded** — a newer mod
may have bumped it past what this build knows about.

## Quest description lines

The mod shows `Descriptions[]` line 1 (offer, the giver) and line 3 (turn-in)
verbatim; line 2 is overridden mid-quest, so the editor leaves it out. The
lines live in the Expansion quest file and are edited in place — pad to three
lines so writing line 3 never leaves gaps.

## Expansion config scanning

Expansion splits quests and NPCs into sibling folders, so the scan starts from
the parent, not the Quests folder alone. Objective configs share the `ID`
field but carry `ObjectiveType`, so they're skipped when indexing quests.

## Tk gotchas

- **Mouse wheel goes to the focused widget, not the one under the pointer.**
  `on_mouse_wheel` reroutes the event to whatever is under the cursor.
- **`ScrollFrame` exists because the taller tabs don't fit a 1080p screen**
  once the window is anything less than maximised.
- **Classic tk widgets ignore ttk styles** (comboboxes' popup listboxes,
  `ColorRow`'s swatch), so they're coloured by hand in `skin_children`. The
  swatch is deliberately left out — its whole job is to show the chosen colour.
- **Unsaved-change tracking** must be created *before* the tabs: editors
  report status while they build themselves, so without the holder in place
  the app starts life claiming unsaved work. The build-time events are ignored
  until the window is actually up.

## Validation

Lives at module level so the same rules run whether checking the current tab
or sweeping every file in the profile folder. Watch the `0` vs `-1` trap: a
quest ID of `0` is exactly what some checks exist to catch, so never collapse
it with `x or -1`.

## Live preview

Polls the editors rather than hooking every widget, so nothing has to notify
it — it just redraws the in-game screen for whatever field the cursor is in.

## Artwork

PNGs are vector-rendered and embedded as base64 so the `.exe` stays a single
file. The header mark is a generic git-branch mark, **not** GitHub's Octocat —
that's GitHub's trademark. Swap in the official one from
<https://github.com/logos> if you want it.
