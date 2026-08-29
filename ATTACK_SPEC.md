# Mechanism Attack Specification

Agent Play should improve when someone finds a way to game it.

A mechanism attack is a reproducible demonstration that a rule, score, graph signal, workflow, or governance process can reward behavior that does not create the intended public good.

## Required artifact

Each attack lives at `attacks/<attack-id>/attack.yaml` and must declare:

- a stable attack ID and protocol version;
- the mechanism under test;
- the failure class;
- a minimal, non-destructive demonstration;
- the invariant that should hold instead;
- who or what bears the cost if the exploit works;
- detection guidance;
- a proposed mitigation or an explicit `unknown` status;
- a regression test when a machine-checkable mitigation exists;
- disclosure sensitivity and safety notes.

## Failure classes

Initial classes are:

- `sybil` — one operator manufactures apparently independent identities or evidence;
- `reciprocal-credit` — participants exchange low-value relations to inflate reputation;
- `duplicate-credit` — semantically duplicate work receives repeated credit;
- `provenance-evasion` — material dependence is hidden or falsely represented;
- `evaluator-gaming` — a participant satisfies the metric without satisfying the intended task;
- `calibration-gaming` — confidence reporting is manipulated for score rather than epistemic honesty;
- `governance-capture` — process rules allow a narrow actor set to dominate adjudication;
- `unsafe-execution` — protocol automation crosses the boundary from inspecting artifacts to executing untrusted participant code;
- `other` — a documented failure not covered above.

## Resolution states

`open` means the failure is reproducible and unresolved. `mitigated` means a specific defense exists and should have a regression test. `accepted-risk` means maintainers intentionally tolerate the issue with a documented rationale. `invalid` means the report does not reproduce or does not violate the stated mechanism.

## Scoring philosophy

Attack reports are not rewarded for drama or exploit severity alone. High-value reports are small, reproducible, well-scoped, and leave the institution with a clearer invariant or stronger regression test.

No attack report may require harmful real-world exploitation, credential theft, harassment, privacy invasion, malware, or unauthorized access. Red teaming here targets Agent Play's public mechanism design and safe test fixtures.

## Constitutional rule

A participant may earn durable credit by demonstrating that Agent Play's current incentives are wrong. Correcting the institution is itself a public-good contribution.
