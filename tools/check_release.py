#!/usr/bin/env python3
"""Compare this repo against the folder that actually gets published to Steam.

    mod/The Prussian Destiny                          <- this repo
    mod/My Mod Releases/The Prussian Destiny Release  <- what is uploaded

The two are kept in step by hand, which invites exactly one failure: publishing
a stale copy, so the workshop ships last version's content while the repo holds
the new one. Nothing in the game or in git notices. This does.

It also checks the reverse direction - that no development file (CLAUDE.md,
docs/, tools/, .claude/, .git/) has leaked into the release, because those
should never reach players.

Run before every upload:  python tools/check_release.py
Exit code 0 when the release is ready, 1 otherwise.
"""
import hashlib
import json
import os
import sys

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(MOD)
REL = os.path.join(BASE, "My Mod Releases",
                   os.path.basename(MOD) + " Release")

SHIP = ("in_game", "main_menu", ".metadata")
DEV_ONLY = {"CLAUDE.md", "docs", "tools", ".claude", ".git", ".gitignore"}


def walk(root):
    out = {}
    for top in SHIP:
        base = os.path.join(root, top)
        if not os.path.isdir(base):
            continue
        for dp, dn, fn in os.walk(base):
            dn[:] = [d for d in dn if d != "__pycache__"]
            for f in fn:
                p = os.path.join(dp, f)
                key = os.path.relpath(p, root).replace("\\", "/")
                out[key] = hashlib.md5(open(p, "rb").read()).hexdigest()
    return out


if not os.path.isdir(REL):
    print("FAIL - no release folder at:\n  %s" % REL)
    sys.exit(1)

dev, rel = walk(MOD), walk(REL)
if not dev:
    print("FAIL - scanned zero files in the repo; the SHIP list is wrong")
    sys.exit(1)

stale = sorted(k for k in set(dev) & set(rel) if dev[k] != rel[k])
missing = sorted(set(dev) - set(rel))
extra = sorted(set(rel) - set(dev))
leaked = sorted(k for k in rel if k.split("/")[0] in DEV_ONLY)

print("repo: %d shippable files | release: %d" % (len(dev), len(rel)))
print()
for label, items in (("STALE in the release", stale),
                     ("MISSING from the release", missing),
                     ("EXTRA in the release", extra),
                     ("DEVELOPMENT FILES LEAKED", leaked)):
    print("%-28s %d" % (label, len(items)))
    for k in items[:15]:
        print("      %s" % k)
    if len(items) > 15:
        print("      ... and %d more" % (len(items) - 15))

# The version field drifts because nothing forces it. Report both.
print()
versions = {}
for label, root in (("repo", MOD), ("release", REL)):
    p = os.path.join(root, ".metadata", "metadata.json")
    try:
        versions[label] = json.loads(open(p, "rb").read().decode("utf-8-sig")).get("version")
    except Exception as exc:
        versions[label] = "unreadable (%s)" % exc
print("metadata version - repo: %s | release: %s" % (versions["repo"], versions["release"]))
if versions["repo"] != versions["release"]:
    print("  the two disagree; they should match before an upload")
print("  (this field is not checked against the Steam page - confirm by hand)")

bad = bool(stale or missing or extra or leaked)
print()
print("RESULT: %s" % ("release is NOT ready" if bad else "release matches the repo"))
sys.exit(1 if bad else 0)
