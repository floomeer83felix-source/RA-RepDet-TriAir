# Task Blocker

Status: `V73_MANUSCRIPT_INTEGRATION_AUTHORIZED_NO_ACTIVE_EXPERIMENT_BLOCKER`

Generated: 2026-07-26

## Current state

V72 completed successfully at commit `121d444e4885445e42f0755f7413c579e4ccf66e` with six complete finite metric records and no reruns.

There is no remaining experimental blocker. The required external-domain stress-test data now exist and are frozen.

## Active task

`V73_TRIAIR_MANUSCRIPT_MMUAV_EXTERNAL_STRESS_TEST_INTEGRATION_AUTHORIZED`

V73 must integrate the V72 result into the research manuscript immediately. It is not authorized to launch another experiment or adapter search.

## Required result boundary

The exact scientific label is:

`zero-shot external-domain stress test on the exposed MM-UAV devval split using a naive normalized-grid five-channel adapter`

The central result is negative:

- Early Fusion mean AP@[.50:.95]: `9.48024496878457e-9`;
- RA-RepDet mean AP@[.50:.95]: `7.208000851646425e-7`;
- paired mean difference: `7.11319840195858e-7`;
- all six AP values are zero or effectively zero;
- the modalities were independently normalized to one grid without physical cross-modal registration.

This may be reported as evidence that direct channel-level transfer fails under severe unregistered cross-sensor domain shift. It may not be reported as successful, independent, blind, official, or physically registered external validation.

## Authorized work

V73 may:

- edit the active research manuscript and its internal appendix/supplement sources;
- add the exact six-checkpoint table and aggregate statistics;
- add protocol, limitation, and interpretation text;
- add one main discussion/limitations pointer to the appendix;
- use an existing MM-UAV bibliography entry;
- retain one explicit internal citation placeholder when no established entry exists;
- run clean LaTeX/BibTeX builds and inspect rendered pages;
- add compact traceability, claim-audit, build, and handoff records.

## V73 may not

- run training, inference, evaluation, tuning, calibration, adaptation, or new adapter variants;
- change or recompute V72 metrics;
- omit zero-valued seeds or emphasize relative ratios over near-zero absolute values;
- insert V72 into the abstract, headline contributions, primary TriAir result table, or conclusion as a positive generalization claim;
- call the split independent, blind, official test, or physically registered;
- modify frozen TriAir in-domain metrics or model definitions;
- place raw data, predictions, checkpoints, local paths, credentials, or heavy/private artifacts in Git.

## Fail-closed conditions

Finish with the matching V73 blocked state only when:

1. the manuscript source or clean build procedure cannot be resolved;
2. inserted numbers cannot be traced exactly to the V72 evidence;
3. prohibited external-validation wording remains after claim audit;
4. the new table or text cannot be rendered legibly;
5. protected files drift outside the authorized manuscript/task scope;
6. private or heavy artifacts enter Git.

A missing established bibliography entry may be retained as one explicit internal draft placeholder and does not block the scientific result integration.

## Next action

Execute `docs/NEXT_TASK.md` now. Add the V72 table, protocol, negative-result interpretation, and limitations to the manuscript; compile, inspect, audit claims, and push the completed V73 integration.