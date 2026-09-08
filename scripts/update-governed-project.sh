#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
GOVERNANCE_ROOT=$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)
CENTRAL_VERSION=$(tr -d '\r\n' < "$GOVERNANCE_ROOT/VERSION")

PROJECT_ROOT=${1:-}
APPLY=0
ALLOW_DIRTY=0

shift_count=0
if [ -n "$PROJECT_ROOT" ]; then
  shift_count=1
fi
if [ "$shift_count" -eq 1 ]; then shift; fi

for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    --allow-dirty-git) ALLOW_DIRTY=1 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

if [ -z "$PROJECT_ROOT" ]; then
  printf "Enter governed project root: "
  IFS= read -r PROJECT_ROOT
fi

[ -d "$PROJECT_ROOT" ] || { echo "Project root does not exist: $PROJECT_ROOT" >&2; exit 1; }
PROJECT_ROOT=$(CDPATH='' cd -- "$PROJECT_ROOT" && pwd)

MANIFEST="$PROJECT_ROOT/project-governance.yml"
AGENTS="$PROJECT_ROOT/AGENTS.md"

[ -f "$MANIFEST" ] || { echo "Not a governed project: missing project-governance.yml" >&2; exit 1; }
[ -f "$AGENTS" ] || { echo "Not a governed project: missing AGENTS.md" >&2; exit 1; }

PROJECT_VERSION=$(sed -n 's/^[[:space:]]*baseline:[[:space:]]*["'\'']\{0,1\}\([^"'\'']*\)["'\'']\{0,1\}[[:space:]]*$/\1/p' "$MANIFEST" | head -n1)
[ -n "$PROJECT_VERSION" ] || { echo "Could not find governance baseline" >&2; exit 1; }

if [ -d "$PROJECT_ROOT/.git" ] && [ "$ALLOW_DIRTY" -ne 1 ]; then
  if [ -n "$(git -C "$PROJECT_ROOT" status --porcelain)" ]; then
    echo "Git worktree is dirty. Commit/stash changes first, or use --allow-dirty-git deliberately." >&2
    exit 1
  fi
fi

if grep -Eq '^technology_baseline:[[:space:]]*$' "$MANIFEST"; then
  TECHNOLOGY_BASELINE_ACTION="preserve existing Technology Baseline"
else
  TECHNOLOGY_BASELINE_ACTION="add missing Technology Baseline as RECONCILIATION_REQUIRED"
fi

echo
echo "Governed project update preview"
echo "Project:          $PROJECT_ROOT"
echo "Project baseline: $PROJECT_VERSION"
echo "Target baseline:  $CENTRAL_VERSION"
echo
echo "Will update project-governance.yml baseline/source/locator and the AGENTS managed block."
echo "Technology Baseline action: $TECHNOLOGY_BASELINE_ACTION."
echo "Will not change project requirements, maturity, assurance, verification commands, an existing project-owned Technology Baseline, or project-specific AGENTS text."

if [ "$APPLY" -ne 1 ]; then
  echo
  echo "DRY RUN ONLY. Re-run with --apply to make changes."
  exit 0
fi

STAMP=$(date +%Y%m%d-%H%M%S)
cp "$MANIFEST" "$MANIFEST.governance-backup-$STAMP"
cp "$AGENTS" "$AGENTS.governance-backup-$STAMP"

python3 - "$MANIFEST" "$AGENTS" "$CENTRAL_VERSION" "$GOVERNANCE_ROOT/templates/repository/AGENTS.md" <<'PY'
from pathlib import Path
import re, sys

manifest = Path(sys.argv[1])
agents = Path(sys.argv[2])
version = sys.argv[3]
template_agents = Path(sys.argv[4])

m = manifest.read_text(encoding="utf-8")
m = re.sub(r'(?m)^(\s*baseline:\s*)["\']?[^"\']+["\']?\s*$', rf'\1"{version}"', m, count=1)

if not re.search(r'(?m)^\s*source:\s*', m):
    m = re.sub(r'(?m)^(\s*baseline:\s*["\'][^"\']+["\']\s*)$', r'\1\n  source: "codex-home-locator"', m, count=1)
if not re.search(r'(?m)^\s*locator:\s*', m):
    m = re.sub(r'(?m)^(\s*source:\s*.+)$', r'\1\n  locator: "$CODEX_HOME/GOVERNANCE_ROOT"', m, count=1)

if not re.search(r'(?m)^technology_baseline:\s*$', m):
    block = '''# Governed architecture-significant technology state.
# Added during legacy governance migration; reconcile before treating the historical stack as established.
technology_baseline:
  state: "RECONCILIATION_REQUIRED"
  record: "docs/design.md#technology-baseline"'''
    if re.search(r'(?m)^platforms:\s*$', m):
        m = re.sub(r'(?m)^platforms:\s*$', block + "\n\nplatforms:", m, count=1)
    else:
        m = m.rstrip() + "\n\n" + block + "\n"

manifest.write_text(m.rstrip()+"\n", encoding="utf-8")

pat = re.compile(r'(?s)<!-- BEGIN CODEX-GOVERNANCE-MANAGED -->.*?<!-- END CODEX-GOVERNANCE-MANAGED -->')
template_text = template_agents.read_text(encoding="utf-8")
managed_match = pat.search(template_text)
if not managed_match:
    raise SystemExit(f"Managed AGENTS block not found in template: {template_agents}")
block = managed_match.group(0)

a = agents.read_text(encoding="utf-8")
if pat.search(a):
    a = pat.sub(block, a, count=1)
else:
    a = a.rstrip()+"\n\n"+block+"\n"
agents.write_text(a.rstrip()+"\n", encoding="utf-8")
PY

echo
echo "Applied governance update to $CENTRAL_VERSION"
echo "Backups:"
echo "  $MANIFEST.governance-backup-$STAMP"
echo "  $AGENTS.governance-backup-$STAMP"
echo
echo "Review with:"
echo "  git -C \"$PROJECT_ROOT\" diff -- AGENTS.md project-governance.yml"
