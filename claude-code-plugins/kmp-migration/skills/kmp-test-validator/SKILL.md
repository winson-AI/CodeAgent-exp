---
name: kmp-test-validator
description: |
  6-role reduced pipeline Swarm Skill that validates Android-to-KMP migration output: workspace ledger, intake/fidelity trust gate, command/build-preview gate, Android-anchored test runner, scoped remediation, and final validation report.
  Use with the kmp-test-validator controller after android-to-kmp-migrator has produced a validation-ready migration report, or when given Android source/SPEC plus a KMP target for migrated behavior validation.
  Do NOT use for generic KMP testing, KMP-only feature work, isolated Gradle troubleshooting, Android analysis, or non-migration refactors.
version: "0.3"
kind: swarm-skill
disable-model-invocation: true
roles:
  - id: validation-workspace-state
    kind: ai_agent
    purpose: Validation ledger — node status, changed-file ownership, stale inputs, rerun/blocker history, next actions. No audit, build, test, fix, or verdict.
    skills: []
    tools: [git]
  - id: validation-intake-fidelity
    kind: ai_agent
    purpose: Intake and fidelity trust gate — verify migration scenario, normalize brief, compare Android source/SPEC vs KMP, and flag test-trust blockers.
    skills: []
    tools: [rg, git]
  - id: validation-plan-gate
    kind: ai_agent
    purpose: Command and build gate — resolve trusted build/preview/test commands, run build and preview/renderability before behavioral tests, route failures.
    skills: []
    tools: [rg, git]
  - id: validation-test-runner
    kind: ai_agent
    purpose: Test workflow — decompose validation requirements into atomic Android-anchored cases, execute them through project conventions, capture evidence.
    skills: []
    tools: [rg, git]
  - id: validation-remediation
    kind: ai_agent
    purpose: Scoped target fixes — fix confirmed target KMP failures inside allowed files and emit required reruns.
    skills: []
    tools: [rg, git]
  - id: validation-report
    kind: ai_agent
    purpose: Final verdict synthesis — passed/failed/blocked from verified fidelity, build, preview, test, and remediation evidence. No new tests or fixes.
    skills: []
    tools: [git]
---

# KMP Test Validator Swarm Skill

This is the agent-facing registry and team definition for the `kmp-test-validator` controller. It validates Android-to-KMP migration output against Android source and migration SPEC evidence.

The team is a **reduced serial pipeline with a remediation loop**. Role overlap has been collapsed from 9 role files to 6 role definitions. See [ROLE_REDUCTION.md](ROLE_REDUCTION.md) for the old-to-new map and merge rationale.

## Protocol Summary

0. **Pre-flight** — check optional dependencies from [dependencies.yaml](dependencies.yaml).
1. **Workspace state** — initialize `validation-workspace-state`.
2. **Intake/fidelity trust gate** — run `validation-intake-fidelity`; block non-migration validation and test-trust blockers.
3. **Plan/build gate** — run `validation-plan-gate`; commands must be trusted, and build/preview must pass before behavioral tests.
4. **Test workflow** — run `validation-test-runner` when validation cases exist.
5. **Remediation loop** — run `validation-remediation` only for confirmed target KMP failures, then rerun affected gates/tests.
6. **Final report** — run `validation-report` to issue `passed | failed | blocked`.

## Roles

| id | Purpose | Role file |
|---|---|---|
| `validation-workspace-state` | Ledger and stale-input tracking | [roles/validation-workspace-state.md](roles/validation-workspace-state.md) |
| `validation-intake-fidelity` | Migration scenario gate and fidelity audit | [roles/validation-intake-fidelity.md](roles/validation-intake-fidelity.md) |
| `validation-plan-gate` | Command resolution plus build/preview gate | [roles/validation-plan-gate.md](roles/validation-plan-gate.md) |
| `validation-test-runner` | Test decomposition and execution | [roles/validation-test-runner.md](roles/validation-test-runner.md) |
| `validation-remediation` | Scoped target fixes and rerun requests | [roles/validation-remediation.md](roles/validation-remediation.md) |
| `validation-report` | Final verdict synthesis | [roles/validation-report.md](roles/validation-report.md) |

## Files

| File | What it contains |
|---|---|
| [ROLE_REDUCTION.md](ROLE_REDUCTION.md) | Reduced role analysis and old-to-new map |
| [workflow.md](workflow.md) | Reduced pipeline, gates, remediation loop, final report format |
| [bind.md](bind.md) | Guardrails, failure handling, resource constraints |
| [roles/](roles/) | Active reduced role specs |
| [dependencies.yaml](dependencies.yaml) | Optional CLI tools checked at startup |

## Shared Return Contract

```json
{
  "status": "completed | passed | failed | needs_rerun | blocked",
  "node": "node-name",
  "output_files": [],
  "changed_files": [],
  "stale_upstream_inputs": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```

Use `needs_rerun` when a previous role can resolve the gap, `failed` when validation evidence is complete and a behavior/build/test failure remains, and `blocked` when required evidence, command, environment, or user input is missing.

## Shared Rules

- Each role must read its role file before work and stay inside its responsibility boundary.
- Build/test/preview commands must come from user input, project scripts/docs/CI, or verified Gradle task discovery.
- A passing KMP test that contradicts Android source/SPEC behavior is a validation failure.
- Only `validation-remediation` edits target code.
- The controller must not substitute itself for a role's audit, command gate, test run, fix, or final verdict.
