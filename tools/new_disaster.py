#!/usr/bin/env python3
"""Disaster scaffold generator - the boilerplate half, with the traps baked in.

Writing this mod's first disaster surfaced three failures that produce nothing
in any log, and a scaffolder is the right place to make them impossible:

  1. **The panel and icon are found by the disaster's KEY, not by the filename
     the key sits in.** vanilla savonarola.txt holds savonarola_disaster and
     ships savonarola_disaster.gui / .dds. Name either wrong and the panel is
     simply never loaded - no error, no missing texture, just the default panel
     where yours should be. This mod shipped exactly that for an afternoon.
  2. **Two art slots, two formats**, and the illustration is an OPAQUE banner -
     never commission one with a magenta key, which belongs to icons only.
  3. **Dates must be checked against the MOD's window, not history's.** This
     mod's calendar is shifted; see tools/check_dates.py.

Usage:
    python tools/new_disaster.py <key> "<Display Name>"

The skeleton is INERT: can_start carries `always = no`, so a generated disaster
never fires until an author removes it. A scaffold can land in the repo without
creating a test debt.

What it does NOT do: triggers, modifiers, events, design. Those are authoring
work under the citation rule in CLAUDE.md.
"""
import os
import re
import sys

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DISASTER = '''\
# {name}
#
# SCAFFOLD - inert until the `always = no` below is removed.
#
# Design note first, please: put the why in docs/, the way
# docs/BOHEMIA-DISASTER.md does. A disaster that weakens somebody is content a
# player is entitled to be suspicious of, so the reasoning is part of the work.

{key} = {{
\t# ART: both files are named after the KEY above, not after this file.
\t# Illustration  in_game/gfx/interface/illustrations/disaster/{key}.dds
\t#               1080x440, 11 mips, DXT1 - an OPAQUE banner, no magenta key.
\t# Icon          main_menu/gfx/interface/icons/disasters/{key}.dds
\t#               128x128, 8 mips, DXT5, 22000 bytes - magenta key IS correct
\t#               here. tools/art_to_dds.py does both.
\t# Left commented until the file exists: pointing at a missing one draws
\t# nothing, silently. verify_pd.py checks both.
\t#image = "gfx/interface/illustrations/disaster/{key}.dds"

\tmonthly_spawn_chance = monthly_spawn_chance_unique

\tfire_only_once = yes

\tcan_start = {{
\t\t# REMOVE THIS LINE to arm the disaster.
\t\talways = no

\t\t# Prefer land to tags - `owns = location:x` follows the crown wherever it
\t\t# goes, `tag = X` stops working the moment somebody is annexed.
\t\t#
\t\t# Vanilla's own guards (turmoil_in_brandenburg.txt:11-12):
\t\tin_civil_war = no
\t\thas_any_active_disaster = no
\t\t#
\t\t# DATES: check them with tools/check_dates.py before you trust them.
\t\t# This mod tells the 1740-1866 story across 1450-1640 or 1520-1755, so a
\t\t# historically perfect year can be mechanically dead and look identical.
\t}}

\tcan_end = {{
\t\t{key}_end_trigger = yes
\t}}

\t# Every tag must appear in docs/EU5-Vanilla-Script-Docs/modifiers.log, whose
\t# format is `Tag: name, Categories: ...` - NOT the `## name` of triggers.log.
\tmodifier = {{
\t}}

\ton_start = {{
\t}}

\ton_monthly = {{
\t}}

\ton_end = {{
\t}}
}}
'''

END_TRIGGER = '''
# Vanilla's pattern (turmoil_in_brandenburg_end_trigger, disaster_triggers.txt:707):
# counters moved by the player's choices, and it ends when one crosses its
# threshold. Two counters rather than one makes both answers real.
{key}_end_trigger = {{
\tcustom_tooltip = {{
\t\ttext = {key}_end_tt
\t\talways = no
\t}}
}}
'''

PANEL = '''\
# {name} - disaster panel.
# The FILENAME MUST BE THE DISASTER KEY: the engine looks it up by key, and a
# differently named file is never loaded, with no error anywhere.
disaster_panel = {{

\tblockoverride "main_image" {{}}

\tblockoverride "disaster_secondary_tab" {{
\t\tmargin_top = 10
\t\tspacing = 5

\t\t# The card stack the situation panels settled on, per
\t\t# ../1066 Test Mod/docs/SITUATION-CRAFT.md: history, live state, what the
\t\t# player can do, then how it ends. Add cards above this one; the End
\t\t# Requirements card below is vanilla's own and wants to stay last.
\t\tdisaster_card_expandable = {{
\t\t\tblockoverride "header_button_onclick" {{
\t\t\t\tonclick = "[LateralView.Vars.Toggle( '{key}_history_toggled' )]"
\t\t\t}}
\t\t\tblockoverride "header_text" {{
\t\t\t\ttext = "{key}_card_history"
\t\t\t}}
\t\t\tblockoverride "header_icon" {{
\t\t\t\ttexture = "gfx/interface/icons/events/history.dds"
\t\t\t}}
\t\t\tblockoverride "bottom_content" {{
\t\t\t\ttext_multi = {{
\t\t\t\t\tmargin = {{ 15 10 }}
\t\t\t\t\tlayoutpolicy_horizontal = expanding
\t\t\t\t\tmax_width = 500
\t\t\t\t\tautoresize = yes
\t\t\t\t\ttext = "{key}_history_body"
\t\t\t\t}}
\t\t\t}}
\t\t\tblockoverride "bottom_content_onclick" {{
\t\t\t\tvisible = "[LateralView.Vars.Exists( '{key}_history_toggled' )]"
\t\t\t}}
\t\t\tblockoverride "icon_replace_visible_yes" {{
\t\t\t\tvisible = "[LateralView.Vars.Exists( '{key}_history_toggled' )]"
\t\t\t}}
\t\t\tblockoverride "icon_replace_visible_not" {{
\t\t\t\tvisible = "[Not(LateralView.Vars.Exists( '{key}_history_toggled' ))]"
\t\t\t}}
\t\t}}

\t\t# Vanilla's End Requirements card, verbatim from reform_society.gui.
\t\tdisaster_card_expandable = {{
\t\t\tblockoverride "header_button_onclick" {{
\t\t\t\tonclick = "[LateralView.Vars.Toggle( 'requirements_toggled' )]"
\t\t\t}}
\t\t\tblockoverride "header_text" {{
\t\t\t\ttext = "END_REQUIREMENTS"
\t\t\t}}
\t\t\tblockoverride "header_icon" {{
\t\t\t\ttexture = "gfx/interface/icons/disasters/end_requirements_green.dds"
\t\t\t}}
\t\t\tblockoverride "bottom_content" {{
\t\t\t\tTooltipRequirementsList = {{
\t\t\t\t\ttextcontext = "[DisasterView.GetDisaster.GetType.GetEndConditions]"
\t\t\t\t}}
\t\t\t}}
\t\t\tblockoverride "bottom_content_onclick" {{
\t\t\t\tvisible = "[LateralView.Vars.Exists( 'requirements_toggled' )]"
\t\t\t}}
\t\t\tblockoverride "icon_replace_visible_yes" {{
\t\t\t\tvisible = "[LateralView.Vars.Exists( 'requirements_toggled' )]"
\t\t\t}}
\t\t\tblockoverride "icon_replace_visible_not" {{
\t\t\t\tvisible = "[Not(LateralView.Vars.Exists( 'requirements_toggled' ))]"
\t\t\t}}
\t\t}}
\t}}

\tblockoverride "disaster_main_content_subheader" {{}}

\tblockoverride "subheader_content"{{
\t\thbox = {{
\t\t\tusing = layoutpolicy_expanding
\t\t\twidget = {{
\t\t\t\tlayoutpolicy_horizontal = expanding
\t\t\t\tsize = {{ -1 40 }}
\t\t\t}}
\t\t}}
\t}}
}}
'''

LOC = [
    ("{key}", "{name}"),
    ("{key}_desc",
     "PLACEHOLDER. Short and in-world. The engine reads this key in places far "
     "narrower than the panel, so keep mechanics on the cards where they can be "
     "live instead of a paragraph that ages."),
    ("{key}_end_tt", "PLACEHOLDER - what ends this, in the player's words"),
    ("{key}_card_history", "Historical Context"),
    ("{key}_history_body",
     "PLACEHOLDER. What actually happened, with dates. This card is why a "
     "player believes the crisis is real rather than invented."),
]


def depth(text):
    d = 0
    for ln in text.split("\n"):
        c = re.sub(r'"[^"]*"', '', ln.split("#")[0])
        d += c.count("{") - c.count("}")
    return d


def main():
    argv = sys.argv[1:]
    if len(argv) != 2:
        print(__doc__)
        return 2
    key, name = argv
    if not re.match(r"^[A-Za-z_][A-Za-z_0-9]*$", key):
        print("FAIL - '%s' is not a usable key" % key)
        return 1

    dis = os.path.join(MOD, "in_game", "common", "disasters", key + ".txt")
    gui = os.path.join(MOD, "in_game", "gui", "panels", "disaster", key + ".gui")
    trg = os.path.join(MOD, "in_game", "common", "scripted_triggers",
                       "PD_scripted_triggers.txt")
    loc = os.path.join(MOD, "main_menu", "localization", "english",
                       "PD_l_english.yml")

    for p in (dis, gui):
        if os.path.exists(p):
            print("FAIL - %s already exists" % os.path.relpath(p, MOD))
            return 1

    body = DISASTER.format(key=key, name=name)
    panel = PANEL.format(key=key, name=name)
    end = END_TRIGGER.format(key=key)
    for label, text in (("disaster", body), ("panel", panel), ("trigger", end)):
        if depth(text) != 0:
            print("FAIL - generated %s is unbalanced (%+d)" % (label, depth(text)))
            return 1

    os.makedirs(os.path.dirname(dis), exist_ok=True)
    os.makedirs(os.path.dirname(gui), exist_ok=True)
    # .txt takes a BOM and this repo's CRLF; .gui takes neither.
    open(dis, "wb").write(b"\xef\xbb\xbf" + body.replace("\n", "\r\n").encode("utf-8"))
    open(gui, "wb").write(panel.encode("utf-8"))

    raw = open(trg, "rb").read()
    t = raw.decode("utf-8-sig")
    open(trg, "wb").write(b"\xef\xbb\xbf"
                          + (t + end.replace("\n", "\r\n")).encode("utf-8"))

    raw = open(loc, "rb").read()
    lines = raw.decode("utf-8-sig").split("\r\n")
    while lines and lines[-1] == "":
        lines.pop()
    lines.append("")
    lines.append(" # --- %s (scaffold) ---" % name)
    for k, v in LOC:
        lines.append(' %s: "%s"' % (k.format(key=key), v.format(key=key, name=name)))
    lines.append("")
    open(loc, "wb").write(b"\xef\xbb\xbf" + "\r\n".join(lines).encode("utf-8"))

    print("created, INERT (can_start carries `always = no`):")
    for p in (dis, gui):
        print("   %s" % os.path.relpath(p, MOD))
    print("   %s  (+ %s_end_trigger)" % (os.path.relpath(trg, MOD), key))
    print("   %s  (+ %d keys)" % (os.path.relpath(loc, MOD), len(LOC)))
    print()
    print("still needed, both named after the KEY:")
    print("   in_game/gfx/interface/illustrations/disaster/%s.dds" % key)
    print("       1080x440, 11 mips, DXT1 - opaque banner, NO magenta key")
    print("   main_menu/gfx/interface/icons/disasters/%s.dds" % key)
    print("       128x128, 8 mips, DXT5, 22000 bytes - magenta key IS correct")
    print("   tools/art_to_dds.py converts both.")
    print()
    print("then: python tools/verify_pd.py  and  python tools/check_dates.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
