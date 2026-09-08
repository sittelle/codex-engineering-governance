# Python Profile

Use an actively supported stable Python version verified at project creation/upgrade. Prefer `pyproject.toml`, isolated deterministic dependencies, type annotations on meaningful boundaries, maintained formatter/linter/type checker, and pytest or justified equivalent.

Use `pathlib` for paths. Prefer direct `subprocess` argument APIs. `shell=True`, eval/exec, unsafe deserialization, archive extraction, temporary-file logic, crypto, and untrusted filesystem paths trigger security scrutiny.

Never use `pickle` for untrusted input, `random` for security tokens, disabled TLS verification, broad exception swallowing, or broad type/security suppressions without justification.
