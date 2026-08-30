# -*- coding: utf-8 -*-
"""Static verification for The Prussian Destiny.

Nothing here runs the game. These checks exist because this mod's failure mode
is silence: a missing localisation key prints its own name, a texture that is
not there draws nothing, and a reference to a tag that no longer exists throws
into the debug log once per location per redraw. Every one of those shipped at
some point without anyone noticing.

Discipline borrowed from the 1066 harness:
  * every check prints how many items it scanned
  * a check that finds NOTHING to scan FAILS - a silent zero is the exact
    failure this file exists to prevent
  * when the game finds something a check did not, add the check

Usage:  python tools/verify_pd.py
Exit code 0 when everything passes, 1 otherwise.
"""
import glob
import os
import re
import sys

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Detect the vanilla tree; probe a known FILE, never a directory, because an
# empty folder passes a directory test and makes every later lookup return a
# confident zero.
VANILLA_CANDIDATES = [
    r"E:\SteamLibrary\steamapps\common\Europa Universalis V\game",
    r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V\game",
    r"D:\SteamLibrary\steamapps\common\Europa Universalis V\game",
]
VANILLA = None
for cand in VANILLA_CANDIDATES:
    if os.path.isfile(os.path.join(cand, "in_game", "map_data", "definitions.txt")):
        VANILLA = cand
        break

# Formatting tags this mod and vanilla actually define. A tag outside this set
# makes pdx_text_formatter.cpp:807 complain and eats the word after it.
KNOWN_FORMAT_TAGS = {
    "G", "Y", "R", "T", "V", "N", "P", "L", "W", "S", "E", "H", "M",
    "bold", "italic", "underline",
    "color_red", "color_green", "color_yellow", "color_white", "color_gray",
    "color_grey", "color_blue", "color_gold",
    "subtle_name", "yellow_titles", "header_titles", "explanation_link",
    "high", "medium", "low", "weak", "flavor", "help", "instruction",
    "important_number", "overview_text", "warning", "placeholder", "mask",
}

# Blocks that the engine evaluates for every location on every redraw. A bare
# c:TAG in one of these is what filled the log when Prussia became the
# Confederation: the optional operator guards the LEFT side of a comparison,
# and a missing tag sits on the right. Use "tag = XXX", which compares a
# literal name and never resolves a scope, or a guarded scripted trigger.
HOT_BLOCKS = ("map_color", "secondary_map_color", "tooltip")

results = []


def record(name, scanned, failures, note=""):
    results.append((name, scanned, failures, note))


def read(path):
    return open(path, "rb").read().decode("utf-8", errors="replace")


def loc_value_lines(text):
    """Yield (lineno, value) for real localisation entries only.

    Lines whose first non-space character is '#' are YAML comments, not
    entries - scanning them reported a commented-out key as a broken
    formatting tag the first time this check ran.
    """
    for n, line in enumerate(text.split("\n"), 1):
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        m = re.match(r'\s*[A-Za-z_][A-Za-z_0-9.]*\s*:\s*(?:\d+\s+)?"(.*)"\s*\r?$', line)
        if m:
            yield n, m.group(1)


def rel(path):
    return os.path.relpath(path, MOD)


# ---------------------------------------------------------------- gather ----
mod_loc_files = sorted(glob.glob(os.path.join(
    MOD, "main_menu", "localization", "**", "*.yml"), recursive=True))
gui_files = sorted(glob.glob(os.path.join(
    MOD, "in_game", "gui", "**", "*.gui"), recursive=True))
situation_files = sorted(glob.glob(os.path.join(
    MOD, "in_game", "common", "situations", "*.txt")))

defined_keys = set()
for f in mod_loc_files:
    defined_keys.update(re.findall(
        r"^\s*([A-Za-z_][A-Za-z_0-9.]*)\s*:", read(f), re.M))
mod_key_count = len(defined_keys)

if VANILLA:
    for f in glob.glob(os.path.join(VANILLA, "**", "localization", "**", "*.yml"),
                       recursive=True):
        defined_keys.update(re.findall(
            r"^\s*([A-Za-z_][A-Za-z_0-9.]*)\s*:", read(f), re.M))


# ------------------------------------------------------------- 1. encoding --
def check_encoding():
    scanned, bad = 0, []
    targets = ([(f, "yml") for f in mod_loc_files] +
               [(f, "gui") for f in gui_files] +
               [(f, "txt") for f in glob.glob(
                   os.path.join(MOD, "in_game", "common", "**", "*.txt"),
                   recursive=True)])
    for path, kind in targets:
        scanned += 1
        raw = open(path, "rb").read()
        has_bom = raw[:3] == b"\xef\xbb\xbf"
        crlf = raw.count(b"\r\n")
        bare_lf = raw.count(b"\n") - crlf
        # .gui carries no BOM (vanilla ships 483 and only 49 have one);
        # everything else here does.
        if kind == "gui" and has_bom:
            bad.append("%s: .gui should not carry a BOM" % rel(path))
        if kind != "gui" and not has_bom:
            bad.append("%s: missing UTF-8 BOM" % rel(path))
        # Line endings are NOT a convention to enforce: 1198 of 1200 sampled
        # vanilla in_game/common .txt files are LF-only, so a CRLF rule here
        # would fail correct files. What does matter is a file that carries
        # BOTH, which means something edited it and got the endings wrong -
        # exactly what a careless regex line-replacement does.
        if crlf and bare_lf:
            bad.append("%s: mixed line endings (%d CRLF, %d bare LF) - something "
                       "edited this file without matching its existing endings"
                       % (rel(path), crlf, bare_lf))
        try:
            body = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            bad.append("%s: not valid UTF-8 (%s)" % (rel(path), exc))
            continue
        if body.count("{") != body.count("}"):
            bad.append("%s: braces unbalanced (%+d)"
                       % (rel(path), body.count("{") - body.count("}")))
    record("encoding + braces", scanned, bad)


# ------------------------------------------------------- 2. gui references --
def check_gui_references():
    keys_scanned, textures_scanned, bad = 0, 0, []
    roots = [os.path.join(MOD, d) for d in ("in_game", "main_menu")]
    if VANILLA:
        roots += [os.path.join(VANILLA, d)
                  for d in ("in_game", "main_menu", "loading_screen")]
    for path in gui_files:
        body = read(path)
        keys = set(re.findall(
            r'(?:^|\s)(?:text|tooltip)\s*=\s*"([A-Za-z_][A-Za-z_0-9.]*)"', body))
        keys |= set(re.findall(
            r"lowpriotextcontext\s*=\s*([A-Za-z_][A-Za-z_0-9.]*)", body))
        for k in sorted(keys):
            keys_scanned += 1
            if k not in defined_keys:
                bad.append("%s: loc key '%s' is not defined anywhere" % (rel(path), k))
        for tex in sorted(set(re.findall(
                r'(?:texture|progresstexture|noprogresstexture)\s*=\s*"(gfx/[^"]+)"',
                body))):
            textures_scanned += 1
            if not any(os.path.isfile(os.path.join(r, tex.replace("/", os.sep)))
                       for r in roots):
                bad.append("%s: texture '%s' not found" % (rel(path), tex))
    record("gui loc keys", keys_scanned, [b for b in bad if "loc key" in b])
    record("gui textures", textures_scanned, [b for b in bad if "texture" in b])


# ------------------------------------------------------------ 3. Show*Name --
def check_show_names():
    scanned, bad = 0, []
    for path in mod_loc_files + gui_files:
        for n, line in enumerate(read(path).split("\n"), 1):
            if line.lstrip().startswith("#"):
                continue
            for m in re.finditer(
                    r"Show([A-Za-z]+?)Name(?:WithNoTooltip)?\('([^']+)'\)", line):
                key = m.group(2)
                if key.startswith("<"):
                    continue
                scanned += 1
                if key not in defined_keys:
                    bad.append("%s:%d: Show%sName('%s') resolves to nothing, so the "
                               "raw key is printed"
                               % (rel(path), n, m.group(1), key))
    record("Show*Name references", scanned, bad)


# -------------------------------------------------------- 4. format tags ----
def check_format_tags():
    scanned, bad = 0, []
    for path in mod_loc_files:
        for n, value in loc_value_lines(read(path)):
            for tag in re.findall(r"#([A-Za-z_][A-Za-z_0-9]*)", value):
                scanned += 1
                if tag not in KNOWN_FORMAT_TAGS:
                    bad.append("%s:%d: unknown formatting tag '#%s' - most likely a "
                               "missing space after the tag letter"
                               % (rel(path), n, tag))
    record("loc formatting tags", scanned, bad)


# ------------------------------------------------- 5. hot-block tag safety --
def slice_block(text, header):
    """Return the body of a top-level '<header> = {' block, or None."""
    start = text.find("\t%s = {" % header)
    if start < 0:
        return None
    depth, i = 0, text.index("{", start)
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[start:j + 1]
    return None


def check_hot_block_tags():
    scanned, bad = 0, []
    for path in situation_files:
        body = read(path)
        for header in HOT_BLOCKS:
            block = slice_block(body, header)
            if block is None:
                continue
            scanned += 1
            for ref in sorted(set(re.findall(r"c:([A-Z]{3})", block))):
                bad.append("%s: %s names c:%s directly. These blocks run for every "
                           "location on every redraw, so a tag that no longer exists "
                           "throws each time. Use 'tag = %s' for equality, or a "
                           "country_exists-guarded scripted trigger for relations."
                           % (rel(path), header, ref, ref))
    record("situation hot blocks", scanned, bad)


# ------------------------------------------------- 6. treaty tooltip noise --
def event_walks_root(event_id):
    """Does this event's body reference ROOT?

    Keyed on ROOT alone, because that is what the measured error names. A bare
    prev inside an iterator resolves within that loop and is ordinary script;
    counting it here produced one false positive (pd_brandenburg.221, whose
    only prev sits inside every_subject).

    An event that walks ROOT must not be reached from a hidden treaty effect:
    hiding the call makes the treaty hover walk into the event, where ROOT is
    unbound, and every hover throws "Event target link 'root' returned an
    invalid object". Returns None when the event cannot be found.
    """
    for path in glob.glob(os.path.join(MOD, "in_game", "events", "**", "*.txt"),
                          recursive=True):
        body = read(path)
        start = body.find("%s = {" % event_id)
        if start < 0:
            continue
        depth, i = 0, body.index("{", start)
        for j in range(i, len(body)):
            if body[j] == "{":
                depth += 1
            elif body[j] == "}":
                depth -= 1
                if depth == 0:
                    block = body[start:j + 1]
                    return len(re.findall(r"\bROOT\b", block))
    return None


def check_treaty_event_tooltips():
    """A peace treaty's trigger_event must NOT sit inside hidden_effect.

    Measured 2026-08-30, the hard way. The visible form renders one cosmetic
    line in the treaty tooltip - "Country gets the Event '...'", because
    scope:winner is unbound while the deal is only being previewed. Wrapping
    the call in hidden_effect to remove that line made the hover walk into the
    event body instead, and every scope the event touches threw there
    (pd_brandenburg.307 -> PD_events.txt:2090 and :2098). The cosmetic line is
    much the cheaper of the two, so this check now runs one way only.

    Note what this check does NOT claim. Hovering these treaties also throws
    "Event target link 'scope'" on the treaty's own scope:winner / scope:loser
    lines, and "Event target link 'root'" inside pd_brandenburg.306. Both are
    older than any of this and are unaffected by hiding: reverting .306 to
    visible did not quiet it. Those belong to a separate problem - the effect
    blocks are written against scopes that only exist once the war is actually
    concluded - and want a redesign, not a tooltip trick.
    """
    scanned, bad = 0, []
    for path in sorted(glob.glob(os.path.join(
            MOD, "in_game", "common", "peace_treaties", "*.txt"))):
        depth, hidden_at = 0, None
        for n, line in enumerate(read(path).split("\n"), 1):
            if hidden_at is not None and depth < hidden_at:
                hidden_at = None
            if "hidden_effect" in line and "{" in line:
                hidden_at = depth + 1
            m = re.search(r"\btrigger_event\w*\s*=\s*([A-Za-z_][A-Za-z_0-9]*\.\d+)", line)
            if m and not line.lstrip().startswith("#"):
                scanned += 1
                if hidden_at is not None:
                    roots = event_walks_root(m.group(1))
                    bad.append("%s:%d: %s sits inside hidden_effect. That makes the "
                               "treaty hover walk into the event body (%s) and throw "
                               "there instead of rendering one harmless placeholder "
                               "line. Leave treaty trigger_event calls visible."
                               % (rel(path), n, m.group(1),
                                  "%d ROOT references" % roots if roots
                                  else "its own scopes"))
            depth += line.count("{") - line.count("}")
    record("peace treaty events", scanned, bad)


for fn in (check_encoding, check_gui_references, check_show_names,
           check_format_tags, check_hot_block_tags, check_treaty_event_tooltips):
    fn()

# ------------------------------------------------------------------ report --
print("The Prussian Destiny - static verification")
print("mod          : %s" % MOD)
print("vanilla      : %s" % (VANILLA or "NOT FOUND - reference checks degraded"))
print("loc keys     : %d in mod, %d including vanilla" % (mod_key_count, len(defined_keys)))
print("files        : %d loc, %d gui, %d situations"
      % (len(mod_loc_files), len(gui_files), len(situation_files)))
print()

failed = False
for name, scanned, failures, note in results:
    if scanned == 0:
        print("[FAIL] %-24s scanned 0 items - the check found nothing to look at"
              % name)
        failed = True
        continue
    if failures:
        print("[FAIL] %-24s %d scanned, %d problem(s)" % (name, scanned, len(failures)))
        for f in failures:
            print("         - %s" % f)
        failed = True
    else:
        print("[ ok ] %-24s %d scanned" % (name, scanned))

if VANILLA is None:
    print()
    print("Vanilla tree not found. Add its path to VANILLA_CANDIDATES; without it "
          "the reference checks cannot tell a missing key from a vanilla one.")

print()
print("RESULT: %s" % ("FAILED" if failed else "all checks passed"))
sys.exit(1 if failed else 0)
