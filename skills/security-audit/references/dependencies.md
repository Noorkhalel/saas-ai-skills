# Dependency & Supply-Chain Audit (Phase 9)

Read this when auditing a repo with a manifest/lockfile. Most application code today is mostly other people's code, so known-vulnerable and untrustworthy dependencies (OWASP A06, A08) are a leading breach vector. Your job is to identify real, reachable risk — not to dump a scanner's raw CVE list.

## Run the tools, then triage

Use the ecosystem's SCA tooling if available and *triage* the output — a scanner lists CVEs; you assess reachability and severity in *this* app:

- **npm/yarn/pnpm:** `npm audit`, `pnpm audit`, or Snyk. Check the lockfile is committed.
- **Python:** `pip-audit`, `safety`; check `requirements.txt`/`poetry.lock`/`Pipfile.lock`.
- **Go:** `govulncheck` (reachability-aware — high signal), `go list -m all`.
- **Rust:** `cargo audit`. **Java:** OWASP Dependency-Check, `mvn versions`. **Ruby:** `bundle audit`. **.NET:** `dotnet list package --vulnerable`.
- **Cross-ecosystem:** Grype/Trivy on the repo or image; OSV.

**Triage each hit:** Is the vulnerable package a direct or transitive dependency? Is the vulnerable *function/path* actually reached by this app (a CVE in an unused code path of a library is lower risk than one on the request path)? Is there a fixed version and is the upgrade breaking? Rank by reachability × severity, not by CVSS alone. Don't report 200 transitive lows as if they're the headline — surface the reachable highs and the upgrade path.

## Beyond known CVEs

- **Abandoned / unmaintained packages:** last release years ago, archived repo, single maintainer, no response to security issues. An unmaintained dependency on the request path is a latent risk — no one will ship the fix when the next CVE lands. Flag with a maintained alternative where one exists.
- **Deprecated packages:** explicitly deprecated on the registry (e.g., `request`, `node-sass`) — migrate.
- **Version pinning & lockfile integrity:** is there a committed lockfile with hashes? Floating ranges (`^`, `~`, `*`, `latest`) plus no lockfile means non-reproducible builds and exposure to a malicious new release. Recommend lockfile + integrity hashes + a review policy for updates.
- **Typosquatting / dependency confusion:** package names that near-miss a popular one; internal package names resolvable from the public registry (dependency-confusion — pin the registry/scope for internal packages). Check unusual or recently-added dependencies.
- **Install-time execution:** `postinstall`/build scripts from dependencies run arbitrary code at install; a compromised package owns the dev/CI machine. Note where `--ignore-scripts` or vetting is warranted.
- **License risk:** copyleft (GPL/AGPL) in a proprietary product, or missing/unknown licenses — a legal/business risk to flag even though it isn't an exploit. Keep it in its own note so it doesn't dilute security severity.

## Supply-chain posture (A08)

- **OpenSSF Scorecard** on key dependencies and on this repo: are dependencies pinned, is branch protection on, are tokens least-privilege, is there signed release provenance?
- **SBOM:** does the project produce one (CycloneDX/SPDX)? Recommend generating one for inventory and faster CVE response.
- **Automated updates:** Dependabot/Renovate configured with review, so security patches land promptly without auto-merging untrusted changes.
- Ties to `cicd.md`: the pipeline is where a poisoned dependency executes — pin actions and verify integrity there too.

## Reporting

Per finding: the package and version, direct-or-transitive, the CVE/issue, whether the vulnerable path is reachable in this app (state if you couldn't determine reachability), the fixed version and upgrade risk, and the priority. Separate the security findings from the license/hygiene notes. Give a short remediation path: "upgrade X to ≥Y (non-breaking), replace abandoned Z, commit the lockfile, enable Dependabot." Because you're often reasoning from a manifest without running the app, be explicit about what a live scan would confirm.
