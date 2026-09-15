# Reproducible evaluation VM bootstrap

Use this facility to provision disposable Windows 11 and Ubuntu 26.04.1 LTS
test VMs from one reviewed, checksum-locked artifact set. Ubuntu 26.04.1 LTS is
the current Ubuntu Desktop LTS release. [Ubuntu](https://ubuntu.com/download/desktop)

The checksum-locked route is optional. A disposable VM may instead use the
latest installer/extension releases; that is repeatable as a procedure but not
bit-for-bit reproducible. `EVALUATION-METADATA.json`, generated when the
campaign is collected, records only response-relevant provenance: the
operating system, VS Code and selected agent-integration versions when
discoverable, and the declared Codex/Claude model and runtime settings.

## Latest disposable-VM route

On a clean Windows 11 VM, run the PowerShell helper. On an Ubuntu Desktop VM,
run the Python helper. Both commands first display the plan; re-running with
`-Apply` or `--apply` is the explicit authorization to change the disposable
VM. They install current Python/VS Code prerequisites, the selected VS Code
extensions, local clipboard support on Ubuntu, and the selected framework host
adapter. They do not sign in to either AI service.

```text
powershell -ExecutionPolicy RemoteSigned -File scripts\bootstrap-evaluation-vm.ps1 -Latest -Host all -VscodeUserDataDir ..\evaluation-vscode-profile
python3 scripts/bootstrap-evaluation-vm.py latest --host all --vscode-user-data-dir ../evaluation-vscode-profile
```

Repeat the appropriate command with `-Apply` or `--apply` after review. The
profile path must be a new directory outside the framework source. Open VS Code
once with both `--user-data-dir <profile>` and
`--extensions-dir <profile>/extensions`, then sign in to the selected Codex or
Claude extension and choose the model/settings to test. The helper records no
credentials; the campaign metadata records only the response-relevant client
versions and declared settings. The dedicated profile selects VS Code's
built-in `Light 2026` theme; no theme extension is installed.

It deliberately separates three phases:

1. A maintainer obtains vendor artifacts and records their exact version, HTTPS
   URL, filename, and SHA-256 in a local bootstrap lock.
2. `fetch` downloads only those pinned artifacts into an otherwise new local
   cache and rejects an existing or downloaded hash mismatch.
3. `install`/`-Apply` verifies the cache again, displays the plan, and invokes
   only the reviewed installer type. It never silently accepts a licence,
   signs into an account, initializes Git, or creates an API key.

Keep the lock and cache outside the framework repository and manual campaign.
They are test-environment material, not source or behavioral evidence.

## Lock format

Create a new JSON lock for the chosen evaluation version. Every artifact needs
an exact version and a SHA-256 obtained from an authoritative vendor release
record. Do not substitute a mutable `latest` URL.

```json
{
  "schema_version": "1",
  "kind": "EVALUATION_VM_BOOTSTRAP_LOCK",
  "artifacts": [
    {
      "id": "vscode",
      "platform": "Windows",
      "kind": "windows-exe",
      "version": "<exact-version>",
      "filename": "VSCodeUserSetup-x64.exe",
      "url": "https://<official-vendor>/<exact-artifact>",
      "sha256": "<64-lowercase-hex-characters>",
      "install_args": ["<reviewed-installer-arguments>"]
    },
    {
      "id": "vscode",
      "platform": "Linux",
      "kind": "ubuntu-deb",
      "version": "<exact-version>",
      "filename": "code_amd64.deb",
      "url": "https://<official-vendor>/<exact-artifact>",
      "sha256": "<64-lowercase-hex-characters>"
    },
    {
      "id": "selected-host-extension",
      "platform": "Windows",
      "kind": "vsix",
      "version": "<exact-version>",
      "filename": "host-extension.vsix",
      "url": "https://<official-vendor>/<exact-artifact>",
      "sha256": "<64-lowercase-hex-characters>"
    }
  ]
}
```

Use `windows-exe` for the Windows Python and VS Code installers, `ubuntu-deb`
for the Ubuntu VS Code and clipboard packages, and `vsix` for the selected
Codex/Claude VS Code extension. Install only artifacts whose publisher,
licence, provenance, and checksum have been reviewed for the test baseline.
Windows installer arguments may not use unattended licence/EULA/quiet/silent
switches; the VM operator reviews and accepts any installer prompt directly.

## Windows

PowerShell is present in Windows 11, so it can bootstrap Python itself:

```text
powershell -ExecutionPolicy RemoteSigned -File scripts\bootstrap-evaluation-vm.ps1 -Lock <lock.json> -ArtifactCache <new-cache> -Fetch
powershell -ExecutionPolicy RemoteSigned -File scripts\bootstrap-evaluation-vm.ps1 -Lock <lock.json> -ArtifactCache <cache> -Artifact python -Artifact vscode -Apply
```

The second command requires the exact confirmation phrase. Then create the
separate test profile and install a selected VSIX row with
`-Artifact selected-host-extension -VscodeCommand <code> -VscodeUserDataDir
<profile>`. This prevents an extension from being installed into the normal
VS Code profile.

## Ubuntu

Ubuntu Desktop includes `python3`. Install from the verified cache only after
reviewing the plan; `sudo apt install <local-deb>` will request administrator
authorization and resolves only normal OS dependencies:

```text
python3 scripts/bootstrap-evaluation-vm.py fetch --lock <lock.json> --artifact-cache <new-cache>
python3 scripts/bootstrap-evaluation-vm.py install --lock <lock.json> --artifact-cache <cache> --artifact vscode --artifact clipboard --apply
```

For each VSIX row, also supply `--vscode-command` and
`--vscode-user-data-dir`. Use a `wl-clipboard` DEB on Wayland or an `xclip` DEB
on X11; the conductor refuses to run without its local clipboard tool.

After creating the separate test profile, install a selected host VSIX without
touching the normal profile:

```text
python3 scripts/bootstrap-evaluation-vm.py install --lock <lock.json> --artifact-cache <cache> --artifact selected-host-extension --vscode-command <code> --vscode-user-data-dir <profile> --apply
```

## Manual boundary and evidence

After bootstrap, initialize the dedicated VS Code profile, install the host
adapter from the copied framework source, and sign in to Codex or Claude
interactively. The official Codex IDE integration uses the VS Code extension
and an interactive ChatGPT sign-in. [OpenAI documentation](https://learn.chatgpt.com/docs/codex/ide)

Record the lock SHA-256, OS release, installed versions, selected host/model,
and profile mode in the campaign's runtime settings. Do not copy the VS Code
profile, its authentication state, installer cache, or raw response data into
Git or a scoring packet.
