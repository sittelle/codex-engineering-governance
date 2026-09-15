#!/usr/bin/env python3
"""Acquire and install a reviewed, checksum-locked VM evaluation toolset.

The lock is supplied outside the framework repository.  This utility never
accepts license terms, signs in to an AI service, initializes Git, or replaces
an existing artifact.  Installation is opt-in via --apply.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Error(RuntimeError):
    pass


HEX = set("0123456789abcdef")
KINDS = {"windows-exe", "ubuntu-deb", "vsix"}
UNATTENDED_LICENSE_MARKERS = ("accept", "eula", "quiet", "silent")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_platform() -> str:
    system = platform.system()
    if system not in {"Windows", "Linux"}:
        raise Error("evaluation VM bootstrap supports Windows and Ubuntu Linux only")
    return system


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value.lower()) <= HEX


def load_lock(path: Path, target: str) -> tuple[Path, list[dict]]:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise Error("bootstrap lock file was not found")
    try:
        lock = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Error("bootstrap lock is not valid JSON") from exc
    if lock.get("schema_version") != "1" or lock.get("kind") != "EVALUATION_VM_BOOTSTRAP_LOCK":
        raise Error("unsupported bootstrap lock schema")
    artifacts = lock.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise Error("bootstrap lock has no artifacts")
    selected: list[dict] = []
    seen: set[str] = set()
    for item in artifacts:
        if not isinstance(item, dict):
            raise Error("bootstrap lock artifact is not an object")
        required = ("id", "platform", "kind", "version", "filename", "url", "sha256")
        if any(not isinstance(item.get(key), str) or not item[key] for key in required):
            raise Error("bootstrap lock artifact has missing required fields")
        if item["kind"] not in KINDS or item["platform"] not in {"Windows", "Linux"}:
            raise Error("bootstrap lock artifact has unsupported platform or kind")
        filename = Path(item["filename"])
        if filename.name != item["filename"] or item["filename"] in {".", ".."}:
            raise Error("bootstrap artifact filename must be a single safe filename")
        if not item["url"].startswith("https://") or not is_sha256(item["sha256"]):
            raise Error("bootstrap artifacts require HTTPS URLs and SHA-256 pins")
        if item["kind"] == "windows-exe":
            reviewed_install_args(item)
        if item["id"] in seen:
            raise Error("bootstrap lock contains duplicate artifact IDs")
        seen.add(item["id"])
        if item["platform"] == target:
            selected.append(item)
    if not selected:
        raise Error(f"bootstrap lock has no artifacts for {target}")
    return path, selected


def select_artifacts(artifacts: list[dict], selected_ids: list[str]) -> list[dict]:
    if not selected_ids:
        return artifacts
    requested = set(selected_ids)
    available = {item["id"] for item in artifacts}
    missing = requested - available
    if missing:
        raise Error("requested artifact is not available for this platform: " + ", ".join(sorted(missing)))
    return [item for item in artifacts if item["id"] in requested]


def reviewed_install_args(item: dict) -> list[str]:
    args = item.get("install_args")
    if not isinstance(args, list) or not all(isinstance(value, str) for value in args):
        raise Error("windows-exe requires reviewed install_args in the lock")
    if any(marker in value.lower() for value in args for marker in UNATTENDED_LICENSE_MARKERS):
        raise Error("windows-exe install_args may not suppress or pre-accept licence prompts")
    return args


def safe_cache(cache: Path, create: bool) -> Path:
    cache = cache.expanduser().resolve()
    if cache.exists():
        if not cache.is_dir():
            raise Error("artifact cache exists but is not a directory")
        return cache
    if not create or not cache.parent.is_dir():
        raise Error("artifact cache must exist, or be a new directory below an existing parent")
    cache.mkdir()
    return cache


def artifact_path(cache: Path, item: dict) -> Path:
    return cache / item["filename"]


def verify_cached(cache: Path, artifacts: list[dict]) -> list[Path]:
    paths: list[Path] = []
    for item in artifacts:
        path = artifact_path(cache, item)
        if not path.is_file() or path.is_symlink():
            raise Error(f"missing regular cached artifact: {item['filename']}")
        if sha256_file(path) != item["sha256"].lower():
            raise Error(f"SHA-256 mismatch for cached artifact: {item['filename']}")
        paths.append(path)
    return paths


def fetch(cache: Path, artifacts: list[dict]) -> None:
    cache = safe_cache(cache, create=True)
    for item in artifacts:
        target = artifact_path(cache, item)
        if target.exists() or target.is_symlink():
            if not target.is_file() or target.is_symlink() or sha256_file(target) != item["sha256"].lower():
                raise Error(f"refusing existing mismatched artifact: {item['filename']}")
            print(f"Verified cached artifact: {item['id']} {item['version']}")
            continue
        temporary = cache / (item["filename"] + ".partial")
        if temporary.exists() or temporary.is_symlink():
            raise Error(f"refusing existing partial artifact: {temporary.name}")
        print(f"Downloading {item['id']} {item['version']}...")
        request = urllib.request.Request(item["url"], headers={"User-Agent": "sittelle-engineering-governance-vm-bootstrap/2"})
        try:
            with urllib.request.urlopen(request, timeout=120) as response, temporary.open("xb") as output:
                shutil.copyfileobj(response, output)
        except Exception as exc:
            if temporary.exists():
                temporary.unlink()
            raise Error(f"download failed for {item['id']}") from exc
        if sha256_file(temporary) != item["sha256"].lower():
            temporary.unlink()
            raise Error(f"download SHA-256 mismatch for {item['id']}")
        temporary.rename(target)
        print(f"Downloaded and verified: {item['id']} {item['version']}")


def run_install(item: dict, artifact: Path, vscode: str | None, profile: Path | None) -> None:
    kind = item["kind"]
    if kind == "windows-exe":
        if platform.system() != "Windows":
            raise Error("windows-exe artifact selected outside Windows")
        command = [str(artifact), *reviewed_install_args(item)]
    elif kind == "ubuntu-deb":
        if platform.system() != "Linux":
            raise Error("ubuntu-deb artifact selected outside Linux")
        command = ["sudo", "apt", "install", str(artifact)]
    else:
        if not vscode or profile is None:
            raise Error("VSIX installation requires --vscode-command and --vscode-user-data-dir")
        profile = profile.expanduser().resolve()
        marker = profile / ".manual-vscode-test-profile.json"
        if not marker.is_file():
            raise Error("VSIX installation requires a separately initialized test profile")
        extensions = profile / "extensions"
        command = [vscode, "--user-data-dir", str(profile), "--extensions-dir", str(extensions), "--install-extension", str(artifact)]
    print("Running reviewed installer: " + item["id"] + " " + item["version"])
    result = subprocess.run(command, check=False)
    if result.returncode:
        raise Error(f"installer failed: {item['id']} (exit {result.returncode})")


def initialize_latest_profile(profile: Path) -> Path:
    profile = profile.expanduser().resolve()
    marker = profile / ".manual-vscode-test-profile.json"
    if profile.exists():
        if not profile.is_dir() or not marker.is_file():
            raise Error("latest bootstrap profile must be new or an initialized dedicated test profile")
        return profile
    if not profile.parent.is_dir() or profile == ROOT or ROOT in profile.parents:
        raise Error("latest bootstrap profile must be a new directory outside the framework source")
    profile.mkdir()
    marker.write_text(json.dumps({"schema_version": "1", "kind": "MANUAL_VSCODE_TEST_PROFILE"}) + "\n", encoding="utf-8")
    return profile


def latest_linux(host: str, profile: Path) -> None:
    if platform.system() != "Linux":
        raise Error("latest Linux bootstrap must run on Ubuntu Linux")
    apt = shutil.which("apt")
    snap = shutil.which("snap")
    if not apt or not snap:
        raise Error("latest Ubuntu bootstrap requires apt and snap")
    profile = initialize_latest_profile(profile)
    for command in (
        ["sudo", apt, "update"],
        ["sudo", apt, "install", "python3", "python3-venv", "wl-clipboard", "xclip"],
    ):
        if subprocess.run(command, check=False).returncode:
            raise Error("latest Ubuntu prerequisite installation failed")
    code = shutil.which("code") or "/snap/bin/code"
    if not Path(code).is_file():
        if subprocess.run(["sudo", snap, "install", "code", "--classic"], check=False).returncode:
            raise Error("latest VS Code installation failed")
    code = shutil.which("code") or "/snap/bin/code"
    if not Path(code).is_file():
        raise Error("VS Code command is unavailable after installation; start a new shell and retry")
    extensions = profile / "extensions"
    extension_ids = ["openai.chatgpt", "anthropic.claude-code"] if host == "all" else ["openai.chatgpt" if host == "codex" else "anthropic.claude-code"]
    for extension in extension_ids:
        if subprocess.run([code, "--user-data-dir", str(profile), "--extensions-dir", str(extensions), "--install-extension", extension], check=False).returncode:
            raise Error(f"latest VS Code extension installation failed: {extension}")
    if subprocess.run([sys.executable, str(ROOT / "governance.py"), "host", "install", "--host", host, "-y"], cwd=ROOT, check=False).returncode:
        raise Error("framework host-adapter configuration failed")
    print("Latest Ubuntu evaluation VM bootstrap: PASS")
    print("Interactive account sign-in, model choice, and licence acceptance: NOT PERFORMED")


def latest_plan(host: str) -> None:
    target = current_platform()
    print(f"Latest evaluation VM plan: {target}; host={host}")
    if target == "Windows":
        print("- install latest Python and VS Code through Windows winget")
    else:
        print("- install current Ubuntu packages: python3, python3-venv, wl-clipboard, xclip")
        print("- install latest VS Code through snap")
    print("- install latest selected Codex/Claude VS Code extension into a dedicated test profile")
    print("- configure the selected framework host adapter")
    print("- account sign-in, model selection, and licence acceptance remain interactive")


def self_test() -> int:
    try:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            payload = b"verified installer bytes\n"
            checksum = hashlib.sha256(payload).hexdigest()
            lock = root / "lock.json"
            lock.write_text(json.dumps({"schema_version": "1", "kind": "EVALUATION_VM_BOOTSTRAP_LOCK", "artifacts": [{
                "id": "fixture", "platform": "Windows", "kind": "windows-exe", "version": "1", "filename": "fixture.exe",
                "url": "https://example.invalid/fixture.exe", "sha256": checksum, "install_args": [],
            }]}), encoding="utf-8")
            _, artifacts = load_lock(lock, "Windows")
            cache = root / "cache"
            cache.mkdir()
            (cache / "fixture.exe").write_bytes(payload)
            verify_cached(cache, artifacts)
            (cache / "fixture.exe").write_bytes(b"tampered")
            try:
                verify_cached(cache, artifacts)
            except Error:
                pass
            else:
                raise Error("tampered artifact was accepted")
    except Error as exc:
        print(f"Evaluation VM bootstrap self-test: FAIL\n- {exc}")
        return 1
    print("Evaluation VM bootstrap self-test: PASS")
    print("- lock schema/platform selection: PASS")
    print("- checksum verification and tamper refusal: PASS")
    print("- installer, downloads, credentials, Git, and system changes: NOT USED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Acquire/install reviewed checksum-locked evaluation VM artifacts.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "fetch", "verify", "install"):
        command = commands.add_parser(name)
        command.add_argument("--lock", required=True, type=Path)
        command.add_argument("--artifact-cache", required=True, type=Path)
        command.add_argument("--artifact", action="append", default=[], help="artifact ID to process; repeat to select a subset")
        if name == "install":
            command.add_argument("--apply", action="store_true")
            command.add_argument("--vscode-command")
            command.add_argument("--vscode-user-data-dir", type=Path)
    latest = commands.add_parser("latest", help="provision current Ubuntu prerequisites; use the PowerShell bootstrap on Windows")
    latest.add_argument("--host", choices=("codex", "claude", "all"), default="all")
    latest.add_argument("--vscode-user-data-dir", required=True, type=Path)
    latest.add_argument("--apply", action="store_true")
    commands.add_parser("self-test")
    args = parser.parse_args()
    if args.command == "self-test":
        return self_test()
    if args.command == "latest":
        latest_plan(args.host)
        if not args.apply:
            print("DRY RUN ONLY. Re-run with --apply after reviewing the plan.")
            return 0
        if current_platform() == "Windows":
            raise Error("run scripts/bootstrap-evaluation-vm.ps1 -Latest -Apply on Windows so Python can be installed first")
        if input("Type APPLY-LATEST-VM-BOOTSTRAP to install current VM prerequisites: ").strip() != "APPLY-LATEST-VM-BOOTSTRAP":
            raise Error("installation confirmation did not match")
        latest_linux(args.host, args.vscode_user_data_dir)
        return 0
    target = current_platform()
    lock, artifacts = load_lock(args.lock, target)
    artifacts = select_artifacts(artifacts, args.artifact)
    print(f"Bootstrap lock: {lock.name} ({sha256_file(lock)})")
    for item in artifacts:
        print(f"- {item['id']} {item['version']} [{item['kind']}]")
    if args.command == "plan":
        print("DRY RUN ONLY. No downloads, installers, credentials, Git, or system changes.")
        return 0
    if args.command == "fetch":
        fetch(args.artifact_cache, artifacts)
        return 0
    cache = safe_cache(args.artifact_cache, create=False)
    paths = verify_cached(cache, artifacts)
    if args.command == "verify":
        print("All cached artifacts match the reviewed lock.")
        return 0
    if not args.apply:
        print("DRY RUN ONLY. Re-run with --apply after reviewing the displayed installers.")
        return 0
    if input("Type APPLY-LOCKED-VM-BOOTSTRAP to install the verified artifacts: ").strip() != "APPLY-LOCKED-VM-BOOTSTRAP":
        raise Error("installation confirmation did not match")
    for index, item in enumerate(artifacts):
        run_install(item, paths[index], args.vscode_command, args.vscode_user_data_dir)
    print("Evaluation VM bootstrap: PASS")
    print("Interactive account sign-in and license acceptance: NOT PERFORMED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Error as exc:
        print(f"Evaluation VM bootstrap: FAIL - {exc}", file=sys.stderr)
        raise SystemExit(1)
