# CI/CD & Pipeline Security (Phase 9)

Read this for GitHub Actions, GitLab CI, Jenkins, CircleCI, and similar. The pipeline is a high-value target: it holds deploy credentials, runs with broad access, and executes code — so a pipeline compromise is often a production compromise and a supply-chain compromise at once (A08).

## Secret handling in pipelines

- **Secrets echoed or leaked:** printing env, `set -x` around secret use, secrets passed as command-line args (visible in process lists/logs), secrets written to artifacts or caches. Masked secrets can still leak via base64/split tricks in a malicious PR.
- **Secrets over-scoped:** repo/org-wide secrets available to every workflow (and every fork PR that can trigger one) rather than environment-scoped with required reviewers. Deploy credentials should be gated behind protected environments.
- **Long-lived cloud keys:** static AWS/GCP/Azure keys stored as CI secrets instead of short-lived **OIDC federation** (GitHub→AWS/GCP/Azure). OIDC eliminates the standing credential — recommend it.

## Untrusted input & injection

- **`pull_request_target` / `pull_request` with write access:** the dangerous GitHub Actions pattern — `pull_request_target` runs with repo secrets and write token but checks out untrusted PR code; if it builds/runs that code, a fork PR steals secrets. Flag any workflow that combines `pull_request_target` (or a self-hosted runner on public PRs) with checkout+execution of PR head.
- **Script injection via expressions:** `${{ github.event.pull_request.title }}`, `...issue.title`, `...head_ref`, comment bodies interpolated directly into a `run:` shell step → command injection controlled by whoever opens the PR/issue. **Fix:** pass through an `env:` variable and reference `"$VAR"`, never inline the expression into the shell.
- **Self-hosted runners on public repos:** a fork PR can run arbitrary code on your runner (and its network/IAM). Ephemeral, isolated runners only; never persistent self-hosted on public PR triggers.

## Token & permission scope

- **`GITHUB_TOKEN` permissions:** default or `write-all` where read is enough. Set `permissions:` to least privilege (often `contents: read`), elevate per-job only where needed. A broad token + a script-injection = repo takeover.
- **Deploy/registry credentials** scoped to the minimum (push to one registry, deploy to one environment), not god-mode service accounts.

## Supply-chain integrity of the pipeline itself (A08)

- **Unpinned third-party actions:** `uses: some/action@v3` or `@main` — a moving tag/branch means the action's owner (or anyone who compromises it) runs code in your pipeline with your secrets. **Pin to a full commit SHA** for third-party actions; `@main` is the worst case.
- **Untrusted action sources:** actions from unknown authors, `curl | bash` of remote scripts, dependencies installed without lockfile/integrity verification during the build.
- **Artifact & build integrity:** builds not reproducible; artifacts unsigned/unverified between build and deploy; no provenance/attestation (SLSA); container images pushed without signing (cosign). A tampered artifact between CI and prod is A08.
- **Cache poisoning:** untrusted PRs writing to shared caches that trusted builds then consume.

## Deployment gates

- No required review/approval on production deploys; anyone who can push can ship.
- No branch protection on the deploy branch; force-push allowed; unsigned commits accepted where the threat model wants signing.
- Rollback and audit: is every deploy attributable and reversible?

## Reporting

Per finding: the workflow file and step, the trigger and who can reach it (any fork? any commenter?), the escalation (secret theft → prod deploy → supply chain), and the fix (SHA-pin the action, scope `permissions:`, move the expression to `env:`, adopt OIDC, gate the environment). The severe ones — script injection on `pull_request_target`, unpinned actions with secrets, self-hosted runners on public PRs — are HIGH–CRITICAL because they yield code execution with production credentials. Also see `dependencies.md` for the application-dependency side of supply chain.
