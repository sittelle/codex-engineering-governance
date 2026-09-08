#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

VALID_STAGES = {"quick", "full"}
VALID_RESULTS = {"PASS", "FAIL", "NOT_APPLICABLE", "DID_NOT_EXECUTE"}
DECISIONS = {"REQUIRED", "OPTIONAL", "NOT_APPLICABLE", "UNRESOLVED"}
VALID_CONTEXTS = {"LOCAL", "CI", "SPECIALIZED"}
M_RANK = {"M0": 0, "M1": 1, "M2": 2, "M3": 3}
SA_RANK = {"SA0": 0, "SA1": 1, "SA2": 2, "SA3": 3}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_command(project_root: Path, *args: str, binary: bool = False):
    return subprocess.run(
        ["git", "-C", str(project_root), *args],
        capture_output=True,
        text=not binary,
        timeout=5,
        check=False,
    )


def git_head(project_root: Path) -> str | None:
    try:
        p = git_command(project_root, "rev-parse", "HEAD")
        if p.returncode == 0:
            return p.stdout.strip() or None
    except Exception:
        pass
    return None


def git_worktree_dirty(project_root: Path) -> bool | None:
    try:
        p = git_command(project_root, "status", "--porcelain")
        return bool(p.stdout.strip()) if p.returncode == 0 else None
    except Exception:
        return None


def artifact_identity(path: Path, project_root: Path, dirty: bool | None) -> dict:
    resolved = path.resolve()
    worktree_hash = sha256_file(resolved)
    rel = None
    try:
        rel = resolved.relative_to(project_root.resolve()).as_posix()
    except ValueError:
        pass
    if dirty is False and rel:
        try:
            p = git_command(project_root, "show", f"HEAD:{rel}", binary=True)
            if p.returncode == 0:
                return {
                    "source": "GIT_HEAD",
                    "repository_path": rel,
                    "sha256": sha256_bytes(p.stdout),
                    "working_tree_sha256": worktree_hash,
                }
        except Exception:
            pass
    return {
        "source": "WORKTREE_BYTES",
        "repository_path": rel,
        "sha256": worktree_hash,
        "working_tree_sha256": worktree_hash,
    }


def normalize_os(value: str) -> str:
    aliases = {
        "windows": "Windows",
        "linux": "Linux",
        "darwin": "Darwin",
        "macos": "Darwin",
        "mac": "Darwin",
    }
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("target os must be non-empty")
    return aliases.get(raw.lower(), raw)


def normalize_machine(value: str) -> str:
    raw = str(value or "").strip().lower().replace("-", "_")
    if not raw:
        raise ValueError("target machine must be non-empty")
    aliases = {
        "amd64": "x86_64",
        "x64": "x86_64",
        "x86_64": "x86_64",
        "x86": "x86",
        "i386": "x86",
        "i686": "x86",
        "arm64": "arm64",
        "aarch64": "arm64",
        "armv7l": "armv7",
        "armv7": "armv7",
    }
    return aliases.get(raw, raw)


def actual_execution_target(context: str) -> dict:
    # OS and machine are derived from the host. Callers may choose only the coarse
    # governance execution context; they cannot assert a different host identity.
    return {
        "context": context,
        "os": normalize_os(platform.system()),
        "machine": normalize_machine(platform.machine()),
    }


def normalize_target(target: dict, *, require_machine: bool = False) -> dict:
    if not isinstance(target, dict):
        raise ValueError("required target must be an object")
    context = target.get("context")
    if context not in VALID_CONTEXTS:
        raise ValueError(f"invalid target context: {context}")
    if "os" not in target:
        raise ValueError("required target must declare os")
    out = {"context": context, "os": normalize_os(target.get("os"))}
    machine = target.get("machine")
    if machine is not None:
        out["machine"] = normalize_machine(machine)
    elif require_machine:
        raise ValueError("target machine is required")
    return out


def target_key(target: dict) -> str:
    return json.dumps(target, sort_keys=True, separators=(",", ":"))


def target_matches(actual: dict, required: dict) -> bool:
    if actual.get("context") != required.get("context"):
        return False
    if normalize_os(actual.get("os")) != normalize_os(required.get("os")):
        return False
    if required.get("machine") is not None:
        return normalize_machine(actual.get("machine")) == normalize_machine(required.get("machine"))
    return True


def target_label(target: dict | None) -> str:
    if not target:
        return "unknown-target"
    bits = [str(target.get("context") or "?"), str(target.get("os") or "?")]
    if target.get("machine"):
        bits.append(str(target["machine"]))
    return "/".join(bits)


def normalized_result_policy(check: dict) -> dict:
    p = check.get("result_policy") or {"mode": "STANDARD"}
    mode = p.get("mode", "STANDARD")
    if mode not in {"STANDARD", "DOCUMENTED_EXIT_CODES"}:
        raise ValueError(f"{check['id']}: invalid result_policy mode")
    codes = p.get("did_not_execute_codes", []) or []
    if (
        not isinstance(codes, list)
        or any(not isinstance(x, int) or x <= 0 for x in codes)
        or len(codes) != len(set(codes))
    ):
        raise ValueError(f"{check['id']}: did_not_execute_codes must be unique positive integers")
    reference = (p.get("reference") or "").strip()
    if mode == "STANDARD" and codes:
        raise ValueError(f"{check['id']}: STANDARD policy cannot map nonzero codes to DID_NOT_EXECUTE")
    if mode == "DOCUMENTED_EXIT_CODES":
        if not codes:
            raise ValueError(f"{check['id']}: DOCUMENTED_EXIT_CODES requires did_not_execute_codes")
        if not reference:
            raise ValueError(f"{check['id']}: DOCUMENTED_EXIT_CODES requires a durable contract reference")
    return {"mode": mode, "did_not_execute_codes": codes, "reference": reference or None}


def normalized_execution(check: dict, plan_version: str) -> dict:
    e = check.get("execution") or {
        "allowed_contexts": ["LOCAL", "CI", "SPECIALIZED"],
        "required_contexts": ["ANY"],
    }
    allowed = e.get("allowed_contexts")
    required = e.get("required_contexts")
    if (
        not isinstance(allowed, list)
        or not allowed
        or not set(allowed).issubset(VALID_CONTEXTS)
        or len(allowed) != len(set(allowed))
    ):
        raise ValueError(f"{check['id']}: invalid execution.allowed_contexts")
    if not isinstance(required, list) or not required or len(required) != len(set(required)):
        raise ValueError(f"{check['id']}: invalid execution.required_contexts")
    if "ANY" in required and len(required) != 1:
        raise ValueError(f"{check['id']}: ANY must be the sole required_context")
    specific = set(required) - {"ANY"}
    if not specific.issubset(VALID_CONTEXTS):
        raise ValueError(f"{check['id']}: invalid required execution context")
    if specific and not specific.issubset(set(allowed)):
        raise ValueError(f"{check['id']}: required contexts must be allowed contexts")

    targets_raw = e.get("required_targets")
    if plan_version == "2":
        if targets_raw is not None:
            raise ValueError(f"{check['id']}: required_targets requires verification-plan schema v3")
        targets = None
    else:
        targets = None
        if targets_raw is not None:
            if not isinstance(targets_raw, list) or not targets_raw:
                raise ValueError(f"{check['id']}: execution.required_targets must be a non-empty array")
            if required == ["ANY"]:
                raise ValueError(f"{check['id']}: ANY is invalid when required_targets is present")
            targets = [normalize_target(t) for t in targets_raw]
            keys = [target_key(t) for t in targets]
            if len(keys) != len(set(keys)):
                raise ValueError(f"{check['id']}: duplicate required target")
            target_contexts = {t["context"] for t in targets}
            if not target_contexts.issubset(set(allowed)):
                raise ValueError(f"{check['id']}: required target contexts must be allowed contexts")
            if target_contexts != set(required):
                raise ValueError(
                    f"{check['id']}: distinct required target contexts must exactly match required_contexts"
                )
    return {"allowed_contexts": allowed, "required_contexts": required, "required_targets": targets}


def _validate_plan_common(data: dict, version: str) -> None:
    if data.get("schema_version") != version:
        raise ValueError(f"not schema v{version}")
    if not isinstance(data.get("project"), str) or not data["project"]:
        raise ValueError("project must be a non-empty string")
    assurance = data.get("assurance")
    if not isinstance(assurance, dict):
        raise ValueError("assurance object is required")
    if assurance.get("maturity") not in M_RANK:
        raise ValueError("invalid assurance.maturity")
    if assurance.get("level") not in SA_RANK:
        raise ValueError("invalid assurance.level")
    if not isinstance(assurance.get("facts"), dict):
        raise ValueError("assurance.facts must be an object")
    caps = assurance.get("capabilities")
    if not isinstance(caps, list):
        raise ValueError("assurance.capabilities must be an array")
    cap_ids = set()
    for cap in caps:
        for key in ("id", "decision", "checks"):
            if key not in cap:
                raise ValueError(f"capability missing required field: {key}")
        if cap["id"] in cap_ids:
            raise ValueError(f"duplicate capability id: {cap['id']}")
        cap_ids.add(cap["id"])
        if cap["decision"] not in DECISIONS:
            raise ValueError(f"{cap['id']}: invalid decision")
        if not isinstance(cap["checks"], list):
            raise ValueError(f"{cap['id']}: checks must be an array")
    checks = data.get("checks")
    if not isinstance(checks, list):
        raise ValueError("checks must be an array")
    ids = set()
    for check in checks:
        for key in ("id", "stages", "command"):
            if key not in check:
                raise ValueError(f"check missing required field: {key}")
        if check["id"] in ids:
            raise ValueError(f"duplicate check id: {check['id']}")
        ids.add(check["id"])
        if not isinstance(check["command"], list) or not check["command"]:
            raise ValueError(f"{check['id']}: command must be a non-empty argv array")
        if not set(check["stages"]).issubset(VALID_STAGES):
            raise ValueError(f"{check['id']}: invalid stage")
        normalized_result_policy(check)
        normalized_execution(check, version)


def validate_v2_plan(data: dict) -> None:
    _validate_plan_common(data, "2")


def validate_v3_plan(data: dict) -> None:
    _validate_plan_common(data, "3")


def load_plan(path: Path) -> dict:
    data = load_json(path)
    version = data.get("schema_version")
    if version == "2":
        validate_v2_plan(data)
        return data
    if version == "3":
        validate_v3_plan(data)
        return data
    if version == "1":
        if not isinstance(data.get("checks"), list):
            raise ValueError("legacy checks must be an array")
        return data
    raise ValueError("unsupported verification plan schema_version")


def load_baseline(path: Path) -> dict:
    data = load_json(path)
    if data.get("schema_version") != "1" or not isinstance(data.get("capabilities"), list):
        raise ValueError("unsupported assurance baseline")
    return data


def threshold_applies(rule: dict, maturity: str, level: str) -> bool:
    mm = rule.get("minimum_maturity")
    ms = rule.get("minimum_assurance")
    if mm and M_RANK[maturity] < M_RANK[mm]:
        return False
    if ms and SA_RANK[level] < SA_RANK[ms]:
        return False
    return True


def baseline_requirement(cap: dict, maturity: str, level: str, facts: dict) -> str:
    if SA_RANK[level] >= SA_RANK["SA3"]:
        req = cap.get("sa3", cap.get("sa2", cap.get("m1_sa1", "CONDITIONAL")))
    elif SA_RANK[level] >= SA_RANK["SA2"]:
        req = cap.get("sa2", cap.get("m1_sa1", "CONDITIONAL"))
    elif M_RANK[maturity] >= M_RANK["M1"] and SA_RANK[level] >= SA_RANK["SA1"]:
        req = cap.get("m1_sa1", "CONDITIONAL")
    else:
        req = "CONDITIONAL"
    for rule in cap.get("required_if", []):
        if threshold_applies(rule, maturity, level) and facts.get(rule.get("fact")) == rule.get("equals"):
            req = "REQUIRED"
    return req


def capability_preflight(plan: dict, baseline: dict) -> dict:
    if plan.get("schema_version") not in {"2", "3"}:
        return {
            "status": "INCOMPLETE_ASSURANCE",
            "issues": [
                {
                    "code": "LEGACY_PLAN_SCHEMA",
                    "message": "schema-v1 plan cannot establish required-capability completeness; reconcile to schema v2 or v3",
                }
            ],
            "capabilities": [],
        }
    assurance = plan["assurance"]
    maturity = assurance["maturity"]
    level = assurance["level"]
    facts = assurance["facts"]
    declared = {c["id"]: c for c in assurance["capabilities"]}
    checks = {c["id"]: c for c in plan["checks"]}
    issues = []
    rows = []
    baseline_ids = set()
    for cap in baseline["capabilities"]:
        cid = cap["id"]
        baseline_ids.add(cid)
        expected = baseline_requirement(cap, maturity, level, facts)
        dc = declared.get(cid)
        if not dc:
            issues.append(
                {
                    "code": "BASELINE_CAPABILITY_OMITTED",
                    "capability": cid,
                    "message": f"baseline capability {cid} is absent from project inventory",
                }
            )
            rows.append({"id": cid, "baseline": expected, "decision": "MISSING", "status": "INCOMPLETE"})
            continue
        decision = dc["decision"]
        reason = (dc.get("reason") or "").strip()
        mapped = dc.get("checks", [])
        status = "OK"
        if expected == "REQUIRED" and decision != "REQUIRED":
            issues.append(
                {
                    "code": "BASELINE_REQUIRED_DOWNGRADED",
                    "capability": cid,
                    "message": f"{cid} is baseline REQUIRED but project decision is {decision}",
                }
            )
            status = "INCOMPLETE"
        if expected == "CONDITIONAL" and decision == "UNRESOLVED":
            issues.append(
                {
                    "code": "CONDITIONAL_UNRESOLVED",
                    "capability": cid,
                    "message": f"{cid} applicability is unresolved",
                }
            )
            status = "INCOMPLETE"
        if decision == "NOT_APPLICABLE" and not reason:
            issues.append(
                {"code": "N_A_REASON_MISSING", "capability": cid, "message": f"{cid} is NOT_APPLICABLE without rationale"}
            )
            status = "INCOMPLETE"
        if decision == "REQUIRED":
            if not mapped:
                issues.append(
                    {"code": "REQUIRED_CAPABILITY_NO_CHECK", "capability": cid, "message": f"{cid} has no evidence check mapping"}
                )
                status = "INCOMPLETE"
            for check_id in mapped:
                check = checks.get(check_id)
                if check is None:
                    issues.append(
                        {
                            "code": "CAPABILITY_CHECK_MISSING",
                            "capability": cid,
                            "check": check_id,
                            "message": f"{cid} maps to unknown check {check_id}",
                        }
                    )
                    status = "INCOMPLETE"
                elif "full" not in check.get("stages", []):
                    issues.append(
                        {
                            "code": "REQUIRED_CAPABILITY_NOT_IN_FULL",
                            "capability": cid,
                            "check": check_id,
                            "message": f"required {cid} check {check_id} is not in full stage",
                        }
                    )
                    status = "INCOMPLETE"
        rows.append({"id": cid, "baseline": expected, "decision": decision, "checks": mapped, "status": status})
    for cid, dc in declared.items():
        if cid in baseline_ids:
            continue
        decision = dc["decision"]
        if decision == "UNRESOLVED":
            issues.append(
                {
                    "code": "PROJECT_CAPABILITY_UNRESOLVED",
                    "capability": cid,
                    "message": f"project-specific capability {cid} is unresolved",
                }
            )
        if decision == "NOT_APPLICABLE" and not (dc.get("reason") or "").strip():
            issues.append(
                {"code": "N_A_REASON_MISSING", "capability": cid, "message": f"{cid} is NOT_APPLICABLE without rationale"}
            )
        if decision == "REQUIRED":
            if not dc.get("checks"):
                issues.append(
                    {
                        "code": "PROJECT_REQUIRED_CAPABILITY_NO_CHECK",
                        "capability": cid,
                        "message": f"project-required {cid} has no evidence check",
                    }
                )
            for check_id in dc.get("checks", []):
                check = checks.get(check_id)
                if check is None or "full" not in check.get("stages", []):
                    issues.append(
                        {
                            "code": "PROJECT_REQUIRED_CAPABILITY_EVIDENCE_MISSING",
                            "capability": cid,
                            "check": check_id,
                            "message": f"project-required {cid} lacks full-stage evidence",
                        }
                    )
    return {"status": "PASS" if not issues else "INCOMPLETE_ASSURANCE", "issues": issues, "capabilities": rows}


def resolve_git_state(project_root: Path) -> tuple[str | None, bool | None]:
    commit = git_head(project_root)
    dirty = git_worktree_dirty(project_root)
    if not commit:
        commit = os.environ.get("GITHUB_SHA")
    return commit, dirty


def result_from_exit(check: dict, code: int) -> tuple[str, str, str | None]:
    policy = normalized_result_policy(check)
    if code == 0:
        return "PASS", "COMPLETED", None
    if policy["mode"] == "DOCUMENTED_EXIT_CODES" and code in policy["did_not_execute_codes"]:
        return "DID_NOT_EXECUTE", "OPERATIONAL_FAILURE", f"tool contract classifies exit {code} as operational nonexecution"
    return "FAIL", "COMPLETED_WITH_FAILURE", None


def result_base(check: dict, plan_version: str, actual_target: dict) -> dict:
    policy = normalized_result_policy(check)
    execution = normalized_execution(check, plan_version)
    base = {
        "id": check["id"],
        "command": check["command"],
        "verified_targets": check.get("verified_targets", []),
        "result_policy": policy,
        "allowed_contexts": execution["allowed_contexts"],
        "required_contexts": execution["required_contexts"],
    }
    if plan_version == "3":
        base["actual_target"] = actual_target
        if execution["required_targets"] is not None:
            base["required_targets"] = execution["required_targets"]
            base["target_match"] = (
                "MATCH" if any(target_matches(actual_target, t) for t in execution["required_targets"]) else "MISMATCH"
            )
        else:
            base["target_match"] = "UNCONSTRAINED"
    return base


def run_check(check: dict, project_root: Path, context: str, plan_version: str, actual_target: dict) -> dict:
    started = time.time()
    execution = normalized_execution(check, plan_version)
    base = result_base(check, plan_version, actual_target)
    if context not in execution["allowed_contexts"]:
        return {
            **base,
            "result": "DID_NOT_EXECUTE",
            "exit_code": None,
            "duration_seconds": 0.0,
            "reason": f"check is assigned to approved context(s): {', '.join(execution['allowed_contexts'])}",
            "resolved_executable": None,
            "execution_disposition": "DEFERRED_TO_APPROVED_ENVIRONMENT",
        }
    if plan_version == "3" and execution["required_targets"] is not None:
        if not any(target_matches(actual_target, t) for t in execution["required_targets"]):
            return {
                **base,
                "result": "DID_NOT_EXECUTE",
                "exit_code": None,
                "duration_seconds": 0.0,
                "reason": f"execution target {target_label(actual_target)} does not match required target(s)",
                "resolved_executable": None,
                "execution_disposition": "ENVIRONMENT_MISMATCH",
            }
    if check["command"][0] == "__NOT_CONFIGURED__":
        return {
            **base,
            "result": "DID_NOT_EXECUTE",
            "exit_code": None,
            "duration_seconds": 0.0,
            "reason": "verification check is not configured",
            "resolved_executable": None,
            "execution_disposition": "NOT_CONFIGURED",
        }
    cwd = project_root
    if check.get("working_directory"):
        cwd = (project_root / check["working_directory"]).resolve()
    env = os.environ.copy()
    env.update(check.get("environment") or {})
    argv = list(check["command"])
    resolved = shutil.which(argv[0], path=env.get("PATH"))
    if not resolved:
        return {
            **base,
            "result": "DID_NOT_EXECUTE",
            "exit_code": None,
            "duration_seconds": round(time.time() - started, 3),
            "reason": f"tool not found: {argv[0]}",
            "resolved_executable": None,
            "execution_disposition": "OPERATIONAL_FAILURE",
        }
    argv[0] = resolved
    try:
        proc = subprocess.run(argv, cwd=str(cwd), env=env, timeout=check.get("timeout_seconds"), check=False)
        result, disp, reason = result_from_exit(check, proc.returncode)
        return {
            **base,
            "result": result,
            "exit_code": proc.returncode,
            "duration_seconds": round(time.time() - started, 3),
            "reason": reason or check.get("reason"),
            "resolved_executable": resolved,
            "execution_disposition": disp,
        }
    except subprocess.TimeoutExpired:
        return {
            **base,
            "result": "DID_NOT_EXECUTE",
            "exit_code": None,
            "duration_seconds": round(time.time() - started, 3),
            "reason": "check timed out",
            "resolved_executable": resolved,
            "execution_disposition": "OPERATIONAL_FAILURE",
        }
    except Exception as exc:
        return {
            **base,
            "result": "DID_NOT_EXECUTE",
            "exit_code": None,
            "duration_seconds": round(time.time() - started, 3),
            "reason": f"runner error: {type(exc).__name__}: {exc}",
            "resolved_executable": resolved,
            "execution_disposition": "OPERATIONAL_FAILURE",
        }


def precondition_result(check: dict, reason: str, plan_version: str, actual_target: dict) -> dict:
    base = result_base(check, plan_version, actual_target)
    return {
        **base,
        "result": "DID_NOT_EXECUTE",
        "exit_code": None,
        "duration_seconds": 0.0,
        "reason": f"verification precondition failed: {reason}",
        "resolved_executable": None,
        "execution_disposition": "PRECONDITION_FAILURE",
    }


def check_satisfied_in_single_report(row: dict, context: str, actual_target: dict, plan_version: str) -> bool:
    if row.get("result") != "PASS":
        return False
    if plan_version == "3" and row.get("required_targets"):
        matches = [t for t in row["required_targets"] if target_matches(actual_target, t)]
        # A single report can fully satisfy a target-aware check only if all of its
        # required targets collapse to the one actual target represented by this report.
        return len(matches) == len(row["required_targets"])
    req = row.get("required_contexts") or ["ANY"]
    if req == ["ANY"]:
        return True
    return len(req) == 1 and req[0] == context


def summarize(
    stage: str,
    preflight: dict,
    results: list[dict],
    required_check_ids: set[str],
    context: str,
    actual_target: dict,
    plan_version: str,
) -> str:
    required_rows = [r for r in results if r["id"] in required_check_ids]
    if any(r["result"] == "FAIL" for r in required_rows):
        return "FAIL"
    if any(r["result"] == "DID_NOT_EXECUTE" for r in required_rows):
        return "INCOMPLETE_ASSURANCE"
    if stage == "full" and preflight["status"] != "PASS":
        return "INCOMPLETE_ASSURANCE"
    if stage == "full" and any(
        not check_satisfied_in_single_report(r, context, actual_target, plan_version) for r in required_rows
    ):
        return "INCOMPLETE_ASSURANCE"
    return "PASS"


def resolve_baseline_path(project_root: Path, explicit: str | None) -> Path | None:
    if explicit:
        p = Path(explicit)
        return p if p.is_absolute() else project_root / p
    managed = project_root / ".governance/assurance-baseline.json"
    if managed.exists():
        return managed
    central = Path(__file__).resolve().parent / "capability-baseline.json"
    return central if central.exists() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=sorted(VALID_STAGES))
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--plan", default="verification-plan.json")
    ap.add_argument("--baseline")
    ap.add_argument("--report")
    ap.add_argument("--execution-context", choices=sorted(VALID_CONTEXTS))
    ap.add_argument("--precondition-failure")
    args = ap.parse_args()

    project_root = Path(args.project_root).resolve()
    plan_path = Path(args.plan)
    plan_path = plan_path if plan_path.is_absolute() else project_root / plan_path
    baseline_path = resolve_baseline_path(project_root, args.baseline)
    context = args.execution_context or ("CI" if os.environ.get("GITHUB_ACTIONS", "").lower() == "true" else "LOCAL")
    actual_target = actual_execution_target(context)

    try:
        plan = load_plan(plan_path)
        if baseline_path is None or not baseline_path.exists():
            raise ValueError("assurance baseline not found")
        baseline = load_baseline(baseline_path)
    except Exception as exc:
        print(f"verification configuration error: {exc}", file=sys.stderr)
        return 3

    plan_version = str(plan.get("schema_version"))
    preflight = capability_preflight(plan, baseline)
    if plan_version in {"2", "3"}:
        selected = [c for c in plan["checks"] if args.stage in c["stages"]]
        cap_by_id = {c["id"]: c for c in plan["assurance"]["capabilities"]}
        required_check_ids: set[str] = set()
        for cap in cap_by_id.values():
            if cap["decision"] == "REQUIRED":
                required_check_ids.update(cap.get("checks", []))
        for c in selected:
            if c["command"][0] == "__NOT_CONFIGURED__":
                required_check_ids.add(c["id"])
    else:
        selected = [c for c in plan.get("checks", []) if args.stage in c.get("stages", [])]
        required_check_ids = {c["id"] for c in selected if c.get("required") and c.get("applicable", True)}

    if not selected:
        print(f"no checks configured for stage {args.stage}", file=sys.stderr)
        return 3
    if args.stage == "full" and preflight["issues"]:
        print("[capability-preflight] INCOMPLETE_ASSURANCE")
        for issue in preflight["issues"]:
            print("  - " + issue["message"])
    print(f"[execution-context] {context}")
    if plan_version == "3":
        print(f"[execution-target] {target_label(actual_target)}")

    results = []
    if args.precondition_failure:
        print(f"[verification-precondition] DID_NOT_EXECUTE ({args.precondition_failure})")
    for check in selected:
        print(f"[{check['id']}]")
        if args.precondition_failure:
            result = precondition_result(check, args.precondition_failure, plan_version, actual_target)
        else:
            result = run_check(check, project_root, context, plan_version, actual_target)
        results.append(result)
        suffix = f" ({result.get('reason')})" if result.get("reason") else ""
        resolved = f" [{result.get('resolved_executable')}]" if result.get("resolved_executable") else ""
        print(f"  -> {result['result']}{resolved}{suffix}")

    overall = summarize(args.stage, preflight, results, required_check_ids, context, actual_target, plan_version)
    commit, dirty = resolve_git_state(project_root)
    plan_identity = artifact_identity(plan_path, project_root, dirty)
    baseline_identity = artifact_identity(baseline_path, project_root, dirty)
    runner_identity = artifact_identity(Path(__file__).resolve(), project_root, dirty)
    identities = {"plan": plan_identity, "assurance_baseline": baseline_identity, "runner": runner_identity}
    environment = {
        "os": normalize_os(platform.system()),
        "release": platform.release(),
        "machine": normalize_machine(platform.machine()),
        "python": platform.python_version(),
    }
    report_schema = "5" if plan_version == "3" else "4"
    report = {
        "schema_version": report_schema,
        "project": plan.get("project"),
        "plan_schema_version": plan_version,
        "stage": args.stage,
        "overall": overall,
        "execution_context": context,
        "plan_sha256": plan_identity["sha256"],
        "assurance_baseline_sha256": baseline_identity["sha256"],
        "runner_sha256": runner_identity["sha256"],
        "artifact_identities": identities,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit,
        "ci_event_sha": os.environ.get("GITHUB_SHA"),
        "git_worktree_dirty": dirty,
        "ci": context == "CI",
        "environment": environment,
        "required_check_ids": sorted(required_check_ids),
        "capability_preflight": preflight,
        "precondition_failure": args.precondition_failure,
        "results": results,
    }
    if report_schema == "5":
        report["execution_target"] = actual_target

    print(f"\nOVERALL: {overall}")
    if args.report:
        rp = Path(args.report)
        rp = rp if rp.is_absolute() else project_root / rp
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if overall == "PASS" else (1 if overall == "FAIL" else 2)


if __name__ == "__main__":
    raise SystemExit(main())
