# Manual behavioral campaign operations

This manual kit supports realistic IDE-chat testing on a disposable virtual
machine or other isolated device. It does not invoke an AI, use an API key,
install an agent, initialize Git, upload responses, or change frozen GOV
scenarios, rubrics, thresholds, or release authority. Its optional Windows or
Ubuntu Linux conductor can only open a local VS Code window, replace the
clipboard with a rubric-free prompt, and save the response that the operator
explicitly pastes into its terminal.

## Prepare a testing machine

Use a clean VM snapshot. VMware is suitable, but the kit is hypervisor-neutral.
Copy the exact framework source to the VM, install the chosen IDE and Codex or
Claude Code normally, and sign in through the developer's own account. Do not
copy an API key or an existing user home/configuration directory.

From the copied framework source, install the selected host adapter:

```text
python governance.py host install --host claude
```

or:

```text
python governance.py host install --host codex
```

To provision a disposable Windows 11 or Ubuntu 26.04.1 VM before this step,
use [Evaluation VM bootstrap](evaluation-vm-bootstrap.md). Its normal route
installs current prerequisites; collection records only the response-relevant
resulting environment. Its optional checksum-locked route supports bit-for-bit
reproduction. Account sign-in remains interactive in both cases.

Then prepare a new sibling directory. The destination must not already exist;
the command refuses overwrites and does not initialize Git:

```text
python scripts/manual-behavioral-campaign.py prepare --destination ..\manual-governance-evaluation
```

On POSIX, use a normal path separator instead. The prepared directory contains
prompt-only files, an empty response folder, an empty global context, and a
minimal governed project. The framework source itself is the framework context.

## Run each challenge

Read the generated `README.md` in the prepared directory. For every challenge:

1. Open the prescribed context in the same IDE the developer would use:
   `contexts/global-kernel`, `contexts/governed-project`, or the copied
   framework source root.
2. Start a **fresh chat** and select the intended model and runtime settings.
3. Paste only `prompts/GOV-###.txt`. Do not reveal the frozen definition,
   expected behavior, forbidden behavior, or scoring rubric.
4. Save the unedited final response as `responses/GOV-###.txt` in UTF-8.

Record the actual host, requested model, IDE/client version, operating system,
and settings such as a Codex reasoning effort. A manual result is always bound
to those recorded conditions; it does not establish behavior for another model,
client, host, or platform.

## Optional Windows and Ubuntu sequential conductor

The conductor is for a realistic IDE-chat evaluation where the human, not this
framework, operates the Codex or Claude chat. It opens one fresh VS Code test
window per challenge in the appropriate context, places the rubric-free prompt
on the clipboard, captures a raw response that the operator pastes into the
terminal, and produces the scoring packet after the final challenge.

It does **not** read, inspect, submit to, or scrape an IDE chat. It does not
call an AI API. The operator must select the intended host/model/settings and
submit each prompt in a fresh chat.

The default mode is `manual-close`: after copying the raw final response, close
the dedicated test window and type `READY` in the conductor. This protects any
other VS Code work from the conductor.

```text
python scripts/manual-behavioral-campaign.py conduct ..\manual-governance-evaluation --host claude --model <selected-model> --client <IDE-and-version> --setting mode=plan --close-mode manual-close --vscode-user-data-dir ..\governance-vscode-test-profile
```

The test profile is optional in `manual-close` mode but recommended: it keeps
the tested integration isolated and lets the result metadata query precisely
that profile's selected integration version. It must first be initialized as
shown below. The platform's `code` command must be available on `PATH`. Use
`--vscode-command <executable>` when it is not named `code`. On Ubuntu, the
conductor requires one local clipboard utility: install `wl-clipboard` for a
Wayland desktop or `xclip` for an X11 desktop. It never installs either package
itself. Ubuntu LTS publishes `wl-clipboard` as the command-line interface for
the Wayland clipboard. [Ubuntu package information](https://packages.ubuntu.com/noble/wl-clipboard)

### Optional force-close mode

At the beginning of a campaign, the operator may instead choose
`force-close-test-instance`. It is deliberately restricted to a dedicated VS
Code profile created outside both the framework source and campaign directory:

```text
python scripts/manual-behavioral-campaign.py vscode-profile-init --destination ..\governance-vscode-test-profile
```

Open VS Code once with that profile's `--user-data-dir` and `--extensions-dir`
options, install the
chosen Codex or Claude extension there, and sign in normally. This profile can
contain authentication state: never copy it into a campaign, scoring packet,
Git repository, release artifact, or shared location.

Then run the conductor with the actual VS Code executable and that marked
profile directory:

```text
python scripts/manual-behavioral-campaign.py conduct ..\manual-governance-evaluation --host claude --model <selected-model> --client <IDE-and-version> --setting mode=plan --close-mode force-close-test-instance --vscode-executable <path-to-Code-executable> --vscode-user-data-dir ..\governance-vscode-test-profile
```

After each response is pasted into the conductor, force-close mode terminates
only the VS Code process tree it started with that dedicated profile. On Linux,
it starts the test instance in its own process group before terminating it. It
first asks for the exact confirmation phrase `FORCE-CLOSE-TEST-INSTANCE`. Do
not use this mode for an ordinary VS Code profile or while another window using
the test profile is open.

You can validate the selected campaign/context sequence without starting VS
Code or changing the clipboard:

```text
python scripts/manual-behavioral-campaign.py conduct ..\manual-governance-evaluation --host claude --model <selected-model> --client <IDE-and-version> --close-mode manual-close --dry-run
```

## Produce a scoring packet

When every selected response is present, run this from the framework source:

```text
python scripts/manual-behavioral-campaign.py collect ..\manual-governance-evaluation --host claude --model <selected-model> --client <IDE-and-version> --setting mode=plan
```

Repeat `--setting` for additional recorded settings. `collect` rejects missing,
empty, symbolic-link, or duplicate-output cases. It writes `campaign.json`,
`EVALUATION-METADATA.json`, and `INDEPENDENT-SCORING-PACKET.md` locally. The
metadata records only response-relevant provenance: the operating system, VS
Code version, selected agent-integration version when discoverable,
host/model/client, and declared runtime settings, without paths or credentials;
the packet includes frozen definitions and rubrics plus raw responses for an
independent scorer.

The raw responses can contain personal or project-specific information. Keep
the campaign outside the framework repository, do not commit it, and transfer
it only through an approved channel. A complete independently scored campaign
can contribute evidence, but it does not itself authorize a release.
