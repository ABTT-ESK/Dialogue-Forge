# Changelog

## 1.3.0

### Added
- **Translations tab.** Pick a language, work down a list of every line in the
  dialogue tree (or quest wording file) you have open, and type the translation
  next to the original. Shows how many are done, has an "only show what's still
  missing" filter and a "next one missing" jump, and saves to
  `Localization\<language>\` in your profile folder — your tree files are never
  touched. Anything left blank shows the original wording in game, so you can
  ship a language before it's finished.
  - Translations are held per language while you work, so flicking between
    German and Russian never loses a half-finished pass.
  - "Load what's on disk" pulls back a translation you saved earlier, and
    opening a `Localization\...` file from the Server files tab lands in the
    right language automatically.
  - Keys are generated and kept in step with the tree for you. Reordering
    responses in the Dialogue tab and coming back re-reads the tree, so the
    lines always line up with what the server will ask for.
- **The editor's own interface can be switched to another language** with the
  dropdown next to the dark-mode button; the choice is remembered. Tabs, the
  toolbar and the Translations tab are translated into all 13 languages out of
  the box, and everything else stays English until a translation exists for it.
- **"Export interface template..."** (on the Translations tab) writes
  `DialogueForge_locales.json` next to DialogueForge.exe with every interface
  string it has shown so far. Fill in the blanks for a language, restart, and
  it's picked up — no rebuild, no Python needed. Visit every tab before
  exporting so nothing is missed.
- **Quest flow report** on the Server files tab. Writes `QuestFlow.txt` into
  your profile folder: every quest your conversations mention, listed by
  quest and by conversation, with the option's own wording next to it. Built
  so you can look up "what shows after 102?" instead of remembering it.
  It also names the mistakes you can't see in game -- an option that shows
  and hides on the same quest, an `OFFER_QUEST` with no quest picked, or a
  quest id that isn't in your quest folder. The same checks now run in
  "Check ALL config files".
- **Two new fields on a response**, both quest pickers with a Browse button:
  - **Hide after** -- the option disappears once that quest is completed.
  - **Quest to use** -- which quest `OFFER_QUEST` or `ACCEPT_QUEST`
    acts on. Greys out for actions that don't use one.
- **`OFFER_QUEST`** in the action dropdown, no longer behind "show advanced":
  it opens one quest's offer screen from any option you write.
- **"Check ALL config files" now checks translations too.** A translation
  points at a line by position, so editing a conversation after translating it
  can leave the translation aimed at the wrong line — nothing errors in game,
  the text just quietly comes out wrong. The sweep reports:
  - lines pointing at text that no longer exists (edit the tree, re-save the
    translation),
  - translations that match no tree at all, or match only by ID because the
    file was renamed,
  - a language folder that isn't one the mod reads,
  - and how many lines of each conversation are done, so you can see at a
    glance what's left across your whole server.
- **"Let players pick their language"** on the Menu appearance tab, next to the
  hint-icons toggle. On by default, and it only does anything on a server that
  has translations installed.
- **"Tell players on screen when an option is misconfigured"** on Menu
  appearance. On by default. Controls the mod's new pop-up for a badly set up
  option; the "you can't take that quest yet" message always shows either way.
- **"Option text scales with panel size"**, also on Menu appearance. Off by
  default to match the mod, so ticking it is a deliberate choice.

- **Screen names now match the mod's.** The quest wording tab headings and the
  live preview titles use the eleven agreed names from the mod's
  `docs/SCREENS.md` -- "Quest turn-in screen" rather than one tab saying
  "Turn-in screen" and the preview saying "Ready to hand in". The no-quests
  screen alone had four different names between them.

### Fixed
- **The live preview no longer says a long option fits when it doesn't.** It
  wrapped and grew option boxes without limit, while the game clipped the text
  to a single line — which is how a truncated response could look perfectly
  fine here and be cut in half in game. The preview now models what the mod
  actually does: wrap and grow to three lines, then shrink the text.

### Changed
- The **Server files** list and **Create folder structure** now include the
  `Localization` folder.
- Menu appearance now writes `ConfigVersion` 6, and never lowers the version a
  file arrived with.

## 1.2.1

### Fixed
- **Copy/paste now works on non-English keyboard layouts.** Ctrl+C, Ctrl+V,
  Ctrl+X and Ctrl+A work in the text boxes regardless of layout — previously they
  did nothing on layouts where the key isn't a Latin letter (e.g. Cyrillic).
  Right-click still has Copy/Paste as well.

## 1.2.0

### Fixed
- **Save now always overwrites the exact file you opened.** Previously the save
  path was recomputed from the profile folder and tree type; if that didn't line
  up with the file's real location, an edit could be written to a different file
  and the original left unchanged — looking like the edit "reverted" on reopen.
  Opened files now save back to themselves; only brand-new trees use the
  computed path. Use "Save as" to deliberately write elsewhere.
- **Picking the profile root by mistake is now caught.** If you browse to the
  profile folder instead of the `DialogFramework` folder inside it, Forge spots
  the `DialogFramework` subfolder and offers to use it — the setup mistake that
  made saves land in the wrong place.

### Editing
- **Reputations are now pick-from-a-list, not typed.** You give a character a
  name and it gets its own reputation automatically — no codes to remember. Every
  "change reputation" or "only show if reputation…" row is a **dropdown** of your
  characters and factions instead of a text box, so a typo can't silently break
  the link. The list fills itself from the NPCs and factions in your profile, and
  power users can still type a custom one-off flag.
- **Factions tab.** Create your own AI factions — name, loadout, stance toward
  players (friendly / guard / hostile), and a won't-fight list of other factions.
  Up to 32. Custom faction names then appear in the AI patrols tab's Faction
  dropdown.
- **AI patrols tab — full patrol generator.** Build talkable patrols from
  scratch. New / Duplicate / Remove, every Expansion patrol setting (identity,
  spawning, movement & formation, spawn area, advanced combat tuning), plus this
  mod's dialogue ID and permanent-hostility override. Faction / formation / behaviour / speed / stance are dropdowns
  filled from Expansion's own script values. A waypoint editor lets you add,
  update, remove or bulk-paste route coordinates. Opening an existing patrols
  file keeps any field the editor doesn't show untouched.
- **Global AI settings tab** (formerly "AI settings"). The server-wide AI
  calm-down rules — the triggers (death / weapon away / hands up / leave area),
  the leave-area distance, and how long a grudge is held — with dropdowns and
  checkboxes, no hand-editing. Patrols can override these on the AI patrols tab.
- **Anti-farm limit on options.** Each response has a "Max times a player can
  pick this (0 = unlimited)" field. Set it and the option disappears after that
  many picks per player — stops reputation-farming by spamming the same choice.
  Forge manages the hidden counter for you.
- **Reputation & story flags.** Every response has a plain-English Variables
  section: "When this option is picked" rows read *Increase by / Decrease by /
  Set to* N points of a reputation, and "Only show this option if" rows read *is
  at least / is more than / is at most / is below / is exactly / is not* N — all
  dropdowns, no codes to learn. The same conditions work on greeting lines and on
  quest-locked conversations.
- **Per-character reputation.** The *Who it's for* tab has a "This character's
  reputation" section: name the character and add display tiers (e.g. *at 3 or
  more, show "Friendly"*) that appear in the in-game window. A response gets
  **"+ change / require this character's reputation"** buttons that fill this
  character in for you.
- **Talkable-AI dialogue.** New **"Talkable AI (Expansion)"** target type on the
  Dialogue tab, with the patrol ID / unit-number fields. New response actions
  (AI conversations only): one recruits the AI into the player's group, another
  turns the AI's whole patrol hostile. The checker flags an AI conversation with
  no patrol ID. On an AI conversation the **Quest talk** page is greyed out and
  the quest-only response actions are hidden — AI never open a quest list.
- **Quest-locked conversations.** On the Dialogue tab, an "Editing conversation"
  dropdown lets you build as many separate conversations per NPC as you like —
  the first is the base (always shown), and each further one opens once its quest
  is completed. Each has its own outline, branch map and starting point, so a
  stage of the story is a clean workspace instead of one sprawling set of screens.
  Set the unlock quest inline, add/remove conversations, and right-click a screen
  to **copy it (or its whole branch) into another conversation** with numbering
  handled for you. NPCs that use only the base conversation are unaffected.

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
