# ADR 0002: Developer language replaces business-led mode; "Professional" replaces "IT Security"

## Status

Accepted. Approved by Gregor Kleiber, framework maintainer, on 2026-09-21, in
conversation on `feature/business-led-mode`. This ADR records the decision;
implementation follows as its own commits. It extends, not supersedes,
[ADR 0001](0001-business-led-mode-architecture.md).

## Context

The framework's main goal is enabling people without professional software
development or security knowledge to build professional-grade software
through vibe coding. Working through that goal surfaced two problems with
how ADR 0001's role model was named and mechanized:

1. **"IT Security" is the wrong name for the concept.** The framework needs
   a person with professional software-development and/or professional
   security knowledge to weigh in on decisions the primary coder cannot
   safely make alone. That person does not have to sit in an IT Security
   department — a professional software developer qualifies exactly as much
   as a security specialist. Naming the role "IT Security" throughout the
   codebase (the `IT_SECURITY` risk classification, `PENDING_IT_SECURITY`,
   the "involve IT Security" routing outcome, registration's "IT Security
   contact") was more specific than the actual requirement and would mislead
   an organization without a formal IT Security function into thinking the
   framework does not apply to them.

2. **`governance.mode` lived in the wrong place, and self-declaring it was
   never actually safe.** `mode: professional | business-led` sat inside the
   `governance:` block, which WS1's integrity system hashes and protects —
   so an ordinary coder changing it would trip tamper detection. But the
   field was never meant to be a security boundary: it selects vocabulary
   and default routing, not which controls apply. Separately, even in
   professional mode, nothing distinguished an ordinary implementation
   decision from one that genuinely requires deep expertise — a person
   fluent in engineering terminology could self-certify a decision beyond
   their actual judgment with no more ceremony than any routine call,
   because "professional mode" carried no explicit acknowledgment step for
   hard decisions.

## Decision

### Rename: `governance.mode` becomes `developer_language`

- Field name: `developer_language`, values `"professional"` /
  `"non-professional"` (was `mode`, values `"professional"` /
  `"business-led"`).
- Location: top-level in `project-governance.yml`, **outside** the
  `governance:` block — project-owned, not governance-owned. The coder may
  change it directly at any time, including changing their mind later.
  Tamper detection excludes it by construction: only the `governance:` block
  is hash-checked, and this field never was and never will be inside it.
- What it selects: which kernel/vocabulary the framework speaks in, and the
  default routing behavior for decisions classified as needing professional
  judgment (see below). It does not change which controls apply, the
  maturity/assurance/change-class model, or governance-artifact integrity
  protection. A self-declared preference must never be able to weaken a
  control; if it could, the "hardened framework that cannot be corrupted"
  goal would not hold.

### Rename: "IT Security" becomes "Professional" throughout

- Risk classification: `BUSINESS` / `IT_SECURITY` becomes `BUSINESS` /
  `PROFESSIONAL`.
- Decision state: `PENDING_IT_SECURITY` becomes
  `PENDING_PROFESSIONAL_REVIEW`.
- Routing outcome: "involve IT Security" becomes "involve a Professional".
- Registration's `approval_authority` field keeps its name (it still
  accurately describes the role) but its placeholder/description changes
  from "IT Security contact" to a named professional — a professional
  software developer and/or a professional security person, not
  necessarily a department.
- "Professional" is defined by demonstrated software-development and/or
  security competence, not by job title, department, or employment
  relationship to the organization.

### New mechanism: explicit acknowledgment for hard decisions under `developer_language: professional`

A decision the framework classifies as needing professional judgment (C2/C3
material direction, or a `PROFESSIONAL`-classified risk) is handled
differently depending on `developer_language`:

- **`non-professional`**: routed to an actual named Professional. Their
  name and their decision are recorded in a durable record — generalizing
  the existing `PENDING_IT_SECURITY` / request-record mechanism from a
  fixed department to a named individual.
- **`professional`**: self-certification remains allowed, but the framework
  states explicitly, at that moment, that the decision will be recorded as
  a professional decision, and that this specific kind of call is hard even
  for someone fluent in the terminology. The decision is then documented as
  such, under the coder's own name. This is new: professional mode
  previously had no equivalent acknowledgment step, so a coder fluent in
  jargon but without the underlying judgment could self-certify a decision
  as routinely as any other, with no audit trail distinguishing it.

Either way, the decision gets recorded with a name attached and is visibly
marked as a professional decision. The difference is only whether that name
can be the coder's own (`professional`) or must be someone else's
(`non-professional`).

### What does not change

The three-layer architecture, the `inform`/`block` enforcement switch, and
the Green/Amber/Red pathway mapping from ADR 0001 are unchanged. The
maturity (M0-M3), assurance (SA0-SA3), and change-class (C0-C3) model is
unchanged. This ADR is a rename and one added acknowledgment mechanism on
top of that architecture, not a replacement for it.

## Consequences

- This rename touches roughly 40+ files: `governance.py`'s mode constant,
  template selection, and CLI flags; both kernel templates and their
  AGENTS.md counterparts (the business-led kernel/AGENTS files are renamed
  to `*.non-professional.md`); `global/governance-standard.md`'s
  approval-authority section; every workflow's routing-outcomes section;
  `templates/repository/registration.yml` and `project-governance.yml`;
  GOV-031 through GOV-036 (built on this branch, not frozen); and the test
  scripts exercising all of the above. It is executed as its own series of
  commits following this ADR, each independently verified.
- `docs/business-led/phase-2-review.md`, `phase-3-review.md`,
  `phase-4-review.md`, `implementation-plan.md`, and the other planning
  documents under `docs/business-led/` are **not** retroactively edited.
  They are durable records of what was actually decided and built at the
  time, using the terminology current then; rewriting them would falsify
  the evidence trail this framework itself insists on. This ADR and the
  commits that follow it are the record of the terminology changing, not a
  correction to make the old records "right."
- The `docs/business-led/` directory name itself is not renamed for the
  same reason: it is the historical record of the workstream that produced
  this architecture, and business-led mode's concepts (registration,
  pathways, drift detection) are unchanged by this ADR — only the mode
  field's name/location and the approval-authority role's name change.
- Any future reference to this capability in new documentation should use
  `developer_language` and "Professional" going forward.

## References

- [ADR 0001](0001-business-led-mode-architecture.md) — the three-layer
  architecture, enforcement switch, and pathway mapping this ADR extends.
- `docs/business-led/implementation-plan.md` — the original work record,
  unchanged, using the terminology current when it was written.
- `global/governance-standard.md` — updated alongside this ADR's
  implementation commits for the renamed approval-authority model and the
  new professional-acknowledgment mechanism.
