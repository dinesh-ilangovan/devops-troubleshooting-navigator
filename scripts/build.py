#!/usr/bin/env python3
"""
build.py - compile src/*.json into standalone HTML.

Emits one file per technology plus a combined file. No hardcoded counts: the
build succeeds whenever validate.py passes, so contributing never breaks it.
"""
from pathlib import Path
import json, subprocess, sys, collections

ROOT = Path(__file__).resolve().parent.parent
SRC, APP, DIST = ROOT / "src", ROOT / "app", ROOT / "dist"

if subprocess.run([sys.executable, str(ROOT / "scripts/validate.py")]).returncode != 0:
    sys.exit("build aborted: validation failed")

tpl = (APP / "navigator.template.html").read_text(encoding="utf-8")
if tpl.count("__DATA__") != 1:
    sys.exit("template must contain exactly one __DATA__ marker")

runbooks = []
for f in sorted(SRC.glob("*.json")):
    runbooks += json.loads(f.read_text(encoding="utf-8"))

DIST.mkdir(exist_ok=True)


def emit(rows, name):
    payload = json.dumps(rows, separators=(",", ":"), ensure_ascii=False) \
                  .replace("</script>", "<\\/script>")
    out = DIST / name
    out.write_text(tpl.replace("__DATA__", payload), encoding="utf-8")
    kb = out.stat().st_size / 1024
    print(f"  {name:34s} {len(rows):4d} runbooks  {kb:8.1f} KB")
    return kb


print(f"\nbuilding from {len(runbooks)} runbooks")
by_tech = collections.defaultdict(list)
for r in runbooks:
    by_tech[r["technology"]].append(r)

for tech, rows in sorted(by_tech.items()):
    emit(rows, f"runbook-{tech.lower().replace(' ', '-')}.html")
total = emit(runbooks, "runbook-all.html")

if total > 3000:
    print(f"\n  warning: combined file is {total/1024:.1f} MB. Ship the per-technology "
          "files to anyone opening this on a jump host.")
print("\nbuild ok")
