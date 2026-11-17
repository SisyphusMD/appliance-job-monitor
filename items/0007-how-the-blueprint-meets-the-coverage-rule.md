# #7 How the blueprint meets the coverage rule

- Kind: issue, state: closed, by cody, created 2026-11-17T11:12:31-08:00
- Labels: status:ready, type:decision; milestone: none

Rule 13 asks for 99% coverage (100% on safety-critical code). The Tests workflow runs both Home Assistant suites, but nothing measures coverage of the blueprint's YAML and templates, and naming a failing test per PR is not a coverage measure.

Options: define and gate a blueprint-appropriate measure (for example, every trigger, condition branch and state transition exercised by a named test, checked by a script), or record an exception in the project-rules Exceptions table. Found by review during adoption (#5).

## cody, 2026-11-17T11:40:42-08:00

Decision: Gate blueprint coverage with a script in CI: every trigger, condition branch and state transition in the blueprint must be exercised by a named test, or CI fails. Why: Real enforcement that matches the coverage rule, rather than loosening it with an exception.

Decided by: Cody, 2026-11-17.
