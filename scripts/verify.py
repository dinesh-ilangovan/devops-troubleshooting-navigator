#!/usr/bin/env python3
"""
verify.py - walk a runbook's steps, then mark it verified.

    python scripts/verify.py                    list what still needs verifying
    python scripts/verify.py k8s-oomkilled      walk that runbook and mark it

Prints each command, waits for you to run it, asks whether the 'look' line was
right. At the end it writes verified_on, verified_against and verified_by.
"""
from pathlib import Path
import json, sys, datetime, os

SRC = Path(__file__).resolve().parent.parent / "src"
WHO = os.environ.get("RUNBOOK_AUTHOR", "dinesh")


def load():
    out = []
    for f in sorted(SRC.glob("*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            out.append((f, r))
    return out


def listing():
    rows = load()
    pend = [(f, r) for f, r in rows if r.get("tier") != "verified"]
    done = len(rows) - len(pend)
    print(f"\n{done} of {len(rows)} verified. {len(pend)} to go.\n")
    tech = None
    for f, r in sorted(pend, key=lambda x: (x[1]["technology"], x[1]["id"])):
        if r["technology"] != tech:
            tech = r["technology"]
            print(f"  {tech}")
        print(f"    {r['id']:32s} {r['title'][:46]}")
    print("\n  python scripts/verify.py <id>\n")


def walk(rid):
    rows = load()
    hit = [(f, r) for f, r in rows if r["id"] == rid]
    if not hit:
        sys.exit(f"No runbook with id {rid!r}. Run with no arguments to list them.")
    path, rb = hit[0]

    print(f"\n{rb['title']}")
    print(f"{rb['technology']} · {len(rb['steps'])} steps")
    if rb.get("source"):
        print(f"docs: {rb['source']}")
    print("\nRun each command, compare what you see against the 'look' line.")
    print("Answer y if it was right, n if it needs fixing, q to stop.\n")

    problems = []
    for i, s in enumerate(rb["steps"], 1):
        risk = {"safe": "read only", "state": "CHANGES STATE",
                "destructive": "DESTRUCTIVE"}[s["risk"]]
        print("-" * 68)
        print(f"Step {i}/{len(rb['steps'])}  [{risk}]  {s['title']}")
        if s.get("note"):
            print(f"\n  ! {s['note']}")
        print(f"\n  $ {s['cmd']}")
        print(f"\n  Expect: {s['look']}")
        for sig in s.get("signals", []):
            print(f"    if output matches /{sig['match']}/ -> {sig['means']}")
        a = input("\n  Was that right? [y/n/q] ").strip().lower()
        if a == "q":
            print("\nStopped. Nothing was changed.")
            return
        if a != "y":
            what = input("  What was wrong? ").strip()
            problems.append(f"step {i} ({s['title']}): {what}")

    print("-" * 68)
    if problems:
        print("\nNot marking this verified. Fix these first:\n")
        for p in problems:
            print(f"  - {p}")
        print(f"\nEdit {path.name}, then run this again.\n")
        return

    against = input("\n  Version you tested against (e.g. Docker 27.2): ").strip()
    if not against:
        print("  A version is required. Nothing changed.")
        return
    who = input(f"  Your name [{WHO}]: ").strip() or WHO

    data = json.loads(path.read_text(encoding="utf-8"))
    for r in data:
        if r["id"] == rid:
            r["tier"] = "verified"
            r["verified_on"] = datetime.date.today().isoformat()
            r["verified_against"] = against
            r["verified_by"] = who
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    total = len(load())
    ver = sum(1 for _, r in load() if r.get("tier") == "verified")
    print(f"\n  Marked verified: {rid}")
    print(f"  {ver} of {total} verified.")
    print("\n  Run: python scripts/build.py\n")


if __name__ == "__main__":
    (walk(sys.argv[1]) if len(sys.argv) > 1 else listing())
