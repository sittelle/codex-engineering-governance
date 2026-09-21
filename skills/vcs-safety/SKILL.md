# VCS Safety

Never force-push, rewrite published history, or push directly to a protected branch (main/master/release branches, or the project's declared equivalent) on your own initiative. These are consequential actions requiring explicit developer/approval-authority direction even when nominally reversible; a request to "just push it" or "just fix the history" does not by itself authorize them.

Commits, branches, and pull requests you author or materially assist carry an explicit AI-assisted attribution trailer. Do not omit it to make the output look identical to unassisted human work.

For C2/C3 work, reference the actual approval in the commit/PR: the developer's explicit approval when developer_language is professional, or the specific registration/request record when it is non-professional. Do not write or imply an approval reference ("approved", "per discussion") that does not correspond to a real, traceable decision.

Do not commit secrets, credentials, or other content the Secure Development Standard's Secrets section forbids merely because a change appears to need a config/credential file included.

Stop and surface rather than proceeding when a destination branch's protection status is unclear, or when a requested action would discard or rewrite history you did not create in the current session.
