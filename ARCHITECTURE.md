# Repository Architecture

## Structure and isolation

Each skill is an independent package under `skills/<lowercase-kebab-case>/`. `SKILL.md` is the canonical instruction file and must remain self-contained. Optional `references/`, `evals/`, `examples/`, and `assets/` folders belong only to their owning skill; they are never shared or moved between skills to create hidden coupling.

## Discovery and installation

The `skills/` directory is the source of truth. `SKILLS.md` catalogs every valid skill folder and uses the folder name as the installation identifier. Compatible loaders select a skill by folder; the Skills CLI supports repository installation and repeated `--skill` selectors. Root docs must not list a skill that lacks `SKILL.md`.

## Scaling model

The repository scales by adding isolated folders, not a shared prompt runtime. New skills use kebab-case names, register in `SKILLS.md`, receive one concise README summary entry, and are checked by the lightweight validation workflow. References are loaded on demand; evaluation fixtures stay outside the canonical prompt.

## Overlap management

Skills may cover adjacent concerns but must remain separately selectable. The catalog documents selection boundaries: repository understanding before changes; planning for future architecture; reviews for current code/boundaries/security/dependencies/performance; refactoring for behavior-preserving implementation; debugging and RCA for failures. Resolve overlap with catalog/documentation notes, not prompt merging.

## Documentation synchronization

`SKILLS.md`, README overview, changelog, and validation workflow are updated whenever skills are added or removed. The validator checks folder names, canonical files, root catalog membership, basic relative links, and unsafe local-path patterns. It does not certify skill quality or runtime compatibility.

## Optional workflow integration

Workflow integration is a project-runtime convention, not a shared skill runtime or dependency. The canonical contract lives at `shared/workflow-contract.md` and is synchronized into every `skills/<skill-name>/shared/workflow-contract.md`. This duplication is deliberate: the supported installer selects and copies individual skill folders, so a repository-level contract alone would not be present for a single-skill installation.

When enabled by a user request or an existing `.ai-workflow/` directory, a skill may write a detailed skill-specific artifact, a concise standardized handoff, and only lightweight run metadata. Skills filter handoffs by their own topic sets, verify inherited claims in project files, and do not load unrelated reports. Missing, malformed, or absent workflow files are recoverable and never prevent standalone execution. The synchronizer and validator enforce identical packaged copies without creating cross-skill prompt dependencies.
