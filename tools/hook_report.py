#!/usr/bin/env python3
"""Turn a failing harness run into a short Stop-hook message.

The hook used to dump the harness's last 20 lines. With a finding that has
eighteen instances those lines wrap into a wall that buries the point, and it
reappears every single turn until the finding is fixed. This keeps the signal -
which checks failed, how many problems, and the first few - and points at the
command for the rest.

Usage:  python tools/verify_mod.py 2>&1 | python tools/hook_report.py verify_mod.py
Reads the harness output on stdin, prints one JSON object on stdout.
"""
import json
import sys

SHOWN = 3

tool = sys.argv[1] if len(sys.argv) > 1 else "the harness"
lines = sys.stdin.read().split("\n")

result = [l.strip() for l in lines if l.strip().startswith("RESULT")]
failed = [l.strip() for l in lines if l.strip().startswith("[FAIL]")]
problems = [l.strip() for l in lines if l.strip().startswith("- ")]

parts = ["%s FAILED" % tool]
parts += result or ["(no RESULT line - the harness may have crashed)"]
parts += failed

if problems:
    parts.append("")
    parts += ["  " + p for p in problems[:SHOWN]]
    if len(problems) > SHOWN:
        parts.append("  ... and %d more. Full list: python tools/%s"
                     % (len(problems) - SHOWN, tool))

print(json.dumps({"systemMessage": "\n".join(parts)}))
