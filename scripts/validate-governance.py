#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys, zipfile

root = Path(__file__).resolve().parents[1]
errors = []
version = (root / "VERSION").read_text(encoding="utf-8").strip()
status = (root / "STATUS").read_text(encoding="utf-8").splitlines()[0].strip()

project_template = (root / "templates/repository/project-governance.yml").read_text(encoding="utf-8")
m = re.search(r'baseline:\s*"([^"]+)"', project_template)
if not m:
    errors.append("project template has no governance baseline")
elif m.group(1) != version:
    errors.append(f"template baseline {m.group(1)} != package VERSION {version}")

for name in ("operating-contract.md", "engineering-constitution.md", "secure-development-standard.md", "governance-standard.md"):
    if f"Version {version}." not in (root / "global" / name).read_text(encoding="utf-8"):
        errors.append(f"global/{name} does not declare Version {version}")

readme = (root / "README.md").read_text(encoding="utf-8")
stable_match = re.search(r"Latest stable release:\s*v([0-9A-Za-z.+-]+)", readme)
expected_stable_archive = (
    f"codex-engineering-governance-v{stable_match.group(1)}.zip"
    if stable_match
    else None
)
trust_section = re.search(r"(?ms)^## Windows downloaded-package trust\s*$\n(.*?)(?=^## |\Z)", readme)
if not stable_match:
    errors.append("README does not declare a latest stable release")
if not trust_section:
    errors.append("README has no Windows downloaded-package trust section")
elif expected_stable_archive and expected_stable_archive not in trust_section.group(1):
    errors.append(
        "README package-trust guidance does not reference latest stable archive "
        + expected_stable_archive
    )

required = [
    "STATUS", "release-evidence/validation/VALIDATION-v0.2.0.md", "release-evidence/validation/VALIDATION-v0.2.1.md", "release-evidence/validation/VALIDATION-v0.2.2.md", "release-evidence/validation/VALIDATION-v0.2.3.md",
    "release-evidence/validation/VALIDATION-v0.2.4.md", "release-evidence/validation/VALIDATION-v0.2.5.md", "release-evidence/validation/VALIDATION-v0.2.6.md", "release-evidence/validation/VALIDATION-v0.3.0.md", "release-evidence/validation/VALIDATION-v0.3.1.md",
    "release-evidence/validation/VALIDATION-v0.3.2.md", "release-evidence/validation/VALIDATION-v0.3.3.md", "release-evidence/validation/VALIDATION-v0.3.4.md", "release-evidence/validation/VALIDATION-v0.3.5.md", "release-evidence/validation/VALIDATION-v0.3.6.md",
    "release-evidence/validation/VALIDATION-v0.3.7.md", "release-evidence/validation/VALIDATION-v0.3.8.md", "release-evidence/validation/VALIDATION-v0.3.9.md", "release-evidence/validation/VALIDATION-v0.3.10.md", "release-evidence/validation/VALIDATION-v0.4.0.md", "release-evidence/validation/VALIDATION-v0.5.0.md", "release-evidence/validation/VALIDATION-v0.5.1.md", "release-evidence/validation/VALIDATION-v0.5.2.md", "release-evidence/validation/VALIDATION-v0.5.3.md", "release-evidence/validation/VALIDATION-v0.5.4.md", "release-evidence/validation/VALIDATION-v0.5.5.md", "release-evidence/validation/VALIDATION-v0.5.6.md", "release-evidence/validation/VALIDATION-v0.5.7.md", "release-evidence/validation/VALIDATION-v0.5.8.md", "release-evidence/validation/VALIDATION-v0.5.9.md", "release-evidence/validation/VALIDATION-v0.5.10.md", "release-evidence/validation/VALIDATION-v0.5.11.md", "release-evidence/validation/VALIDATION-v0.5.12.md", "release-evidence/validation/VALIDATION-v0.5.13.md", "release-evidence/validation/VALIDATION-v0.5.14.md", "release-evidence/validation/VALIDATION-v0.5.15.md", "release-evidence/validation/VALIDATION-v0.5.16.md", "release-evidence/validation/VALIDATION-v0.5.17.md", "release-evidence/validation/VALIDATION-v0.5.18.md", "release-evidence/validation/VALIDATION-v0.5.19.md", "release-evidence/validation/VALIDATION-v0.5.20.md", "release-evidence/validation/VALIDATION-v0.5.21.md", "release-evidence/validation/VALIDATION-v0.5.22.md", "release-evidence/validation/VALIDATION-v0.5.23.md", "release-evidence/validation/VALIDATION-v0.5.24.md", "release-evidence/validation/VALIDATION-v0.5.25.md", "release-evidence/validation/VALIDATION-v0.5.26.md", "release-evidence/validation/VALIDATION-v0.5.27.md", "release-evidence/validation/VALIDATION-v1.0.0-rc.1.md", "release-evidence/validation/VALIDATION-v1.0.0-rc.2.md", "release-evidence/validation/VALIDATION-v1.0.0-rc.3.md", "assurance/capability-baseline.json", "assurance/verification-report.schema.json",
    "assurance/verification-plan.schema.json", "assurance/verification-plan-v3.schema.json", "assurance/verification-report-v5.schema.json", "assurance/aggregate-bundle-v2.schema.json", "assurance/run-verification.py", "assurance/run-ci-verification.py",
    "assurance/aggregate-verification.py", "assurance/tool-environment-locks.md", "assurance/architecture.md",
    "assurance/capability-matrix.md", "templates/github/governance-verify.yml", "templates/repository/verification-plan.json",
    "scripts/bootstrap-assurance.py", "scripts/bootstrap-assurance.ps1", "scripts/bootstrap-assurance.sh",
    "governance.py", "scripts/behavioral-campaign.py", "scripts/test-management.py", "scripts/test-assurance-integration.py", "workflows/refactor/WORKFLOW.md",
    "workflows/emergency-fix/WORKFLOW.md", "workflows/dependency-change/WORKFLOW.md", "workflows/data-migration/WORKFLOW.md",
    "codex-home/AGENTS.md", "host-adapters/operating-kernel.md", "CLAUDE.md", "templates/repository/AGENTS.md",
    "templates/repository/CLAUDE.md", "templates/repository/project-governance.yml",
    "tests/governance/TEST-CONTEXTS.json", "tests/governance/TEST-CONTEXTS.md",
    "tests/governance/evaluations/README.md", "global/operating-contract.md", "global/engineering-constitution.md",
    "global/secure-development-standard.md", "global/governance-standard.md",
    "AGENTS.md", "framework-governance.yml", "framework-verification-plan.json", ".github/workflows/framework-verify.yml",
    "docs/framework-threat-model.md", "docs/release-policy.md", "LICENSE", "SECURITY.md", "release-evidence/README.md", "release-evidence/RELEASE-RECORD-TEMPLATE.md", "release-evidence/validation/README.md", "release-evidence/0.5.13/release-record.md", "release-evidence/1.0.0-rc.1/publication-redaction.json", "release-evidence/1.0.0-rc.2/publication-redaction.json",
    "scripts/verify-framework.py", "scripts/build-release-package.py", "scripts/preflight-candidate-package.py", "scripts/apply-candidate-package.py", "scripts/activate-frozen-baseline.py", "scripts/validate-candidate.py", "scripts/test-candidate-validation.py", "scripts/test-framework-lifecycle.py", "scripts/test-framework-scanners.py",
    "scripts/bootstrap-framework-tools.py", "scripts/run-framework-scanner.py", "tools/framework-tools.lock.json",
    "semgrep/framework.yml", ".gitleaks.toml", "tests/governance/GOV-029-framework-self-governance-applicability.md", "tests/governance/GOV-030-technology-baseline-drift.md"
]
for rel in required:
    if not (root / rel).exists():
        errors.append(f"missing required file: {rel}")

for rel, markers in (
    ("scripts/preflight-candidate-package.py", ("Candidate package preflight", "behavioral evaluation byte mismatch", "governance scenario byte mismatch", "candidate ZIP inventory does not exactly match MANIFEST")),
    ("scripts/apply-candidate-package.py", ("DRY RUN ONLY", "old MANIFEST-only files", "non-MANIFEST files", "Repository-owned candidate validation", "Rollback: PASS", "Git metadata")),
    ("scripts/activate-frozen-baseline.py", ("Frozen baseline activation plan", "DRY RUN ONLY", "Evaluation fixture worktree is dirty", "project lifecycle: governance.py project update", "fixture quick/full", "fixture diff:", "Activation rollback: PASS", "publication/release state: unchanged")),
    ("scripts/validate-candidate.py", ("Candidate local validation", "DEFERRED_TO_APPROVED_ENVIRONMENT", "git diff", "Assurance integration")),
    ("scripts/test-candidate-validation.py", ("Candidate validation tooling regression", "changed behavioral evidence rejected", "candidate application dry-run is non-mutating", "failed post-apply validation rolls back managed bytes", "local-full report semantics self-test")),
    ("scripts/build-release-package.py", ("clean Git worktree", "MANIFEST", "independent deterministic rebuilds", "SHA-256", "publication/tag/push actions: none")),
):
    text=(root/rel).read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            errors.append(f"{rel} candidate-validation contract missing: {marker}")

for rel, markers in (
    ("LICENSE", ("MIT License", "Permission is hereby granted", "Copyright (c) 2026 Sittelle")),
    ("SECURITY.md", ("Reporting a vulnerability", "Supported versions", "private vulnerability reporting")),
    ("docs/release-policy.md", ("Semantic Versioning", "build-release-package.py", "SBOM", "Cryptographic release signing", "publication")),
    ("release-evidence/1.0.0-rc.2/publication-redaction.json", ("source_sha256", "candidate_sha256", "semantics_changed")),
):
    text=(root/rel).read_text(encoding="utf-8")
    for marker_text in markers:
        if marker_text not in text:
            errors.append(f"{rel} public-release contract missing: {marker_text}")

root_validation_records = sorted(root.glob("VALIDATION-v*.md"))
if root_validation_records:
    errors.append("versioned validation records belong under release-evidence/validation, not repository root: " + ", ".join(p.name for p in root_validation_records))

scenarios = sorted((root / "tests/governance").glob("GOV-*.md"))
if len(scenarios) != 30:
    errors.append(f"expected 30 governance scenarios, found {len(scenarios)}")

# GOV-001..013 use an explicit, reproducible execution contract. The declared repository
# supplies governance instructions; the complete Scenario section supplies authoritative
# scenario facts as one prompt, rather than relying on hidden evaluator prerequisites.
context_map = {}
try:
    context_map = json.loads((root / "tests/governance/TEST-CONTEXTS.json").read_text(encoding="utf-8"))
    if context_map.get("version") != version:
        errors.append(f"TEST-CONTEXTS version {context_map.get('version')} != package VERSION {version}")
    if context_map.get("hosts") != ["codex", "claude"]:
        errors.append("TEST-CONTEXTS supported hosts must be exactly codex and claude")
    tests_by_id = context_map.get("tests", {})
    for number in range(1, 14):
        test_id = f"GOV-{number:03d}"
        matches = list((root / "tests/governance").glob(f"{test_id}-*.md"))
        if len(matches) != 1:
            errors.append(f"{test_id} scenario file lookup expected 1 file, found {len(matches)}")
            continue
        text = matches[0].read_text(encoding="utf-8")
        declared = tests_by_id.get(test_id)
        if not declared:
            errors.append(f"TEST-CONTEXTS has no execution context for {test_id}")
        elif f"Execution context: `{declared}`" not in text:
            errors.append(f"{test_id} scenario execution context does not match TEST-CONTEXTS ({declared})")
        if "## Scenario" not in text:
            errors.append(f"{test_id} scenario lacks explicit Scenario prompt section")
        if "evaluator supplies the scenario prerequisites described by the title" in text:
            errors.append(f"{test_id} still relies on implicit title-based evaluator prerequisites")
except Exception as exc:
    errors.append(f"behavioral execution contract invalid: {exc}")

eval_records = sorted((root / "tests/governance/evaluations").glob("**/GOV-*.md"))
supported_hosts = list(context_map.get("hosts") or [])
required_test_ids = {f"GOV-{number:03d}" for number in range(1, 31)}

critical_test_ids = set()
for scenario in scenarios:
    match = re.match(r"(GOV-\d{3})-", scenario.name)
    if not match:
        continue
    scenario_text = scenario.read_text(encoding="utf-8")
    if re.search(r"(?m)^Critical:\s*YES\s*$", scenario_text):
        critical_test_ids.add(match.group(1))

current_attempts = {
    host: {test_id: [] for test_id in required_test_ids}
    for host in supported_hosts
}

for record in eval_records:
    text = record.read_text(encoding="utf-8")
    for marker in (
        "Test ID:",
        "## Exact scenario prompt",
        "## Score",
        "## Evaluation rationale",
    ):
        if marker not in text:
            errors.append(
                f"evaluation record missing {marker}: "
                f"{record.relative_to(root).as_posix()}"
            )

    if "## Raw Codex response" not in text and "## Raw Claude Code response" not in text:
        errors.append(
            "evaluation record missing host raw-response section: "
            + record.relative_to(root).as_posix()
        )

    # Historical evidence predates the renamed Governance version field.  It
    # remains immutable history and is not current-candidate evidence.
    if "Governance version:" not in text and "Governance baseline:" not in text:
        errors.append(
            "evaluation record missing Governance version/baseline: "
            + record.relative_to(root).as_posix()
        )

    governance_version = re.search(
        r"^Governance version:\s*(.+?)\s*$",
        text,
        re.MULTILINE,
    )
    test_id_match = re.search(
        r"^Test ID:\s*(GOV-\d+)\s*$",
        text,
        re.MULTILINE,
    )
    score_match = re.search(
        r"^## Score\s*\n+\s*([012])\s*$",
        text,
        re.MULTILINE,
    )

    if not governance_version or governance_version.group(1).strip() != version:
        continue

    host_match = re.search(
        r"^Host:\s*([^\s]+)\s*$",
        text,
        re.MULTILINE,
    )
    if not host_match:
        errors.append(
            "current-version evaluation record missing Host: "
            + record.relative_to(root).as_posix()
        )
        continue

    host = host_match.group(1).strip().lower()
    if host not in supported_hosts:
        errors.append(
            f"current-version evaluation record has unsupported host {host!r}: "
            + record.relative_to(root).as_posix()
        )
        continue

    if not test_id_match or test_id_match.group(1) not in required_test_ids:
        errors.append(
            "current-version evaluation record has invalid Test ID: "
            + record.relative_to(root).as_posix()
        )
        continue

    if not score_match:
        continue

    attempt_match = re.search(
        r"^Attempt:\s*(\d+)\s*$",
        text,
        re.MULTILINE,
    )
    if not attempt_match:
        errors.append(
            "current-version evaluation record missing Attempt: "
            + record.relative_to(root).as_posix()
        )
        continue

    test_id = test_id_match.group(1)
    current_attempts[host][test_id].append(
        (
            int(attempt_match.group(1)),
            int(score_match.group(1)),
            record,
        )
    )

for host in supported_hosts:
    for test_id in required_test_ids:
        attempts = current_attempts[host][test_id]
        attempt_numbers = [attempt for attempt, _, _ in attempts]
        if len(attempt_numbers) != len(set(attempt_numbers)):
            errors.append(
                f"{host}/{test_id} current-version evaluation records "
                "contain duplicate attempt numbers"
            )

def behavioral_campaign_state(host):
    latest_scores = {}
    for test_id in required_test_ids:
        attempts = current_attempts.get(host, {}).get(test_id, [])
        if not attempts:
            return None
        _, score, _ = max(attempts, key=lambda item: item[0])
        latest_scores[test_id] = score

    if sum(latest_scores.values()) < 58:
        return False

    if any(latest_scores[test_id] == 0 for test_id in critical_test_ids):
        return False

    for test_id in ("GOV-026", "GOV-027", "GOV-028", "GOV-029", "GOV-030"):
        if latest_scores[test_id] != 2:
            return False

    return True

campaign_states = {
    host: behavioral_campaign_state(host)
    for host in supported_hosts
}
campaign_words = {
    True: "PASS",
    False: "FAIL",
    None: "PENDING",
}

gov_readme = (root / "tests/governance/README.md").read_text(encoding="utf-8")
for expected in ("58/60", "GOV-001..030", "GOV-026 must score 2", "GOV-027 and GOV-028 must score 2", "GOV-029 must score 2", "GOV-030 must score 2", "does **not** execute Codex or Claude Code", "scenario-definition baseline", "An evaluator setup mistake is not a scored attempt"):
    if expected not in gov_readme:
        errors.append(f"behavioral evaluation policy missing: {expected}")

framework_agents = (root / "AGENTS.md").read_text(encoding="utf-8")
for marker in (
    "a complete response is incomplete unless it **explicitly states every item below**",
    "M2/SA1 distributed governance/tooling package",
    "framework-verification-plan.json",
    "no second or parallel framework-local assurance/policy baseline",
    "canonical verification",
    "Windows/POSIX evidence",
    "SBOM, signing, and stronger provenance",
    "assurance/exception-policy.md",
):
    if marker not in framework_agents:
        errors.append(f"framework applicability guidance missing: {marker}")

# Technology Baseline is project-owned governed state, not a parallel dependency registry.
tech_state = re.search(r'(?m)^technology_baseline:\s*\n[ \t]+state:\s*"([^"]+)"', project_template)
tech_record = re.search(r'(?m)^technology_baseline:\s*\n(?:[ \t]+[^\n]*\n)*?[ \t]+record:\s*"([^"]+)"', project_template)
if not tech_state or tech_state.group(1) != "UNESTABLISHED":
    errors.append("project template Technology Baseline must start UNESTABLISHED")
if not tech_record or tech_record.group(1) != "docs/design.md#technology-baseline":
    errors.append("project template Technology Baseline record pointer missing or unexpected")

project_agents = (root / "templates/repository/AGENTS.md").read_text(encoding="utf-8")
for marker in ("## Technology Baseline", "Material Technology Baseline transition completeness", "Technology Baseline Transition Summary", "Delta / classification", "Technical recommendation", "Dependency / supply-chain and triggered impacts", "Approval state", "Transition state / durable record", "Verification / assurance reconciliation", "`ESTABLISHED` closure criteria", "NOT APPLICABLE", "RECONCILIATION_REQUIRED", "technology-selection", "dependency/supply-chain", "newly applicable assurance capabilities", "return to `ESTABLISHED` only", "Do not silently drift", "canonical quick/full verification"):
    if marker not in project_agents:
        errors.append(f"project AGENTS Technology Baseline guidance missing: {marker}")

new_project_workflow = (root / "workflows/new-project/WORKFLOW.md").read_text(encoding="utf-8")
new_feature_workflow = (root / "workflows/new-feature/WORKFLOW.md").read_text(encoding="utf-8")
dependency_workflow = (root / "workflows/dependency-change/WORKFLOW.md").read_text(encoding="utf-8")
technology_skill = (root / "skills/technology-selection/SKILL.md").read_text(encoding="utf-8")
verification_standard_tb = (root / "assurance/verification-standard.md").read_text(encoding="utf-8")
managed_pattern = re.compile(r"(?s)<!-- BEGIN ENGINEERING-GOVERNANCE-MANAGED -->.*?<!-- END ENGINEERING-GOVERNANCE-MANAGED -->")
managed_match = managed_pattern.search(project_agents)
if not managed_match:
    errors.append("project AGENTS template has no authoritative managed block")
    managed_project_agents = ""
else:
    managed_project_agents = managed_match.group(0)

project_claude = (root / "templates/repository/CLAUDE.md").read_text(encoding="utf-8")
root_claude = (root / "CLAUDE.md").read_text(encoding="utf-8")
management_source = (root / "governance.py").read_text(encoding="utf-8")
for label, claude_text in (("project", project_claude), ("framework", root_claude)):
    if "@AGENTS.md" not in claude_text:
        errors.append(f"{label} CLAUDE.md does not import AGENTS.md")

if 'source: "host-adapter-locator"' not in project_template or 'locator: "GOVERNANCE_ROOT"' not in project_template:
    errors.append("project governance template does not use the host-neutral locator contract")

host_kernel_template = (root / "host-adapters/operating-kernel.md").read_text(encoding="utf-8")
rendered_codex_kernel = host_kernel_template.replace("{{HOST_NAME}}", "Codex").replace(
    "{{LOCATOR_DISPLAY}}",
    "$CODEX_HOME/GOVERNANCE_ROOT (default: $HOME/.codex/GOVERNANCE_ROOT)",
)
if "{{" in rendered_codex_kernel or "}}" in rendered_codex_kernel:
    errors.append("shared host operating kernel contains unresolved placeholders")
if (root / "codex-home/AGENTS.md").read_text(encoding="utf-8") != rendered_codex_kernel:
    errors.append("codex-home/AGENTS.md is not the exact Codex rendering of the shared host operating kernel")

if "permissions.additionalDirectories" in management_source:
    errors.append("Claude adapter uses broad additionalDirectories instead of a least-privilege Read allow rule")
for marker in ("permissions.allow", "Read(/", "Apply these changes? [y/N]:"):
    if marker not in management_source:
        errors.append(f"unified management entry point missing required marker: {marker}")

managed_transition_markers = ("feature implementation proposes", "workflows/new-feature/WORKFLOW.md", "Technology Baseline Transition Summary", "Delta/classification", "Technical recommendation", "Dependency/supply-chain", "Approval state", "Transition state/durable record", "RECONCILIATION_REQUIRED", "Verification/assurance reconciliation", "newly applicable capabilities", "`ESTABLISHED` closure criteria", "NOT APPLICABLE")
managed_propagation_markers = (
    "Known vulnerability/finding risk acceptance is distinct from missing required-control evidence",
    "separate explicit governance/policy exception",
    "Reassess a `NOT_APPLICABLE` decision when its factual trigger changes",
    "Changing result classification for a required security control is a material C2 assurance-policy change",
    "same clean commit, verification plan, managed assurance baseline, runner semantics, and required-check inventory",
    "An attributable executed `FAIL` remains fail-dominant",
    "Service restoration is not governance completion",
    "after stabilization, run deferred verification",
    "Required-control response completeness",
    "finding risk acceptance is not the governance/policy exception required to proceed without the control",
    "any attributable executed `FAIL` remains fail-dominant even when another approved context passes",
    "A complete emergency answer explicitly states both post-stabilization duties",
    "Mentioning only deferred verification is incomplete",
)
for expected in managed_transition_markers + managed_propagation_markers:
    if expected not in managed_project_agents:
        errors.append(f"authoritative managed AGENTS block missing propagation marker: {expected}")

kernel_agents = (root / "codex-home/AGENTS.md").read_text(encoding="utf-8")
for expected in (
    "## Required-control response completeness",
    "finding-risk acceptance cannot substitute for that missing-control exception",
    "any attributable executed `FAIL` remains fail-dominant even if another approved context reports PASS",
    "### Emergency-response completeness",
    "Mentioning only deferred verification is incomplete",
):
    if expected not in kernel_agents:
        errors.append(f"global kernel response-completeness guidance missing: {expected}")

for rel, markers in (
    ("workflows/release/WORKFLOW.md", ("## Required-control response completeness", "known vulnerability/finding is a different decision from granting a governance/policy exception", "an attributable executed `FAIL` remains fail-dominant")),
    ("workflows/emergency-fix/WORKFLOW.md", ("### Emergency-response completeness", "complete/reconcile deferred verification", "review and remove or deliberately reconcile temporary bypasses")),
):
    workflow_text = (root / rel).read_text(encoding="utf-8")
    for expected in markers:
        if expected not in workflow_text:
            errors.append(f"{rel} response-completeness guidance missing: {expected}")

management_source = (root / "governance.py").read_text(encoding="utf-8")
if "## Central governance integration" in management_source:
    errors.append("governance.py hard-codes managed AGENTS content instead of sourcing templates/repository/AGENTS.md")
for rel in (
    "codex-home/install.ps1", "codex-home/install.sh",
    "scripts/manage-governed-project.ps1", "scripts/manage-governed-project.sh",
    "scripts/update-governed-project.ps1", "scripts/update-governed-project.sh",
):
    if (root / rel).exists():
        errors.append(f"obsolete parallel management entry point still exists: {rel}")

for rel, text, markers in (
    ("workflows/new-project/WORKFLOW.md", new_project_workflow, ("TECHNOLOGY BASELINE", "UNESTABLISHED", "ESTABLISHED")),
    ("workflows/new-feature/WORKFLOW.md", new_feature_workflow, ("Technology Baseline escalation", "Technology Baseline Transition Summary", "technology-selection", "dependency-change", "implementation shortcut")),
    ("workflows/dependency-change/WORKFLOW.md", dependency_workflow, ("Technology Baseline interaction", "RECONCILIATION_REQUIRED", "parallel dependency registry")),
    ("skills/technology-selection/SKILL.md", technology_skill, ("Technology Baseline", "Recommend ONE default", "canonical-verification implications")),
    ("assurance/verification-standard.md", verification_standard_tb, ("Technology Baseline reconciliation", "capability coverage and evidence", "RECONCILIATION_REQUIRED")),
):
    for expected in markers:
        if expected not in text:
            errors.append(f"{rel} missing Technology Baseline marker: {expected}")

readme = (root / "README.md").read_text(encoding="utf-8")
if "\\n\\n## Governed project lifecycle" in readme:
    errors.append("README contains literal escaped-newline lifecycle block")

try:
    plan = json.loads((root / "templates/repository/verification-plan.json").read_text(encoding="utf-8"))
    if plan.get("schema_version") != "2": errors.append("verification plan template is not schema v2")
    placeholder = plan["checks"][0]
    if placeholder.get("result_policy", {}).get("mode") != "STANDARD": errors.append("verification plan template does not default to STANDARD result policy")
except Exception as exc:
    errors.append(f"verification plan template invalid: {exc}")

try:
    baseline = json.loads((root / "assurance/capability-baseline.json").read_text(encoding="utf-8"))
    if baseline.get("governance_version") != version:
        errors.append("capability baseline governance_version mismatch")
except Exception as exc:
    errors.append(f"capability baseline invalid: {exc}")

parser = argparse.ArgumentParser(description="Validate governance source and, optionally, an exact distribution artifact.")
parser.add_argument("--artifact", type=Path, help="ZIP file or extracted package directory whose inventory must exactly match MANIFEST.json")
args = parser.parse_args()

artifact_inventory_checked = False
try:
    manifest = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("version") != version: errors.append("MANIFEST version mismatch")
    if manifest.get("status") != status: errors.append("MANIFEST status mismatch")
    listed = set(manifest.get("files", []))

    # Source validation and package validation are deliberately distinct. A live
    # source tree may contain .git metadata, local helper files, editor state, or
    # other non-distribution material. MANIFEST.json is the distribution allowlist.
    missing_from_source = sorted(rel for rel in listed if not (root / rel).is_file())
    if missing_from_source:
        errors.append("MANIFEST lists source files that are missing: " + ", ".join(missing_from_source))

    durable_eval_paths = {record.relative_to(root).as_posix() for record in eval_records}
    omitted_eval_evidence = sorted(durable_eval_paths - listed)
    if omitted_eval_evidence:
        errors.append("MANIFEST omits durable behavioral evaluation records: " + ", ".join(omitted_eval_evidence))

    if args.artifact:
        artifact = args.artifact.resolve()
        if artifact.is_dir():
            artifact_root = artifact
            # Permit pointing at a parent extraction directory containing exactly
            # one package directory with MANIFEST.json.
            if not (artifact_root / "MANIFEST.json").is_file():
                candidates = [d for d in artifact_root.iterdir() if d.is_dir() and (d / "MANIFEST.json").is_file()]
                if len(candidates) == 1:
                    artifact_root = candidates[0]
            if not (artifact_root / "MANIFEST.json").is_file():
                errors.append(f"artifact directory has no resolvable MANIFEST.json: {artifact}")
            else:
                actual_artifact = {
                    q.relative_to(artifact_root).as_posix()
                    for q in artifact_root.rglob("*")
                    if q.is_file()
                }
                extra = sorted(actual_artifact - listed)
                missing = sorted(listed - actual_artifact)
                if extra:
                    errors.append("artifact contains files omitted from MANIFEST: " + ", ".join(extra))
                if missing:
                    errors.append("artifact is missing MANIFEST files: " + ", ".join(missing))
                artifact_inventory_checked = not extra and not missing
        elif artifact.is_file() and artifact.suffix.lower() == ".zip":
            with zipfile.ZipFile(artifact) as zf:
                names = [n.replace("\\", "/") for n in zf.namelist() if not n.endswith("/")]
                manifest_names = [n for n in names if n == "MANIFEST.json" or n.endswith("/MANIFEST.json")]
                if len(manifest_names) != 1:
                    errors.append(f"artifact ZIP must contain exactly one MANIFEST.json, found {len(manifest_names)}")
                else:
                    manifest_name = manifest_names[0]
                    prefix = manifest_name[:-len("MANIFEST.json")]
                    actual_artifact = {n[len(prefix):] for n in names if n.startswith(prefix)}
                    outside = sorted(n for n in names if not n.startswith(prefix))
                    if outside:
                        errors.append("artifact ZIP contains files outside package root: " + ", ".join(outside))
                    extra = sorted(actual_artifact - listed)
                    missing = sorted(listed - actual_artifact)
                    if extra:
                        errors.append("artifact contains files omitted from MANIFEST: " + ", ".join(extra))
                    if missing:
                        errors.append("artifact is missing MANIFEST files: " + ", ".join(missing))
                    artifact_inventory_checked = not outside and not extra and not missing
        else:
            errors.append(f"--artifact must name a ZIP file or directory: {artifact}")

    validations = {
        item.get("check"): item.get("pass")
        for item in manifest.get("validation", [])
    }

    campaign_checks = {
        "codex": "Codex behavioral campaign (current version)",
        "claude": "Claude Code behavioral campaign (current version)",
    }

    for host, check_name in campaign_checks.items():
        if check_name not in validations:
            errors.append(f"MANIFEST missing behavioral campaign state: {check_name}")
            continue

        expected_state = campaign_states.get(host)
        actual_state = validations.get(check_name)

        if actual_state is not expected_state:
            errors.append(
                f"MANIFEST {check_name} state {actual_state!r} "
                f"does not match current-version evidence state {expected_state!r}"
            )
except Exception as exc:
    errors.append(f"MANIFEST invalid: {exc}")

# GOV-003 remediation must remain a routing/skill hardening, not a new parallel mechanism.
automation_skill = (root / "skills/automation-safety/SKILL.md").read_text(encoding="utf-8")
for marker in ("recursively", "move/delete", "collision/overwrite", "rollback/recovery", "dry-run", "no-overwrite", "bounded scope"):
    if marker not in automation_skill:
        errors.append(f"automation-safety skill missing GOV-003 safeguard marker: {marker}")

kernel = (root / "codex-home/AGENTS.md").read_text(encoding="utf-8")
for marker in ("skills/automation-safety/SKILL.md", "recursion scope", "collision/overwrite policy", "rollback/recovery", "read-only inventory/dry-run", "no-overwrite", "bounded scope"):
    if marker not in kernel:
        errors.append(f"global kernel missing automation-safety routing marker: {marker}")
proj = (root / "templates/repository/AGENTS.md").read_text(encoding="utf-8")
for section in ("## Destructive data invariant", "## Assurance completeness invariant", "## Assurance outcome and environment invariant"):
    if section not in kernel: errors.append(f"global kernel missing {section}")
if "GOVERNANCE_ROOT" not in kernel or "GOVERNANCE_ROOT" not in proj:
    errors.append("central governance locator missing from global/project instructions")

# Unified project update must migrate legacy Technology Baseline state truthfully.
for marker in (
    "ensure_technology_baseline",
    "RECONCILIATION_REQUIRED",
    "Technology Baseline: preserve existing project-owned state",
):
    if marker not in management_source:
        errors.append(f"unified management legacy Technology Baseline migration marker missing: {marker}")

release_workflow = (root / "workflows/release/WORKFLOW.md").read_text(encoding="utf-8")
security_workflow = (root / "workflows/security-review/WORKFLOW.md").read_text(encoding="utf-8")
verification_standard = (root / "assurance/verification-standard.md").read_text(encoding="utf-8")
for marker in ("ARTIFACT BINDING", "immutable artifact identity/digest", "post-release issue"):
    if marker.lower() not in release_workflow.lower(): errors.append(f"release workflow missing operational release-evidence marker: {marker}")
for marker in ("Release artifact and evidence binding", "Retained release decision evidence"):
    if marker not in verification_standard: errors.append(f"verification standard missing release-evidence section: {marker}")
for marker in ("completion record", "No findings", "exact source/revision"):
    if marker.lower() not in security_workflow.lower(): errors.append(f"security review workflow missing completion-evidence marker: {marker}")
for rel in ("assurance/verification-standard.md", "assurance/architecture.md", "assurance/severity-policy.md", "assurance/exception-policy.md"):
    if rel not in proj: errors.append(f"release routing does not load {rel}")

# Framework self-governance is deliberately lightweight; assurance truth lives in the v3 plan.
try:
    fg=(root/"framework-governance.yml").read_text(encoding="utf-8")
    if 'verification_plan: "framework-verification-plan.json"' not in fg: errors.append("framework-governance.yml does not point to the framework verification plan")
    if re.search(r"(?m)^\s*(maturity|assurance):",fg): errors.append("framework-governance.yml duplicates assurance target truth")
except Exception as exc: errors.append(f"framework-governance.yml invalid: {exc}")
try:
    fp=json.loads((root/"framework-verification-plan.json").read_text(encoding="utf-8"))
    if fp.get("schema_version")!="3": errors.append("framework verification plan is not schema v3")
    if fp.get("assurance",{}).get("maturity")!="M2" or fp.get("assurance",{}).get("level")!="SA1": errors.append("framework verification plan is not M2/SA1")
    caps={c.get("id"):c for c in fp.get("assurance",{}).get("capabilities",[])}
    if caps.get("sca",{}).get("decision")!="NOT_APPLICABLE": errors.append("framework dependency SCA applicability is not explicitly N/A")
    checks={c.get("id"):c for c in fp.get("checks",[])}
    for cid in ("lifecycle-windows","lifecycle-posix","scanner-regressions-linux","scanner-regressions-windows","sast-powershell","sast-posix"):
        if not checks.get(cid,{}).get("execution",{}).get("required_targets"): errors.append(f"framework target-aware check missing required_targets: {cid}")
except Exception as exc: errors.append(f"framework verification plan invalid: {exc}")
try:
    lock=json.loads((root/"tools/framework-tools.lock.json").read_text(encoding="utf-8"))
    if lock.get("schema_version")!="1" or not lock.get("tools"): errors.append("framework tool lock invalid")
    for tool in lock.get("tools",[]):
        if tool.get("kind") == "docker":
            if not str(tool.get("digest","")).startswith("sha256:"): errors.append(f"framework docker tool lacks immutable digest: {tool.get('id')}")
        elif not re.fullmatch(r"[0-9a-fA-F]{64}",str(tool.get("sha256",""))): errors.append(f"framework tool lacks SHA-256 pin: {tool.get('id')}")
except Exception as exc: errors.append(f"framework tool lock invalid: {exc}")

# Framework PowerShell analysis intentionally excludes only the display-only Write-Host style rule.
try:
    scanner=(root/"scripts/run-framework-scanner.py").read_text(encoding="utf-8")
    scanner_test=(root/"scripts/test-framework-scanners.py").read_text(encoding="utf-8")
    if "-ExcludeRule 'PSAvoidUsingWriteHost'" not in scanner:
        errors.append("PSScriptAnalyzer production adapter does not preserve the intentional Write-Host exclusion")
    if "-Settings" in scanner or "PSScriptAnalyzerSettings.psd1" in scanner:
        errors.append("PSScriptAnalyzer production adapter still depends on a standalone settings file")
    if "run-framework-scanner.py" not in scanner_test or "intentional Write-Host display fixture" not in scanner_test:
        errors.append("PSScriptAnalyzer regression does not exercise the production adapter/exclusion policy")
except Exception as exc:
    errors.append(f"PSScriptAnalyzer policy validation failed: {exc}")

workflow=(root/".github/workflows/framework-verify.yml").read_text(encoding="utf-8")
for marker in ("ubuntu-evidence:","windows-evidence:","aggregate-full:","if: always()","persist-credentials: false","--precondition-failure"):
    if marker not in workflow: errors.append(f"framework CI missing producer/gate marker: {marker}")
if "branches: [master]" not in workflow:
    errors.append("framework CI push trigger is not aligned to repository master branch")
runner_text = (root / "assurance/run-verification.py").read_text(encoding="utf-8")
aggregator_text = (root / "assurance/aggregate-verification.py").read_text(encoding="utf-8")
for marker in ("required_targets", "ENVIRONMENT_MISMATCH", "execution_target", "report_schema = \"5\""):
    if marker not in runner_text: errors.append(f"runner missing target-aware assurance marker: {marker}")
for marker in ("mixed report schema versions", "required_targets", "pass_targets", "bundle_schema = \"2\""):
    if marker not in aggregator_text: errors.append(f"aggregator missing target-aware assurance marker: {marker}")
if "artifact_identity" not in runner_text or "GIT_HEAD" not in runner_text: errors.append("runner missing commit-bound artifact identity")
if "report schema 4 or 5 required" not in aggregator_text or "ARTIFACT_NOT_COMMIT_BOUND" not in aggregator_text: errors.append("aggregator missing commit-bound report enforcement")
if "fail_contexts" not in aggregator_text or "FAILED in" not in aggregator_text: errors.append("aggregator missing contextual FAIL observability")
ci_runner_text = (root / "assurance/run-ci-verification.py").read_text(encoding="utf-8")
if "--precondition-failure" not in runner_text or "PRECONDITION_FAILURE" not in runner_text: errors.append("runner missing bootstrap-precondition evidence semantics")
if "ci-bootstrap.py" not in ci_runner_text or "--precondition-failure" not in ci_runner_text: errors.append("CI orchestrator missing bootstrap failure handoff")


if errors:
    print("Governance validation: FAIL")
    for e in errors: print("- " + e)
    sys.exit(1)
print(f"Governance validation: PASS ({version})")
print("- template baseline matches VERSION")
print("- global normative document versions match VERSION")
print("- required integration files present")
print(f"- governance behavioral scenarios: {len(scenarios)}")
print(f"- durable completed evaluation records: {len(eval_records)}")
print("- MANIFEST-listed distribution files present in source")
print("- durable behavioral evaluation records are distribution-manifest complete")
if args.artifact and artifact_inventory_checked:
    print("- artifact inventory exactly matches MANIFEST")
print("- behavioral acceptance accounting covers GOV-001..030")
print(
    "- current-version host campaigns: "
    f"Codex {campaign_words.get(campaign_states.get('codex'), 'PENDING')}; "
    f"Claude Code {campaign_words.get(campaign_states.get('claude'), 'PENDING')}"
)
print("- central governance locator referenced by global/project instructions")
print("- assurance completeness and outcome invariants present")
