# ADR 0001: Business-led mode — three-layer architecture, enforcement switch, and pathway mapping

## Status

Accepted. Approved by Gregor Kleiber, framework maintainer, on 2026-09-18, as
part of `docs/business-led/implementation-plan.md` (change class C2). This
ADR is the durable design decision required by
[global/governance-standard.md](../../global/governance-standard.md#new-project-evidence-boundary)
before substantial implementation of business-led mode; the plan remains the
detailed work record and is referenced from here.

## Context

The framework in its 2.0.0 form governs a competent developer working alone
with a coding agent, and it assumes that person can judge security, approve
risk, and decide whether software may be used for real work. IBO wants to use
the framework for business employees who describe software and let an agent
build it. That person cannot make those judgments; IT Security holds them
instead.

The September 2026 gap assessment of framework 2.0.0 found that governance
artifacts are agent-writable and unverified, enforcement is prompt-only with
no compensating deterministic control, there is no role model for a business
user, and agent runtime configuration (MCP servers, hooks, plugins, memory,
bypass modes) is ungoverned. A role model that still asks the business
employee to approve C2/C3 direction or accept risk would not close these gaps;
it would just relocate the same failure to a different job title. The
decision recorded here is the architecture that makes IT Security's approval
authority real rather than advisory, without creating a second policy or
assurance model alongside the existing one.

## Decision

### Three layers

Every control introduced for business-led mode is placed on exactly one of
three layers, chosen by who can change it and therefore how much it can be
trusted:

| Layer | Owner and location | Examples | Who can write |
| --- | --- | --- | --- |
| 1 | IT-owned, outside the repository | Managed agent settings, governance hook, read-only framework root, enforcement mode, CI pipeline execution policy | Neither the agent nor the user |
| 2 | Machine-readable state in the repository, agent-readable only | Registration file, assurance facts, integrity manifest, pinned baseline | Governance tooling; protected by hashes and the hook |
| 3 | Instructions to the model | Kernel, managed blocks, workflows, skills | Framework maintainers; kept short, tested by behavioral campaigns, treated as probabilistic |

The managed client makes Layer 1 real: because the business employee has no
administrative rights on the VM or computer, hooks, deny rules and the
read-only root cannot be removed by the person using them. The IT-owned CI
pipeline is the evidence gate for real use, so a local circumvention of a
lower layer never reaches an approval. This ordering is a direct response to
gap 1 (governance artifacts are agent-writable) and gap 2 (prompt-only
enforcement without a compensating control) in the plan's background section.

### Enforcement switch

The framework ships two managed-settings templates, `inform` and `block`,
differing only in one parameter passed to the governance hook. IT Security
decides which one IT deploys; the framework never makes that choice for
itself.

- `inform` is the default and reflects IBO's current stance that deployment
  rules are organisational, not the framework's to enforce.
- `block` pauses mutating tools when the registration says the highest risk
  level, is missing, fails integrity, or when drift is unreconciled.

The CI pipeline policy carries the same switch as a variable, and every
report records the mode observed and its source, `MANAGED` or `ABSENT`. The
fail-closed rule is: an enforcement file that is present but invalid means
`block`; a missing file means `inform`, reported as `ABSENT` so IT Security
can see clients that lack the policy rather than silently assuming coverage.

### Pathway mapping

IT Security's risk assessment yields one of three pathways, which the
framework consumes as input without defining the assessment itself:

| Pathway | Meaning at IBO | Approval authority in business-led mode | What the framework does |
| --- | --- | --- | --- |
| Green | No relevant security risk, business-owned | IT Security, automated rule permitted | Lightweight rigor, readiness packet for automated approval |
| Amber | Relevant but manageable risk, business-owned with IT Security conditions | IT Security, manual | Threat model, security tests, authentication design where triggered, readiness packet for manual review |
| Red | Relevant risk, IT ownership required before real use | Professional IT before real use | Full rigor, development continues, readiness packet states IT ownership is required |

Consistent with principle 1 in the plan, the pathway changes rigor and
routing; it never blocks development on its own. Blocking behaviour exists
only behind the `block` enforcement switch above, which only IT-managed
settings can select.

### What this does not create

No parallel policy, severity, exception, or assurance model. Business-led
mode feeds the existing maturity (M0-M3) and assurance (SA0-SA3) levels and
the existing C0-C3 approval boundaries defined in
[global/governance-standard.md](../../global/governance-standard.md) and
[global/operating-contract.md](../../global/operating-contract.md). It adds a
role model, a registration contract, and deterministic Layer 1/2 controls;
it does not redefine what a finding, an exception, or a risk acceptance is.

## Consequences

- Deployment and run-location restrictions remain organisational. The
  framework informs, records, and routes; it does not stop development, not
  even for the Red pathway. This is a deliberate boundary, not a gap: see
  `docs/business-led/implementation-plan.md` section 3.
- Local evidence and local enforcement are deterrence, not the gate, whenever
  the managed client cannot be fully trusted (for example if the "no
  administrative rights" assumption in the plan's section 11 later proves
  false for some client population). The CI pipeline remains the evidence
  gate in every case.
- Every new deliverable in the workstreams that follow this ADR (WS1-WS7 in
  the implementation plan) must declare which of the three layers it belongs
  to. A deliverable that cannot be placed on Layer 1 or 2 and needs to be
  trusted for a security-relevant decision is a design defect, not a
  workstream to build as specified.
- If a host (Claude Code or Codex) turns out to offer no managed policy
  surface for Layer 1, that host's Layer 1 is incomplete for business-led
  mode. The implementation plan requires recording this as a KNOWN RISK
  rather than substituting a project-level, user-editable setting that would
  collapse Layer 1 into Layer 3.
- This architecture is extended, not superseded, by later phases: the
  registration contract and drift detection (WS4, phase 2-3) populate Layer
  2; the normative AI-specific content (WS5, phase 4) populates Layer 3.

## References

- `docs/business-led/implementation-plan.md` — the approved work record,
  sections 2-5.
- `docs/framework-threat-model.md` — updated alongside this ADR to add the
  threats this architecture is a control for (agent tampering, inbound
  prompt injection, agent over-privilege, registration drift).
- `global/governance-standard.md`, `global/operating-contract.md` — the
  existing maturity/assurance/change-class model this architecture feeds
  rather than replaces.
