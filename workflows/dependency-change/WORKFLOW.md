# Dependency Change Workflow

Use this workflow when adding, removing, upgrading, replacing, pinning, or materially reconfiguring a direct or transitive dependency.

Examples:
- new runtime/build/dev dependency;
- patch/minor/major upgrade;
- security-driven upgrade;
- package replacement/removal;
- lockfile regeneration that changes transitive versions materially;
- runtime/platform-support changes caused by dependencies.

## Flow

CLASSIFY → ESTABLISH NEED → ASSESS TRUST/RISK → ANALYZE IMPACT → RECOMMEND DIRECTION → APPROVE MATERIAL TRADEOFFS → CHANGE → VERIFY → REVIEW LOCKFILE/TRANSITIVES → DOCUMENT

## 1. Classify the change

Determine:
- direct or transitive;
- runtime, build, development, test, or tooling dependency;
- patch/minor/major version change;
- security-driven or maintenance-driven;
- whether API, data, platform, runtime-support, licensing, privilege, network, build, or deployment behavior changes;
- whether the change establishes or materially changes the project Technology Baseline;
- C1/C2/C3 impact.

Routine well-maintained patch updates with no material behavior/support/security/Technology-Baseline change may remain C1.

Escalate to C2 when the dependency materially affects APIs, architecture, supported runtimes/platforms, security posture, licensing, operational behavior, transitive surface, or an established Technology Baseline.

C3 may apply when the change enables dangerous privilege/external effects, irreversibly changes persisted data, or has another high-consequence boundary.

## 2. Establish necessity

For additions:
- state the exact capability needed;
- check whether the standard library/platform/current dependencies already provide it;
- compare local implementation when the functionality is small and stable;
- avoid dependencies whose lifecycle cost is disproportionate to the value.

For upgrades:
- state why now: vulnerability, bug, support/EOL, compatibility, feature requirement, maintenance, or ecosystem constraint.

For removals/replacements:
- identify what capability is being removed/replaced and what consumers depend on it.

Do not add a dependency merely because it saves generated lines.

## 3. Assess dependency trust and provenance

As applicable, inspect:
- authoritative package/project source;
- maintainer/project continuity;
- release history and maintenance activity;
- package provenance/publisher identity;
- security advisories;
- known malicious/compromised-package history;
- transitive dependency count and material risk;
- licensing/usage compatibility;
- install/build scripts or native-code execution;
- binary/prebuilt artifact provenance;
- network access or telemetry behavior;
- privilege/sandbox implications.

Prefer mature, well-scoped, maintained dependencies with understandable provenance.

## 4. Security finding reachability

When an upgrade is driven by a vulnerability/advisory:
- identify affected versions and feature/path prerequisites;
- determine whether the project actually invokes the vulnerable code path where feasible;
- distinguish `VULNERABLE AND REACHABLE`, `VULNERABLE BUT NOT DEMONSTRATED REACHABLE`, `NOT AFFECTED`, and `UNVERIFIED`;
- do not call a vulnerability false-positive solely because the project believes it does not use the affected feature;
- preserve release-gate semantics required by assurance policy.

If a High/Critical dependency issue is required to block release, a temporary stay-on-old-version decision is a risk disposition, not remediation.

The agent cannot approve its own risk acceptance.

## 5. Analyze compatibility and product impact

Before a material upgrade/replacement, identify:
- breaking API/configuration changes;
- runtime/compiler/platform support changes;
- changed defaults;
- security model changes;
- file/data/protocol format changes;
- performance/resource changes;
- deprecations/removals;
- required source/config/test changes;
- downstream/public API impact;
- deployment/rollback implications.

A dependency upgrade that drops an existing supported runtime/platform is a product/support decision. Recommend the technical direction, but obtain developer approval before narrowing an approved support promise.

Do not silently modify declared support to satisfy a package upgrade.

## 6. Analyze lockfile and transitive impact

Treat lockfile changes as evidence, not noise.

After dependency resolution:
- inspect direct version changes;
- identify material transitive additions/removals/upgrades/downgrades;
- flag unexpected package-source/provenance changes;
- check duplicate/conflicting versions where relevant;
- distinguish intended resolver churn from unexplained churn;
- avoid unrelated lockfile refresh when a scoped update is possible.

Do not review only the manifest while ignoring a materially changed lockfile.

## 7. Recommend a direction

Present:
- recommended dependency/version/change;
- why it is the best fit;
- meaningful alternatives only when they affect security, support, complexity, licensing, or architecture;
- migration cost;
- temporary risk if deferring;
- material support/product tradeoffs.

Technical dependency choices are recommendations by default.

Product scope/support reductions and material risk acceptance require developer direction.

## 8. Approval boundary

Obtain approval before implementation when the dependency change materially:
- drops an approved runtime/platform;
- introduces a new external service/trust boundary;
- changes licensing obligations materially;
- adds privileged/native/install-time execution;
- changes security-critical behavior;
- introduces a major architecture/runtime commitment;
- accepts a known release-blocking risk rather than remediating it.

Routine C1 maintenance does not require ceremonial approval.

## Technology Baseline interaction

A framework, runtime, persistence, deployment/packaging, supported-platform, or other architecture-significant dependency may be both a dependency/supply-chain commitment and a Technology Baseline decision.

When this workflow would materially establish or change the Technology Baseline:
- do not treat the change as ordinary manifest/lockfile maintenance;
- invoke/reuse `technology-selection` analysis for the architecture-significant direction;
- record the intended target in the durable Technology Baseline;
- use `RECONCILIATION_REQUIRED` during an approved transition;
- obtain the existing C2/C3 approval before substantial implementation;
- reconcile canonical quick/full verification and newly applicable assurance capabilities for the resulting stack;
- return to `ESTABLISHED` only when the durable baseline, implementation/dependency graph, support claims, and verification agree.

Do not create a parallel dependency registry or duplicate the complete resolved dependency graph in the Technology Baseline.

## 9. Make the change

Keep the dependency change scoped:
- change only necessary manifest/lock/config/source/test files;
- avoid opportunistic unrelated upgrades;
- use ecosystem-native resolution/install commands;
- preserve reproducibility and committed lockfiles where the ecosystem expects them;
- do not bypass integrity/provenance checks just to complete installation.

## 10. Verify

Run the project canonical verification interface.

Additionally, as applicable:
- dependency consistency/resolution;
- unit/integration/regression tests for affected paths;
- supported runtime/platform matrix impacted by the change;
- security/advisory scan;
- build/package/install verification;
- license/compliance check;
- smoke test of changed defaults/configuration;
- rollback/downgrade feasibility for operationally risky changes.

Do not claim support for runtimes/platforms that were not actually verified.

## 11. Review final dependency graph

After verification:
- inspect final direct and material transitive versions;
- ensure the intended vulnerability/support issue is actually resolved;
- ensure no unexpected dependency/source was introduced;
- record remaining advisories/known risks accurately.

A scanner recommendation to “upgrade” does not prove the chosen resulting graph is safe.

## 12. Completion evidence

Report:
- dependency and old/new version or add/remove action;
- reason for change;
- security/advisory disposition;
- material support/API/license/transitive changes;
- Technology Baseline impact and reconciliation state when applicable;
- verification actually run and results;
- unverified supported environments;
- accepted/known risks;
- remaining migration/deprecation work.

Use `VERIFIED`, `UNVERIFIED`, `KNOWN RISK`, `ACCEPTED RISK`, `NOT APPLICABLE`, and `REMAINING WORK` accurately.

## Stop conditions

Stop and surface the issue when:
- package identity/provenance is unclear;
- a material license conflict is unresolved;
- a security advisory is not understood enough to characterize;
- an upgrade would silently drop an approved runtime/platform;
- unexpected lockfile/transitive changes cannot be explained;
- required verification cannot execute;
- the requested shortcut weakens security/integrity controls;
- dependency behavior introduces an unapproved trust boundary or privileged effect;
- an architecture-significant dependency change would create unapproved or unexplained Technology Baseline drift.

## Prohibited behaviors

Do not:
- install a package only because it is convenient;
- equate popularity with trust;
- ignore transitive or lockfile changes;
- mark a vulnerability false-positive without evidence;
- suppress advisories merely to make CI green;
- silently drop supported runtimes/platforms;
- perform unrelated bulk dependency upgrades during a scoped change;
- disable integrity/signature/provenance checks to force installation;
- claim compatibility based only on declared version metadata;
- silently change an established Technology Baseline through dependency maintenance.
