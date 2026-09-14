# Direction

## What this is

An offline incident companion. An engineer with a broken system and no safe way
to paste logs into a chat box opens one HTML file, finds the runbook for their
symptom, works the checks in order, pastes real output to find out what it means,
and leaves with a timestamped record of what they did.

## What this is not

A command search engine. navi and tldr already do that, better, and they are
installed. If a feature of this project overlaps with navi, that feature is not
the product.

## The three things nobody else does

**1. Provenance.** Every runbook says who ran it, when, and against what version.
An LLM cannot offer that. A cheat sheet does not carry it. It is the only
durable reason to trust a static file over a model that reads your actual output.

**2. The incident log.** Ticking a check records a timestamp. At the end you copy
a markdown table of what was checked and what was observed. That is the postmortem
first draft, and it is the artifact a junior engineer most needs and least often
produces. No competing tool has state.

**3. Output signals.** Paste your real output; deterministic regexes route you to
the cause. This is the honest version of "understands what you typed" — no model,
no network, no fabrication. It fails visibly when it does not know, which is
exactly the behaviour you want in an incident.

## Importing navi / tldr

Yes, but into a walled tier. The schema has three:

- `verified` — you ran it. Full guidance.
- `documented` — from official docs, not yet run. Marked as unconfirmed.
- `reference` — imported from tldr (CC-BY-4.0) or navi (mostly MIT/Apache).
  Attributed, and **the validator rejects any reference entry that carries
  `steps`, `causes` or `signals`.**

That last rule is the whole reason importing is safe. Imported bulk can never be
mistaken for something you verified, because the schema physically cannot hold
the fields that make it look verified. You get the breadth without paying for it
in trust.

Do imports last. Breadth is worthless until the verified core is real.

## Roadmap

**Now.** Run `scripts/triage.py` against the old `src/`. It collapses 961
scenarios into 154 distinct procedures. Work `build/worklist.csv` top-down and
verify on a real cluster. Expect 30–60 survivors. Publish that number.

**Next.** Git. It is where `destructive` actually fires, where the branching is
real, and where juniors do irreversible damage. Kubernetes-only content leaves
the risk model and the signal model both untested.

**Then.** Linux, Terraform, Argo CD. One technology per file, built separately,
so a 300 KB file opens on a jump host.

**Later.** Reference tier imports. A `verified_on` staleness report in CI. A
`CODEOWNERS` per technology so verification has an owner.

## The headline

Not "961 scenarios". Something that survives someone grepping the JSON:

> 47 runbooks, every one run against a real cluster, with the date and version
> recorded on each.
