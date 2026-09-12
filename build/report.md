# Triage report

- Scenarios in `src/`: **961**
- Distinct command sequences: **154**
- Collapse ratio: **6.2 scenarios per real procedure**
- Sequences already unique (verify as-is): **116**
- Sequences with no symptom-specific command: **0**
- Scenarios sitting inside a 10+ way collision: **823**

## Worst collisions

| symptoms | tech | first command | example titles |
|---|---|---|---|
| 115 | Kubernetes | `kubectl get pod <x> -n <x> -o wide` | CRI reports image filesystem unavailable; CSI driver registration missing on node; CSINode object missing expected driver |
| 40 | Kubernetes | `kubectl get ingress -n <x> -o wide` | Backend HTTPS certificate validation fails; Gateway Programmed condition false; Gateway TLS listener certificate issue |
| 35 | Kubernetes | `kubectl describe pod <x> -n <x>` | DaemonSet not scheduled on expected node; Device plugin resource missing from node capacity; Extended resource request cannot be satisfied |
| 34 | Kubernetes | `kubectl get pods -n kube-system -l k8s-app=kube-dns -o wide` | Cluster DNS works but external DNS fails; CoreDNS CPU throttling; CoreDNS ConfigMap change breaks resolution |
| 34 | Kubernetes | `kubectl get svc <x> -n <x> -o yaml` | ClusterIP connection refused; ClusterIP times out; Dual-stack Service has missing IPv4 endpoints |
| 24 | Kubernetes | `kubectl get pod <x> -n <x> -o wide` | Conntrack stale entry suspected after endpoint change; Direct Pod IP works but Service IP fails; Hairpin Service traffic fails |
| 21 | Docker | `docker pull <x>` | Credential helper — Registry, Auth & TLS: behaves differently than configured; Credential helper — Registry, Auth & TLS: fails completely; Credential helper — Registry, Auth & TLS: fails intermittently under load or restart |
| 21 | Docker | `docker buildx build --progress=plain -f <x> <x>` | .dockerignore rule — Build Context & .dockerignore: behaves differently than configured; .dockerignore rule — Build Context & .dockerignore: fails completely; .dockerignore rule — Build Context & .dockerignore: fails intermittently under load or restart |
| 21 | Docker | `docker buildx inspect --bootstrap` | Build result output — BuildKit & Cache: behaves differently than configured; Build result output — BuildKit & Cache: fails completely; Build result output — BuildKit & Cache: fails intermittently under load or restart |
| 21 | Docker | `docker buildx ls` | BUILDPLATFORM/TARGETPLATFORM — Buildx & Multi-platform: behaves differently than configured; BUILDPLATFORM/TARGETPLATFORM — Buildx & Multi-platform: fails completely; BUILDPLATFORM/TARGETPLATFORM — Buildx & Multi-platform: fails intermittently under load or restart |

## What to do

1. Work `worklist.csv` top-down.
2. SPLIT rows first: those are symptoms sharing a path that cannot
   distinguish them. Give each a command whose output differs.
3. Everything you verify on a real cluster gets `verified_on`,
   `verified_against` and `verified_by`. Nothing else ships as verified.
