# DevOps Troubleshooting Navigator

An offline, evidence-driven troubleshooting navigator with realistic incident walkthroughs for Kubernetes and Docker.

**Current coverage:** 520 Kubernetes scenarios + 441 Docker scenarios = **961 troubleshooting scenarios**, with **5,766 modeled troubleshooting walkthrough paths**.

## Why this exists
During an incident, the hard part is often not remembering a command. It is deciding what to check first, what the output means, where to go next, what the likely root cause is, and how to verify the fix.

The Navigator provides a deterministic baseline:

**Symptom → Check → Example output → Root cause → Fix → Verify**

It is designed to run locally in a browser. It does not require an LLM/API, backend, login, cluster connection, or automatic command execution.

## Use the Navigator
Open `dist/DevOps_Troubleshooting_Navigator.html` in a modern browser.

> Walkthroughs and outputs are simulated/illustrative. Verify commands, environment, permissions, and change policy before acting in a real system.

## Repository structure
- `src/kubernetes.json` — Kubernetes troubleshooting knowledge
- `src/docker.json` — Docker troubleshooting knowledge
- `app/navigator.template.html` — standalone UI template
- `scripts/validate.py` — structural validation
- `scripts/build.py` — compiles the source into one standalone HTML
- `dist/` — generated standalone Navigator

## Build
Requires Python 3.

```bash
python scripts/validate.py
python scripts/build.py
```

## Contributing
Please read `CONTRIBUTING.md`. Add or improve troubleshooting evidence rather than simply increasing scenario count. Keep examples generic and never submit credentials, internal hostnames, customer data, proprietary incidents, or other confidential information.

## Project status
Kubernetes and Docker are the first modules. Additional DevOps technologies can be added through the same validated source/build model.

## Author
Designed & developed by **Dinesh Ilangovan**.
