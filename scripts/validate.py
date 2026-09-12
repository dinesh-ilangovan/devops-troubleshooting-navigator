#!/usr/bin/env python3
"""
validate.py - enforce the rules in SCHEMA.md.

No hardcoded counts. Adding a runbook must never break the build; shipping a
bad one always must.
"""
from pathlib import Path
import json, re, sys, collections

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

TIERS = {"verified", "documented", "reference"}
RISKS = {"safe", "state", "destructive"}
PLACEHOLDER = re.compile(r"\{([a-z0-9_]+)\}")

errors, warnings = [], []


def err(rid, msg):
    errors.append(f"{rid}: {msg}")


def warn(rid, msg):
    warnings.append(f"{rid}: {msg}")


def check_runbook(r, seen_ids):
    rid = r.get("id") or "<missing id>"

    if not r.get("id"):
        err(rid, "missing id")
    elif r["id"] in seen_ids:
        err(rid, "duplicate id")
    seen_ids.add(r.get("id"))

    for f in ("tier", "technology", "title", "summary"):
        if not r.get(f):
            err(rid, f"missing {f}")

    tier = r.get("tier")
    if tier not in TIERS:
        err(rid, f"tier must be one of {sorted(TIERS)}, got {tier!r}")
        return

    # --- provenance, by tier -------------------------------------------------
    if tier == "verified":
        for f in ("verified_on", "verified_against", "verified_by"):
            if not r.get(f):
                err(rid, f"tier 'verified' requires {f}")
        d = r.get("verified_on", "")
        if d and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            err(rid, f"verified_on must be YYYY-MM-DD, got {d!r}")
    if tier == "documented" and not r.get("source"):
        err(rid, "tier 'documented' requires a source URL")
    if tier == "reference":
        for f in ("import_source", "license", "attribution"):
            if not r.get(f):
                err(rid, f"tier 'reference' requires {f}")
        for f in ("steps", "causes", "signals"):
            if r.get(f):
                err(rid, f"tier 'reference' must not carry {f} - it is a lookup card, "
                         "not guidance")
        return

    if not r.get("aliases"):
        warn(rid, "no aliases - it will only be findable by its exact title")

    # --- steps ---------------------------------------------------------------
    steps = r.get("steps") or []
    if not steps:
        err(rid, "no steps")
    declared = {i["key"] for i in r.get("inputs", []) if isinstance(i, dict) and "key" in i}
    cause_ids = {c.get("id") for c in r.get("causes", []) if isinstance(c, dict)}

    for n, s in enumerate(steps, 1):
        tag = f"{rid} step {n}"
        cmd = s.get("cmd", "")
        if not cmd:
            err(tag, "missing cmd")
        if not s.get("title"):
            err(tag, "missing title")
        if not s.get("look"):
            err(tag, "missing 'look' - a step that does not say what the output "
                     "means is just a cheat sheet line")

        risk = s.get("risk")
        if risk not in RISKS:
            err(tag, f"risk must be one of {sorted(RISKS)}, got {risk!r}")
        elif risk in ("state", "destructive") and not (s.get("note") or "").strip():
            err(tag, f"risk '{risk}' requires a note explaining the consequence")

        for p in PLACEHOLDER.findall(cmd):
            if p not in declared:
                err(tag, f"placeholder {{{p}}} is not declared in inputs")

        for sig in s.get("signals", []):
            try:
                re.compile(sig.get("match", ""))
            except re.error as e:
                err(tag, f"signal regex does not compile: {e}")
            goto = sig.get("goto", "")
            if goto.startswith("cause:"):
                if goto[6:] not in cause_ids:
                    err(tag, f"signal goto {goto!r} has no matching cause id")
            elif goto.startswith("step:"):
                if not (goto[5:].isdigit() and 1 <= int(goto[5:]) <= len(steps)):
                    err(tag, f"signal goto {goto!r} is out of range")
            elif goto:
                err(tag, f"signal goto must be 'cause:<id>' or 'step:<n>', got {goto!r}")

    # --- causes --------------------------------------------------------------
    for c in r.get("causes", []):
        for f in ("id", "cause", "fix"):
            if not c.get(f):
                err(rid, f"cause is missing {f}")

    if not r.get("verify"):
        warn(rid, "no verify section - the engineer has no way to know they are done")


def main():
    if not SRC.is_dir():
        sys.exit(f"No src/ directory at {SRC}")

    files = sorted(SRC.glob("*.json"))
    if not files:
        sys.exit(f"No JSON files in {SRC}")

    seen_ids, all_rb = set(), []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{f.name}: invalid JSON - {e}")
            continue
        if not isinstance(data, list):
            errors.append(f"{f.name}: top level must be an array")
            continue
        for r in data:
            all_rb.append(r)
            check_runbook(r, seen_ids)

    # --- cross-runbook: identical procedures ---------------------------------
    sigs = collections.defaultdict(list)
    for r in all_rb:
        if r.get("tier") == "reference" or not r.get("steps"):
            continue
        key = (r.get("technology"),
               tuple(re.sub(r"\s+", " ", s.get("cmd", "").strip().lower())
                     for s in r["steps"]))
        sigs[key].append(r.get("id"))
    for (tech, _), ids in sigs.items():
        if len(ids) > 1:
            errors.append(
                f"{tech}: {len(ids)} runbooks share an identical command sequence "
                f"({', '.join(map(str, ids[:5]))}{'...' if len(ids) > 5 else ''}) - "
                "merge them, or give each a step whose output differs")

    tiers = collections.Counter(r.get("tier") for r in all_rb)
    stale = [r.get("id") for r in all_rb if r.get("tier") == "verified"
             and r.get("verified_on", "9999") < "2026-03-01"]

    print(f"files      {len(files)}")
    print(f"runbooks   {len(all_rb)}  " +
          "  ".join(f"{k}={v}" for k, v in sorted(tiers.items()) if k))
    if stale:
        print(f"stale      {len(stale)} verified runbooks older than 6 months")
    for w in warnings[:25]:
        print(f"  warn  {w}")
    if len(warnings) > 25:
        print(f"  ... and {len(warnings)-25} more warnings")

    if errors:
        print(f"\nFAILED with {len(errors)} error(s):")
        for e in errors[:60]:
            print(f"  {e}")
        if len(errors) > 60:
            print(f"  ... and {len(errors)-60} more")
        sys.exit(1)
    print("\nPASSED")


if __name__ == "__main__":
    main()
