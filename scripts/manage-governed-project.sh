#!/usr/bin/env sh
set -eu
SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
GOV_ROOT=$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)
VERSION=$(tr -d '\r\n' < "$GOV_ROOT/VERSION")
TEMPLATE="$GOV_ROOT/templates/repository"

MODE=${1:-}
if [ "$#" -gt 0 ]; then shift; fi
APPLY=0; NO_GIT=0; PARENT=""; NAME=""; PROJECT=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --no-git-init) NO_GIT=1 ;;
    --parent) shift; PARENT=${1:-} ;;
    --name) shift; NAME=${1:-} ;;
    --project) shift; PROJECT=${1:-} ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
  shift
done

if [ -z "$MODE" ]; then printf "Mode (New/Adopt): "; IFS= read -r MODE; fi

case "$MODE" in
  New|new)
    [ -n "$PARENT" ] || { printf "Parent folder: "; IFS= read -r PARENT; }
    [ -n "$NAME" ] || { printf "Project name: "; IFS= read -r NAME; }
    [ -d "$PARENT" ] || { echo "Parent does not exist: $PARENT" >&2; exit 1; }
    TARGET="$PARENT/$NAME"
    if [ -d "$TARGET" ] && [ -n "$(find "$TARGET" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
      echo "Target exists and is not empty; use Adopt." >&2; exit 1
    fi
    echo "NEW governed project preview"
    echo "Target: $TARGET"
    echo "Governance version: $VERSION"
    [ "$APPLY" -eq 1 ] || { echo "DRY RUN ONLY. Add --apply."; exit 0; }
    mkdir -p "$TARGET/docs" "$TARGET/src" "$TARGET/tests"
    cp "$TEMPLATE/AGENTS.md" "$TARGET/AGENTS.md"
    cp "$TEMPLATE/project-governance.yml" "$TARGET/project-governance.yml"
    [ ! -f "$TEMPLATE/verification-plan.json" ] || cp "$TEMPLATE/verification-plan.json" "$TARGET/verification-plan.json"
    [ ! -f "$TEMPLATE/.editorconfig" ] || cp "$TEMPLATE/.editorconfig" "$TARGET/.editorconfig"
    [ ! -f "$TEMPLATE/.gitignore" ] || cp "$TEMPLATE/.gitignore" "$TARGET/.gitignore"
    python3 - "$TARGET/project-governance.yml" "$NAME" <<'PY'
from pathlib import Path
import re, sys
p=Path(sys.argv[1]); s=p.read_text(encoding="utf-8")
s=re.sub(r'(?m)^(\s*name:\s*).+$', rf'\1"{sys.argv[2]}"', s, count=1)
p.write_text(s.rstrip()+"\n", encoding="utf-8")
PY
    [ "$NO_GIT" -eq 1 ] || git -C "$TARGET" init >/dev/null
    echo "Created governed project: $TARGET"
    ;;
  Adopt|adopt)
    [ -n "$PROJECT" ] || { printf "Existing project root: "; IFS= read -r PROJECT; }
    [ -d "$PROJECT" ] || { echo "Project does not exist: $PROJECT" >&2; exit 1; }
    [ ! -f "$PROJECT/project-governance.yml" ] || { echo "Already governed; use update-governed-project.sh." >&2; exit 1; }
    if [ -d "$PROJECT/.git" ] && [ -n "$(git -C "$PROJECT" status --porcelain)" ]; then
      echo "Git worktree is dirty; commit/stash before adoption." >&2; exit 1
    fi
    echo "ADOPT governance preview"
    echo "Project: $PROJECT"
    echo "Governance version: $VERSION"
    echo "State will be RECONCILIATION_REQUIRED."
    [ "$APPLY" -eq 1 ] || { echo "DRY RUN ONLY. Add --apply."; exit 0; }
    if [ ! -f "$PROJECT/AGENTS.md" ]; then
      cp "$TEMPLATE/AGENTS.md" "$PROJECT/AGENTS.md"
    else
      cp "$PROJECT/AGENTS.md" "$PROJECT/AGENTS.md.governance-backup-$(date +%Y%m%d-%H%M%S)"
      python3 - "$TEMPLATE/AGENTS.md" "$PROJECT/AGENTS.md" <<'PY'
from pathlib import Path
import re, sys

template = Path(sys.argv[1])
agents = Path(sys.argv[2])
pat = re.compile(r'(?s)<!-- BEGIN CODEX-GOVERNANCE-MANAGED -->.*?<!-- END CODEX-GOVERNANCE-MANAGED -->')
managed_match = pat.search(template.read_text(encoding="utf-8"))
if not managed_match:
    raise SystemExit(f"Managed AGENTS block not found in template: {template}")
block = managed_match.group(0)
a = agents.read_text(encoding="utf-8")
if pat.search(a):
    a = pat.sub(block, a, count=1)
else:
    a = a.rstrip() + "\n\n" + block + "\n"
agents.write_text(a.rstrip() + "\n", encoding="utf-8")
PY
    fi
    cp "$TEMPLATE/project-governance.yml" "$PROJECT/project-governance.yml"
    leaf=$(basename "$PROJECT")
    python3 - "$PROJECT/project-governance.yml" "$leaf" <<'PY'
from pathlib import Path
import re, sys
p=Path(sys.argv[1]); s=p.read_text(encoding="utf-8")
s=re.sub(r'(?m)^(\s*name:\s*).+$', rf'\1"{sys.argv[2]}"', s, count=1)
s=re.sub(r'(?m)^([ \t]*state:[ \t]*)"UNESTABLISHED"[ \t]*$', r'\1"RECONCILIATION_REQUIRED"', s, count=1)
s += "\nadoption:\n  state: \"RECONCILIATION_REQUIRED\"\n  adopted_from_existing_project: true\n  historical_governance_approval: false\n  note: \"Pre-existing project decisions require governance reconciliation.\"\n"
p.write_text(s.rstrip()+"\n", encoding="utf-8")
PY
    mkdir -p "$PROJECT/docs"
    cat > "$PROJECT/docs/governance-adoption.md" <<EOF
# Governance adoption
Governance baseline: $VERSION
Status: RECONCILIATION_REQUIRED

This repository existed before governance adoption. No pre-existing project decision is represented as historically approved under this baseline.
EOF
    [ "$NO_GIT" -eq 1 ] || [ -d "$PROJECT/.git" ] || git -C "$PROJECT" init >/dev/null
    echo "Governance adopted. Status: RECONCILIATION_REQUIRED"
    ;;
  *) echo "Mode must be New or Adopt." >&2; exit 1 ;;
esac
