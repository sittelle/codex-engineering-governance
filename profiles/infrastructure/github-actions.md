# GitHub Actions Profile

Treat workflows as privileged executable code. Use minimal explicit token permissions, immutable/pinned third-party actions for security-sensitive workflows, no privileged secrets for untrusted PR code, careful `pull_request_target`, safe handling of event data, and separation of verification from publication.

Required gates never use failure-ignoring merely to stay green. Self-hosted runners are high-value infrastructure and must not execute arbitrary untrusted fork code without strong isolation.
