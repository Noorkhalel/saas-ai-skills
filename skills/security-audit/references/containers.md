# Container & Kubernetes Security (Phase 8)

Read this when the target includes Dockerfiles, Compose files, or Kubernetes manifests. Container security is mostly about blast radius: assume the app inside can be compromised, and check what an attacker gains from there.

## Docker / Dockerfile

- **Runs as root:** no `USER` directive (or `USER root`) means the process — and anything that escapes it — is root in the container and, with a host mount or a kernel escape, potentially on the host. **Fix:** create and switch to a non-root user; set `USER` before the entrypoint. HIGH on internet-facing services.
- **Secrets baked into the image:** `ENV API_KEY=...`, `ARG`-passed secrets, copied `.env`/keys/`.npmrc`/cloud creds. Every layer is inspectable (`docker history`, pull the image) — a secret in *any* build stage is exposed even if a later stage removes it (unless you use multi-stage + `--mount=type=secret`). **Any leaked secret is burned — rotate.** CRITICAL.
- **Base image risk:** `latest` tags (unpinned, unreproducible), unmaintained/unofficial bases, full OS images where a slim/distroless would cut the attack surface. Pin by digest for critical images; scan with Trivy/Grype.
- **Build context leakage:** no `.dockerignore` → `.git`, `.env`, secrets, `node_modules` with local config copied into the image.
- **Exposed/oversized surface:** unnecessary packages, dev tools, shells in the final image; `EXPOSE` of management ports; `curl | bash` in build (untrusted fetch → supply chain).
- **Compose:** `privileged: true`, host network mode, Docker socket mounted into a container (`/var/run/docker.sock` = host root), secrets in `environment:` blocks committed to the repo, `ports:` binding management services to `0.0.0.0`.
- **Healthcheck / least capability:** drop capabilities (`--cap-drop=ALL`, add back only what's needed), `--read-only` root filesystem, `no-new-privileges`.

## Kubernetes

**Pod / container security context**
- `privileged: true`, `allowPrivilegeEscalation: true`, or missing `securityContext` → container can escalate. **Fix:** `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, drop all capabilities.
- `hostNetwork`, `hostPID`, `hostIPC`, or `hostPath` mounts — each punches through container isolation to the node. `hostPath` mounting `/` or the container runtime socket = node compromise. HIGH–CRITICAL.
- Running as root (`runAsUser: 0` or unset with a root image).

**Secrets & config**
- Secrets in plain ConfigMaps or inline env instead of `Secret` objects (and ideally an external manager — Vault, cloud secrets, sealed-secrets). Note: base64 `Secret`s are *not* encrypted — check that etcd encryption-at-rest is on.
- Service-account tokens automounted where not needed (`automountServiceAccountToken: false` if the pod doesn't call the API).

**RBAC**
- Over-broad `Role`/`ClusterRole`: `verbs: ["*"]`, `resources: ["*"]`, `apiGroups: ["*"]`; `cluster-admin` bound to a workload service account; wildcard bindings to `system:authenticated` or default service accounts. An over-permissioned pod is a cluster takeover after one app compromise.

**Network**
- No `NetworkPolicy` → flat pod network, any compromised pod can reach any other (lateral movement). Default-deny plus explicit allows is the goal.
- Ingress without TLS; services exposed via `LoadBalancer`/`NodePort` that should be internal.

**Workload hygiene**
- No resource `limits` → one pod can starve the node (DoS). Missing liveness/readiness probes.
- Images pulled by mutable tag with `imagePullPolicy: Always` and no digest pinning or admission control (no signature verification — cosign/Sigstore, no OPA/Kyverno policy gate).
- Admission control absent: no policy engine (OPA Gatekeeper/Kyverno) enforcing the above at deploy time.

## Reporting

Per finding: the manifest/Dockerfile and line, what an attacker gains (container root → host → cluster is the escalation chain to name), and the fix (the specific `securityContext` field, the multi-stage secret mount, the NetworkPolicy). Prioritize by blast radius: a `hostPath: /` mount or mounted Docker socket outranks a missing resource limit. State what's already hardened.
