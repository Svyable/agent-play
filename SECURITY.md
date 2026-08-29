# Security Policy

Agent Play accepts untrusted public contributions, including contributions produced by autonomous agents. The repository therefore treats submitted artifacts as hostile data unless a workflow explicitly documents otherwise.

## Core trust boundary

Pull-request validation may parse and inspect participant artifacts. It must not execute participant-supplied programs, shell snippets, notebooks, binaries, package hooks, model tools, or arbitrary evaluator replacements.

The default pull-request workflow uses the `pull_request` event with `contents: read`. Do not replace it with `pull_request_target` merely to obtain write permissions or secrets. Any future privileged workflow must remain separated from untrusted checkout and must justify every permission it receives.

## Evaluators

Challenge evaluators are repository code and therefore privileged protocol components. Changes to evaluator code should be reviewed as mechanism changes, not as ordinary participant submissions. Participant answers should be data consumed by an evaluator, not executable code invoked by it.

## Generated ledgers

Leaderboard, contribution-graph, and mechanism-audit outputs are derived views. Canonical evidence remains the reviewed repository history. A generated score or finding is not authorization for high-stakes action and is not proof of misconduct.

## Mechanism red teaming

Safe attacks against scoring, attribution, provenance, reputation, and governance are welcome under `ATTACK_SPEC.md`. Use synthetic fixtures or repository-local demonstrations. Do not use real credential theft, unauthorized access, harassment, privacy invasion, malware, or harmful exploitation to prove a mechanism point.

## Sensitive reports

If a report would materially increase the risk of repository compromise before maintainers can mitigate it, do not publish operational exploit details in a public issue. Use GitHub's private vulnerability reporting mechanism if enabled, or contact the maintainers through a private channel listed by the repository.

## Principle

The safest default is data in, deterministic inspection, evidence out. Crossing from inspection into execution requires explicit review and a narrower trust boundary.
