# Reconnaissance and repository map

Start with the smallest high-signal set: root files/directories, manifests/locks/workspaces, framework config, README/architecture docs, environment examples, Docker/CI/IaC, migrations/schema, test config, and scripts. Then inspect the actual source/config referenced by those artifacts. Mark generated, vendored, build, migration, and hand-written code distinctly.

Technology evidence comes from manifest plus imports/config/deploy where possible. Locate bootstrap/router/provider/client on frontend; server/route/middleware/DI/worker/schedule/serverless handler on backend; migration/schema/connection/seed on data; image/entrypoint/workflow/module/chart on deployment. Read source and callers before treating a path as active.

For each important module record responsibility, key files, public API, inbound/outbound dependencies, consumers, owned data, tests, risk, and confidence. Use a directory tree only to orient; use a responsibility map to explain. In a monorepo map apps, packages/libraries, workspace/build edges, ownership, public exports, and deployment units. Evidence for ownership can include CODEOWNERS, package/service metadata, deployment/on-call configuration, Git history, and team documentation; label each source rather than assuming directory ownership. Deep imports and shared packages need public-contract context before calling them violations.

Verified commands come from package scripts, Makefiles, CI, docs plus config, or tool output. Do not invent an install/build/test/deploy command. Record configuration variable names/purposes/scopes, never values; distinguish public, optional, secret, flags, defaults, and validation.
