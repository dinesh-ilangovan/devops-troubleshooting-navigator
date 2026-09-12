# DevOps Runbook

**Designed and built by [Dinesh Ilangovan](https://github.com/dinesh-ilangovan)**

An offline incident companion for DevOps engineers. One HTML file, no backend, no
LLM, no login, no cluster connection, and nothing is executed for you.

Built for the moment where an engineer has a broken system, no safe way to paste
logs into an external AI, and needs to know what to check, what the output means,
and what it is safe to run.

---

## What makes it different

Three things no cheat sheet and no chat assistant can offer.

**Provenance on every runbook.** Each one records who ran it, on what date, and
against which version. A model cannot tell you that. A cheat sheet does not carry
it. It is the reason to trust a static file.

**An incident log.** Tick each check as you work through it and the tool records a
timestamp. At the end, one button gives you a markdown table of what you checked
and what you observed — the first draft of the postmortem, written while you were
working rather than from memory afterwards.

**Output signals.** Paste your real terminal output into a step and deterministic
pattern matching tells you what it means and routes you to the cause. No model, no
network. When it does not recognise something, it says so instead of guessing.

---

## Safety model

Every command carries a risk level, and the interface treats them differently.

| | |
|---|---|
| **Read only** | Safe to run anywhere. Copy freely. |
| **Changes state** | Carries a note explaining the consequence before the command. |
| **Destructive** | The command is **hidden** until you have read the warning and chosen to reveal it. |

There is no one-click execute, on purpose. The tool generates and explains; the
engineer stays responsible for running it in their approved environment.

---

## Trust tiers

Nothing in this repository pretends to be more reliable than it is.

| tier | meaning |
|---|---|
| `verified` | Run against a real system. Carries date, version and author. |
| `documented` | Written from official documentation. Not yet run. Shown as unconfirmed. |
| `reference` | Imported from tldr or navi. Attributed. Command lookup only — the schema forbids it from carrying guidance. |

The validator enforces this. A `verified` runbook without a date, a version and an
author is rejected at build time.

---

## Use it

Open any file in `dist/` in a browser. That is the whole installation.

- `runbook-kubernetes.html`
- `runbook-docker.html`
- `runbook-git.html`
- `runbook-all.html` — everything

Per-technology files stay small enough to open on a jump host.

---

## Build

Python 3, no dependencies.

```bash
python scripts/validate.py    # enforces every rule in SCHEMA.md
python scripts/build.py       # validates, then compiles dist/
```

`scripts/triage.py` analyses a runbook set and reports how many distinct
procedures it actually contains, writing a prioritised verification worklist.

---

## Contributing

Read `SCHEMA.md` first. The rules the validator will hold you to:

- Every step needs a `look` field. A step that does not say what its output means
  is a cheat sheet line, not a runbook step.
- `state` and `destructive` steps need a `note` explaining the consequence.
- Every `{placeholder}` must be declared in `inputs`.
- **Two runbooks may not share an identical command sequence.** If they do, they
  are the same runbook. Give one of them a step whose output differs, or merge them.

That last rule is the important one. It is what keeps the count honest.

Quality over volume. A wrong production command causes an incident.

---

## Roadmap

- **Now** — verify the Docker runbooks and move them from `documented` to `verified`
- **Next** — Linux, Terraform, Argo CD, AWS, CI/CD, observability
- **Later** — `reference` tier imports from tldr (CC-BY-4.0) and navi, attributed
- **Later** — staleness reporting in CI, per-technology ownership

---

## Author

**Dinesh Ilangovan** — Senior DevOps Engineer.

Every runbook marked `verified` in this repository was run by hand against a real
system before it shipped.
