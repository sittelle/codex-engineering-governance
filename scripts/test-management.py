#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANAGER = ROOT / "governance.py"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
HOST_BEGIN = "<!-- BEGIN SITTELLE-ENGINEERING-GOVERNANCE -->"
HOST_END = "<!-- END SITTELLE-ENGINEERING-GOVERNANCE -->"
PROJECT_BEGIN = "<!-- BEGIN ENGINEERING-GOVERNANCE-MANAGED -->"
CLAUDE_BEGIN = "<!-- BEGIN SITTELLE-ENGINEERING-GOVERNANCE-CLAUDE -->"


def run(
    args: list[str],
    *,
    input_text: str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(MANAGER), *args],
        cwd=ROOT,
        text=True,
        input=input_text,
        capture_output=True,
        check=False,
        env=env,
    )


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def detail(result: subprocess.CompletedProcess[str]) -> str:
    text = "\n".join(
        part.strip() for part in (result.stdout, result.stderr) if part and part.strip()
    )
    return text[-1600:]


def require_ok(
    result: subprocess.CompletedProcess[str], message: str, failures: list[str]
) -> bool:
    if result.returncode == 0:
        return True
    failures.append(f"{message} (exit {result.returncode}): {detail(result)}")
    return False


def git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def init_clean_git(path: Path) -> None:
    git(["init", "-q"], path)
    git(["config", "user.email", "governance-test@example.invalid"], path)
    git(["config", "user.name", "Governance Test"], path)
    git(["add", "-A"], path)
    committed = git(["commit", "-qm", "fixture"], path)
    if committed.returncode != 0:
        raise RuntimeError(detail(committed))


def host_cycle(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="governance-host-") as td:
        base = Path(td)
        codex = base / "codex"
        claude = base / "claude"
        env = os.environ.copy()
        env["CODEX_HOME"] = str(codex)
        env["CLAUDE_CONFIG_DIR"] = str(claude)

        # Existing personal instructions/settings must survive install and uninstall.
        codex.mkdir()
        (codex / "AGENTS.md").write_text(
            "# Personal Codex instructions\n\nKEEP_CODEX\n",
            encoding="utf-8",
            newline="\n",
        )

        claude.mkdir()
        (claude / "CLAUDE.md").write_text(
            "# Personal Claude instructions\n\nKEEP_CLAUDE\n",
            encoding="utf-8",
            newline="\n",
        )
        (claude / "settings.json").write_text(
            json.dumps(
                {
                    "model": "user-choice",
                    "permissions": {
                        "deny": ["Read(.env)"],
                        "allow": ["Bash(git status)"],
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

        # A declined interactive confirmation must be non-mutating.
        before = (codex / "AGENTS.md").read_bytes()
        declined = run(
            [
                "host", "install", "--host", "codex",
            ],
            input_text="n\n",
            env=env,
        )
        check(declined.returncode == 0, "declined host install failed", failures)
        check(
            (codex / "AGENTS.md").read_bytes() == before
            and not (codex / "GOVERNANCE_ROOT").exists(),
            "declined host install mutated Codex home",
            failures,
        )

        installed = run(
            [
                "host", "install", "--host", "all", "-y",
            ],
            env=env,
        )
        if not require_ok(installed, "host install all failed", failures):
            return

        # ADR 0005: governance loads from governed projects, never from user scope.
        check(
            (codex / "AGENTS.md").read_text(encoding="utf-8") == "# Personal Codex instructions\n\nKEEP_CODEX\n",
            "Codex install changed personal instructions or wrote governance text into user scope",
            failures,
        )
        check(
            (claude / "CLAUDE.md").read_text(encoding="utf-8") == "# Personal Claude instructions\n\nKEEP_CLAUDE\n",
            "Claude install changed personal instructions or wrote governance text into user scope",
            failures,
        )

        settings = json.loads((claude / "settings.json").read_text(encoding="utf-8"))
        check(settings.get("model") == "user-choice", "Claude install changed user model", failures)
        check(
            settings.get("permissions", {}).get("deny") == ["Read(.env)"],
            "Claude install changed user deny rules",
            failures,
        )
        check(
            "Bash(git status)" in settings.get("permissions", {}).get("allow", []),
            "Claude install changed pre-existing user allow rules",
            failures,
        )
        root_text = ROOT.resolve().as_posix()
        if re.match(r"^[A-Za-z]:/", root_text):
            root_text = "/" + root_text[0].lower() + root_text[2:]
        expected_rule = f"Read(/{root_text.rstrip('/')}/**)"
        check(
            expected_rule in settings.get("permissions", {}).get("allow", []),
            "Claude install did not add least-privilege governance Read allow rule",
            failures,
        )
        locator_text = (claude / "GOVERNANCE_ROOT").resolve().as_posix()
        if re.match(r"^[A-Za-z]:/", locator_text):
            locator_text = "/" + locator_text[0].lower() + locator_text[2:]
        expected_locator_rule = f"Read(/{locator_text})"
        check(
            expected_locator_rule in settings.get("permissions", {}).get("allow", []),
            "Claude install did not add the exact-file GOVERNANCE_ROOT Read allow rule",
            failures,
        )

        # An installation from before the locator rule existed gains it on update.
        claude_state_path = claude / ".sittelle-engineering-governance.json"
        old_style_state = json.loads(claude_state_path.read_text(encoding="utf-8"))
        old_style_state.pop("claude_locator_read_ownership", None)
        claude_state_path.write_text(json.dumps(old_style_state, indent=2) + "\n", encoding="utf-8", newline="\n")
        stripped = json.loads((claude / "settings.json").read_text(encoding="utf-8"))
        stripped["permissions"]["allow"].remove(expected_locator_rule)
        (claude / "settings.json").write_text(json.dumps(stripped, indent=2) + "\n", encoding="utf-8", newline="\n")
        stale_verify = run(["host", "verify", "--host", "claude"], env=env)
        check(stale_verify.returncode != 0, "host verify passed without the GOVERNANCE_ROOT Read allow rule", failures)
        upgraded = run(["host", "update", "--host", "claude", "-y"], env=env)
        if require_ok(upgraded, "host update of a pre-locator-rule Claude install failed", failures):
            upgraded_allow = json.loads((claude / "settings.json").read_text(encoding="utf-8"))["permissions"]["allow"]
            check(expected_locator_rule in upgraded_allow, "host update did not add the GOVERNANCE_ROOT Read allow rule", failures)

        verified = run(
            [
                "host", "verify", "--host", "all",
            ],
            env=env,
        )
        require_ok(verified, "host verification failed", failures)

        # Update uses the same code path and restores current version state.
        codex_state_path = codex / ".sittelle-engineering-governance.json"
        codex_state = json.loads(codex_state_path.read_text(encoding="utf-8"))
        codex_state["version"] = "0.0.0-test"
        codex_state["framework"] = "codex-engineering-governance"
        codex_state_path.write_text(json.dumps(codex_state, indent=2) + "\n", encoding="utf-8", newline="\n")
        updated_host = run(
            [
                "host", "update", "--host", "codex", "-y",
            ],
            env=env,
        )
        if require_ok(updated_host, "host update failed", failures):
            updated_state = json.loads(codex_state_path.read_text(encoding="utf-8"))
            check(updated_state.get("version") == VERSION, "host update did not restore current version state", failures)
            check(updated_state.get("framework") == "sittelle-engineering-governance", "host update did not migrate the legacy framework identifier", failures)

        # User changes outside the managed blocks after install.
        with (codex / "AGENTS.md").open("a", encoding="utf-8", newline="\n") as f:
            f.write("\nAFTER_CODEX_INSTALL\n")
        with (claude / "CLAUDE.md").open("a", encoding="utf-8", newline="\n") as f:
            f.write("\nAFTER_CLAUDE_INSTALL\n")

        removed = run(
            [
                "host", "uninstall", "--host", "all", "-y",
            ],
            env=env,
        )
        if not require_ok(removed, "host uninstall all failed", failures):
            return

        codex_text = (codex / "AGENTS.md").read_text(encoding="utf-8")
        claude_text = (claude / "CLAUDE.md").read_text(encoding="utf-8")
        check(
            "KEEP_CODEX" in codex_text
            and "AFTER_CODEX_INSTALL" in codex_text
            and HOST_BEGIN not in codex_text,
            "Codex uninstall did not preserve unrelated user content",
            failures,
        )
        check(
            "KEEP_CLAUDE" in claude_text
            and "AFTER_CLAUDE_INSTALL" in claude_text
            and HOST_BEGIN not in claude_text,
            "Claude uninstall did not preserve unrelated user content",
            failures,
        )
        settings = json.loads((claude / "settings.json").read_text(encoding="utf-8"))
        check(settings.get("model") == "user-choice", "Claude uninstall changed user model", failures)
        check(
            settings.get("permissions", {}).get("deny") == ["Read(.env)"],
            "Claude uninstall changed user deny rules",
            failures,
        )
        check(
            settings.get("permissions", {}).get("allow") == ["Bash(git status)"],
            "Claude uninstall did not restore pre-existing user allow rules",
            failures,
        )
        check(
            expected_rule not in settings.get("permissions", {}).get("allow", []),
            "Claude uninstall retained installer-added governance Read allow rule",
            failures,
        )
        check(
            expected_locator_rule not in settings.get("permissions", {}).get("allow", []),
            "Claude uninstall retained installer-added GOVERNANCE_ROOT Read allow rule",
            failures,
        )

        # A pre-ADR-0005 install carried a host-level kernel block. `host update`
        # removes exactly that recorded block and keeps the user's own text.
        installed_again = run(["host", "install", "--host", "codex", "-y"], env=env)
        if not require_ok(installed_again, "Codex reinstall failed", failures):
            return
        agents = codex / "AGENTS.md"
        state_path = codex / ".sittelle-engineering-governance.json"
        old_block = f"{HOST_BEGIN}\n# Legacy host kernel\n{HOST_END}"

        def plant_old_install(block_text: str) -> str:
            text = agents.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + block_text + "\n"
            agents.write_text(text, encoding="utf-8", newline="\n")
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["managed_sha256"] = __import__("hashlib").sha256(old_block.encode("utf-8")).hexdigest()
            state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8", newline="\n")
            return text

        plant_old_install(old_block)
        stale = run(["host", "verify", "--host", "codex"], env=env)
        check(stale.returncode != 0, "host verify passed with a host-level kernel block still installed", failures)
        migrated = run(["host", "update", "--host", "codex", "-y"], env=env)
        if require_ok(migrated, "host update of a pre-ADR-0005 install failed", failures):
            migrated_text = agents.read_text(encoding="utf-8")
            check(HOST_BEGIN not in migrated_text, "host update did not remove the host-level kernel block", failures)
            check("KEEP_CODEX" in migrated_text and "AFTER_CODEX_INSTALL" in migrated_text,
                  "host update removed user text along with the kernel block", failures)
            check(json.loads(state_path.read_text(encoding="utf-8")).get("managed_sha256") is None,
                  "host update still records a host-level kernel block", failures)

        # An edited host-level block must fail closed rather than be removed.
        modified = plant_old_install(old_block.replace("# Legacy host kernel", "# Legacy host kernel\nUSER_EDIT_INSIDE_MANAGED_BLOCK"))
        refused = run(["host", "update", "--host", "codex", "-y"], env=env)
        check(refused.returncode != 0, "modified host-level kernel block was removed", failures)
        check(
            "refusing to remove user-modified content" in refused.stderr,
            "modified host-level block refusal was not explicit",
            failures,
        )
        check(agents.read_text(encoding="utf-8") == modified, "refused update still mutated AGENTS.md", failures)


def project_agents_layout(failures: list[str]) -> None:
    """ADR 0005 migration: the managed block moves to the top (Codex truncates
    from the end); unedited framework-authored project text is refreshed, edited
    text is preserved."""
    import hashlib
    import importlib.util

    spec = importlib.util.spec_from_file_location("governance_under_test", MANAGER)
    gov = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = gov  # dataclasses resolve their module during class creation
    spec.loader.exec_module(gov)
    template = (ROOT / "templates" / "repository" / "AGENTS.md").read_text(encoding="utf-8")
    block = gov.PROJECT_RE.search(template).group(0)
    old_remainder = "# Repository Engineering Instructions\n\nOld framework-authored project text."
    old_layout = f"{old_remainder}\n\n{PROJECT_BEGIN}\nold block\n<!-- END ENGINEERING-GOVERNANCE-MANAGED -->\n"
    gov.FRAMEWORK_AUTHORED_AGENTS_REMAINDERS = frozenset(
        {hashlib.sha256(gov.agents_remainder(old_layout).encode("utf-8")).hexdigest()}
    )

    refreshed = gov.compose_project_agents(old_layout, block, template)
    check(refreshed.startswith(block), "project update did not move the managed block to the top", failures)
    check("Old framework-authored project text" not in refreshed, "unedited framework-authored project text was not refreshed", failures)
    check(gov.agents_remainder(refreshed) == gov.agents_remainder(template), "refreshed project text is not the current template's", failures)

    edited = old_layout.replace("Old framework-authored project text.", "Team-specific rule we wrote ourselves.")
    kept = gov.compose_project_agents(edited, block, template)
    check(kept.startswith(block), "managed block not at top for an edited project file", failures)
    check("Team-specific rule we wrote ourselves." in kept, "project update discarded project-owned text", failures)
    check(gov.compose_project_agents(kept, block, template) == kept, "project update is not idempotent", failures)


def host_binary_independence(failures: list[str]) -> None:
    """Host adapter setup manages files/config only; host binaries are not prerequisites."""
    with tempfile.TemporaryDirectory(prefix="governance-no-host-binaries-") as td:
        base = Path(td)
        env = os.environ.copy()
        env["CODEX_HOME"] = str(base / "codex")
        env["CLAUDE_CONFIG_DIR"] = str(base / "claude")
        env["PATH"] = ""

        installed = run(
            ["host", "install", "--host", "all", "-y"],
            env=env,
        )
        if not require_ok(
            installed,
            "host adapters required external host executables",
            failures,
        ):
            return

        check(
            "Codex: adapter not configured" in installed.stdout
            and "Claude Code: adapter not configured" in installed.stdout,
            "host install preview does not identify adapter state explicitly",
            failures,
        )

        status = run(
            ["host", "status", "--host", "all"],
            env=env,
        )
        if not require_ok(status, "binary-independent host status failed", failures):
            return

        check(
            f"Codex: adapter installed {VERSION}" in status.stdout,
            "Codex status does not report adapter installation explicitly",
            failures,
        )
        check(
            f"Claude Code: adapter installed {VERSION}" in status.stdout,
            "Claude status does not report adapter installation explicitly",
            failures,
        )

        verified = run(
            ["host", "verify", "--host", "all"],
            env=env,
        )
        require_ok(
            verified,
            "host adapter verification required external host executables",
            failures,
        )


def ownership_and_legacy_cycle(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="governance-ownership-") as td:
        base = Path(td)

        # A matching pre-existing locator may be reused but must never be claimed/deleted.
        claude = base / "claude"
        claude.mkdir()
        claude_env = os.environ.copy()
        claude_env["CLAUDE_CONFIG_DIR"] = str(claude)
        locator = claude / "GOVERNANCE_ROOT"
        locator.write_text(str(ROOT.resolve()), encoding="utf-8", newline="\n")
        installed = run([
            "host", "install", "--host", "claude", "-y",
        ], env=claude_env)
        if require_ok(installed, "install with pre-existing locator failed", failures):
            state = json.loads((claude / ".sittelle-engineering-governance.json").read_text(encoding="utf-8"))
            check(state.get("locator_created") is False, "pre-existing locator was incorrectly claimed", failures)
            removed = run([
                "host", "uninstall", "--host", "claude", "-y",
            ], env=claude_env)
            if require_ok(removed, "uninstall with pre-existing locator failed", failures):
                check(locator.exists(), "uninstall deleted pre-existing locator", failures)
                check(locator.read_text(encoding="utf-8") == str(ROOT.resolve()), "uninstall changed pre-existing locator", failures)

        # A pre-existing empty settings file must remain user-owned after uninstall.
        empty = base / "claude-empty-settings"
        empty.mkdir()
        (empty / "settings.json").write_text("{}\n", encoding="utf-8", newline="\n")
        empty_env = os.environ.copy()
        empty_env["CLAUDE_CONFIG_DIR"] = str(empty)
        installed_empty = run(["host", "install", "--host", "claude", "-y"], env=empty_env)
        if require_ok(installed_empty, "install with pre-existing empty Claude settings failed", failures):
            removed_empty = run(["host", "uninstall", "--host", "claude", "-y"], env=empty_env)
            if require_ok(removed_empty, "uninstall with pre-existing empty Claude settings failed", failures):
                check((empty / "settings.json").is_file(), "uninstall deleted pre-existing empty Claude settings file", failures)
                check(json.loads((empty / "settings.json").read_text(encoding="utf-8")) == {}, "uninstall did not restore empty Claude settings structure", failures)

        # Legacy Codex migration is allowed only when ownership is provable byte-for-byte.
        old_root = base / "legacy-framework"
        (old_root / "codex-home").mkdir(parents=True)
        legacy_kernel = "# Legacy framework-owned Codex kernel\n"
        (old_root / "codex-home" / "AGENTS.md").write_text(legacy_kernel, encoding="utf-8", newline="\n")
        legacy_home = base / "legacy-codex-home"
        legacy_home.mkdir()
        legacy_env = os.environ.copy()
        legacy_env["CODEX_HOME"] = str(legacy_home)
        (legacy_home / "AGENTS.md").write_text(legacy_kernel, encoding="utf-8", newline="\n")
        (legacy_home / "GOVERNANCE_ROOT").write_text(str(old_root.resolve()), encoding="utf-8", newline="\n")
        migrated = run([
            "host", "update", "--host", "codex", "-y",
        ], env=legacy_env)
        if require_ok(migrated, "legacy Codex migration failed", failures):
            check(not (legacy_home / "AGENTS.md").exists(), "legacy Codex migration left the provably framework-owned kernel in user scope", failures)
            check((legacy_home / ".sittelle-engineering-governance.json").exists(), "legacy Codex migration did not create ownership state", failures)

        # An unprovable legacy-looking pair must fail closed.
        unknown = base / "unknown-codex-home"
        unknown.mkdir()
        unknown_env = os.environ.copy()
        unknown_env["CODEX_HOME"] = str(unknown)
        (unknown / "AGENTS.md").write_text("# User-owned unknown instructions\n", encoding="utf-8", newline="\n")
        (unknown / "GOVERNANCE_ROOT").write_text(str(old_root.resolve()), encoding="utf-8", newline="\n")
        refused = run([
            "host", "install", "--host", "codex", "-y",
        ], env=unknown_env)
        check(refused.returncode != 0, "unprovable legacy Codex state was taken over", failures)
        check("manual review is required" in refused.stderr, "unprovable legacy refusal was not explicit", failures)


def project_cycle(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="governance-project-") as td:
        base = Path(td)
        parent = base / "projects"
        parent.mkdir()

        # New: preview/decline is non-mutating, -y applies.
        target = parent / "Demo"
        declined = run(
            [
                "project", "new",
                "--parent", str(parent),
                "--name", "Demo",
                "--no-git-init",
            ],
            input_text="n\n",
        )
        check(declined.returncode == 0 and not target.exists(), "declined New mutated target", failures)

        created = run(
            [
                "project", "new",
                "--parent", str(parent),
                "--name", "Demo",
                "--no-git-init",
                "-y",
            ]
        )
        if not require_ok(created, "project New failed", failures):
            return
        for rel in ("AGENTS.md", "CLAUDE.md", "project-governance.yml", "verification-plan.json"):
            check((target / rel).is_file(), f"New missing {rel}", failures)
        check(
            PROJECT_BEGIN in (target / "AGENTS.md").read_text(encoding="utf-8"),
            "New AGENTS managed block missing",
            failures,
        )
        check(
            CLAUDE_BEGIN in (target / "CLAUDE.md").read_text(encoding="utf-8")
            and "@AGENTS.md" in (target / "CLAUDE.md").read_text(encoding="utf-8"),
            "New Claude adapter missing",
            failures,
        )
        check(
            not any((target / "src").iterdir()) and not any((target / "tests").iterdir()),
            "New generated application content",
            failures,
        )

        # Update: preserve project-owned host text and established technology baseline.
        agents = target / "AGENTS.md"
        claude = target / "CLAUDE.md"
        manifest = target / "project-governance.yml"
        agents.write_text(
            agents.read_text(encoding="utf-8") + "\nLOCAL_AGENT_KEEP\n",
            encoding="utf-8",
            newline="\n",
        )
        claude.write_text(
            claude.read_text(encoding="utf-8") + "\nLOCAL_CLAUDE_KEEP\n",
            encoding="utf-8",
            newline="\n",
        )
        m = manifest.read_text(encoding="utf-8")
        m = m.replace(f'baseline: "{VERSION}"', 'baseline: "0.4.0"', 1)
        m = m.replace('state: "UNESTABLISHED"', 'state: "ESTABLISHED"', 1)
        m = m.replace(
            'record: "docs/design.md#technology-baseline"',
            'record: "docs/design.md#approved-technology-baseline"',
            1,
        )
        manifest.write_text(m, encoding="utf-8", newline="\n")

        updated = run(["project", "update", "--project", str(target), "-y"])
        if not require_ok(updated, "project update failed", failures):
            return
        new_agents = agents.read_text(encoding="utf-8")
        new_claude = claude.read_text(encoding="utf-8")
        new_manifest = manifest.read_text(encoding="utf-8")
        check("LOCAL_AGENT_KEEP" in new_agents, "Update lost AGENTS custom content", failures)
        check("LOCAL_CLAUDE_KEEP" in new_claude, "Update lost CLAUDE custom content", failures)
        check(f'baseline: "{VERSION}"' in new_manifest, "Update did not repin baseline", failures)
        check('state: "ESTABLISHED"' in new_manifest, "Update changed established Technology Baseline", failures)
        check(
            'record: "docs/design.md#approved-technology-baseline"' in new_manifest,
            "Update changed Technology Baseline record",
            failures,
        )

        # Adopt: preserve existing host files and mark reconciliation.
        existing = base / "existing"
        existing.mkdir()
        (existing / "keep.txt").write_text("v1\n", encoding="utf-8")
        (existing / "AGENTS.md").write_text(
            "# Existing AGENTS\n\nADOPT_AGENT_KEEP\n", encoding="utf-8", newline="\n"
        )
        (existing / "CLAUDE.md").write_text(
            "# Existing CLAUDE\n\nADOPT_CLAUDE_KEEP\n", encoding="utf-8", newline="\n"
        )
        init_clean_git(existing)

        adopted = run(["project", "adopt", "--project", str(existing), "-y"])
        if not require_ok(adopted, "project Adopt failed", failures):
            return
        check(
            "ADOPT_AGENT_KEEP" in (existing / "AGENTS.md").read_text(encoding="utf-8"),
            "Adopt lost existing AGENTS content",
            failures,
        )
        check(
            "ADOPT_CLAUDE_KEEP" in (existing / "CLAUDE.md").read_text(encoding="utf-8"),
            "Adopt lost existing CLAUDE content",
            failures,
        )
        adopted_manifest = (existing / "project-governance.yml").read_text(encoding="utf-8")
        check(
            'adoption:\n  state: "RECONCILIATION_REQUIRED"' in adopted_manifest,
            "Adopt did not record reconciliation state",
            failures,
        )
        check(
            'technology_baseline:\n  state: "RECONCILIATION_REQUIRED"' in adopted_manifest,
            "Adopt did not require Technology Baseline reconciliation",
            failures,
        )

        # Dirty repository is a hard refusal; -y must not bypass it.
        dirty = base / "dirty"
        dirty.mkdir()
        (dirty / "keep.txt").write_text("v1\n", encoding="utf-8")
        init_clean_git(dirty)
        (dirty / "keep.txt").write_text("dirty\n", encoding="utf-8")
        refused = run(["project", "adopt", "--project", str(dirty), "-y"])
        check(refused.returncode != 0, "-y bypassed dirty-worktree safety", failures)
        check(
            not (dirty / "project-governance.yml").exists(),
            "dirty Adopt mutated project before refusal",
            failures,
        )


def platform_contract(mode: str, failures: list[str]) -> None:
    if mode == "windows":
        check(os.name == "nt", "Windows lifecycle evidence ran on non-Windows OS", failures)
    elif mode == "posix":
        check(os.name != "nt", "POSIX lifecycle evidence ran on Windows", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("common", "windows", "posix"), required=True)
    args = parser.parse_args()

    failures: list[str] = []
    platform_contract(args.mode, failures)
    host_cycle(failures)
    host_binary_independence(failures)
    ownership_and_legacy_cycle(failures)
    project_agents_layout(failures)
    project_cycle(failures)

    if failures:
        print(f"Unified governance management regression ({args.mode}): FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Unified governance management regression ({args.mode}): PASS")
    print("- host install/update/verify/uninstall: PASS")
    print("- host binaries are not adapter-install prerequisites: PASS")
    print("- custom user instruction/settings preservation: PASS")
    print("- managed-content ownership refusal: PASS")
    print("- pre-existing locator + legacy Codex ownership migration: PASS")
    print("- project AGENTS.md layout migration (block first, unedited text refreshed, edits kept): PASS")
    print("- project New/Adopt/Update/Verify lifecycle: PASS")
    print("- -y confirms only; safety checks remain active: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
