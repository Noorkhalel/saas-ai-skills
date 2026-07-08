# Infrastructure Debugging: Docker, Kubernetes, CI/CD, Network (Phase 5)

For bugs in containers, orchestration, pipelines, and the network between services. These fail with *exit codes and events* that read like a diagnosis once you know them — get the code/event first, theorize second.

## Docker: container exits immediately / won't start

Get `docker ps -a` (exit code) and `docker logs <container>` (the app's own error) before anything else. The exit code classifies it:
- **Exit 0** — the main process *finished*. The container ran a command that returned, not a long-lived server (e.g., `CMD` runs a script that exits, or the server forked to background and PID 1 exited). Containers live only as long as PID 1.
- **Exit 1 / app error** — the app crashed on startup: read `docker logs` for *its* exception. Usually config/env (missing/wrong env var, unreadable secret), can't reach a dependency (DB/queue not up yet — startup ordering), a bad mount, or a port bind failure.
- **Exit 137 (SIGKILL, often OOMKilled)** — killed by the memory cgroup limit; `docker inspect` shows `OOMKilled: true`. The container's memory limit is too low or the app over-allocates at startup. Not a code crash — a limit/footprint mismatch.
- **Exit 139 (SIGSEGV)** native crash; **143 (SIGTERM)** orderly stop (something asked it to stop).
- **Common causes to check:** `CMD`/`ENTRYPOINT` shape (shell vs exec form changes signal handling and PID 1); the process daemonizing instead of staying foreground; missing executable/`exec format error` (architecture mismatch — arm64 image on amd64 or vice versa); a healthcheck killing a container that's actually fine but slow to start.

## Kubernetes: CrashLoopBackOff and friends

`kubectl describe pod <p>` (events + last state + exit code) and `kubectl logs <p> --previous` (the *crashed* instance's logs, not the restarted one) are the whole diagnosis most of the time. CrashLoopBackOff is not a cause — it's "the container keeps exiting and K8s keeps restarting with backoff." Find *why it exits*:
- **App crashes on startup** → `logs --previous` shows the exception: usually missing/wrong **ConfigMap/Secret/env**, an unreachable dependency at boot, or a failed migration. Most CrashLoops are ordinary app startup errors wearing a K8s name.
- **OOMKilled** (`describe` → Last State: OOMKilled, reason 137) → memory `limit` too low or a leak; raise the limit or fix the footprint. `requests`/`limits` mismatch also causes eviction.
- **Failing liveness probe** → K8s SIGTERMs a container it thinks is unhealthy; if the probe is too aggressive (short `initialDelaySeconds`/`timeout`) it kills a healthy-but-slow-starting app in a loop. The tell: app logs look *fine* then get a SIGTERM. Check probe timing against real startup time.
- **Readiness probe failing** → not a crash, but "pod never becomes Ready / no traffic": the probe endpoint is wrong, or a dependency it checks is down.
- **Image/exec errors:** `ImagePullBackOff` (wrong tag/registry/creds — `describe` events say which), `CreateContainerConfigError` (referenced secret/configmap missing), `exec format error` (arch mismatch), command not found (wrong `command`/`args`).
- **Pending, not crashing:** unschedulable — insufficient CPU/memory on nodes, unsatisfiable node selector/affinity, a PVC that won't bind. `describe` events state the reason plainly.

## CI/CD and deployment failures

- **"Failed after a recent merge/deploy":** the change is the prime suspect (`references/evidence.md` git section). Diff the range; check migrations, dependency/lockfile bumps, config, and env changes — the break is often non-code.
- **Passes locally, fails in CI:** environment difference — dependency versions (lockfile not honored, cache stale), missing env/secret in CI, services not available (DB/Redis in the pipeline), timezone/locale, file-ordering or case-sensitivity (Linux CI vs mac/Windows dev), test-ordering/parallelism exposing shared state, absolute-path assumptions.
- **Flaky pipeline:** the same job passes on re-run → non-determinism — test isolation, real network calls, timing/sleeps, unseeded randomness, resource limits in the runner.
- **Deploy succeeds, app breaks:** migration/code ordering (new code needs a column the migration didn't add yet, or vice versa — backward-compat one release each way); config/secret not promoted to the new environment; a changed default; health check flapping; build artifact/image mismatch (deployed the wrong or stale image — verify the digest).
- **Read the first failing step**, not the final "job failed" line; get exit codes and the step's own logs.

## Network between services

- **Connection refused** → nothing listening there (wrong host/port, service not up, wrong container/service name in the orchestrator's DNS). **Timeout** → reachable but not answering (downstream hung/overloaded, or a firewall/security-group/NetworkPolicy dropping packets silently — refused vs dropped distinguishes closed-port from blocked). **DNS** → name doesn't resolve (K8s service DNS, wrong namespace, external DNS).
- **TLS:** cert expired/untrusted/hostname-mismatch; verification disabled hiding a MITM/misroute. **Intermittent network errors** under load → connection-pool/limit exhaustion, keep-alive/idle-timeout mismatches between client and server/proxy, or an LB idle timeout cutting long requests.
- **Proxy/Nginx:** `502` (upstream unreachable/crashed — check the upstream, not Nginx), `504` (upstream too slow vs `proxy_read_timeout`), `413` (body over `client_max_body_size`), `499` (client gave up first — upstream too slow). Read *which* status: it points at which hop.

## Reporting

Lead with the classifying signal (exit code, K8s event, HTTP status, `refused` vs `timeout`) as the evidence, then the cause it implies, confidence, and the fix (config/limit/probe/ordering change — usually not app code). For infra, prevention is often the strongest lever: a readiness gate, a resource limit set from real usage, a migration-ordering rule, a smoke test in the pipeline — name it.
