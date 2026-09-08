# Docker Profile

Docker is not a professionalism checkbox. Use trusted/minimal maintained bases, non-root runtime where feasible, multi-stage builds where useful, minimal build context, `.dockerignore`, no embedded secrets, only required ports/packages/capabilities, and scan final images when delivered/deployed.

Privileged containers, Docker socket access, host namespaces, broad mounts, and mutable `latest` release dependencies require justification.
