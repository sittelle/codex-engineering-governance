# Emergency Fix Workflow

Use this workflow for:
- active production outages;
- severe regressions materially affecting users or operations;
- urgent security containment;
- critical dependency/service breakage;
- emergency recovery where normal delivery sequencing is too slow.

Core principle:

**Emergency means compressed process, not absent process.**

## Flow

CONFIRM INCIDENT → CONTAIN → CLASSIFY RISK → CHOOSE SMALLEST SAFE ACTION → APPROVE MATERIAL EMERGENCY TRADEOFF → IMPLEMENT → MINIMUM VERIFY → RELEASE/RECOVER → MONITOR → RECONCILE

## 1. Confirm the incident

Establish only what is necessary to act safely:
- what is failing;
- who/what is affected;
- production/environment scope;
- severity and urgency;
- known recent change or trigger, if any;
- whether security, integrity, availability, privacy, or data loss is involved.

Do not spend incident time producing complete documentation before containment.

Do not act on an assumed root cause when a reversible containment step can reduce harm first.

## 2. Contain before broad change

Prefer, where applicable:
- rollback to last known good version;
- disable/isolate only the failing feature;
- traffic restriction/routing;
- failover;
- rate limiting;
- read-only mode;
- queue pause;
- credential/key revocation;
- narrow configuration rollback.

Prefer containment that reduces blast radius and is easy to reverse.

Do not globally weaken security merely because it restores availability if a narrower safe containment exists.

## 3. Classify the emergency change

Determine the minimum useful change class.

Escalate when the emergency action:
- weakens authentication/authorization;
- broadens public exposure;
- changes privilege;
- risks data loss/corruption;
- disables required security controls;
- changes trust boundaries;
- alters destructive automation;
- changes release-gate policy;
- cannot be safely reversed.

C3 rules still apply to high-consequence actions even during an incident.

Urgency is not approval.

## 4. Choose the smallest safe action

Recommend the smallest action that restores or protects service while preserving important invariants.

Prefer:
1. rollback;
2. targeted feature disablement/isolation;
3. bounded configuration change;
4. minimal code hotfix;
5. broader architectural/security change only when no safer bounded option exists.

Do not bundle cleanup/refactoring/unrelated upgrades into an emergency fix.

## 5. Security and destructive stop conditions remain active

Emergency work MUST NOT silently:
- disable authentication/authorization globally;
- suppress Critical/High findings simply to release;
- bypass required security controls without an explicit policy exception;
- delete/overwrite data without the destructive-data approval boundary;
- disable integrity/signature/provenance protections;
- expose secrets;
- expand privileges beyond the emergency need.

If an emergency action knowingly introduces a material security/safety risk, surface it explicitly and require developer/authorized-owner approval.

The agent cannot approve its own risk acceptance.

## 6. Emergency approval brief

For C2/C3 emergency work, present a short emergency brief:
- incident/impact;
- proposed action;
- why narrower containment/rollback is insufficient;
- affected systems/users/data;
- material security/data/support tradeoffs;
- rollback/recovery path;
- minimum verification before deployment;
- checks/evidence that will be deferred.

Obtain approval of the emergency direction before implementation when a material tradeoff remains.

Do not require a full normal design package before an urgent bounded fix.

## 7. Implement the smallest viable patch

Keep the patch:
- narrow;
- reviewable;
- reversible where possible;
- isolated from unrelated changes;
- free of opportunistic dependency upgrades/refactors;
- instrumented enough to determine whether the fix worked.

If a feature flag/config toggle is used, define owner/expiry/follow-up so the emergency state does not silently become permanent.

## 8. Minimum verification

Run the strongest verification that is feasible within incident constraints.

At minimum, verify:
- the changed path behaves as intended;
- the original incident reproduces before / no longer reproduces after where feasible;
- no obvious adjacent critical behavior is broken;
- security/destructive invariants relevant to the fix;
- build/package/startup viability as applicable;
- rollback/recovery command/path.

For SA2/SA3 or security-sensitive incidents, required controls remain required unless a distinct explicit governance/policy exception authorizes proceeding without them.

If a check cannot execute, record `DID_NOT_EXECUTE` / `INCOMPLETE ASSURANCE`, not PASS.

## 9. Release / recovery decision

Before deploying the emergency fix, report:
- what was verified;
- what was not verified;
- known residual risks;
- whether any exception/risk acceptance exists;
- rollback trigger and procedure;
- monitoring signals.

Emergency release may proceed with incomplete non-critical evidence only when the responsible developer/owner explicitly accepts the bounded residual risk and no non-waivable security/destructive blocker remains.

Do not redefine the baseline merely to make the emergency pass.

## 10. Monitor

After deployment:
- confirm service/incident recovery;
- watch relevant error, security, performance, and data-integrity signals;
- be prepared to roll back if the fix worsens impact or violates assumptions;
- avoid immediately layering unrelated follow-up changes onto an unstable system.

## 11. Mandatory reconciliation

After stabilization, perform a normal governance reconciliation.

Record:
- incident summary and root cause status;
- exact emergency change;
- approvals/risk acceptances/exceptions;
- skipped/deferred verification;
- full verification results when run;
- temporary controls/toggles and their removal date;
- follow-up tests/monitoring/docs;
- whether the emergency patch should be retained, redesigned, or reverted.

Deferred governance work is `REMAINING WORK`, not silently complete.

A temporary emergency bypass MUST have an owner and review/expiry trigger.

### Emergency-response completeness

An emergency recommendation is incomplete if it states only how to restore service or only that deferred checks will run later. When deferred verification or temporary measures are possible, explicitly state both post-stabilization obligations:
1. complete/reconcile deferred verification; and
2. review and remove or deliberately reconcile temporary bypasses, toggles, exceptions, and emergency risk acceptances.

Temporary measures require owner/review/expiry while active and must not silently become permanent after recovery.

## 12. Completion

The emergency workflow is complete only when:
- the incident is stabilized;
- the current deployed state is understood;
- deferred required verification has been resolved or explicitly dispositioned;
- temporary emergency measures are either removed or governed as intentional;
- the repository has durable evidence of the emergency and reconciliation.

## Stop conditions

Stop and surface the issue when:
- the proposed fix broadly weakens authentication/authorization without explicit owner approval;
- destructive impact is unclear;
- rollback/recovery is unavailable for a high-consequence change and that risk is not explicitly accepted;
- required assurance is missing and no valid policy exception exists;
- the incident scope cannot be bounded enough to act safely;
- the proposed “hotfix” includes unrelated changes;
- the fix requires changing governance rules just to permit release.

## Prohibited behaviors

Do not:
- treat urgency as permission;
- disable security globally when narrower containment exists;
- change release thresholds to force an emergency deployment;
- call unexecuted checks PASS;
- hide skipped verification;
- leave temporary security bypasses without owner/expiry;
- bundle refactors or broad dependency upgrades into the hotfix;
- claim root cause is fixed when only symptoms were contained.
