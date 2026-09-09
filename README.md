# Codex Engineering Governance

> **Latest stable release: v1.0.0**
>
> The `master` branch may contain unreleased documentation or framework-development changes. For normal installation, use a published stable release.

Codex Engineering Governance is a practical engineering-governance framework for people who build software with Codex.

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

The normal setup has three parts:

```text
one local copy of the governance framework
        ↓
a small global Codex instruction file
        ↓
governance metadata inside each governed project
```

You install the global framework once.

After that, each project can use the same central governance installation.

### Requirements

You should have:

- Codex;
- Git;
- Python 3;
- PowerShell on Windows, or a POSIX-compatible shell on macOS/Linux.

You do not need to understand the internal governance architecture before installing it.

### 1. Download a stable release

For normal use, install a published release rather than an arbitrary snapshot of `master`.

Open the repository's **Releases** page and download both the release ZIP and its `.sha256` file.

For v1.0.0 they are:

```text
codex-engineering-governance-v1.0.0.zip
codex-engineering-governance-v1.0.0.zip.sha256
```

### 2. Verify the download

Before extracting the ZIP, verify that its SHA-256 matches the published sidecar.

#### Windows

```powershell
$zip = ".\codex-engineering-governance-v1.0.0.zip"

$actual = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
$expected = ((Get-Content "$zip.sha256" -Raw).Trim() -split '\s+')[0].ToLowerInvariant()

if ($actual -ne $expected) {
    throw "SHA-256 mismatch"
}

"SHA-256 verified: $actual"
```

Do not continue if the values differ.

#### Linux

```sh
sha256sum codex-engineering-governance-v1.0.0.zip
cat codex-engineering-governance-v1.0.0.zip.sha256
```

#### macOS

```sh
shasum -a 256 codex-engineering-governance-v1.0.0.zip
cat codex-engineering-governance-v1.0.0.zip.sha256
```

The values must agree.

### 3. Extract the framework to a permanent location

Choose a location you intend to keep.

For example on Windows:

```text
D:\development\codex-engineering-governance
```

or on macOS/Linux:

```text
~/development/codex-engineering-governance
```

Do not install the framework into a temporary download directory.

Codex stores the framework location and uses it later.

### 4. Connect the framework to Codex

Open a terminal in the extracted framework directory.

#### Windows

```powershell
.\codex-home\install.ps1
```

#### macOS / Linux

```sh
./codex-home/install.sh
```

The installer:

- installs the framework's global Codex `AGENTS.md`;
- records the framework location in `GOVERNANCE_ROOT`;
- backs up an existing global `AGENTS.md` before replacing it.

By default these files are stored under:

```text
~/.codex
```

The important locator is:

```text
~/.codex/GOVERNANCE_ROOT
```

It contains the absolute path to this governance repository.

After installation, **start a fresh Codex session**.

### 5. Create a new governed project

The project-management scripts are preview-first.

Running them without `-Apply` / `--apply` shows what will happen without changing the project.

#### Windows — preview

```powershell
.\scripts\manage-governed-project.ps1 `
  -Mode New `
  -ParentRoot "D:\development" `
  -ProjectName "my-project"
```

Apply after reviewing the preview:

```powershell
.\scripts\manage-governed-project.ps1 `
  -Mode New `
  -ParentRoot "D:\development" `
  -ProjectName "my-project" `
  -Apply
```

#### macOS / Linux — preview

```sh
./scripts/manage-governed-project.sh New \
  --parent ~/development \
  --name my-project
```

Apply:

```sh
./scripts/manage-governed-project.sh New \
  --parent ~/development \
  --name my-project \
  --apply
```

The command creates the governance/project structure and can initialize Git.

It does **not** generate your application automatically.

Afterward, open the project in Codex and describe what you want to build.

### 6. Add governance to an existing project

You can also adopt an existing project.

The framework deliberately does not pretend that decisions made before governance was installed were already reviewed under this framework.

An adopted project therefore starts in:

```text
RECONCILIATION_REQUIRED
```

That tells Codex to understand and reconcile the project's existing architecture, dependencies, verification, and other relevant state.

#### Windows — preview

```powershell
.\scripts\manage-governed-project.ps1 `
  -Mode Adopt `
  -ProjectRoot "D:\development\existing-project"
```

Apply:

```powershell
.\scripts\manage-governed-project.ps1 `
  -Mode Adopt `
  -ProjectRoot "D:\development\existing-project" `
  -Apply
```

#### macOS / Linux — preview

```sh
./scripts/manage-governed-project.sh Adopt \
  --project ~/development/existing-project
```

Apply:

```sh
./scripts/manage-governed-project.sh Adopt \
  --project ~/development/existing-project \
  --apply
```

Existing project content is preserved.

### 7. Use Codex normally

Once governance is installed, you do not need to repeat governance instructions in every prompt.

For example:

```text
Add password-reset functionality.
```

```text
Review the current authentication design and recommend improvements.
```

```text
I want to replace SQLite with PostgreSQL. Recommend how we should approach the transition.
```

```text
Prepare this project for release.
```

Codex should:

1. read the project instructions;
2. find the central governance framework;
3. load the workflow and specialist guidance relevant to the task;
4. apply only the amount of process justified by the consequences.

You generally do not need to decide whether something is “C0”, “C1”, “C2”, or “C3” yourself.

Codex should classify the change and explain the important approval boundary when it matters.

### 8. Updating an already governed project

When you install a newer governance baseline, update governed projects using the project updater instead of manually editing version metadata.

#### Windows — preview

```powershell
.\scripts\update-governed-project.ps1 `
  -ProjectRoot "D:\development\my-project"
```

Apply:

```powershell
.\scripts\update-governed-project.ps1 `
  -ProjectRoot "D:\development\my-project" `
  -Apply
```

#### macOS / Linux — preview

```sh
./scripts/update-governed-project.sh /path/to/my-project
```

Apply:

```sh
./scripts/update-governed-project.sh /path/to/my-project --apply
```

The updater preserves project-specific instructions and does not silently accept new risks or architectural changes on your behalf.

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
