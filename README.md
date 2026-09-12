# Codex Engineering Governance

> **Latest stable release: v1.0.0**
>
> **Current development candidate: v2.0.0-rc.1 (unpublished)**
>
> The `master` branch may contain unreleased documentation or framework-development changes. For normal installation, use a published stable release.

Codex Engineering Governance is a practical engineering-governance framework for people who build software with Codex or Claude Code.

It is especially useful if you work by describing what you want, letting Codex implement much of it, and iterating from there — often called **vibe coding**.

The framework is designed around a simple problem:

**AI can produce software very quickly, but speed does not remove the need for good engineering decisions.**

Codex can write a lot of code before requirements are clear. It can choose technologies without discussing the consequences, change security-sensitive behavior while solving an unrelated problem, or treat “the code runs” as equivalent to “the change is ready.”

This framework adds a lightweight engineering process around Codex so you can keep the speed of AI-assisted development while making important decisions, risks, verification, and release actions explicit.

---

## Background and goals

### What problem does this solve?

When you ask Codex to build something, there are two different kinds of work happening.

One is easy to see:

- writing code;
- changing files;
- fixing errors;
- running tests.

The other is less visible, but often more important:

- understanding what the product is actually supposed to do;
- deciding which technical approach is appropriate;
- identifying security and data risks;
- deciding whether an architecture change is worth its consequences;
- determining what must be tested before the change is considered complete;
- deciding whether something is safe and ready to publish.

Without a governance model, an AI agent can make those decisions implicitly while it is implementing your request.

This framework tries to prevent that.

### What should change when the framework is installed?

You should still be able to talk to Codex normally.

For example:

```text
Build me a small web app for tracking expenses.
```

```text
Add Google login.
```

```text
I want to move this project from SQLite to PostgreSQL.
```

```text
Prepare this project for its first public release.
```

You do not need to translate those requests into formal engineering documents yourself.

Instead, Codex should apply more or less engineering rigor depending on the consequences of the task.

A typo or harmless cleanup should stay lightweight.

A database migration, authentication change, architecture transition, security exception, or public release should receive more analysis, verification, and explicit approval.

### What remains your decision?

The framework deliberately keeps the developer in control of product intent and consequential decisions.

You decide:

- what you want the product to do;
- which important trade-offs you accept;
- whether a material architecture change should happen;
- whether an identified risk is acceptable;
- whether an exception to normal policy is justified;
- whether something should be released or published.

Codex is expected to do the engineering due diligence around those decisions.

It should:

- inspect the existing project before changing it;
- identify important ambiguity instead of inventing requirements;
- recommend a technical approach;
- explain material trade-offs;
- identify relevant security, dependency, data, and operational consequences;
- obtain approval before implementing decisions that require it;
- implement the approved change;
- run the applicable verification;
- report failures and incomplete checks truthfully.

### Recommendation first, implementation second

For material changes, the intended pattern is:

```text
Your goal
    ↓
Codex investigates the project
    ↓
Codex explains the important choices
    ↓
Codex recommends an approach
    ↓
You approve or change the direction
    ↓
Codex implements it
    ↓
Codex verifies the result
```

The framework is not intended to force this ceremony onto trivial work.

Its goal is **proportional engineering rigor**.

### Durable project knowledge

Important engineering decisions should not exist only in a chat transcript.

A governed project therefore keeps a small amount of durable information in the repository.

The main project files are:

| File | Purpose |
| --- | --- |
| `AGENTS.md` | Tells Codex how to load the governance framework for this repository. |
| `project-governance.yml` | Records the project's governance baseline and important governance state. |
| `verification-plan.json` | Describes the checks used to verify the project. |
| `docs/design.md` | A place for important architecture and Technology Baseline decisions. |

Detailed governance rules remain in this central framework repository. They do not need to be copied into every project.

### Framework-maintainer behavioral campaigns

The framework's own Codex and Claude Code behavioral evidence is collected
separately from normal project verification. The protected GitHub-hosted Claude
Code process, its response-packet retention, and its exact-commit trigger are
documented in [Behavioral campaign operations](docs/behavioral-campaigns.md).

### Technology Baseline in plain language

For maintained projects, the framework keeps major stack decisions explicit.

For example:

```text
language/toolchain
runtime
main application framework
database/persistence approach
deployment or packaging model
supported platforms
```

Together these form the project's **Technology Baseline**.

You can think of it as:

> “These are the big technical choices this project currently depends on.”

Adding a small library normally does not mean redesigning the Technology Baseline.

Replacing the database, application framework, runtime, or another architecture-shaping component usually does.

Codex should not silently make that kind of transition as a side effect of another task.

### What this framework is not

This framework is not a compliance certification system.

It does not guarantee that a project is secure merely because governance is installed.

It does not replace human responsibility for important product, risk, or publication decisions.

It also does not require every small project to produce a large pile of documents.

The principle is:

**preserve enough durable information and evidence to make engineering decisions understandable and verifiable, without unnecessary ceremony.**

---

## Local setup

> **Unreleased master interface:** the commands below describe the current 2.0 development line on `master` / feature branches. The latest stable release remains v1.0.0; when installing v1.0.0, follow the README bundled with that release.

The current setup has one management entry point:

```text
one local copy of the governance framework
        ↓
python governance.py
        ↓
Codex and/or Claude Code host adapters
        ↓
governance metadata inside each governed project
```

### Requirements

You need Python 3 to run the management interface.

Git is needed for Git-backed governed-project operations and for developing
the framework itself.

Codex or Claude Code does **not** need to be installed merely to configure
its governance adapter. A host-adapter operation manages the host's
conventional configuration location and may create that directory when it
does not yet exist. The host application is only required when you actually
use that coding agent.

The management interface itself has no third-party Python dependencies.

### 1. Put the framework in a permanent location

Choose a location you intend to keep, for example:

```text
D:\development\codex-engineering-governance
```

or:

```text
~/development/codex-engineering-governance
```

Do not manage a host adapter from a temporary download directory. The adapter records the framework location in its `GOVERNANCE_ROOT` locator.

### Unified management entry point

Run the same file for setup, updates, uninstall, verification, and governed-project operations:

```text
python governance.py
```

With no parameters, the tool is interactive and only offers actions applicable to the managed adapter/project state.

The same operations are available with parameters:

```text
python governance.py host status
python governance.py host install --host codex
python governance.py host install --host claude
python governance.py host install --host all
python governance.py host update --host all
python governance.py host verify --host all
```

Every mutating command prints a preview first and then asks:

```text
Apply these changes? [y/N]:
```

Use `-y` to answer that confirmation non-interactively:

```text
python governance.py host update --host all -y
```

`-y` confirms only the displayed plan. It never bypasses ownership checks, modified-managed-content refusal, dirty-worktree checks, version checks, path validation, or post-operation verification.

For Codex, the default user adapter location is `~/.codex`. For Claude Code, it is `~/.claude` unless `CLAUDE_CONFIG_DIR` is set.

The Claude adapter uses a user `CLAUDE.md` and an exact `permissions.allow` `Read(...)` rule for the central governance root. It does not add the governance root as a broadly editable additional working directory.

After installing or updating a host adapter, start a fresh coding-agent session.

### 2. Create a new governed project

Preview and confirm interactively:

```text
python governance.py project new --parent D:\development --name my-project
```

or on macOS/Linux:

```text
python governance.py project new --parent ~/development --name my-project
```

For unattended confirmation after the same preview:

```text
python governance.py project new --parent D:\development --name my-project -y
```

The command creates the governance/project structure and can initialize Git. It does **not** generate your application automatically.

### 3. Adopt an existing project

```text
python governance.py project adopt --project D:\development\existing-project
```

or:

```text
python governance.py project adopt --project ~/development/existing-project
```

An adopted project starts with governance reconciliation required rather than pretending its historical decisions were previously approved:

```text
RECONCILIATION_REQUIRED
```

Existing project content and project-specific `AGENTS.md` / `CLAUDE.md` text are preserved. A dirty Git worktree is a hard refusal; `-y` does not override it.

### 4. Inspect or verify a governed project

```text
python governance.py project status --project /path/to/project
python governance.py project verify --project /path/to/project
```

### 5. Update an already governed project

```text
python governance.py project update --project /path/to/project
```

Use `-y` for non-interactive confirmation after the preview:

```text
python governance.py project update --project /path/to/project -y
```

The updater changes only governance-owned fields/blocks, preserves project-specific instructions and established project-owned Technology Baseline state, and creates backups before changing existing governed files.

### 6. Uninstall a host adapter

Use the same management file:

```text
python governance.py host uninstall --host codex
python governance.py host uninstall --host claude
python governance.py host uninstall --host all
```

Add `-y` for unattended confirmation after the preview.

Uninstall is ownership-aware. It removes only the exact managed instruction block, locator or Claude read-permission entry that this framework instance created, and its own state record. Unrelated user content in `AGENTS.md`, `CLAUDE.md`, and Claude `settings.json` is preserved. If framework-managed content was edited after installation, uninstall refuses to guess or delete it.

Uninstalling a host adapter does not remove governance files from application repositories.

### 7. Use the coding agent normally

Once the applicable governance host adapter is configured, you do not need to repeat governance instructions in every prompt. Codex or Claude Code should read the project instructions, find the central governance framework, load the relevant workflow/specialist guidance, and apply the amount of process justified by the consequences of the task.

---

## Windows downloaded-package trust

Windows may attach Internet-zone metadata (Mark-of-the-Web) to a downloaded ZIP and propagate it to extracted PowerShell scripts. Under common `RemoteSigned` execution-policy configurations, PowerShell can then refuse to run the unsigned framework scripts even though their contents are unchanged.

Treat this as a package-trust decision, not as permission to bypass PowerShell policy.

For the current v1.0.0 release, first verify `codex-engineering-governance-v1.0.0.zip` against its published SHA-256 as described above. After that verification, unblock the **verified archive before extraction**:

```powershell
Unblock-File .\codex-engineering-governance-v1.0.0.zip
```

Then extract it normally and run the framework scripts without an execution-policy bypass.

If you already extracted the verified archive and its `.ps1` files still carry zone metadata, deliberately unblock only those trusted scripts from the extracted framework directory:

```powershell
Get-ChildItem . -Recurse -File -Filter *.ps1 | Unblock-File
```

Do not edit or resave scripts merely to make them executable: doing so changes the distributed bytes and makes package/evidence identity harder to reason about. Do not weaken the machine-wide PowerShell execution policy or use a blanket `-ExecutionPolicy Bypass` just to run the governance tooling.

---

## Developing this governance framework

This section is for contributors changing the governance framework itself.

Normal users do not need these steps merely to use the framework.

### Repository self-governance

The framework repository governs itself.

Start with:

```text
AGENTS.md
framework-governance.yml
```

`framework-governance.yml` identifies the repository's authoritative verification plan, release workflow, evidence locations, and change-classification rules.

The framework is a distributed governance/tooling package, not a hosted application.

That means its assurance model applies controls appropriate to this repository rather than mechanically requiring application-only checks whose factual triggers do not exist.

### Main repository areas

| Path | Purpose |
| --- | --- |
| `global/` | Normative engineering, security, and governance standards. |
| `workflows/` | Task-specific execution procedures. |
| `skills/` | Reusable specialist engineering procedures. |
| `profiles/` | Technology and platform specialization. |
| `templates/` | Files installed into governed projects. |
| `assurance/` | Verification semantics, runners, schemas, and release gates. |
| `tests/governance/` | Behavioral regression scenarios and retained evaluation evidence. |
| `reference-projects/` | Framework integration/validation fixtures. |
| `release-evidence/` | Durable verification, security-review, and release records. |

Avoid creating a second policy, assurance model, severity model, or exception mechanism when an existing framework component already owns that responsibility.

### Change classification

Documentation-only changes without normative effect are normally C0/C1.

Changes to framework policy, assurance semantics, installers, updaters, or bootstrap behavior are material and are normally C2.

Control weakening and other high-consequence changes may require C3 depending on their consequences.

C2/C3 changes require the applicable recommendation and approval before substantial implementation.

### Development verification

For fast feedback:

```text
python scripts/verify-framework.py quick
```

For canonical local verification:

```text
python scripts/verify-framework.py full
```

The framework also uses Windows and Ubuntu CI evidence and combines those reports for cross-platform assurance.

A required check that did not execute is never treated as PASS.

Do not disable, suppress, or weaken a control simply to obtain a green result.

### Behavioral governance tests

The scenarios under:

```text
tests/governance/
```

test whether Codex actually follows the intended governance behavior.

They are decision probes, not ordinary unit tests.

Behavioral evaluations use fresh Codex sessions and declared execution contexts.

The raw response is preserved as evidence.

Historical failures remain historical failures. Do not delete or rewrite them merely because a later attempt succeeds.

When a governance or instruction change could materially alter agent behavior, evaluate the applicable behavioral scenarios according to the repository's behavioral-test protocol.

### Deterministic release packages

A candidate/release package must be built from a clean committed repository state:

```text
python scripts/build-release-package.py
```

The builder reads package content from exact Git `HEAD`, verifies deterministic reproduction, and produces:

```text
codex-engineering-governance-v<version>.zip
codex-engineering-governance-v<version>.zip.sha256
```

Building the archive does not authorize:

- committing;
- tagging;
- pushing;
- creating a GitHub Release;
- changing repository visibility;
- any other consequential publication action.

Those are separate decisions.

### Release and compatibility policy

Public stable releases use Semantic Versioning.

See:

```text
docs/release-policy.md
workflows/release/WORKFLOW.md
```

for the compatibility promise, deterministic package contract, assurance requirements, and publication boundary.

### Version history

Detailed version-by-version history intentionally lives in:

```text
CHANGELOG.md
```

rather than in this README.

That keeps this document focused on:

1. why the framework exists;
2. how to install and use it;
3. how to develop the framework.

### Security

See:

```text
SECURITY.md
```

for vulnerability-reporting guidance.

---

## License

MIT — Copyright (c) 2026 Sittelle
