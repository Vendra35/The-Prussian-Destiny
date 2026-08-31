#!/usr/bin/env python3
"""Check every dated gate against the era it actually belongs to.

This exists because of a real mistake, made 2026-08-31: the Bohemian disaster
was gated at 1600-1645 and 1725-1775, chosen from the real calendar, when the
situation it was written to open cannot start before 1522 or 1648. Both windows
sat roughly 78 years too late, so the crisis could only ever have arrived once
the story was over. Nothing errors on that. A date that is historically perfect
and mechanically dead looks exactly like one that works.

**This mod's calendar is shifted.** It tells the 1740-1866 Prussian story across
1450-1640 or 1520-1755 depending on the timeline rule. Content written for it
has to be checked against the MOD's window, not history's, and the two look
identical in a diff.

    python tools/check_dates.py

The first version of this tool declared ONE window per game rule and reported
12 problems, 11 of them false: it was applying the Ascension's window to the
Ambition's dates. The mod is a CHAIN of eras and the tool has to know that.
Dates are attributed by the block they sit in, not the file, because all three
end triggers live in one file.

Advisory, not a harness check: the windows are declared by hand from measured
line references, so this reports and ranks rather than gating a build.
"""
import glob
import os
import re
import sys

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Every number measured, with where. Update these when the chain moves - they
# are the entire basis of the tool.
ERAS = {
    "ambition": {
        "PD_timeline_frontloaded": (1450, 1500),
        "PD_timeline_strict_historical": (1450, 1525),
        "why": "opens from 1450 (PD_events.txt:15); failsafe 1495/1520 "
               "(brandenburg_rise.txt:248,253); the 'TEU destroyed by other' "
               "clause closes it at 1500/1525 (PD_scripted_triggers.txt:42,46)",
    },
    "ascension": {
        "PD_timeline_frontloaded": (1522, 1640),
        "PD_timeline_strict_historical": (1648, 1755),
        "why": "activates from 1522.3.9 / 1648.1.1 (PD_events.txt:1007,1016); "
               "auto-conquest failsafe closes the era at 1632 / 1745 "
               "(the_prussian_ascension.txt:254,259)",
    },
    "blood_and_iron": {
        "PD_timeline_frontloaded": (1638, 1900),
        "PD_timeline_strict_historical": (1751, 1900),
        "why": "opens from 1638 / 1751 (the_blood_and_iron.txt:41,46); no "
               "closing date, it ends on its own trigger",
    },
}

# Which era a block belongs to. Keys are matched against the enclosing
# top-level block name first, then the file name.
BLOCK_ERA = {
    "prussian_ambition_end_trigger": "ambition",
    "prussian_ascension_end_trigger": "ascension",
    "blood_and_iron_end_trigger": "blood_and_iron",
}
FILE_ERA = {
    "brandenburg_rise.txt": "ambition",
    "the_prussian_ascension.txt": "ascension",
    "the_blood_and_iron.txt": "blood_and_iron",
    # The disaster is written to open the Ascension, so that is the window it
    # has to sit inside - the whole reason this tool exists.
    "PD_bohemian_estates_crisis.txt": "ascension",
}

DATE = re.compile(r"current_date\s*[<>]=?\s*(\d{3,4})\.\d+\.\d+")
RULE = re.compile(r"has_game_rule\s*=\s*(PD_timeline_\w+)")
TOP = re.compile(r"^([A-Za-z_][A-Za-z_0-9.]*)\s*=\s*\{")
LOOKBACK = 6          # PD pairs rule and date inside one AND block


def scan():
    rows = []
    files = sorted(glob.glob(os.path.join(MOD, "in_game", "**", "*.txt"),
                             recursive=True)
                   + glob.glob(os.path.join(MOD, "main_menu", "**", "*.txt"),
                               recursive=True))
    for path in files:
        base = os.path.basename(path)
        lines = open(path, "rb").read().decode("utf-8", "replace").split("\n")
        block = None
        for n, line in enumerate(lines, 1):
            t = TOP.match(line)
            if t:
                block = t.group(1)
            if line.lstrip().startswith("#"):
                continue
            m = DATE.search(line)
            if not m:
                continue
            rule = None
            for back in range(1, LOOKBACK + 1):
                if n - back - 1 < 0:
                    break
                prev = lines[n - back - 1]
                if prev.lstrip().startswith("#"):
                    continue
                r = RULE.search(prev)
                if r:
                    rule = r.group(1)
                    break
            era = BLOCK_ERA.get(block) or FILE_ERA.get(base)
            rows.append((os.path.relpath(path, MOD), n, int(m.group(1)),
                         rule, era, line.strip()))
    return rows, len(files)


rows, nfiles = scan()
print("PD dated-gate review")
print("scanned %d .txt files, found %d dated gates\n" % (nfiles, len(rows)))
if not rows:
    print("FAIL - no dated gates found at all; the pattern is wrong, not the mod")
    sys.exit(1)

for era in ("ambition", "ascension", "blood_and_iron"):
    e = ERAS[era]
    print("%-15s frontloaded %d..%-6d strict %d..%d"
          % (era,
             e["PD_timeline_frontloaded"][0], e["PD_timeline_frontloaded"][1],
             e["PD_timeline_strict_historical"][0],
             e["PD_timeline_strict_historical"][1]))
    print("                %s" % e["why"])
print()

outside, unchecked = [], []
for rel, n, year, rule, era, text in rows:
    if era and rule:
        lo, hi = ERAS[era][rule]
        if not (lo <= year <= hi):
            outside.append((rel, n, year, era, rule, lo, hi, text))
    else:
        unchecked.append((rel, n, year, era or "-", rule or "-", text))

print("OUTSIDE their era: %d" % len(outside))
for rel, n, year, era, rule, lo, hi, text in outside:
    print("   %s:%d" % (rel, n))
    print("       %s   ->  %d under %s/%s is %d..%d"
          % (text, year, era, rule.replace("PD_timeline_", ""), lo, hi))
print()

print("NOT CHECKED: %d  (no era, or no timeline rule nearby)" % len(unchecked))
print("   Not wrong - DHE and ordinary event windows live outside the chain.")
print("   But each is a date nothing is verifying; skim them when the chain moves.")
for rel, n, year, era, rule, text in unchecked[:20]:
    print("   %-52s %s" % ("%s:%d" % (rel, n), text[:48]))
if len(unchecked) > 20:
    print("   ... and %d more" % (len(unchecked) - 20))

print()
print("RESULT: %s"
      % ("%d gate(s) outside their era" % len(outside) if outside
         else "every era-attributed date sits inside its window"))
sys.exit(1 if outside else 0)
