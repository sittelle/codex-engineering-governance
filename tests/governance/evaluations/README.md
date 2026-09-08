# Behavioral Evaluation Evidence

Store completed, unedited behavioral evaluation records here. A scenario file is a test definition; it is not evidence that the scenario was executed or passed.

For candidate acceptance, preserve the exact scenario prompt, raw response, score, rationale, governance version, scenario-definition baseline, date, and known execution-context metadata. Use `unknown` where historical metadata was not recorded rather than inventing it. Historical records created before the scenario-definition-baseline field existed remain valid historical evidence without retroactive edits.

The v0.4.0 package includes the exact GOV-024, GOV-025, and GOV-026 records available from the August 27 validation cycle. It intentionally does not fabricate records for earlier scenarios. A complete candidate evaluation set is required before a 1.0 release decision.

GOV-027 and GOV-028 were introduced in v0.4.0 and intentionally have no completed evaluation record until their fresh-session responses are actually executed and scored.

## Re-evaluation and retry records

Do not overwrite or edit a prior scored attempt merely because governance guidance changed afterward. Preserve the original attempt and add a separate record for every fresh retry. For repeated attempts of the same GOV scenario:

- keep the exact scenario wording and scoring rubric unchanged unless the test definition itself is separately approved for change;
- include `Attempt: N` in each new record; historical records without an attempt number are treated as attempt 1 when unambiguous;
- use a distinct filename for attempt 2 and later, for example `GOV-029-framework-self-governance-applicability-attempt-2.md`;
- candidate acceptance uses the latest completed attempt **against the scenario definition currently under evaluation**; attempts against an older deliberately revised definition remain durable regression/history evidence but do not satisfy the current candidate set; and
- a failed or partial attempt remains durable behavioral failure/regression evidence in its evaluation record; it is not an approved exception or risk acceptance and does not require a second parallel record.


## Invalid evaluator probes

A run is not a scored attempt when the evaluator failed to supply facts required by the scenario definition, used the wrong declared execution context, or otherwise did not exercise the defined behavior. Do not manufacture a score for such a probe and do not overwrite a valid prior attempt. Record the harness defect or validation finding in the version validation/changelog when it materially affects the evaluation campaign.
