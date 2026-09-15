# Manual behavioral campaign operations

This manual kit supports realistic IDE-chat testing on a disposable virtual
machine or other isolated device. It does not invoke an AI, use an API key,
install an agent, initialize Git, upload responses, or change the canonical
GOV scenario goals, rubrics, thresholds, or release authority. Its protocol-v2
prompt rendering adds one shared text-only response rule to every challenge.
Its optional Windows or Ubuntu Linux conductor can only open a local VS Code window, replace the
clipboard with a rubric-free prompt, and save a response that the operator
explicitly copies to the clipboard and confirms in its terminal.

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
protocol-v2 prompt-only files, an empty response folder, an empty global
context, and a minimal governed project. The framework source itself is the
framework context.

## Run each challenge

Read the generated `README.md` in the prepared directory. For every challenge:

1. Open the prescribed context in the same IDE the developer would use:
   `contexts/global-kernel`, `contexts/governed-project`, or the copied
   framework source root.
2. Start a **fresh chat** and select the intended model and runtime settings.
3. Paste only `prompts/GOV-###.txt`. The prompt includes protocol v2: produce
   one self-contained written response; write any necessary clarification
   questions rather than opening an interactive question/input tool; do not
   wait for or supply an answer. Do not reveal the canonical definition,
   expected behavior, forbidden behavior, or scoring rubric.
4. Save the unedited final response as `responses/GOV-###.txt` in UTF-8.

Record the actual host, requested model, IDE/client version, operating system,
settings such as a Codex reasoning effort, and evaluation protocol v2. A manual
result is always bound to those recorded conditions; it does not establish
behavior for another model, client, host, platform, or protocol.

## Optional Windows and Ubuntu sequential conductor

The conductor is for a realistic IDE-chat evaluation where the human, not this
framework, operates the Codex or Claude chat. By default it reuses one
dedicated VS Code test window, switches it to the appropriate challenge
context, places the rubric-free prompt on the clipboard, captures a final
response that the operator explicitly copies to the clipboard, and produces
the scoring packet after the final challenge.

It does **not** read, inspect, submit to, or scrape an IDE chat. It does not
call an AI API. The operator must select the intended host/model/settings and
submit each prompt in a fresh chat.

The default `shared-window` workflow is sequential and does not close VS Code.
For each challenge it does exactly this:

1. Replaces the clipboard with the rubric-free prompt and opens or reuses the
   dedicated VS Code window in the required context. Wait until the required
   folder is visible before using the prompt; the first dedicated-profile
   launch can take a moment.
2. The operator starts a fresh chat, pastes the prompt, and copies the
   unedited final response from that chat to the clipboard.
3. The operator presses Enter in the conductor. It saves that clipboard text
   as the response. Typing `1` instead re-copies the same prompt; `QUIT`
   stops without overwriting any existing response.
4. It switches the same window to the next required context.

After a response is saved, the conductor continues directly to the next
challenge; it does not require a second Enter keypress.

Use a separately initialized test profile so the tested integration is
isolated and the result metadata can query that profile's selected integration
version. The profile uses VS Code's built-in `Light 2026` theme; no theme
extension is installed.

```text
python scripts/manual-behavioral-campaign.py conduct ..\manual-governance-evaluation --host claude --model <selected-model> --client <IDE-and-version> --setting mode=plan --vscode-user-data-dir ..\governance-vscode-test-profile
```

Initialize the profile once before the command above. The platform's `code`
command must be available on `PATH`; use `--vscode-command <executable>` when
it is not named `code`. The conductor removes VS Code's inherited terminal IPC
variable when launching so an explicit test-profile command is not redirected
through the editor that started it. On Ubuntu, it requires `wl-clipboard` for a
Wayland desktop or `xclip` for an X11 desktop. It never installs either package
itself. Ubuntu LTS publishes `wl-clipboard` as the command-line interface for
the Wayland clipboard. [Ubuntu package information](https://packages.ubuntu.com/noble/wl-clipboard)

```text
python scripts/manual-behavioral-campaign.py vscode-profile-init --destination ..\governance-vscode-test-profile
```

### Optional close-after-each-challenge modes

`manual-close` retains the earlier workflow: close the dedicated test window
and type `READY` before pasting the raw response into the conductor. The
optional `force-close-test-instance` workflow terminates only the separately
configured test-profile instance after each response. It never targets the
ordinary VS Code profile.

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

After each terminal-pasted response, force-close mode terminates
only the VS Code process tree it started with that dedicated profile. On Linux,
it starts the test instance in its own process group before terminating it. It
does not use this mode for an ordinary VS Code profile or while another window
using the test profile is open.

You can validate the selected campaign/context sequence without starting VS
Code or changing the clipboard:

```text
python scripts/manual-behavioral-campaign.py conduct ..\manual-governance-evaluation --host claude --model <selected-model> --client <IDE-and-version> --dry-run
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
host/model/client, evaluation protocol, and declared runtime settings, without
paths or credentials;
the packet includes frozen definitions and rubrics plus raw responses for an
independent scorer.

The raw responses can contain personal or project-specific information. Keep
the campaign outside the framework repository, do not commit it, and transfer
it only through an approved channel. A complete independently scored campaign
can contribute evidence, but it does not itself authorize a release.
