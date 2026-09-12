# Contributing

Thanks for helping improve the DevOps Troubleshooting Navigator.

## What makes a useful contribution
A scenario should help an engineer move from a real symptom to evidence. Prefer:

**Symptom → Check → Example output → Root cause → Fix → Verify**

Keep wording short and operational. Commands should be specific enough to be useful, while placeholders must remain generic.

## Safety and privacy
Do not contribute real credentials, tokens, secrets, private URLs, internal hostnames, customer names/data, proprietary incident details, or confidential company information. Use simulated names and outputs.

Do not turn vague symptoms directly into destructive actions. Clearly preserve risk warnings for state-changing operations.

## Workflow
1. Fork the repository or create a branch.
2. Edit the relevant file under `src/`.
3. Run `python scripts/validate.py`.
4. Run `python scripts/build.py` and test the generated HTML locally.
5. Open a pull request describing the symptom, evidence path, and why the change is technically correct.

Structural validation does not prove semantic technical correctness. Review commands, expected output, root cause, remediation, and verification carefully.
