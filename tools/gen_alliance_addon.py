# -*- coding: utf-8 -*-
"""Generate in_game/common/scripted_relations/PD_alliance_addon.txt
-- vanilla's alliance relation repeated WHOLE under TRY_REPLACE:, with this
mod's alliance locks added at the end of offer_enabled and of
should_ai_offer_trigger. Everything else is the installed vanilla body.

    python tools/gen_alliance_addon.py            # write the file
    python tools/gen_alliance_addon.py --check    # compare, exit 1 on drift

WHY A GENERATOR. The file used to be a hand copy of an older vanilla body.
Checked 2026-09-14 against the installed alliance.txt (504 lines), it lacked
the ai_expansionist conquer-desire terms (alliance.txt:281, :385), the
CHALLENGER_BEYLIK -1000 of Rise of the Ottomans (:301, :362),
scope_country_can_join_coalition_against (:428) and the Protestant Union /
Catholic League -1000 (:499). TRY_REPLACE swaps the whole object, so every
campaign with this mod loaded ran without those rules and nothing said so.
Re-run this after every patch; --check reports when the patch moved vanilla.

WHY THE LOCKS. An alliance carries disallow_war = yes, so an AI protagonist
allied to a country it has to take can never attack it and its situation
never ends. That reason binds the AI and nobody else, so every lock tests
is_ai = yes (triggers.log:6087) and a human player picks their own allies.
tag = BRA / tag = PRU (triggers.log:10438, country scope) compare a name and
never resolve c:BRA / c:PRU, so they stay false once the tag has left the map
instead of throwing.
  Phase 1 -- while the_prussian_ambition is active, an AI Brandenburg may not
             ally anyone.
  Phase 2 -- while the_prussian_ascension is active, an AI Prussia may not
             ally the Emperor or anyone holding land in the regions it must
             take.

WHY is_situation_active. It is a global on/off (triggers.log:7604, Supported
Scopes: none; vanilla writes `is_situation_active = situation:X` 252 times,
country_interactions/hre.txt:1795 among them), true exactly while the
situation runs. Two earlier keys were each wrong:
  prussian_destiny_modifier_1 -- pd_brandenburg.10 grants it only under the
      Terminator and Historical buff rules, so under Vanilla (No Buffs) an AI
      Brandenburg had no lock at all.
  prussian_ambition_active / prussian_ascension_active -- pd_brandenburg.10
      and .299 set them without asking can_start, so a situation that never
      starts (the Teutonic Order already gone, brandenburg_rise.txt:6; Prussia
      already holding every target area, the_prussian_ascension.txt:7) left
      its flag set for good and the AI locked for the rest of the game. The
      modifier key carried the same risk.

WHY NOT allowed_alliance. prussian_destiny_modifier_1 carried
allowed_alliance = no. allowed_alliance is a boolean modifier
(00_modifier_types.txt:12955) that every country rank grants as yes
(country_ranks/00_default.txt:20), and vanilla never writes it as no anywhere;
the author recalls it not holding. The lock therefore lives here, where it can
be gated on is_ai.
"""
import os
import re
import sys

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(MOD, "in_game", "common", "scripted_relations", "PD_alliance_addon.txt")
REL = os.path.join("in_game", "common", "scripted_relations", "alliance.txt")
KEY = "alliance"
NL = "\n"
TAB = "\t"

# Same list as tools/verify_pd.py. Probe the FILE this generator reads, never a
# directory: an empty folder passes a directory test.
VANILLA_CANDIDATES = [
    r"E:\SteamLibrary\steamapps\common\Europa Universalis V\game",
    r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V\game",
    r"D:\SteamLibrary\steamapps\common\Europa Universalis V\game",
]


def vanilla_file():
    for cand in VANILLA_CANDIDATES:
        path = os.path.join(cand, REL)
        if os.path.isfile(path):
            return path
    raise SystemExit("gen_alliance_addon: vanilla %s not found; add the install to "
                     "VANILLA_CANDIDATES" % REL)


def block_span(text, name):
    """(start of the opening line, index of the matching closing brace)."""
    found = list(re.finditer(r"^[ \t]*%s\s*=\s*\{" % name, text, re.M))
    if len(found) != 1:
        raise SystemExit("gen_alliance_addon: expected one %s block in vanilla's %s, found %d "
                         "-- read the patch before regenerating" % (name, KEY, len(found)))
    depth, k = 1, found[0].end()
    in_comment = in_string = False
    while k < len(text):
        ch = text[k]
        if in_comment:
            in_comment = ch != NL
        elif in_string:
            in_string = ch != '"'
        elif ch == "#":
            in_comment = True
        elif ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return found[0].start(), k
        k += 1
    raise SystemExit("gen_alliance_addon: %s block in vanilla's %s never closes" % (name, KEY))


def indent(lines, depth):
    return [(TAB * depth + line) if line else "" for line in lines]


def ai_tag(side, tag):
    return [
        "scope:%s = {" % side,
        TAB + "tag = %s" % tag,
        TAB + "is_ai = yes",
        "}",
    ]


def phase1_lock(a, b):
    return [
        "NOT = {",
        TAB + "AND = {",
        TAB * 2 + "is_situation_active = situation:the_prussian_ambition",
        TAB * 2 + "OR = {",
    ] + indent(ai_tag(a, "BRA") + ai_tag(b, "BRA"), 3) + [
        TAB * 2 + "}",
        TAB + "}",
        "}",
    ]


def phase2_pair(prussia, other):
    return ["AND = {"] + indent(ai_tag(prussia, "PRU"), 1) + [
        TAB + "scope:%s = {" % other,
        TAB * 2 + "OR = {",
        TAB * 3 + "this = international_organization:hre.leader_country",
        TAB * 3 + "has_presence_in = region:north_german_region",
        TAB * 3 + "has_presence_in = area:prussia_area",
        TAB * 3 + "has_presence_in = area:silesia_area",
        TAB * 2 + "}",
        TAB + "}",
        "}",
    ]


def locks(a, b):
    lines = [
        "",
        "# --- The Prussian Destiny: alliance locks (tools/gen_alliance_addon.py) ---",
        "# They bind an AI protagonist only, and only while its situation runs. An",
        "# alliance forbids war between its members, so an AI allied to its own",
        "# targets would stall its situation for good; a human player picks their own",
        "# allies. tag = never resolves c:TAG.",
        "# Phase 1, the_prussian_ambition: an AI Brandenburg, with anyone at all.",
    ]
    lines += phase1_lock(a, b)
    lines += [
        "# Phase 2, the_prussian_ascension: an AI Prussia, and the Emperor or anyone",
        "# holding land it has to take.",
        "NOT = {",
        TAB + "AND = {",
        TAB * 2 + "is_situation_active = situation:the_prussian_ascension",
        TAB * 2 + "OR = {",
    ]
    lines += indent(phase2_pair(a, b), 3) + indent(phase2_pair(b, a), 3)
    lines += [
        TAB * 2 + "}",
        TAB + "}",
        "}",
    ]
    return lines


def insert_before_close(text, name, lines):
    _, close = block_span(text, name)
    line_start = text.rfind(NL, 0, close) + 1
    return text[:line_start] + NL.join(indent(lines, 2)) + NL + text[line_start:]


def generate():
    src = vanilla_file()
    text = open(src, encoding="utf-8-sig").read().replace("\r\n", NL)
    if len(re.findall(r"^%s\s*=\s*\{" % KEY, text, re.M)) != 1:
        raise SystemExit("gen_alliance_addon: %s has no single top-level %s block" % (src, KEY))
    # Later block first, so the earlier one's offsets stay valid.
    text = insert_before_close(text, "should_ai_offer_trigger", locks("first", "second"))
    text = insert_before_close(text, "offer_enabled", locks("actor", "recipient"))
    text = re.sub(r"^%s(\s*=\s*\{)" % KEY, r"TRY_REPLACE:%s\1" % KEY, text, count=1, flags=re.M)
    head = [
        "# GENERATED by tools/gen_alliance_addon.py from the installed vanilla",
        "# in_game/common/scripted_relations/alliance.txt -- do not edit by hand;",
        "# change the generator and re-run it, and re-run it after every patch.",
        "# Vanilla's alliance, whole, plus this mod's AI-only alliance locks at the",
        "# end of offer_enabled and should_ai_offer_trigger.",
        "",
    ]
    return NL.join(head) + text.rstrip(NL) + NL


def main():
    text = generate()
    if "--check" in sys.argv[1:]:
        cur = open(OUT, "rb").read() if os.path.isfile(OUT) else b""
        if cur.replace(b"\r\n", b"\n") != b"\xef\xbb\xbf" + text.encode("utf-8"):
            print("DIFFERS: %s is not what gen_alliance_addon.py generates from the "
                  "installed vanilla; re-run it" % os.path.relpath(OUT, MOD))
            sys.exit(1)
        print("%s matches the generator" % os.path.basename(OUT))
        return
    # BOM, and CRLF to match the working copy this repo keeps (core.autocrlf).
    data = b"\xef\xbb\xbf" + text.replace(NL, "\r\n").encode("utf-8")
    open(OUT, "wb").write(data)
    print("wrote %s (%d bytes, BOM, CRLF)" % (os.path.relpath(OUT, MOD), len(data)))


if __name__ == "__main__":
    main()
