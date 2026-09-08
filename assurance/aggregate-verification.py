#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

VALID_CONTEXTS = {"LOCAL", "CI", "SPECIALIZED"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_os(value: str) -> str:
    aliases = {"windows": "Windows", "linux": "Linux", "darwin": "Darwin", "macos": "Darwin", "mac": "Darwin"}
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


def normalize_target(target: dict) -> dict:
    if not isinstance(target, dict):
        raise ValueError("target must be an object")
    context = target.get("context")
    if context not in VALID_CONTEXTS:
        raise ValueError(f"invalid target context: {context}")
    if "os" not in target:
        raise ValueError("target os missing")
    out = {"context": context, "os": normalize_os(target.get("os"))}
    if target.get("machine") is not None:
        out["machine"] = normalize_machine(target.get("machine"))
    return out


def target_matches(actual: dict, required: dict) -> bool:
    actual = normalize_target(actual)
    required = normalize_target(required)
    if actual["context"] != required["context"] or actual["os"] != required["os"]:
        return False
    if required.get("machine") is not None:
        return actual.get("machine") == required.get("machine")
    return True


def target_key(target: dict) -> str:
    return json.dumps(normalize_target(target), sort_keys=True, separators=(",", ":"))


def target_label(target: dict | None) -> str:
    if not target:
        return "unknown-target"
    try:
        t = normalize_target(target)
    except Exception:
        return "invalid-target"
    bits = [t["context"], t["os"]]
    if t.get("machine"):
        bits.append(t["machine"])
    return "/".join(bits)


def load(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    if d.get("schema_version") not in {"4", "5"}:
        raise ValueError(f"{path}: report schema 4 or 5 required")
    if d.get("stage") != "full":
        raise ValueError(f"{path}: only full-stage evidence can be aggregated")
    if d.get("schema_version") == "4" and d.get("plan_schema_version") not in {"1", "2"}:
        raise ValueError(f"{path}: report schema 4 cannot establish target-aware plan guarantees")
    if d.get("schema_version") == "5":
        if d.get("plan_schema_version") != "3":
            raise ValueError(f"{path}: report schema 5 requires verification-plan schema 3")
        if not d.get("execution_target"):
            raise ValueError(f"{path}: report schema 5 requires execution_target")
        target = normalize_target(d["execution_target"])
        if target["context"] != d.get("execution_context"):
            raise ValueError(f"{path}: execution_target context disagrees with execution_context")
        env = d.get("environment") or {}
        if normalize_os(env.get("os")) != target["os"] or normalize_machine(env.get("machine")) != target.get("machine"):
            raise ValueError(f"{path}: execution_target disagrees with environment identity")
    return d


def _policy_signature(row: dict, report_schema: str) -> str:
    policy = {
        "required_contexts": row.get("required_contexts") or ["ANY"],
        "allowed_contexts": row.get("allowed_contexts") or ["LOCAL", "CI", "SPECIALIZED"],
        "result_policy": row.get("result_policy") or {"mode": "STANDARD"},
    }
    if report_schema == "5":
        policy["required_targets"] = row.get("required_targets")
    return json.dumps(policy, sort_keys=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("reports", nargs="+")
    ap.add_argument("--output")
    args = ap.parse_args()
    paths = [Path(x).resolve() for x in args.reports]
    try:
        reports = [load(p) for p in paths]
    except Exception as exc:
        print(f"evidence aggregation configuration error: {exc}", file=sys.stderr)
        return 3

    schemas = {r.get("schema_version") for r in reports}
    if len(schemas) != 1:
        print(
            "evidence aggregation configuration error: mixed report schema versions are not aggregatable; v4 evidence cannot satisfy v5 target-aware guarantees",
            file=sys.stderr,
        )
        return 3
    report_schema = next(iter(schemas))
    bundle_schema = "2" if report_schema == "5" else "1"

    issues: list[dict] = []

    def equal_field(field: str, require_non_null: bool = False):
        vals = [r.get(field) for r in reports]
        if require_non_null and any(v in (None, "") for v in vals):
            issues.append({"code": field.upper() + "_MISSING", "message": f"{field} must be present in every report"})
        if len({json.dumps(v, sort_keys=True) for v in vals}) != 1:
            issues.append({"code": field.upper() + "_MISMATCH", "message": f"{field} differs across reports"})

    for f in ("project", "plan_sha256", "assurance_baseline_sha256", "runner_sha256", "required_check_ids"):
        equal_field(f, require_non_null=True)
    equal_field("git_commit", require_non_null=True)

    def canonical_artifact_identities(report: dict) -> dict:
        identities = report.get("artifact_identities") or {}
        out = {}
        for artifact in ("plan", "assurance_baseline", "runner"):
            identity = identities.get(artifact) or {}
            out[artifact] = {
                "source": identity.get("source"),
                "repository_path": identity.get("repository_path"),
                "sha256": identity.get("sha256"),
            }
        return out

    canonical_sets = [canonical_artifact_identities(r) for r in reports]
    if any(
        not item.get(artifact, {}).get("source")
        or not item.get(artifact, {}).get("repository_path")
        or not item.get(artifact, {}).get("sha256")
        for item in canonical_sets
        for artifact in ("plan", "assurance_baseline", "runner")
    ):
        issues.append({
            "code": "ARTIFACT_IDENTITIES_MISSING",
            "message": "canonical artifact identities must include source, repository_path, and sha256 in every report",
        })
    if len({json.dumps(v, sort_keys=True) for v in canonical_sets}) != 1:
        issues.append({
            "code": "ARTIFACT_IDENTITIES_MISMATCH",
            "message": "canonical artifact identity differs across reports",
        })

    identities = reports[0].get("artifact_identities") or {}
    for artifact in ("plan", "assurance_baseline", "runner"):
        identity = identities.get(artifact) or {}
        if identity.get("source") != "GIT_HEAD":
            issues.append(
                {
                    "code": "ARTIFACT_NOT_COMMIT_BOUND",
                    "artifact": artifact,
                    "message": f"{artifact} identity must come from committed Git HEAD for aggregation",
                }
            )
        if not identity.get("repository_path"):
            issues.append(
                {
                    "code": "ARTIFACT_REPOSITORY_PATH_MISSING",
                    "artifact": artifact,
                    "message": f"{artifact} repository path is required for aggregation",
                }
            )
    if any(r.get("git_worktree_dirty") is not False for r in reports):
        issues.append({"code": "DIRTY_OR_UNKNOWN_WORKTREE", "message": "every aggregated report must attest a clean worktree"})
    if any(r.get("capability_preflight", {}).get("status") != "PASS" for r in reports):
        issues.append({"code": "PREFLIGHT_INCOMPLETE", "message": "capability preflight must PASS in every report"})

    required = reports[0].get("required_check_ids") or []
    check_rows = {cid: [] for cid in required}
    for r in reports:
        context = r.get("execution_context")
        if context not in VALID_CONTEXTS:
            issues.append({"code": "INVALID_EXECUTION_CONTEXT", "message": f"invalid report execution context: {context}"})
        report_target = r.get("execution_target") if report_schema == "5" else None
        by_id = {x.get("id"): x for x in r.get("results", [])}
        for cid in required:
            if cid in by_id:
                check_rows[cid].append((context, report_target, by_id[cid]))

    status_rows = []
    any_fail = False
    for cid, rows in check_rows.items():
        if not rows:
            issues.append({"code": "REQUIRED_CHECK_NO_EVIDENCE", "check": cid, "message": f"{cid} has no evidence row"})
            status_rows.append({"id": cid, "status": "INCOMPLETE"})
            continue
        policies = {_policy_signature(row, report_schema) for _, _, row in rows}
        if len(policies) != 1:
            issues.append({"code": "CHECK_POLICY_MISMATCH", "check": cid, "message": f"{cid} execution/result policy differs across reports"})
            status_rows.append({"id": cid, "status": "INCOMPLETE"})
            continue

        required_targets = rows[0][2].get("required_targets") if report_schema == "5" else None
        failed = []
        for ctx, rpt_target, row in rows:
            if row.get("result") != "FAIL":
                continue
            if required_targets:
                actual = row.get("actual_target") or rpt_target
                if not any(target_matches(actual, t) for t in required_targets):
                    issues.append(
                        {
                            "code": "FAIL_OUTSIDE_REQUIRED_TARGET",
                            "check": cid,
                            "message": f"{cid} reports FAIL from non-required target {target_label(actual)}",
                        }
                    )
                    continue
            failed.append((ctx, rpt_target, row))
        if failed:
            any_fail = True
            failure_rows = []
            for ctx, rpt_target, row in failed:
                actual = row.get("actual_target") or rpt_target
                failure_rows.append(
                    {
                        "context": ctx,
                        "target": normalize_target(actual) if actual else None,
                        "exit_code": row.get("exit_code"),
                        "reason": row.get("reason"),
                        "execution_disposition": row.get("execution_disposition"),
                    }
                )
            status = {
                "id": cid,
                "status": "FAIL",
                "failures": failure_rows,
            }
            if report_schema == "5":
                status["fail_targets"] = [f["target"] for f in failure_rows]
                status["pass_targets"] = [
                    normalize_target(row.get("actual_target") or rpt_target)
                    for _, rpt_target, row in rows
                    if row.get("result") == "PASS" and (row.get("actual_target") or rpt_target)
                ]
                status["required_targets"] = required_targets
            else:
                status["pass_contexts"] = [ctx for ctx, _, row in rows if row.get("result") == "PASS"]
                status["fail_contexts"] = [ctx for ctx, _, _ in failed]
            status_rows.append(status)
            continue

        if report_schema == "5" and required_targets:
            pass_targets = []
            for _, rpt_target, row in rows:
                if row.get("result") != "PASS":
                    continue
                actual = row.get("actual_target") or rpt_target
                if actual and any(target_matches(actual, t) for t in required_targets):
                    pass_targets.append(normalize_target(actual))
            missing_targets = [
                normalize_target(req)
                for req in required_targets
                if not any(target_matches(actual, req) for actual in pass_targets)
            ]
            ok = not missing_targets
            if not ok:
                issues.append(
                    {
                        "code": "REQUIRED_TARGET_EVIDENCE_MISSING",
                        "check": cid,
                        "required_targets": required_targets,
                        "missing_targets": missing_targets,
                        "message": f"{cid} lacks required PASS evidence for target(s): {', '.join(target_label(t) for t in missing_targets)}",
                    }
                )
            status_rows.append(
                {
                    "id": cid,
                    "status": "PASS" if ok else "INCOMPLETE",
                    "required_targets": required_targets,
                    "pass_targets": pass_targets,
                    "missing_targets": missing_targets,
                }
            )
            continue

        required_contexts = rows[0][2].get("required_contexts") or ["ANY"]
        passes = [ctx for ctx, _, row in rows if row.get("result") == "PASS"]
        if required_contexts == ["ANY"]:
            ok = bool(passes)
        else:
            ok = all(ctx in passes for ctx in required_contexts)
        if not ok:
            issues.append(
                {
                    "code": "REQUIRED_CONTEXT_EVIDENCE_MISSING",
                    "check": cid,
                    "message": f"{cid} lacks required PASS evidence for {required_contexts}",
                }
            )
        status_rows.append(
            {
                "id": cid,
                "status": "PASS" if ok else "INCOMPLETE",
                "pass_contexts": passes,
                "required_contexts": required_contexts,
            }
        )

    overall = "FAIL" if any_fail else ("INCOMPLETE_ASSURANCE" if issues else "PASS")
    report_rows = []
    for p, r in zip(paths, reports):
        item = {
            "path": str(p),
            "sha256": sha(p),
            "context": r.get("execution_context"),
            "overall": r.get("overall"),
        }
        if report_schema == "5":
            item["execution_target"] = normalize_target(r.get("execution_target"))
            item["environment"] = r.get("environment")
        report_rows.append(item)

    bundle = {
        "schema_version": bundle_schema,
        "report_schema_version": report_schema,
        "overall": overall,
        "project": reports[0].get("project"),
        "git_commit": reports[0].get("git_commit"),
        "plan_sha256": reports[0].get("plan_sha256"),
        "assurance_baseline_sha256": reports[0].get("assurance_baseline_sha256"),
        "runner_sha256": reports[0].get("runner_sha256"),
        "artifact_identities": reports[0].get("artifact_identities"),
        "reports": report_rows,
        "issues": issues,
        "required_checks": status_rows,
    }

    print(f"EVIDENCE BUNDLE: {overall}")
    for row in status_rows:
        if row.get("status") != "FAIL":
            continue
        details = []
        for failure in row.get("failures") or []:
            label = target_label(failure.get("target")) if report_schema == "5" else str(failure.get("context"))
            exit_code = failure.get("exit_code")
            disposition = failure.get("execution_disposition")
            detail = f"{label}: exit {exit_code}" if exit_code is not None else label
            if disposition:
                detail += f" ({disposition})"
            details.append(detail)
        if report_schema == "5":
            where = ", ".join(target_label(t) for t in row.get("fail_targets") or []) or "unknown target"
        else:
            where = ", ".join(row.get("fail_contexts") or []) or "unknown context"
        suffix = f" [{'; '.join(details)}]" if details else ""
        print(f"  - {row.get('id')} FAILED in {where}{suffix}")
    for issue in issues:
        print("  - " + issue["message"])

    if args.output:
        p = Path(args.output).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    return 0 if overall == "PASS" else (1 if overall == "FAIL" else 2)


if __name__ == "__main__":
    raise SystemExit(main())
