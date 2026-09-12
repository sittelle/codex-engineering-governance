# Manual behavioral campaign operations

This manual kit supports realistic IDE-chat testing on a disposable virtual
machine or other isolated device. It does not invoke an AI, use an API key,
install an agent, initialize Git, upload responses, or change frozen GOV
scenarios, rubrics, thresholds, or release authority.

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

## Produce a scoring packet

When every selected response is present, run this from the framework source:

```text
python scripts/manual-behavioral-campaign.py collect ..\manual-governance-evaluation --host claude --model <selected-model> --client <IDE-and-version> --setting mode=plan
```

Repeat `--setting` for additional recorded settings. `collect` rejects missing,
empty, symbolic-link, or duplicate-output cases. It writes `campaign.json` and
`INDEPENDENT-SCORING-PACKET.md` locally; the latter includes frozen definitions
and rubrics plus raw responses for an independent scorer.

The raw responses can contain personal or project-specific information. Keep
the campaign outside the framework repository, do not commit it, and transfer
it only through an approved channel. A complete independently scored campaign
can contribute evidence, but it does not itself authorize a release.
