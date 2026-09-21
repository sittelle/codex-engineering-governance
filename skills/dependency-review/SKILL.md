# Dependency Review

Establish necessity before adding a package. Consider platform/built-in alternatives, maintenance, provenance, security history, transitives, install hooks, license, compatibility, and deterministic versioning.

Before trusting a package name the agent itself suggested, confirm it actually exists on the authoritative registry under that exact name, is not a plausible typosquat/namespace-confused near-miss of an intended package, and has a publisher/maintainer identity and publication history consistent with a real, established project. Install only through the ecosystem's lockfile-aware resolution command; a name that does not resolve, or resolves to something unexpected, is a stop condition.

Apply stronger scrutiny to authentication, crypto, parsers, networking, files/archives, process execution, templates, secrets, and database libraries.

Do not add supply-chain liability merely to save a few trivial lines.
