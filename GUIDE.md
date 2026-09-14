# What to do, in order

Your repo: `C:\Users\DineshI1\Desktop\devops-troubleshooting-navigator-github-ready`

Do these in order. Do not skip ahead. Each step ends with something you can look at.

---

## Step 1 — See the real number (15 minutes)

Copy `scripts/triage.py` from this folder into your repo's `scripts\` folder.

```powershell
cd C:\Users\DineshI1\Desktop\devops-troubleshooting-navigator-github-ready
git checkout -b v2-rebuild
python scripts\triage.py
```

It writes `build\worklist.csv`. Open it in Excel.

**Look at row 1.** It lists 115 different symptoms that all share the same four
commands. Read those 115 titles. Among them are "Container exits with code 126"
and "Container exits with code 127" — different causes, identical guidance.

That is the problem, and it is the only reason for everything below.

---

## Step 2 — Replace the two scripts (10 minutes)

Copy from this folder into your repo, overwriting:

- `scripts\validate.py`
- `scripts\build.py`

Also copy in `SCHEMA.md` at the repo root.

**Why:** your current `validate.py` reads `scripts/data/` which does not exist, so
it crashes on a fresh clone. And both scripts hardcode `961`, `520`, `441`, `5766`,
`exactly 3 branches`, `exactly 6 walkthroughs`. That means **the build breaks the
moment anyone adds a runbook** — including you. The new ones check rules, not counts.

```powershell
python scripts\validate.py
```

It will fail loudly against your old data. That is correct. Do not try to fix the
old data to make it pass.

---

## Step 3 — Start the new source, empty (5 minutes)

```powershell
mkdir src-v2
git mv src src-old
git mv src-v2 src
```

Copy these three files from this folder into the new `src\`:

- `kubernetes.json` — 3 runbooks, marked `verified`
- `docker.json` — 4 runbooks, marked `documented`
- `git.json` — 2 runbooks, marked `verified`

```powershell
python scripts\build.py
```

You get `dist\runbook-kubernetes.html`, `runbook-docker.html`, `runbook-git.html`
and `runbook-all.html`. The combined one is 59 KB. Your old one was 17 MB.

Open `runbook-all.html` in Edge. Type `docker exits`. Open it. That is the product.

---

## Step 4 — Verify, and move things from documented to verified (this is the work)

The nine runbooks I wrote are the template, not the content. Three states:

| tier | what it means |
|---|---|
| `documented` | Written from official docs. Correct in theory. **Not run.** |
| `verified` | You ran every step and saw the output. Carries date, version, your name. |

The four Docker runbooks are marked `documented` on purpose — I have not run them,
so it would be a lie to mark them otherwise. **That honesty is the product.**

For each one:

1. Run every step on your demolitions cluster or a local Docker.
2. Where the output differs from what the `look` field says, fix the `look` field.
3. Where you see an output pattern the `signals` do not catch, add a signal.
4. Change `"tier": "documented"` to `"verified"` and add:

```jsonc
"verified_on": "2026-09-13",
"verified_against": "Docker 27.2 / Docker Desktop 4.34",
"verified_by": "dinesh"
```

5. `python scripts\validate.py` — it refuses if you forget any of those three.

Budget one evening for the four Docker ones. That is a realistic pace and it is
the pace that produces something true.

---

## Step 5 — Port the survivors from src-old (a few evenings)

Work `build\worklist.csv` top-down. Rows marked **SPLIT** first.

For each one you decide to keep:

- Write it in the new schema by hand. Do not bulk-convert — the old entries have
  no real `signals`, and `signals` is the whole point.
- Give it 5–8 aliases. Real phrases an engineer types in a panic, not synonyms
  of the title. "committed accidentally", not "commit undone".
- Give at least one step a `signals` array. If no step's output can distinguish
  this runbook from a neighbouring one, it is not a separate runbook.
- Mark it `documented` until you have run it. Then `verified`.

**Expect 30 to 60 survivors out of 961.** That is not a failure. That is the
number being true for the first time.

---

## Step 6 — Fix the README (10 minutes)

Delete "961 troubleshooting scenarios" and "5,766 walkthrough paths".

The 5,766 is `branches × 2`, and inside those walkthroughs there are 69 unique
fixes and 3 unique "verified" strings. Anyone who clones the repo and greps the
JSON finds that in ten minutes. It is the single biggest risk to the project's
credibility, and it costs nothing to remove.

Replace with the count of `verified` runbooks. Whatever it is.

> 34 runbooks, every one run against a real system, with the date and version
> recorded on each.

---

## Step 7 — Then add technologies, one at a time

Order: **Git → Linux → Terraform → Argo CD → AWS.**

Git first because it is where `destructive` actually fires. Your entire Kubernetes
and Docker set has almost no state-changing commands, so the risk model has never
been tested. Look at `git-force-push-safely` in `src\git.json` — that is what the
risk model is for.

One JSON file per technology. `build.py` emits a separate HTML per technology
automatically, so a 300 KB file opens on a jump host.

---

## Step 8 — Import navi and tldr, last

Only after the verified core is real.

The schema has a third tier, `reference`. The validator **rejects any reference
entry that carries `steps`, `causes` or `signals`.** Imported bulk physically
cannot impersonate a verified runbook, because the schema will not hold the
fields that make it look like one.

- tldr — CC-BY-4.0. Attribution required, commercial use fine.
- navi cheats — mostly MIT/Apache, but check per repo.

Every imported entry needs `import_source`, `license` and `attribution`.

Do not import before Step 5 is done. Breadth is worthless until the core is true.

---

## The rule to remember

You already wrote it yourself: **60 verified workflows beat 1000 unverified
commands, because a wrong production command causes an incident.**

Everything above is just making the repo obey that sentence.
