# Changelog

## 1.1.1

### A calmer, less crowded layout
- **Every tab is grouped by the in-game screen a field belongs to.** On Quest
  wording and Quest talk, each box is one screen the player sees — offer,
  in-progress, turn-in, the reward picker, the quest-list greeting, and the
  no-quests screen — instead of one flat grid of boxes. The quest-list greeting
  no longer shares a box with the no-quests wording.
- **Sections collapse.** Each screen is a dropdown you open as needed, so a tab
  opens as a short list of headers rather than a wall of fields. The most-used
  section on each tab starts open; the rest stay tucked away, and their help
  text tucks away with them. The Flow tab folds its optional bits too — a node
  is just an ID, a type and a line of speech, with voice lines, extra spoken
  lines, and per-option quest gating behind their own dropdowns.
- **Bolder section headings** across every tab, so it's clear where one group
  ends and the next begins.

### Editing
- **Per-screen "back to the conversation" buttons.** Every quest screen has its
  own back-button box, so the wording can differ per screen instead of one line
  reused everywhere. Set NPC-wide defaults on the Quest talk tab and override
  per quest on the Quest wording tab. The live preview shows each screen's back
  buttons in place. Writes QuestText files at version 2 (matching the mod);
  older files gain the new fields automatically.
- **Right-click a row in the conversation outline** to edit or delete that exact
  node or option. Deleting is now on the thing you clicked, instead of a
  node-delete button and an option-delete button in different corners.
- **The quest-file preview** (the read-only offer and turn-in lines) now sits in
  a labelled "Preview from Expansion quest file" box that names the quest.

### Fixed
- **"Add option" no longer eats what you typed.** Type a label into the Button
  text box and hit Add and the new option keeps that label; each Add stages a
  fresh option instead of overwriting the last one.
- A harmless error that printed to the console on start-up (a colour row's alpha
  slider updating before its label existed) is gone.

## 1.1.0

### Editing
- **Spellcheck** in every typing box. Misspellings get a red underline in the
  multi-line boxes; right-click any flagged word for suggestions or to add it
  to your own dictionary. ALL-CAPS acronyms, CamelCase class names and words
  with digits are left alone, so proper nouns aren't flagged as errors.
- **Undo / redo** (Ctrl+Z / Ctrl+Y) in the text boxes, including the single-line
  fields — delete a whole line by accident and you can bring it straight back.
- The **quest description lines** now show on the Quest wording tab and can be
  edited in place. The **On offer** line (what the giver says) and the **On
  turn-in** line (what the turn-in NPC says) each have their own box labelled
  with who speaks it; **Edit** then **Save** writes that line straight back to
  the Expansion quest file. The live preview shows the real offer and turn-in
  lines too.
- **NPC names shown for context** across the tabs. The Dialogue tab shows whose
  conversation you're editing next to the NPC ID and in the preview
  (`NPC 2 "Steve"`); the Quest wording tab shows which NPC gives the quest and
  uses that name as the preview speaker. The **Hand it in** box names the
  turn-in NPC too, so a quest whose giver and turn-in differ is easy to tell
  apart. Names come from your Expansion NPC and quest configs (via
  `QuestGiverIDs` / `QuestTurnInIDs`).
- The **Once this quest is completed** section now spells out whose quest list
  the wording lands on. Because the mod matches the giver *and* the turn-in NPC,
  both are listed with their role, and for each it shows where this quest sits
  in that NPC's override chain - which lower quest's wording it replaces and
  which higher quest will replace it - so overrides and turn-in-only NPCs are
  clear without opening other quests.

### Dialogue tab
- The quest-lock control is now a single dropdown that defaults to **Not
  locked** — no more checkbox. Picking a quest updates the hint underneath
  immediately.
- **Multiple spoken lines per node**, so a greeting need not be the same every
  time. Any node can carry a list of extra lines; the mod picks one at random
  from the main line plus whichever extras the player qualifies for. Each extra
  line can be **locked to a completed quest** and carry its **own voice lines**,
  so you can have, say, three always-on greetings and two that only appear once
  particular quests are done. Requires the matching DialogueFramework update
  (new `SpeakerLines` node field); files without it are unchanged and older mod
  builds ignore it.
- Each extra line also has a separate **"Standard greeting after"** dropdown.
  Point it at a quest and, once that quest is completed, this line stops being
  one of the random options and becomes the NPC's fixed greeting (highest such
  quest wins if several apply). It's independent of the quest lock, so a line
  can be a random extra, a locked reveal, a permanent post-quest greeting, or a
  combination.

### Live preview
- Long option text now wraps cleanly — the highlight box around each option
  grows to fit however many lines it wraps to, instead of the text clipping out
  of a fixed-height box. Speaker-line spacing is measured the same way, so the
  options always start clear of it.

### The application
- The release `.exe` now bundles `pyspellchecker`. Running from source without
  it still works; spellcheck simply switches off.

## 1.0.0

First public release.

### Editing
- Visual editor for dialogue trees — quest NPC, trader and shared
- Branch map showing the whole conversation as connected boxes
- Quest wording editor covering accept, decline, in-progress and turn-in text,
  the reward picker line, and what an NPC says once a quest is finished
- **Quest talk** page for the lines an NPC uses around their quest list, and
  for when they have nothing available
- Menu appearance editor with colour pickers, position presets, font style and
  the hint-icon toggle
- Pick quests and NPCs by name straight from your Expansion configs
- Copy a conversation from one NPC to another

### Live preview
- Separate preview window you can put on a second monitor, showing the in-game
  screen for whatever you're editing as you type
- On the quest wording tab it follows your cursor, switching between the
  offer, in-progress, turn-in, reward, quest list and no-quests screens
- Draws hint icons using the same rule the mod applies, so an option that
  closes the menu shows the exit icon before a player ever clicks it
- Colours, sizing and font style come from your Menu appearance tab, so it
  reflects your server rather than a generic theme

### Getting it right
- Problem checker for a single file or every config at once, catching dead
  node references, unreachable branches, duplicate IDs and wording that can
  never appear
- Every field labelled **(NPC says)** or **(Player says)**, and optional
  groups marked as optional
- Writes the `ConfigVersion` the mod expects, and never lowers a newer one
- Closing with unsaved work asks first, naming which editors are affected

### The application
- Runs standalone on Windows — no Python and no install
- Opens sized to your screen; tall panels scroll rather than being cut off
- Dark and light themes
