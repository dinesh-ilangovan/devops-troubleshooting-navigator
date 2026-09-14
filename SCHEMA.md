# Runbook schema v2

One JSON file per technology in `src/`. Each file is an array of runbooks.

## Trust tiers

Every runbook declares a `tier`. The UI never mixes tiers in one result list, and
never styles them alike. This is what lets you import outside content without
poisoning your own.

| tier | meaning | requires |
|---|---|---|
| `verified` | You ran every step against a real system and saw the output | `verified_on`, `verified_against`, `verified_by` |
| `documented` | Written from official docs, not yet run | `source` |
| `reference` | Imported from tldr / navi / cheat repos. Command lookup only, no guidance | `import_source`, `license`, `attribution` |

A `reference` entry may not contain `steps`, `causes` or `signals`. It is a
command card, nothing more. That restriction is enforced by the validator, and it
is the whole point: imported bulk can never masquerade as a verified walkthrough.

## Runbook

```jsonc
{
  "id": "k8s-crashloop",              // stable, kebab-case, unique across all files
  "tier": "verified",
  "technology": "Kubernetes",
  "category": "Pods & Containers",
  "title": "Pod is in CrashLoopBackOff",
  "summary": "One line. What the engineer is seeing right now.",

  "aliases": ["crashloop", "pod keeps restarting", "restarts increasing",
              "back-off restarting failed container"],

  "verified_on": "2026-09-11",
  "verified_against": "kind v0.23 / Kubernetes 1.31",
  "verified_by": "dinesh",
  "source": "https://kubernetes.io/docs/tasks/debug/debug-application/",

  "inputs": [
    { "key": "pod",       "label": "Pod name",  "example": "checkout-api-7d9f6b8c5-x4k2m" },
    { "key": "namespace", "label": "Namespace", "example": "production" }
  ],

  "steps": [ /* see below */ ],
  "causes": [ /* ranked, most likely first */ ],
  "verify": ["What must be true before you call this fixed."],
  "escalate": ["What to attach when you hand this over."]
}
```

## Step

```jsonc
{
  "title": "Read the previous container's logs",
  "cmd": "kubectl logs {pod} -n {namespace} --previous --tail=200",
  "risk": "safe",              // safe | state | destructive
  "look": "The first fatal line, not the last. Startup errors scroll away.",
  "note": "Required when risk is state or destructive. States the consequence.",

  "signals": [
    { "match": "OOMKilled|exit code 137",
      "means": "The kernel killed it for memory. Restart limits will not help.",
      "goto":  "cause:memory-limit-too-low" },
    { "match": "no such file or directory",
      "means": "The entrypoint path does not exist in the image.",
      "goto":  "cause:bad-entrypoint" }
  ]
}
```

`signals` is the honest, deterministic replacement for "the app understands
English". The engineer pastes their real output, the tool regex-matches it, and
routes them. No model, no network, no guessing.

Rules the validator enforces:

- Every `{placeholder}` in a `cmd` must appear as an `inputs[].key`.
- `risk: state | destructive` requires a non-empty `note`.
- `signals[].goto` must resolve to a real `cause.id` or step index.
- Two runbooks in the same technology may not have an identical command sequence.
  If they do, they are the same runbook and must be merged, or one of them needs
  a step that actually distinguishes it.

## Cause

```jsonc
{
  "id": "memory-limit-too-low",
  "cause": "The container's memory limit is below its real working set.",
  "fix": "Raise limits.memory in the owning Deployment and roll it out.",
  "confirm": "kubectl get pod {pod} -n {namespace} -o jsonpath='{.status.containerStatuses[0].lastState}'"
}
```

## Reference card (tier: reference)

```jsonc
{
  "id": "ref-tldr-kubectl-logs",
  "tier": "reference",
  "technology": "Kubernetes",
  "title": "kubectl logs",
  "summary": "Print container logs.",
  "examples": [
    { "cmd": "kubectl logs {pod} -c {container}", "desc": "Logs of one container" }
  ],
  "import_source": "tldr-pages",
  "license": "CC-BY-4.0",
  "attribution": "tldr-pages contributors, https://github.com/tldr-pages/tldr"
}
```
