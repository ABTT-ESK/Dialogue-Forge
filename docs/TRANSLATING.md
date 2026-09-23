# Translating DialogueForge

The editor's interface can be read in any language. English is what the source
says; everything else is a lookup, keyed by the English string itself.

There are two places a translation can live, and you almost certainly want the
first one.

## Correcting or adding a language without rebuilding

Put a file called **`DialogueForge_locales.json`** next to `DialogueForge.exe`:

```json
{
  "german": {
    "Add node": "Knoten hinzufügen",
    "Save": "Speichern"
  }
}
```

Restart DialogueForge and it is picked up. No build, no Python, nothing to
install. Anything in this file wins over what is built in, so it is also how
you correct a single word you disagree with.

To get a starting point with every string already listed, open DialogueForge,
visit each tab, then use **Export interface template...** on the Server files
tab. It writes that file for you with the blanks in place.

Language codes: `czech`, `german`, `russian`, `polish`, `hungarian`, `italian`,
`spanish`, `french`, `chinese`, `japanese`, `portuguese`, `chinesesimp`.

## Contributing a language back

Built-in translations live in `src/forge_locales.py`, keyed by the English
string. `tools/translations.py` does the work:

```
python tools/translations.py list
```

writes every string the editor can show to `tools/interface_strings.txt`
(numbered, for reading) and `tools/interface_strings.json` (exact text, for
anything that has to be precise — a caption's leading spaces and line breaks
matter and the readable listing cannot show them).

```
python tools/translations.py check
```

reports how much of the interface each language covers, and what is wrong with
what is already there.

```
python tools/translations.py merge <code> <yourfile.json>
```

puts a finished language in. It **refuses** anything that would break the
interface, which is the whole point of it:

- a `%s`, `%d` or `%.2f` that went missing, changed order or appeared from
  nowhere — the editor fills those in afterwards, so a lost one is a crash,
  not a typo;
- a different number of line breaks, which is what turns a tidy pop-up into a
  wall of text;
- a translation of something that is a name rather than a word —
  `DialogueForge`, `GitHub`, file names like `AIPatrolSettings.json`, JSON
  keys, and the mod's own field names. Those are what the author types, so
  translating them sends somebody looking for a file that does not exist.

It also drops entries no label uses any more, so an old translation does not
quietly rot in the file.

## Things worth knowing before you start

**A half-finished language is safe to ship.** Any string without a translation
is shown in English. Nothing breaks, nothing is blank.

**Leading and trailing spaces are load-bearing.** Tab captions are padded
(`"  Dialogue  "`), and some captions are sentence fragments that get a value
glued onto them (`"Saves to: "`, `"Quest given by  "`). Keep the spacing.

**Some captions are half a sentence.** `"Shown "` is completed by one of
several phrases chosen at runtime. Translate the fragment so it still reads
when something follows it.

**The strings are read out of the source**, not kept in a list by hand, so a
label added to the editor turns up in `list` the moment it exists — and `check`
will start reporting it as missing. That is the intended behaviour: it is how
a language stays honest as the editor grows.

## Current state

`german` and `russian` cover the whole interface (485 strings). The other ten
languages have only the tab names and a handful of buttons — enough to see the
app is
translatable, not enough to call them translated. The Russian translation
began as a contribution from **ave-ladan** through pull request #1; their
wording is kept as they wrote it.
