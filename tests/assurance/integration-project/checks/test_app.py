from pathlib import Path
ns={}
exec(Path("src/app.py").read_text(encoding="utf-8"),ns)
assert ns["add"](2,3)==5
