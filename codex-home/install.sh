#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
GOVERNANCE_ROOT=${1:-$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)}
CODEX_HOME_DIR=${CODEX_HOME:-"$HOME/.codex"}

KERNEL="$GOVERNANCE_ROOT/codex-home/AGENTS.md"
VERSION_FILE="$GOVERNANCE_ROOT/VERSION"

[ -f "$KERNEL" ] || { echo "Governance kernel not found: $KERNEL" >&2; exit 1; }
[ -f "$VERSION_FILE" ] || { echo "Governance VERSION not found: $VERSION_FILE" >&2; exit 1; }

mkdir -p "$CODEX_HOME_DIR"

TARGET="$CODEX_HOME_DIR/AGENTS.md"
LOCATOR="$CODEX_HOME_DIR/GOVERNANCE_ROOT"

if [ -f "$TARGET" ]; then
  TS=$(date +%Y%m%d-%H%M%S)
  cp "$TARGET" "$TARGET.backup-$TS"
  echo "Backed up existing AGENTS.md to $TARGET.backup-$TS"
fi

cp "$KERNEL" "$TARGET"
printf '%s' "$GOVERNANCE_ROOT" > "$LOCATOR"

VERSION=$(tr -d '\r\n' < "$VERSION_FILE")

echo
echo "Installed Codex engineering governance $VERSION"
echo "AGENTS.md:       $TARGET"
echo "GOVERNANCE_ROOT: $LOCATOR"
echo "Governance repo: $GOVERNANCE_ROOT"
echo
echo "Start a fresh Codex session after installation."
