# Working on this project

This project is set up for a non-professional developer language. See your working
agreement (installed with your coding tool) for how decisions get made and
when to ask before building something. The rest of this file is
project-specific.

<!-- BEGIN ENGINEERING-GOVERNANCE-MANAGED -->
## This project follows the governance rules

This project is governed by `project-governance.yml`. Before doing substantial work:
1. read this file and `project-governance.yml`;
2. find the shared governance rules using the locator your tool provides;
3. if you're not sure which detailed guidance applies, ask rather than guess.

If the shared governance rules have been updated to a newer version than this project is using, say so plainly rather than assuming the project is still up to date.

## Don't quietly change the technology stack

If your work would mean swapping out a major piece of how this project is built (a different language, framework, database, or deployment approach), that's a decision for the business owner and a Professional, not something to do as a side effect of a feature. Flag it and keep working on anything that doesn't depend on it.

## Checking your work

Use this project's own checks (see `project-governance.yml`) before calling work finished. Local checks are informational; the checks that actually decide whether this project is ready run in the project's shared pipeline, where a Professional can see them. If a required check didn't run, say so -- never describe it as passed.

Do not create or edit rules, settings, or configuration files for this project. See the "You never change your own rules" section of your working agreement.
<!-- END ENGINEERING-GOVERNANCE-MANAGED -->
