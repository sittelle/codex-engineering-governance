from pathlib import Path
bad=[]
for p in Path("src").rglob("*"):
    if p.is_file() and "EXAMPLE_SECRET_MARKER" in p.read_text(encoding="utf-8",errors="ignore"): bad.append(str(p))
raise SystemExit(1 if bad else 0)
