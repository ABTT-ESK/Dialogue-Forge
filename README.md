<div align="center">

<img src="docs/images/logo.png" width="120" alt="DialogueForge">

# DialogueForge

**Build NPC and trader conversations for the DayZ Dialogue Framework — without touching a single line of JSON.**

[**⬇ Download**](../../releases/latest) · [Setup guide](docs/GUIDE.md) · [Dialogue Framework on Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=3767910705)

</div>

---

Writing dialogue by hand means a lot of time in a text editor, counting node
numbers and hunting for the one missing comma that stops the whole file
loading. DialogueForge gives you the same files through a normal Windows
program.

No install.  No coding. Download it, run it, point it at your
server profile folder.

<img src="docs/images/dfw1.png" alt="The dialogue editor, showing the conversation outline, the node editor and the branch map">

<img src="docs/images/dfw2.png" alt="The dialogue editor, showing the conversation outline, the node editor and the branch map">

## What it does

**Writes every config the mod uses**

Dialogue trees for quest NPCs, traders and shared conversations, per-quest
wording, and the menu appearance — all from one window.

**Shows you the shape of the conversation**

The branch map on the right draws your whole conversation as connected
boxes. The one you're editing glows gold, so you always know where you are.
Click any box to jump to it.

**Catches mistakes before your players do**

One button checks every config in your folder and tells you, in plain
English, what will break. Dead ends, options nobody can ever see, two files
fighting over the same NPC.

**Picks quests by name**

Point it at your Expansion quests folder once and every quest field becomes
a dropdown of real names. No more digging through files for an ID number.

## A look around

### Menu appearance

Colour pickers for every part of the window, sliders for size and position,
and a live preview so you can see what you're building. Colours are always
written in the right order, which removes the single most common cause of an
invisible dialogue box.

<img src="docs/images/dfw4.png" alt="The menu appearance tab with colour pickers and a live preview">

### Quest wording

Write what your NPCs say when a quest is offered, accepted, in progress or
handed in — and what they say once they have nothing left, so a finished
chain can point players at whoever hands out the next one. Add as many phrasings as you like — each one becomes its own
button in game. Anything you leave blank falls back to the mod's built-in
text, so you only fill in what you care about.

<img src="docs/images/dfw3.png" alt="The quest wording tab">

### Check everything at once

<img src="docs/images/DFW6.png" alt="The check-all-files report showing 30 files checked with nothing to report">

### Your whole setup, listed

Every config found in your profile folder. Double-click one to open it.

<img src="docs/images/dfw5.png" alt="The server files tab listing every config found">

**Updating a config after a mod update?** Open the file and save it — that
writes any newly-added fields while keeping your work. Nothing breaks if you
don't; you just won't see the new options until you do.

**Live preview** opens a second window showing where your text lands on the
in-game menu, updating as you type. Put it on a second monitor while you
write.

## Getting started

1. **[Download the latest release](../../releases/latest)** and unzip it
   anywhere.
2. Run `DialogueForge.exe`.
3. Click **Browse...** and pick the `DialogFramework` folder inside your
   server profile — the one with `MenuConfig.json` in it. Start your server
   once first if that folder doesn't exist yet.

That's it. The **Server files** tab now lists everything you have, and
double-clicking a file opens it.

> **Windows will show a blue "Windows protected your PC" box the first
> time.** That happens with any small free tool that isn't signed with an
> expensive certificate. Click **More info**, then **Run anyway**. If you'd
> rather not take my word for it, all the source is in this repo and you can
> build it yourself with `build_exe.bat`.

**After saving anything:** restart your server, then fully close and reopen
your game — a reconnect isn't enough. Then check
`Dialogues\LoadLog.txt`; there's a button for it on the Server files tab.

## Needs

- Windows 10 or 11
- The [Dialogue Framework](https://steamcommunity.com/sharedfiles/filedetails/?id=3767910705) mod on your server

Nothing else. No runtime, no install, no dependencies.

## Help and guides

- **[Setup guide](docs/GUIDE.md)** — every tab, explained
- **Something wrong?** [Open an issue](../../issues) and say what you were
  doing and what happened.

## Credits

Made for the DayZ Dialogue Framework by [ABTT-ESK](https://github.com/ABTT-ESK).

Released under the MIT licence — see [LICENSE](LICENSE).
