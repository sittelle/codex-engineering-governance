from pathlib import Path
text=Path("src/app.py").read_text(encoding="utf-8")
raise SystemExit(1 if "eval(" in text else 0)
