# DialogueForge guide

Everything the program does, tab by tab. Skim the bit you need.

---

## Before anything else

Two folder boxes sit at the top of the window. Set them once and
DialogueForge remembers them.

**Server profile folder** — the `DialogFramework` folder inside your server
profile, the one containing `MenuConfig.json` and `Dialogues\`. Start your
server once if it isn't there yet.

**Expansion quests** — optional but worth doing. Point it at your Expansion
`Quests` folder and every quest field turns into a dropdown of real quest
names instead of ID numbers. It finds NPC names too.

---

## Dialogue

Where you write conversations. It splits into two pages.

### Who it's for & voice lines

Set this first. Pick what the conversation belongs to:

| Choice | What to enter |
|---|---|
| **A single quest NPC** | The NPC's ID. Use **Pick NPC...** to choose by name. |
| **A trader** | The trader's name, e.g. `Weapons`. |
| **Shared by several NPCs** | Every NPC ID that should use it, comma separated. |

The strip at the top of the tab always shows where the file will save.

Greeting and farewell voice lines are optional. Add several and the mod
picks one at random.

**Traders only:** you can narrow down *which* trader by class name or world
position. "Keys that must agree" is how many of those need to match. If you
only fill in the trader name, set it to 1.

**This character's reputation** — give the character a **name** (e.g. *Silent
Guard*) and it gets its own reputation to track. You never type a code: Forge
turns the name into the key for you (shown as *saved as: rep_silent_guard*), and
that name then appears in the reputation dropdowns on every other NPC, so anyone
can raise or lower it without knowing the key. Add **tiers** to show a word
(*Hostile / Friendly / Trusted*) next to the name in-game instead of a raw
number. Leave the name blank for no reputation.

### Quest talk

What this NPC says around their quest list, for this NPC as a whole.

- **What they say when showing their quests** — when a player asks for work,
  the buttons become that NPC's quest list. These are the lines spoken above
  it. Blank means every NPC uses the built-in *"What do you need done?"*
- **What they say when they have no quests** — the lines, plus buttons that go
  back to the start of the conversation or end it, plus optional voice lines

Both are lists, and one entry is picked at random each visit. Three or four
phrasings is enough to stop a busy NPC sounding scripted, and costs nothing
per quest.

All of it is optional; blank means the mod's built-in text. Leave even the
buttons empty and players still get a plain **Back** button, so this step can
never strand them.

Anything a completed quest sets under **Quest wording → When this NPC has
nothing left to give** overrides the line here. Buttons fall back
independently, so a quest can supply the line while these supply the buttons.

Voice lines for this step are NPC-wide — there's no per-quest version.

### Flow

Three panels.

**Conversation outline (left)** — your whole conversation as a list. Nodes
are the top level, and each node's player options sit underneath it. The
"Leads to" column shows where each option goes. A padlock means the option
is hidden until a quest is done. The ▶ marks where the conversation starts.

**Editor (middle)** — click a node to edit what the NPC says. Click an
option to edit the option.

**Branch map (right)** — the same conversation drawn as boxes, laid out left
to right. Gold outline is where you are. Click any box to jump to it. A gold
`!` means nothing leads to that node, so players can never reach it.

### Writing a conversation

A **node** is one screen: what the NPC says, plus the buttons the player can
press.

Each button needs two things — its text, and what it does:

| What it does | Result |
|---|---|
| **NONE** | Go to the node you pick in "Next node". |
| **SHOW_QUEST_LIST** | Open this NPC's quest list. |
| **END_CONVERSATION** | Say goodbye and close. |
| **OPEN_TRADER** | Close and open the shop. Traders only. |
| **OFFER_QUEST** | Open one quest's offer screen, so the player can read it and accept or decline. Pick the quest in "Quest to use". |

"Next node" only applies to **NONE** — it greys itself out otherwise.

**Quest lock** hides a button until the player has *completed* that quest.
**Hide after** does the opposite — the button disappears once that quest is
completed, so a line can retire itself instead of hanging around forever. Use
both on one button and it appears after the first quest and goes away after
the second. **Browse quests...** picks by name for either.

Renaming a node ID automatically repoints everything that led to it, so you
can renumber without breaking anything.

**Reputation & story flags** (on each button, under the optional section) —
change or check a reputation when a button is picked. The **Reputation**
dropdown lists every character you've named and every faction you've made, so
you just pick one and choose *Increase by / Decrease by / Set to* (or, to gate a
button, *is at least / is below / …*). Because it's one shared list, what a
player says to one NPC can move another NPC's — or a whole faction's —
reputation. You can still type a custom flag name if you want a one-off. The
**+ change / require this character's reputation** buttons fill in this
character for you.

---

## Quest wording

> The headings on this tab are the mod's official screen names. There are
> eleven screens in all and each is named after the field that controls its
> wording, so `TurnInTexts` belongs to the **quest turn-in screen**. The full
> list is in the mod's `docs/SCREENS.md` -- worth a look before asking for
> help, so you can name the screen you mean.


Every field is labelled **(NPC says)** or **(Player says)**. NPC lines are
spoken above the buttons and one is picked at random; player lines each become
their own button.

What your NPCs say around a quest. One entry per quest, five sets of
wording:

- **Accept buttons** — when the quest is offered
- **Decline buttons** — ways to say no
- **While in progress** — accepted but not finished
- **Turn-in buttons** — ready to hand in
- **Back out of turn-in** — the "not yet" button

Every line you add becomes its own button, so a few phrasings makes an NPC
feel less robotic.

Anything you leave empty uses the mod's built-in wording. Partial files are
completely fine.

The **Reward picker line** is a single spoken line above the reward choice,
used only by quests that let the player pick a reward.

### Once this quest is completed

The last group on the tab changes what an NPC says as a player works through
their quests.

**These apply after the quest is turned in, not while it is available.** Fill
them in on quest 101 and they take effect the moment 101 is completed — while
102 is sitting on the list waiting to be taken — and last until the player
completes something higher-numbered for that NPC.

**Their quest list greeting from now on** is the line over the quest list;
**What they say with nothing left** covers having nothing to offer, with
buttons that return to the start of the conversation or end it.

If several completed quests have wording, the **highest quest ID wins**, so a
chain advances what the NPC says on its own — a veteran isn't greeted like a
stranger, and their parting words can point at whoever gives the next quest:

> Quest 2 — *"Wall's done. Talk to Hana at the docks, she's the one hiring
> now."*

The moment quest 2 is turned in, that becomes the NPC's parting line, until
the player finishes something later in the chain.

A quest's buttons are only used when that same quest also has a line, so
buttons on their own never appear — the problem checker flags this. Leave the
buttons empty and the NPC falls back to the ones on its dialogue tab. Leave
everything empty and players still get a plain **Back** button, so this step
can never strand them.

---

## Menu appearance

**Let players pick their language** adds a Language option to the conversation
window. It's on by default and costs you nothing on a single-language server —
it only ever shows up if `Localization\` actually has translations in it.

**Option text scales with panel size** ties response text to how wide you've
made the menu, so a big menu gets big text and a compact one shrinks to fit
rather than cutting anything off. It's **off by default** — turning it on is
the only way your existing menu's text size changes.

Long options wrap and the button grows to fit, up to three lines; past that the
text shrinks instead. You don't have to count characters — write the option and
the preview shows you what it will look like.


How the dialogue window looks.

**Placement** — nine screen positions, plus sliders for size and nudging.
`BOTTOM_CENTER` keeps the NPC's face visible; `CENTER` covers them up.

**Colours** — a picker and a transparency slider for each part of the
window. Four ready-made palettes are in the Preset dropdown.

**Font style** — four text presets built into the mod: `DEFAULT`, `LIGHT`
(thinner), `LARGE` (bigger), `COMPACT` (smaller, fits more options).

**Already-picked fade** dims options the player has already chosen this
conversation.

The preview on the right shows roughly what you'll get. It's a guide to
placement, size and colour balance, not an exact match for in-game fonts.

---

### Hint icons

**Hint icons on buttons** puts a small icon on the right of every response
button so players can see what one does before clicking: an exit door for
anything that closes the menu, a shopping cart for opening the market, a
speech bubble for anything that keeps the conversation going.

They take their colour from your response text colour, so they match whatever
theme you set. Off by default.

Turn it on and both previews show the icons, picked from what each option
actually does — so on the Dialogue tab you can see at a glance whether an
option reads as "this ends the chat" before a player ever clicks it.

## Global AI settings

The server-wide defaults for what a talkable AI does after a `GO_HOSTILE`
dialogue choice turns it on the player. Saves to `AISettings.json`. Only affects
AI angered through dialogue — ordinary AI combat is untouched. Individual patrols
can override the permanent-hostility parts on the AI patrols tab.

**Let them calm down when the player…** — tick which of dies / puts their weapon
away / puts their hands up / leaves the area make an angered AI stand down.
**Leave-area distance** and **Check every** tune the last one and how often the
mod re-checks.

**Permanent hostility** — after angering an AI this many times, that player is
hostile for good. `0` = never permanent. **Remembered by** decides whether the
grudge is held by the whole faction, just that patrol, or both.

## Factions

Make your own AI factions in `Factions\Factions.json` and hand them to talkable
patrols — a way past Expansion's small set of built-in factions. **New /
Duplicate / Remove**, up to 32 factions (a limit baked into the mod). Each has:

- **Name** — what you'll pick on the AI patrols tab, and the name other factions
  reference as friend or foe.
- **Loadout** — a loadout file name; blank uses the default human loadout.
- **Toward players** — *Friendly* (walk up and talk, never attacks unless a
  dialogue choice turns them hostile), *Guard* (tolerates you until you raise a
  weapon at them), or *Hostile* (attacks on sight).
- **Won't fight these factions** — tick allies (built-in or your own). For two
  *custom* factions to truly ignore each other, tick it on **both**. Befriending
  a built-in Expansion faction only works if the built-in's own rules allow it
  (guards and passive factions), which is an Expansion limitation, not ours.

Behind the scenes the mod maps each faction onto a pre-registered slot, so this
all works without touching Expansion's own files.

## AI patrols

A full generator for the talkable patrols in `AIPatrol\AIPatrols.json`. Each
entry is a normal Expansion patrol plus the two links this mod adds. Dropdowns
(faction, formation, behaviour, speed, stance) are filled from Expansion's own
script values, so you can't fat-finger a bad one.

**New patrol** makes one from scratch with sensible defaults; **Duplicate**
copies the selected one (handy for a second unit or a nearby route); **Remove**
deletes it.

The detail panel is grouped:

- **Identity & dialogue link** — the patrol's name and its **Dialogue ID**
  (match a dialogue tree's `AIPatrolID`).
- **Spawning** — faction, loadout, unit count and max, spawn chance, persist,
  respawn/despawn, looting, contaminated-area and AI-trigger toggles. The
  **Faction** dropdown lists Expansion's built-ins plus any factions you made on
  the Factions tab. **Units** is an optional comma-separated list of AI
  classnames; blank uses the faction default.
- **Movement & formation** — behaviour, walk/threat speed, formation and its
  scale/looseness, default stance and look angle, unlimited reload.
- **Spawn area** — the distance/spread/despawn radii and the random-start-point
  toggle. `-1` means "use Expansion's default".
- **Waypoints** — where the patrol lives. **At least one is required** — with
  none the patrol does not spawn at all. One waypoint = it spawns there and holds
  position; extra waypoints = a route it walks (the first is the spawn point).
  Type X/Y/Z and **Add**, or **Paste coords…** to drop in a whole route (any
  lines with three numbers); select a row to **Update** or **Remove** it.
- **Advanced combat** *(the remaining fields)* — accuracy, damage multipliers,
  threat/noise distances, flanking, headshot resistance and the rest. Left at
  their defaults (`-1` / `0`) they behave exactly like a stock Expansion patrol.
- **Permanent hostility for this patrol** — overrides the Global AI settings tab
  for this patrol only. *Use server default* leaves it alone; *Never permanent*
  always forgives; *After a set number* makes it permanent after that many bad
  runs. **Remembered by** overrides the faction/patrol/both choice the same way.

## Translations

For running your dialogue in more than one language.

**How players get a language:** whatever DayZ is set to on their machine. If
you have a folder for it they read your translation, and if you don't they
read your original wording. They don't press anything, and you don't set
anything up per player.

You only need this tab if you want **one server serving several languages**.
If your whole server is in one language — English or otherwise — just write
your conversations in that language and ignore this tab entirely.

The mod's own wording (`Reward:`, `Confirm`, `Cancel`) is already translated
into all 14 languages and needs nothing from you either way.

**Your conversation files are never touched.** A translation is a separate
overlay listing only the lines you've translated, saved to
`Localization\<language>\` in your profile folder.

How it goes:

1. Open the conversation you want to translate on the **Dialogue** tab (or the
   file you want on the **Quest wording** tab).
2. Come to **Translations**. Every line in it is listed — what the character
   says, every button, every alternate line, every story tree.
3. Pick the language at the top left.
4. Click a line, type the translation on the right, **Apply**.
5. **Save** (the button along the top), same as any other tab.

Along the way:

- The counter at the top right says how many are done.
- **Only show lines still missing** hides everything you've already done, and
  **Next one missing** jumps straight to the next gap.
- **Copy the original across** fills the box with the original, handy when a
  line is a name or a number that shouldn't change.
- **Load what's on disk** pulls back a translation you saved earlier.
- Switching language keeps what you've typed for the one you were on, so you
  can work on two at once.

**You don't have to finish.** Any line you leave blank shows your original
wording in game — a half-translated language is safe to put on a live server.
Same for a language you never make a folder for: those players just see the
original.

Two things worth knowing:

- Save your conversation into your profile folder before translating it. A tree
  that isn't there yet can only be matched by its ID, which goes wrong if two
  conversations share one. The tab warns you when you check it.
- If you reorder or delete responses in a conversation, come back to this tab
  and save the translation again. The tab itself re-reads the conversation each
  time you open it and lines everything back up — but the file already on disk
  doesn't update itself, and a translation pointing at a line that moved will
  show the wrong text in game.

**Check ALL config files catches that for you.** Run it after any round of
editing and it reports every translation pointing at text that isn't there any
more, plus how many lines of each conversation are done. That's the one thing
worth doing before you push translations to a live server.

### The editor's own language

The dropdown next to Dark mode switches DialogueForge itself. Tabs, the toolbar
and this tab are translated; anything not translated yet stays English.

**Export interface template...** (bottom of this tab) writes
`DialogueForge_locales.json` next to DialogueForge.exe with every piece of
interface text it has shown you. Fill in the blanks for a language, restart, and
it's picked up — no rebuilding, no Python. Click through every tab first so
nothing gets missed.

---

## Server files

Everything found in your profile folder. Double-click any file to open it in
the right editor.

**Quest flow report** writes `QuestFlow.txt` into your profile folder and
shows it to you: every quest your conversations mention, listed both by quest
and by conversation, with each option's own wording beside it. It's there so
you can look up "what shows after quest 102?" rather than keeping it in your
head.

It also names three things you can't spot in game: an option that shows and
hides on the same quest (so it can never appear), an `OFFER_QUEST` with no
quest picked, and any quest id that isn't in your quest folder. Regenerate it
whenever you change a quest lock.

**Create folder structure** makes the folders for you if you're starting
fresh. **Open LoadLog.txt** shows what the mod made of your files last time
the server started — the first place to look when something didn't work.

---

## The buttons along the top

| Button | What it does |
|---|---|
| **New (blank)** | Clears the current tab to start fresh. Files on disk aren't touched. |
| **Open file...** | Opens any config in the right editor. |
| **Save** | Saves to the path shown on the tab. |
| **Save as / copy to...** | Saves somewhere else, leaving the original alone. |
| **Check this tab** | Checks what you're working on. |
| **Check ALL config files** | Checks everything in your folder. |
| **Dark / Light mode** | Switches the look of the program. |
| **Language dropdown** | Switches the program's own interface language. Remembered next time. |

### Copying a conversation to another NPC

The reason **Save as / copy to...** exists:

1. Open an existing conversation from the Server files tab.
2. Change whatever you want.
3. **Save as / copy to...**, pick the new NPC or trader, confirm.

The file you opened is never modified.

---

## Live preview

**Live preview** in the top right opens a second window you can drag onto
another monitor or beside the app. It shows the in-game screen for whatever
you're currently editing, and follows your cursor:

- **Dialogue tab** — the node you have selected, with its buttons. The
  response you're editing is outlined the way a hover looks in game
- **Quest wording** — click into a field and the preview switches to the
  screen that field appears on. Accept and decline show the offer screen,
  turn-in shows the hand-in screen, the no-quests fields show that step
- **Menu appearance** — sample text, so you can judge colours and size

Colours, window size and font style come from your Menu appearance tab, so it
reflects your server rather than a generic theme. It's approximate: real fonts
and spacing come from the game.

Close it and reopen any time; it doesn't hold anything.

## Checking for problems

Both check buttons split what they find into **will break in game** and
**worth a look**.

Things it catches:

- Buttons pointing at nodes that don't exist
- Nodes nothing leads to
- Nodes where every option is hidden behind a quest — players who haven't
  done them see a line of dialogue with no buttons at all
- Shared conversations with no NPC IDs listed
- Traders set to match on more keys than you've filled in, which never matches
- A trader conversation with no way to reach the shop
- Invisible colours and windows pushed off-screen

**Check ALL config files** adds problems you can only see across files:

- Two files claiming the same NPC — only one wins, and the other is ignored
- The same quest worded in two files
- Files sitting in a folder the mod doesn't recognise
- Files with broken JSON

**Copy report** puts the whole thing on your clipboard, handy for pasting
into a support thread.

---

## Bringing an old file up to date

When the mod adds new settings, opening a file here and **saving it** is all
it takes — DialogueForge always writes the complete current set of fields, and
leaves everything you already wrote exactly as it was.

This matters most for **dialogue trees**, which the mod deliberately never
rewrites. Menu config and quest text files add new fields to themselves on the
next server start; dialogue trees don't, because they're the files with the
most work in them.

Nothing breaks if you skip this. An old tree keeps working exactly as it did —
you just won't see the newer options until you open and save it, or add the
keys by hand.

## Closing with unsaved work

If you try to close the app with changes you haven't saved, it asks first and
names which editors are affected — **Yes** saves them all and closes, **No**
closes and loses them, **Cancel** goes back. The title bar carries a `*` while
anything is unsaved.

If a save is cancelled on the way out (you decline an overwrite, say), the app
stays open rather than closing anyway.

## After you save

Dialogue and appearance changes need:

1. A server restart
2. A **full** game restart — closing to the menu and reconnecting isn't
   enough

Then check `Dialogues\LoadLog.txt` to confirm the mod read your files.

---

## Window size

The window opens sized to your screen, so it fits whether you're on 1080p or
something larger, and it's designed to be used windowed alongside other
things.

If a panel is taller than the space available, it scrolls — a scrollbar
appears on that panel only when it's needed, and the mouse wheel scrolls
whatever the pointer is over. Nothing gets cut off with no way to reach it.

## When something isn't working

| What you see | Likely cause |
|---|---|
| Changes didn't appear | Client wasn't fully restarted |
| NPC has no buttons | Every option is quest-gated — run a check |
| Dialogue box invisible | A colour with transparency set to 0 |
| Window off-screen | Nudge sliders pushed too far; set both to 0 |
| A conversation didn't load | Check `LoadLog.txt` |
| Quest dropdown is empty | Expansion quests folder isn't set |
