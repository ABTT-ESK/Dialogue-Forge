# Changelog

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
