"""Keep DialogueForge's interface translations honest.

Three jobs, one file. Run from anywhere:

    python tools/translations.py list
        Every interface string the editor can show, numbered. Written to
        tools/interface_strings.txt for a translator to work against.

    python tools/translations.py check
        How much of it each language covers, and what is wrong with what is
        already there -- a dropped %s, a changed line count, a name that
        should have stayed in English.

    python tools/translations.py merge <code> <file.json>
        Put a finished language in, refusing anything that would break the
        interface. <file.json> maps English strings to their translation.

The strings are read out of the source rather than kept in a list by hand, so
a label added to the editor turns up here the moment it exists. A string with
no translation is shown in English: a half-finished language is safe.
"""
import ast
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITOR = os.path.join(ROOT, "src", "DialogueForge.py")
LOCALES = os.path.join(ROOT, "src", "forge_locales.py")
LISTING = os.path.join(ROOT, "tools", "interface_strings.txt")
EXACT = os.path.join(ROOT, "tools", "interface_strings.json")

#! The editor fills these in after translating, so one that goes missing is a
#! crash rather than a typo.
PLACEHOLDER = re.compile(r"%(?:\([^)]*\))?[-+ #0]*[\d*]*(?:\.\d+)?[sdifgeExXo%]")

#! Names, not language. They read the same everywhere, and translating them
#! would have somebody typing a word the mod has never heard of.
KEEP_AS_IS = {
    "DialogueForge", "GitHub", "Steam Workshop", "Ag", "...",
    "%s%s", "%.2f", "[%d, %d, %d, %d]",
}


def literals(node):
    """Every string a caption could end up being.

    A caption is not always one literal: some switch between two words
    ("Light mode" / "Dark mode"), some glue a prefix onto a value
    ("Saves to: " + path). Each of those literals reaches the screen, so each
    is a string that needs translating -- missing one is how a label stays
    stubbornly English with nothing obviously wrong.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        return literals(node.left)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return literals(node.left) + literals(node.right)
    if isinstance(node, ast.IfExp):
        return literals(node.body) + literals(node.orelse)
    return []


#! Helpers whose caption is handed in by position rather than as text=.
#! Their titles reach the screen like any other, and translate_children swaps
#! them at runtime, so leaving them out of this list means a visible string
#! nobody is ever told is missing. (class name -> which arguments are text)
POSITIONAL = {
    "CollapsibleSection": (1, 3),     # title, subtitle
    "StringListEditor": (1, 2),       # title, hint
    "ColorRow": (1,),                 # label
    "book_row": (2, 3),               # label, what it says when left empty
}


#! Module-level tables of (value, caption) pairs. The caption reaches the
#! screen through a widget that is handed it as a variable, so nothing above
#! can see it -- which is how every font description stayed English from the
#! day the picker was written.
CAPTION_TABLES = {
    "FONTS": 1,
    "TEXT_SIZES": 1,
    "FONT_STYLES": 1,
}


def table_captions(tree):
    """The caption out of each row of the tables named above."""
    found = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            at = CAPTION_TABLES.get(target.id)
            if at is None:
                continue
            if not isinstance(node.value, (ast.List, ast.Tuple)):
                continue
            for row in node.value.elts:
                if not isinstance(row, (ast.List, ast.Tuple)):
                    continue
                if at < len(row.elts):
                    found.update(text for text in literals(row.elts[at])
                                 if text.strip())
    return found


def interface_strings():
    """Every string the editor can put on screen: a widget's own caption,
    which is swapped automatically, anything handed to tr(), the captions the
    helpers above take by position, and the caption column of the tables."""
    tree = ast.parse(io.open(EDITOR, encoding="utf-8").read())
    found = table_captions(tree)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "tr" \
                and node.args:
            found.update(literals(node.args[0]))
        for keyword in node.keywords:
            if keyword.arg == "text":
                found.update(text for text in literals(keyword.value)
                             if text.strip())

        #! Either a plain call or a method on something -- self.book_row(...)
        #! hands its captions over by position just the same.
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        else:
            name = ""
        if name in POSITIONAL:
            for at in POSITIONAL[name]:
                if at < len(node.args):
                    found.update(text for text in literals(node.args[at])
                                 if text.strip())

    return sorted(s for s in found if s.strip() and len(s.strip()) > 1)


def translations():
    tree = ast.parse(io.open(LOCALES, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) \
                and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id == "UI_TRANSLATIONS":
            return ast.literal_eval(node.value), (node.lineno, node.end_lineno)
    raise SystemExit("UI_TRANSLATIONS not found in %s" % LOCALES)


def faults(entries, known):
    """What is wrong with one language, in plain terms."""
    problems = []
    for english, translated in entries.items():
        if english not in known:
            problems.append("no label uses this any more: %r" % english)
            continue
        if not str(translated).strip():
            problems.append("left empty: %r" % english)
            continue
        want = PLACEHOLDER.findall(english)
        got = PLACEHOLDER.findall(translated)
        if want != got:
            problems.append("placeholders changed (%s -> %s): %r"
                            % (want, got, english))
        if english.count("\n") != translated.count("\n"):
            problems.append("line breaks changed (%d -> %d): %r"
                            % (english.count("\n"), translated.count("\n"),
                               english))
        if english in KEEP_AS_IS and translated != english:
            problems.append("should have been left in English: %r" % english)
        #! Tab captions are padded to set their width, and some captions are
        #! sentence fragments that get a value glued on. Trimming that
        #! spacing changes the layout or runs two words together.
        if english[:1].isspace() != translated[:1].isspace() \
                or english[-1:].isspace() != translated[-1:].isspace():
            problems.append("spacing at the ends changed (%r -> %r)"
                            % (english, translated))
    return problems


def quoted(text):
    return '"%s"' % (text.replace("\\", "\\\\").replace('"', '\\"')
                     .replace("\n", "\\n").replace("\t", "\\t"))


def do_list():
    strings = interface_strings()
    io.open(LISTING, "w", encoding="utf-8").write(
        "\n".join("%3d  %s" % (i, s.replace("\n", "\\n"))
                  for i, s in enumerate(strings, 1)))
    #! The numbered listing is for reading: line breaks are shown as \n and
    #! leading spaces are impossible to see, so it cannot be read back. The
    #! JSON beside it is the exact text, for anything that has to be precise.
    io.open(EXACT, "w", encoding="utf-8").write(
        json.dumps(strings, indent=1, ensure_ascii=False))
    print("%d interface strings -> %s and %s"
          % (len(strings), os.path.relpath(LISTING, ROOT),
             os.path.relpath(EXACT, ROOT)))


def do_check():
    strings = interface_strings()
    known = set(strings)
    languages, _span = translations()

    print("%d interface strings\n" % len(strings))
    worst = 0
    for code, entries in languages.items():
        covered = sum(1 for s in strings if s in entries)
        problems = faults(entries, known)
        worst += len(problems)
        print("   %-12s %4d/%-4d %5.1f%%   %s"
              % (code, covered, len(strings),
                 100.0 * covered / max(1, len(strings)),
                 "%d problem(s)" % len(problems) if problems else "clean"))
        for text in problems[:5]:
            print("        %s" % text)
        if len(problems) > 5:
            print("        ...and %d more" % (len(problems) - 5))

    return 1 if worst else 0


def do_merge(code, path):
    strings = interface_strings()
    known = set(strings)
    entries = json.load(io.open(path, encoding="utf-8"))

    problems = faults(entries, known)
    if problems:
        print("REFUSED -- %d problem(s):" % len(problems))
        for text in problems[:40]:
            print("   %s" % text)
        return 1

    languages, span = translations()
    before = len(languages.get(code) or {})
    merged = dict(languages.get(code) or {})
    merged.update(entries)
    for dead in [k for k in merged if k not in known]:
        del merged[dead]
    languages[code] = merged

    block = ["UI_TRANSLATIONS = {"]
    for language, items in languages.items():
        block.append("    %s: {" % quoted(language))
        for english in sorted(items):
            block.append("        %s: %s," % (quoted(english),
                                              quoted(items[english])))
        block.append("    },")
    block.append("}")

    lines = io.open(LOCALES, encoding="utf-8", newline="").read().split("\n")
    text = "\n".join(lines[:span[0] - 1] + block + lines[span[1]:])
    ast.parse(text)
    io.open(LOCALES, "w", encoding="utf-8", newline="\n").write(text)

    covered = sum(1 for s in strings if s in merged)
    print("%s: %d -> %d strings, %.1f%% of the interface"
          % (code, before, len(merged), 100.0 * covered / len(strings)))
    return 0


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    what = sys.argv[1]
    if what == "list":
        do_list()
        return 0
    if what == "check":
        return do_check()
    if what == "merge":
        if len(sys.argv) < 4:
            sys.exit("usage: translations.py merge <code> <file.json>")
        return do_merge(sys.argv[2], sys.argv[3])
    sys.exit(__doc__)


sys.exit(main())
