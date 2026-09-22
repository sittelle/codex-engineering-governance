# ADR 0004: Full scenario goal audit (2026-09-22)

## Status

Accepted. Approved by Gregor Kleiber, framework maintainer, on 2026-09-22,
in conversation on `feature/business-led-mode`, following directly from the
GOV-029/GOV-030 rubric-calibration findings in
`docs/adr/0003-automated-behavioral-campaign.md`.

## Context

Reviewing GOV-029 and GOV-030's failed attempts (ADR 0003, "Follow-up")
surfaced a real flaw in two of the 36 canonical GOV scenarios: their
rubrics required a response to *verbally restate* something already true
and already enforced elsewhere, rather than testing an actual safety
property. Both were corrected. That raised the obvious next question: is
this an isolated pair of miscalibrated tests, or a pattern across the
whole 36-scenario set?

The maintainer asked for a full reverification: for every scenario, state
its goal in plain language, and check whether that goal actually points at
the framework's real objectives — enabling a non-professional developer to
build genuinely professional-grade software through AI assistance,
regulated by mechanisms that keep the AI's judgment sound, inside a
framework that resists being talked into weakening or corrupting itself.

## Decision

### Method

For each of the 36 scenarios, in file order: read the current Expected/
Forbidden/Score text, write a one-sentence goal statement naming the real
risk being tested and why it matters, then check whether the scenario's
actual scoring boundary (what separates a 1 from a 2, and a 1 from a 0)
tracks that real risk — or, as with GOV-029, tracks something narrower
like verbal completeness that doesn't actually change the real-world
outcome.

### Finding: 34 of 36 were already well-aimed

Going through the full set, every scenario from GOV-001 through GOV-028,
and GOV-031 through GOV-036, maps cleanly to a genuine, concrete risk:
protecting user/production data from AI-inferred destructive action
(GOV-003, GOV-009, GOV-014); keeping security-relevant decisions with the
people entitled to make them (GOV-002, GOV-010); resisting the AI being
talked into weakening its own verification signals (GOV-005, GOV-018,
GOV-021, GOV-023, GOV-024, GOV-026, GOV-035); preventing false or
incomplete assurance claims (GOV-006, GOV-020, GOV-025, GOV-027, GOV-028);
real engineering judgment under ambiguity or pressure (GOV-001, GOV-007,
GOV-008, GOV-011 through GOV-013, GOV-015 through GOV-017, GOV-019,
GOV-022, GOV-036); and — the most directly load-bearing scenarios for "a
framework that cannot be corrupted" — resisting the AI editing its own
governing rules (GOV-031), being fooled by a planted rule file (GOV-032),
or treating file/issue content it merely *read* as authoritative instead
of data (GOV-033, GOV-034). None of these needed adjustment; their 1-vs-2
boundaries already track a real difference in outcome, not just
phrasing.

GOV-029 and GOV-030 were the exceptions, and both are already corrected
per ADR 0003: GOV-029's rubric no longer requires reciting a list that
`framework-verification-plan.json` already enforces regardless of what the
response says; GOV-030 keeps its original wording (citing the project's
real transition-tracking term is still worth asking for) but is no longer
one of the scenarios that must individually score 2 for the whole campaign
to pass, since the property that actually matters — refusing the silent
drift — is protected by its `Critical: YES` no-zero floor regardless of
gate status.

### Goal field made permanent

Added a `Goal: <one sentence>` metadata line to every scenario file,
positioned like `Critical:`/`Execution context:` — a plain line, not a
markdown heading, sitting entirely outside the `## Scenario` section so it
can never leak into the candidate-facing prompt (confirmed directly:
`scenario_rows()` still loads all 36 cleanly, and no rendered prompt
contains the string `Goal:`). `manual-behavioral-campaign.py`'s
`validate_scenario_format()` now requires this field, so a future scenario
cannot be added without first stating what real risk it tests for and,
implicitly, forcing the same alignment question this audit just answered
for all 36 existing ones.

## Consequences

- The framework's test bank is confirmed, not merely assumed, to test what
  it claims to test. This is durable evidence, not a one-time check: the
  goal statements themselves are now part of the canonical, validated
  scenario format, so a future contributor changing a scenario's
  Expected/Forbidden/Score text has to reconcile it against a stated goal
  sitting right next to it, not against an unwritten assumption.
- This audit does not itself change any scored evidence. The two
  substantive changes it confirms (GOV-029's rubric wording, GOV-030's
  gate status) were already made and committed under ADR 0003; this ADR
  documents that they were the only ones needed, with the reasoning shown
  for the other 34.
- Future scenario reviews have a cheap, repeatable check: does the 1-vs-2
  (or 1-vs-0) boundary track a real difference in what would actually
  happen, or just a difference in how completely the response describes
  something already true? GOV-029 is the canonical example of the failure
  mode to watch for.

## References

- `docs/adr/0003-automated-behavioral-campaign.md` — the campaign findings
  that prompted this audit, and the GOV-029/GOV-030 fixes it documents.
- `tests/governance/README.md` — canonical scenario-file format,
  acceptance-target list.
- `scripts/manual-behavioral-campaign.py` — `validate_scenario_format()`,
  `scenario_rows()`.
