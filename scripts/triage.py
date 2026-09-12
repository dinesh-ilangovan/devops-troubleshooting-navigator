#!/usr/bin/env python3
"""
triage.py - collapse the generated scenario set into distinct diagnostic procedures.

Reads every src/*.json, groups scenarios by their command sequence, and writes:

  build/procedures.json  one entry per distinct command sequence, with the
                         scenarios that collapsed into it
  build/worklist.csv     verification queue, highest-value procedure first
  build/report.md        human-readable summary of what collapsed and why

Nothing is deleted. This tells you what to verify and in what order.
"""
from pathlib import Path
import json, csv, hashlib, re, collections, sys

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "build"

# Commands that appear in almost every procedure and therefore carry no
# diagnostic signal on their own. A procedure made only of these is generic.
GENERIC = {
    "kubectl get pod <pod> -n <namespace> -o wide",
    "kubectl describe pod <pod> -n <namespace>",
    "kubectl get events -n <namespace> --sort-by=.lastTimestamp",
    "docker ps -a",
    "docker inspect <container>",
    "docker logs <container> --tail=200",
}

RISK_ORDER = {"DESTRUCTIVE": 3, "CHANGES STATE": 2, "CHANGES LOCAL": 2,
              "SENSITIVE READ": 1, "READ ONLY": 0}


def norm(cmd: str) -> str:
    """Normalise a command so trivial spacing/placeholder differences collapse."""
    c = cmd.strip().lower()
    c = re.sub(r"<[^>]+>", "<x>", c)          # all placeholders equivalent
    c = re.sub(r"--tail=\d+", "--tail=<n>", c)
    c = re.sub(r"\s+", " ", c)
    return c


def load():
    rows = []
    for f in sorted(SRC.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        for s in data:
            s.setdefault("_file", f.name)
            rows.append(s)
    return rows


def signature(s):
    cmds = [norm(x.get("command", "")) for x in s.get("steps", [])]
    return tuple(cmds)


def main():
    rows = load()
    if not rows:
        sys.exit(f"No scenarios found in {SRC}")

    groups = collections.defaultdict(list)
    for s in rows:
        groups[signature(s)].append(s)

    procedures = []
    for sig, members in groups.items():
        head = members[0]
        distinct_cmds = [c for c in sig if c not in {norm(g) for g in GENERIC}]
        risk = max((RISK_ORDER.get(x.get("risk", "READ ONLY"), 0)
                    for m in members for x in m.get("steps", [])), default=0)
        procedures.append({
            "proc_id": "p-" + hashlib.sha1("|".join(sig).encode()).hexdigest()[:8],
            "technology": head.get("technology") or head.get("module") or "?",
            "category": head.get("category", ""),
            "commands": list(sig),
            "step_count": len(sig),
            "specific_step_count": len(distinct_cmds),
            "collapsed_count": len(members),
            "max_risk": risk,
            "representative_title": head.get("title", ""),
            "collapsed_titles": sorted(m.get("title", "") for m in members),
            "collapsed_ids": sorted(m.get("id", "") for m in members),
            "generic_only": len(distinct_cmds) == 0,
        })

    # Ranking: procedures that swallowed many distinct symptoms are the worst
    # offenders and the highest-value things to split and verify first.
    procedures.sort(key=lambda p: (-p["collapsed_count"], -p["max_risk"],
                                   p["specific_step_count"]))

    OUT.mkdir(exist_ok=True)
    (OUT / "procedures.json").write_text(
        json.dumps(procedures, indent=2, ensure_ascii=False), encoding="utf-8")

    with (OUT / "worklist.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["rank", "proc_id", "technology", "category",
                    "symptoms_collapsed", "steps", "specific_steps",
                    "generic_only", "action", "representative_title",
                    "first_command"])
        for i, p in enumerate(procedures, 1):
            if p["collapsed_count"] >= 10:
                action = "SPLIT - one sequence is covering too many symptoms"
            elif p["generic_only"]:
                action = "REWRITE - no symptom-specific command in the path"
            elif p["collapsed_count"] > 1:
                action = "MERGE or differentiate"
            else:
                action = "VERIFY on cluster"
            w.writerow([i, p["proc_id"], p["technology"], p["category"],
                        p["collapsed_count"], p["step_count"],
                        p["specific_step_count"], p["generic_only"], action,
                        p["representative_title"],
                        p["commands"][0] if p["commands"] else ""])

    total = len(rows)
    uniq = len(procedures)
    swallowed = sum(p["collapsed_count"] for p in procedures if p["collapsed_count"] >= 10)
    singles = sum(1 for p in procedures if p["collapsed_count"] == 1)
    generic = sum(1 for p in procedures if p["generic_only"])

    lines = [
        "# Triage report", "",
        f"- Scenarios in `src/`: **{total}**",
        f"- Distinct command sequences: **{uniq}**",
        f"- Collapse ratio: **{total/uniq:.1f} scenarios per real procedure**",
        f"- Sequences already unique (verify as-is): **{singles}**",
        f"- Sequences with no symptom-specific command: **{generic}**",
        f"- Scenarios sitting inside a 10+ way collision: **{swallowed}**", "",
        "## Worst collisions", "",
        "| symptoms | tech | first command | example titles |",
        "|---|---|---|---|",
    ]
    for p in procedures[:10]:
        ex = "; ".join(p["collapsed_titles"][:3])
        lines.append(f"| {p['collapsed_count']} | {p['technology']} | "
                     f"`{p['commands'][0] if p['commands'] else ''}` | {ex} |")
    lines += ["", "## What to do", "",
              "1. Work `worklist.csv` top-down.",
              "2. SPLIT rows first: those are symptoms sharing a path that cannot",
              "   distinguish them. Give each a command whose output differs.",
              "3. Everything you verify on a real cluster gets `verified_on`,",
              "   `verified_against` and `verified_by`. Nothing else ships as verified.",
              ""]
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"scenarios         {total}")
    print(f"real procedures   {uniq}")
    print(f"collapse ratio    {total/uniq:.1f}x")
    print(f"generic-only      {generic}")
    print(f"wrote             {OUT/'procedures.json'}, {OUT/'worklist.csv'}, {OUT/'report.md'}")


if __name__ == "__main__":
    main()
