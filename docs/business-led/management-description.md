# Governing Business-led AI Development

A management description of roles, responsibilities, and the technical and
organisational measures that make vibe coding by business employees safe
enough to allow, with the Sittelle Engineering Governance Framework at the
centre.

| | |
| --- | --- |
| Audience | Management, function heads |
| Status | Draft |
| Framework | Sittelle Engineering Governance, business-led mode (planned) |
| Date | 2026-09-18 |

## 1. Summary

**Why.** AI coding agents let employees without development skills build
working software in hours. That is an opportunity: small tools, automations
and business ideas can be realised without waiting for a development team. It
is also a risk. The software may leak information, take actions nobody asked
for, contain vulnerabilities or unsafe components, and the person who built it
cannot tell.

**What.** Business employees may build software with AI, but only after IT has
approved them for it, only on a managed client that IT provides, and only for
projects whose risk has been assessed beforehand. Software without relevant
security risk stays with the business. Software with relevant risk is either
handed over to IT or stays with the business under IT Security's explicit
approval and conditions. Even the most sensitive software may be developed
this way; whether and where it may be run is a separate organisational
decision.

**How.** Three things work together. A managed client limits what the AI can
do. The governance framework guides the AI, keeps it inside the assessed
scope, collects evidence and routes decisions. IT Security takes the decisions
the employee cannot take. The employee stays responsible for saying what the
software should do and for checking that it does that. Nobody expects them to
judge security.

## 2. The problem in plain words

When a business employee tells an AI agent "build me a tool that reads our
supplier list and sends reminders", two things happen at once. The visible
part is code appearing and a program that runs. The invisible part is a series
of decisions: where the supplier data is stored, which internet service sends
the mail, which software libraries are pulled in, what happens when a name is
misspelt, and whether the tool can also delete things. The agent takes these
decisions in seconds, silently, and it is sometimes wrong.

A professional developer would notice most of this. A business employee will
see only that the tool works. A program that runs is not evidence that it is
correct or safe. The governance model exists to make the invisible decisions
visible, to route the important ones to people who can judge them, and to
stop the AI from doing things nobody should do without asking.

## 3. The model, end to end

1. **Approve the person.** IT approves an employee for AI-assisted
   development and provides a managed client.
2. **Describe and assess the project.** Before code is written, the project
   is described and its risk assessed: what data it touches, what it connects
   to, what it can do, who uses it. The assessment result and the approved
   scope are recorded and handed to the framework as its reference. This is
   not a one-time form. The description lives with the project and is kept
   current as the software grows.
3. **Develop.** The employee works with the AI agent on the managed client.
   The framework guides the agent, keeps the work inside the approved scope,
   notices when the software is about to gain a capability that was not
   assessed, proposes the update to the project description, and turns
   anything that needs a decision into a plain-language action for the
   employee and a request for IT Security. Description and assessment are
   therefore continuous: the framework helps the employee keep them true,
   and IT Security reassesses when the scope changes.
4. **Store and verify.** All code lives in the company Git. The company
   verification pipeline runs secret scanning, security analysis, package
   checks and tests. A check that did not run is never reported as passed.
5. **Decide on use.** Before the software is used for real work, IT Security
   checks it against the assessed scope and the evidence. Low-risk software
   can pass this step automatically; software with relevant risk gets a human
   decision or moves to IT.
6. **Operate and maintain.** The software runs only in the hardened,
   isolated environment provided for it, with only the approved connections.
   The employee keeps it maintained, asks for reassessment when it changes,
   and retires it when it is no longer needed.

The project description and its assessment are the anchor. Everything is
compared against them: the framework compares the code, IT Security compares
the evidence, and the employee keeps them current, with the framework
pointing out when an update is due.

Two kinds of risk are decided by two different people. The business employee
may accept business risks that sit within their own responsibility, for
example that a tool covers only part of a process or that a manual fallback
remains. IT and security risks, such as data exposure, unsafe components,
unauthorised access or effects on other systems, are decided by IT Security
only. The framework keeps the two apart and routes each to the right person.

## 4. Three outcomes of the risk assessment

| Outcome | When | Who owns the software | Before real use |
| --- | --- | --- | --- |
| Business-owned | No relevant security risk, for example a local tool that crops images to squares | The business employee | Automated readiness check, where IT Security has approved the rule |
| Business-owned with IT approval | Relevant but manageable risk, for example a tool that reads an internal list and sends reminder mails to colleagues | The business employee, under conditions set by IT Security | IT Security review and the additional safeguards it requires |
| Handed over to IT | Relevant risk that should not sit with the business, for example anything that changes customer records, moves money or grants access | Professional IT development | Transfer into the professional development lifecycle |

Two points matter for management. First, the outcome is about consequences,
not about technology. Second, the outcome does not stop development. A
business employee may build a prototype of even the most sensitive software.
The framework applies more rigor as the risk rises and records that IT must
take over before real use. Whether the employee may nevertheless run it
locally, in the data centre or in the cloud is an organisational rule, not
something the framework enforces.

## 5. Roles and responsibilities

| Role | Responsible for | Not responsible for | How the framework supports |
| --- | --- | --- | --- |
| **Business employee** (owner of the software) | Describing purpose and use truthfully, at the start and whenever the software changes; keeping the project description current; following the framework's plain-language actions; checking that the software does what was intended; accepting **business risks** within their own responsibility, for example that a report may be late or a manual step remains; maintaining and retiring the software; not giving the AI extra access or credentials | Judging security; reviewing code; accepting **IT or security risks** such as data exposure, unsafe components, unauthorised access or effects on other systems; approving exceptions; deciding on real use of risk-relevant software | Asks the right questions before building instead of assuming; keeps the project description as a living record and proposes updates when the software changes; turns technical situations into plain actions; generates the validation checklist the employee works through; records the employee's business-risk decisions so they are traceable; never asks the employee to decide a security question |
| **IT Security** | Assessing projects and setting their scope, at the start and on every material change; accepting or rejecting IT and security risks; owning and configuring the governance framework and how strictly it enforces; deciding on requests the framework routes to them; approving real use; watching the evidence; testing that the controls work; handling incidents | Building the client; operating the Git platform; writing the software | Delivers structured requests with the facts and the recommendation already prepared; detects scope drift and proposes the reassessment; derives verification settings from the assessed scope; produces the readiness packet; protects its own files and reports tampering; records enforcement mode and evidence truthfully so IT Security can trust what it sees |
| **IT** (client, network, identity, endpoint management) | Approving employees for AI-assisted development together with IT Security; providing the managed client; installing the framework read-only; deploying IT Security's settings and versions; network and package-source restrictions; keeping credentials off the client; logging; inventory; first-line support | Deciding rules, assessments, approvals or exceptions | Ships the templates IT deploys: managed agent settings, governance hook, pipeline definition; verifies its own installation and reports whether the managed policy is in effect; announces the minimum version so outdated clients are visible |
| **Professional IT development** | Taking over software that must not stay with the business; bringing it into the professional lifecycle; deciding what of the prototype can be reused | Assuming that a prototype is already secure or production-ready | Hands over a repository with a current project description, recorded decisions, verification evidence and open findings, so the takeover starts from facts rather than from reverse engineering |
| **Git platform team** | Protected branches, required checks, and the IT Security-owned verification pipeline that projects cannot edit | Content of the checks | Provides the pipeline definition and the checks it runs; binds every result to the exact commit so evidence cannot be mixed up |
| **The AI agent with the governance framework** | Doing the engineering due diligence the employee cannot: asking before assuming, recommending technical defaults, recording decisions, running verification, flagging scope drift, routing decisions to IT Security, reporting truthfully | Accepting risk of any kind; approving exceptions; changing rules or the assessed scope; declaring unexecuted checks as passed; deciding on deployment | The framework is the agent's rulebook and toolset: it defines what the agent must ask, recommend, record and verify, and the client makes sure the agent cannot rewrite those rules |
| **Management** | Adopting the model; assigning the responsibilities above; resourcing IT and IT Security; accepting the residual risks knowingly | Individual project decisions | Produces the evidence and the numbers management asks for: assessed projects, open requests, findings, tampering alerts, framework versions in the field |

## 6. Technical measures

| Measure | Protects against | Operated by |
| --- | --- | --- |
| Managed client (VM or computer) without administrative rights for the employee | Removal of any other protection, by mistake or intent | IT |
| Approved AI tools with company accounts only | Company code in unapproved services; personal accounts | IT, allowlist from IT Security |
| Governance framework installed read-only | The AI or the employee rewriting the rules the AI follows | IT deploys, IT Security owns |
| Managed agent settings and governance hook | The AI editing governance files, reading credentials, destroying Git history, using unapproved extensions | IT deploys, IT Security defines |
| Integrity checks on governance files | Undetected tampering with rules, verification settings or the assessed scope | Framework, results to IT Security |
| Scope drift detection | Software quietly gaining network access, storage, login or delete capability that was never assessed | Framework, requests to IT Security |
| Company Git only, protected branches, IT Security-owned verification pipeline | Code outside company control; verification that a project can switch off; unreviewed changes reaching use | Git platform team, IT Security |
| Secret scanning, static security analysis, package and vulnerability analysis, tests | Leaked credentials, common vulnerabilities, unsafe or malicious components | Framework in the pipeline |
| Curated package proxy | Non-existent, malicious or wrongly licensed packages proposed by the AI | IT |
| Restricted network egress; no route to production from the client | Unexpected data transfer; the AI or the software reaching systems it should not | IT |
| Hardened, isolated execution environment with only approved connections | Business software affecting other systems; uncontrolled access to information | IT, requirements by IT Security |
| Truthful verification semantics | A missing or crashed check being presented as a pass | Framework |
| Enforcement switch (inform or block), set only by IT Security outside the repository | The AI or the employee loosening enforcement | IT Security decides, IT deploys |

## 7. Organisational measures

| Measure | Protects against | Owner |
| --- | --- | --- |
| Strict approval of employees before they get a client | Uncontrolled spread of AI development | IT with IT Security |
| Project description and risk assessment before development and continuously as the software changes | Software nobody knows about; a description that no longer matches the software; no reference for what was intended | Business employee describes and keeps current, IT Security assesses, the framework proposes updates |
| Ownership decided by risk: business, business with IT approval, or IT | High-risk software treated like a hobby tool | IT Security |
| Business risks decided by the business employee, IT and security risks by IT Security, never by the AI | Security risk accepted by someone who cannot judge it; the AI approving itself | Business employee and IT Security, separated and routed by the framework |
| Employee checks intended behaviour before real use | Software that runs but does the wrong thing | Business employee |
| Approval for real use separate from permission to develop | "It works on my machine" becoming "it is in use" | IT Security |
| Deployment and run-location rules | Software running where it should not | Organisational rule, not enforced by the framework |
| Maintenance and retirement duties | Orphaned software running for years | Business employee |
| No secrets or highly sensitive information in prompts | Information leaving to AI services | All employees; partly enforced by the client |
| Incident process for leaks, tampering and malicious components | Slow or improvised reactions | IT Security |
| Regular testing of framework and client controls | Silent decay of controls as tools and AI models change | IT Security |
| One authoritative framework version with a required minimum | Outdated rules on individual clients | IT Security decides, IT deploys |

## 8. What the framework does and does not do

**The framework does:**

- guide the AI agent to ask before assuming and to recommend rather than
  decide on material matters;
- apply more engineering and security rigor as the assessed risk rises, while
  keeping trivial work lightweight;
- translate technical situations into plain actions for the employee:
  continue, update the project description, obtain reassessment, involve IT
  Security, hand over to IT;
- keep the project description alive: compare the implementation with the
  assessed scope, flag drift, and propose the description update before the
  capability is built in;
- separate business risks, which the employee may decide, from IT and
  security risks, which go to IT Security;
- run and record verification, and report truthfully what did and did not
  execute;
- protect its own files and detect tampering;
- prepare requests and records for IT Security;
- produce a readiness packet for each project.

**The framework does not:**

- accept any risk, approve exceptions or change the assessed scope;
- stop development, unless IT Security chooses the stricter enforcement mode;
- prevent deployment to a local machine, a data centre or a cloud; that is an
  organisational rule;
- replace IT Security's judgement or the employee's check of intended
  behaviour;
- certify that software is secure; it produces evidence, not guarantees;
- isolate the network, sandbox execution or curate packages; the client and
  platform do that.

## 9. Current stance and honest limits

**Inform, not block, for now.** Deployment and ownership rules are applied
organisationally. The framework records and reports, including for the most
sensitive projects, and development continues. IT Security can switch to
blocking enforcement per client group later without changing the framework
itself.

**Instructions to an AI are not guarantees.** An AI model follows its rules
most of the time, not always. That is why every material control has a
technical counterpart the AI cannot override, and why effectiveness is tested
rather than assumed.

**The client is the first line, the pipeline is the last.** Because employees
have no administrative rights on the managed client, local protections are
real. Still, only evidence produced by the company pipeline counts for
approval, so a local circumvention never reaches a decision unnoticed.

**Drift detection is not complete.** Automated detection of new connections,
storage or actions catches common patterns. It does not catch everything. The
assessment, the employee's honesty and IT Security's review remain necessary.

**The framework is open source.** Anyone can read its rules. Its value lies
in how it is installed, configured and enforced, not in secrecy.

## 10. What management needs to decide and provide

- **Adopt the model** and give IT Security the mandate to assess projects,
  approve real use, set enforcement, and withdraw approvals.
- **Assign the responsibilities**: who approves employees, who provides the
  managed client, who runs the Git platform and its protected pipeline, who
  provides the hardened execution environments, who curates packages and
  licences.
- **Resource IT Security** for assessments, request handling, readiness
  decisions and effectiveness testing. Automation reduces this over time for
  low-risk software, but only after it has proven reliable.
- **Resource IT** for the managed client, its network controls and its update
  pipeline.
- **Accept the residual risks** named above knowingly, and decide when to move
  from informing to blocking enforcement.
- **Ask for a few numbers regularly:** approved employees, assessed projects
  per outcome, projects in real use, open requests and their age, integrity or
  tampering alerts, findings open beyond target, framework versions in the
  field.

## 11. Glossary

- **Vibe coding.** Developing software by describing what you want to an AI
  agent and iterating on what it produces.
- **Business-led AI development.** Development by employees whose main role
  is not software development, with AI doing most of the implementation.
- **Managed client.** The virtual machine or computer, provided by IT, on
  which business-led development takes place and on which the employee has no
  administrative rights.
- **Project description and risk assessment.** The description of what a
  piece of software is for, what data it touches, what it connects to, what
  it can do and who uses it, and IT Security's judgement of the consequences.
  Made before development and kept current throughout, with the framework
  proposing updates when the software changes.
- **Business risk.** A risk within the employee's own area of responsibility,
  for example incomplete automation or a remaining manual step. The business
  employee may accept it.
- **IT or security risk.** A risk to information, systems, access or other
  parties, for example data exposure or an unsafe component. Only IT Security
  may accept it.
- **Assessed scope.** The approved characteristics from the assessment,
  handed to the framework as the reference for what the software may do.
- **Governance framework.** The Sittelle Engineering Governance package:
  rules, workflows and tooling that guide the AI agent and produce
  verification evidence.
- **Enforcement mode.** IT Security's choice whether the framework only
  informs and records (current) or pauses the agent in defined situations
  (block).
- **Drift.** The implementation gaining a capability that the assessed scope
  does not cover.
- **Readiness packet.** The bundle of evidence the framework produces for the
  decision whether software may be used for real work.
