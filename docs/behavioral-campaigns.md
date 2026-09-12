# Behavioral campaign operations

This document describes the framework-maintainer workflow for collecting
behavioral evidence. It does not change the frozen GOV scenarios, their
rubrics, acceptance threshold, or release authority.

## GitHub-hosted Claude Code campaign

`behavioral-claude-full.yml` runs the current candidate in a fresh GitHub
Ubuntu runner. It installs the pinned Claude Code CLI, creates the harness's
isolated temporary host home and three context-specific workspaces, and runs
GOV-001 through GOV-030 using `opus`. The harness records the resolved model,
CLI binary/version, exact clean commit, scenario hashes, and per-scenario
capture status in `campaign.json`.

Claude runs in its native `plan` mode. This permits it to read and search the
isolated context, including the governed-project or framework instructions it
would consult while planning in an IDE, but prevents edits and command
execution. The harness does not use `--tools ""`; it records the
`native-plan-readonly-v1` tool profile in each capture instead. The temporary
contexts do not contain the repository `.git` directory or user host data.

The job has `contents: read`, disables persisted checkout credentials, has no
pull-request trigger, and runs only after the `behavioral-evals` environment
approver releases `ANTHROPIC_API_KEY`. The secret is scoped to the capture
step. Raw responses are captured by the harness rather than written to the
workflow log.

Before triggering a run, a maintainer must configure the GitHub environment
to require a reviewer and to permit only `ci/behavioral-claude-full`, then add
the `ANTHROPIC_API_KEY` environment secret. This branch restriction is a
required part of the workflow's credential boundary.

To evaluate an exact already-pushed candidate commit, create the temporary
trigger branch at that commit and push it:

```text
git push origin <candidate-commit>:refs/heads/ci/behavioral-claude-full
```

Approve the resulting environment deployment in GitHub. Do not reuse an
existing trigger branch for a different candidate without deleting it first;
the campaign's Git commit must be the candidate under evaluation. After the
run, delete the temporary trigger branch to prevent additional automatic API
use.

The job uploads a repository-accessible artifact containing only
`INDEPENDENT-SCORING-PACKET.md` (frozen definitions/rubrics plus raw responses)
and `campaign.json` (capture metadata). GitHub deletes it after seven days.
Download the packet for independent scoring; do not upload raw responses to
issues, commits, or public logs. The artifact and its scoring result are
evidence only. A complete independently scored campaign meeting the threshold
is still required before it can contribute to candidate acceptance.

If raw model output is not permitted to be retained in the repository's GitHub
Actions storage, do not use this workflow; run the local campaign instead.
