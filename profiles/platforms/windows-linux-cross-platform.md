# Windows/Linux Cross-Platform Profile

Declare whether each OS is development/runtime/build/release target. Use platform-aware paths and app-data/temp APIs; do not hard-code separators or user paths.

Account for case sensitivity, filenames, path normalization, line endings, encoding, shell differences, permissions, symlinks, file locking, process behavior, and packaging.

Claim cross-platform support only with appropriate target testing. Prefer one cross-platform verification mechanism over duplicate scripts.
