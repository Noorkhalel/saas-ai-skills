# Package risk, supply chain, and upgrade strategy

## Package-level false-positive gates

Before unused classification inspect static/dynamic imports, config/plugins, CLI/build/test scripts, code generation, environment-specific entries, framework auto-discovery, optional peer dependencies, native bindings, and postinstall behavior. Classify as Confirmed unused, Likely unused, Development-only, Indirectly used, or Needs manual verification. Do not remove without test/build/runtime validation.

For version duplication/conflicts capture exact versions and dependency paths, peer/runtime/framework constraints, actual bundle/image/build impact, and whether deduplication changes behavior. A transitive dependency is not an issue solely because it exists; a newer major is not inherently safer or compatible.

## Supply-chain evidence

Record exact package/version/source/path and scanner/advisory provenance. Distinguish confirmed vulnerability, scanner warning, potential risk, and unknown. Review registry and private namespace configuration, typosquatting/dependency confusion, Git/local sources, maintainer/deprecation/EOL evidence, install scripts/binary downloads/native extensions, checksums/lock integrity/provenance, SBOM, license policy, and supported runtime. Never invent a CVE or claim compromised status without evidence.

## Upgrade sequence

1. Freeze baseline: clean lockfile, manager/runtime/framework versions, tests/build, deployment and rollback path.
2. Address confirmed urgent security issues with a compatible patch or temporary containment; retest reachability and regression.
3. Batch low-risk patch/minor upgrades by compatible ecosystem/framework group, one group per change.
4. Plan framework-aligned/build/runtime and deprecated replacement migrations separately.
5. Isolate major breaking upgrades: read migration notes, identify API/peer/runtime changes, update one boundary, run focused then full tests, canary/release monitor, and retain rollback/forward repair.

For removal/replacement compare provided functionality, usage, API/behavior, security/maintenance, bundle/build/container cost, license, team familiarity, and migration risk. Possible good answer: keep unchanged, pin/constrain, move to dev dependency, consolidate, isolate behind adapter, fork temporarily, or vendor critical code.
