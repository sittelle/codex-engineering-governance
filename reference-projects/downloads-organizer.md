# Reference Project — Downloads Organizer

Recommended: M1 / SA1, new-project workflow, technology-selection + architecture + automation-safety + testing.

Default direction:
- local Windows/Linux app;
- no server/cloud;
- dry-run;
- no deletion;
- no overwrite;
- bounded Downloads root;
- operation journal;
- no DB unless durable structured history/rules actually require it.

Potential C3: bulk filesystem operation with credible large-scale displacement/loss even when moves are reversible.

Key tests: dry-run immutability, root confinement, symlink escape, collision handling, repeated execution, partial failure.
