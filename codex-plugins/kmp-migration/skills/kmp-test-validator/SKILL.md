---
name: kmp-test-validator
description: |
  9-role pipeline Swarm Skill (C) with a remediation loop that validates Android-to-KMP migration output: input gate, fidelity audit, validation plan, build/preview gate, test decomposition and execution, remediation, and report.
  Use with the kmp-test-validator controller after a migration report is ready, or when given Android source/SPEC plus a KMP target.
  Do NOT use for generic KMP testing, KMP-only feature work, isolated Gradle troubleshooting, Android analysis, or non-migration refactors.
version: "0.2"
kind: swarm-skill
disable-model-invocation: false
roles:
  - id: validation-workspace-state
    kind: ai_agent
    purpose: Validation ledger — node status, changed-file ownership, stale inputs, rerun/blocker history, next actions. No audit, build, or fix.
    skills: []
    tools: [git]
  - id: validation-input-contract
    kind: ai_agent
    purpose: Gate — verify this is a post-migration validation scenario, confirm KMP evidence, normalize paths, and produce the validation brief.
    skills: []
    tools: [rg]
  - id: android-kmp-fidelity-audit
    kind: ai_agent
    purpose: Compare Android source/SPEC vs migrated KMP across UI, logic, data flow, control flow before tests are trusted; flag test-trust blockers.
    skills: []
    tools: [rg, git]
  - id: kmp-validation-plan
    kind: ai_agent
    purpose: Discover target structure and resolve trusted build/preview/test commands and scope-to-target mapping. Never invents commands.
    skills: []
    tools: [rg]
  - id: build-preview-gate
    kind: ai_agent
    purpose: Run the resolved build and Compose preview/renderability gate before behavioral tests; classify and route failures by owner.
    skills: []
    tools: [rg]
  - id: test-case-decomposition
    kind: ai_agent
    purpose: Decompose user tests, SPEC acceptance, and migration validation inputs into atomic Android-anchored cases. No fabricated expectations.
    skills: []
    tools: [rg]
  - id: test-execution
    kind: ai_agent
    purpose: Execute atomic cases via project conventions and capture evidence; a KMP pass that contradicts Android evidence is a failure.
    skills: []
    tools: [rg, git]
  - id: validation-remediation
    kind: ai_agent
    purpose: Fix confirmed target failures inside allowed files, anchored to Android/SPEC; emit required reruns of build/preview and tests.
    skills: []
    tools: [rg, git]
  - id: validation-report
    kind: ai_agent
    purpose: Synthesize fidelity/build/preview/test/remediation into the final passed/failed/blocked verdict. No new tests or fixes.
    skills: []
    tools: [git]
---

# KMP Test Validator Swarm Skill

This is the agent-facing registry and team definition for the `kmp-test-validator` controller (the same-name subagent in `kmp-migration/agents/`). It validates Android-to-KMP migration output against Android source and the migration SPEC, and is invoked only after an `android-to-kmp-migrator` migration report is `ready_for_validation` (or when the user supplies Android source/SPEC plus a KMP target).

The team is a **specialization pipeline (C) with a remediation loop**: an input-contract gate, then a fidelity audit before tests are trusted, then a validation plan, a build/preview gate before behavioral tests, test decomposition and execution, a remediation loop back to the gate/tests, and a final report. A single agent attempting validation conflates these stages — it trusts green tests without auditing fidelity, runs behavioral tests before the build compiles, invents build commands, and lets a KMP pass that contradicts Android behavior count as success. Isolating each concern into an owned node with hard gates keeps Android source/SPEC as ground truth and every verdict evidence-backed. The controller (Leader) owns scenario gating, routing, rerun handling, and the final verdict; nodes own bounded validation work.

## Workflow

The full playbook (Mermaid topology, per-step gates, remediation loop, Final Report format) is in [workflow.md](workflow.md). Protocol summary:

0. **Pre-flight: check dependencies** — read [dependencies.yaml](dependencies.yaml) and verify `rg` / `git` (both `required: false`; the target Gradle wrapper drives build/test). Report status; **user decides** whether to proceed.
1. **Workspace state** — `validation-workspace-state` initializes the ledger (refreshed after each node group). Default `output_dir` = `~/.a2c_agents/validation/`.
2. **Input contract gate** — `validation-input-contract` verifies the migration scenario and KMP evidence; missing migration evidence → `blocked` (never downgrade to generic testing).
3. **Fidelity audit** — `android-kmp-fidelity-audit` compares Android source/SPEC vs KMP across UI/logic/data-flow/control-flow before tests are trusted.
4. **Validation plan** — `kmp-validation-plan` resolves trusted build/preview/test commands (user → project scripts/CI → verified Gradle tasks); else `blocked`.
5. **Build/preview gate** — `build-preview-gate` runs the resolved build and (UI in scope) preview/renderability; behavioral tests do NOT run on failure.
6. **Test decomposition** — `test-case-decomposition` produces atomic, Android-anchored cases.
7. **Test execution** — `test-execution` runs cases via project conventions; a KMP pass that contradicts Android evidence is a failure.
8. **Remediation loop** — `validation-remediation` fixes confirmed target failures within `allowed_files` and re-runs the affected gate/tests until pass or `blocked` (see [bind.md](bind.md)).
9. **Final: validation report** — `validation-report` synthesizes the `passed | failed | blocked` verdict. Leader routes non-target failures out; it never fabricates a pass.

## Roles

Each node is dispatched as a subagent that must read its role file (`skill_spec_path`), paste its `## Inline Persona for Teammate` into the dispatch prompt, and execute only that role's bounded slice. The dispatch order enforces fidelity-before-tests and build-before-tests gating.

| id | Purpose | When dispatched | Key dependencies | Role file |
|---|---|---|---|---|
| validation-workspace-state | Ledger / stale-input tracking | Step 1 + refreshed after each group | git | [roles/validation-workspace-state.md](roles/validation-workspace-state.md) |
| validation-input-contract | Migration-scenario gate + brief | Step 2 | rg | [roles/validation-input-contract.md](roles/validation-input-contract.md) |
| android-kmp-fidelity-audit | Android-vs-KMP fidelity audit | Step 3 (before tests trusted) | rg, git | [roles/android-kmp-fidelity-audit.md](roles/android-kmp-fidelity-audit.md) |
| kmp-validation-plan | Trusted command + scope resolution | Step 4 | rg | [roles/kmp-validation-plan.md](roles/kmp-validation-plan.md) |
| build-preview-gate | Compile + render gate | Step 5 (before behavioral tests) | rg | [roles/build-preview-gate.md](roles/build-preview-gate.md) |
| test-case-decomposition | Atomic Android-anchored cases | Step 6 | rg | [roles/test-case-decomposition.md](roles/test-case-decomposition.md) |
| test-execution | Run cases + capture evidence | Step 7 (after build gate) | rg, git | [roles/test-execution.md](roles/test-execution.md) |
| validation-remediation | Scoped target fixes + reruns | Step 8 loop (on failures) | rg, git | [roles/validation-remediation.md](roles/validation-remediation.md) |
| validation-report | Final verdict synthesis | Step 9 | git | [roles/validation-report.md](roles/validation-report.md) |

> Before dispatching each teammate, read its role file and paste its `## Inline Persona for Teammate`
> section directly into the dispatch prompt — adopting agents do NOT auto-load role files. Fill the
> `{PLACEHOLDER}` inputs from the contract.

## Files

| File | What it contains | When to read |
|---|---|---|
| [workflow.md](workflow.md) | Mermaid C topology, staged protocol with gates, remediation loop, Final Report format | Before first dispatch — the complete playbook |
| [bind.md](bind.md) | Resource limits, team behavioral constraints, trigger boundary, `max_remediation_cycles`, failure & degraded modes | When hitting limits, handling failures, or scoping a large validation |
| [roles/\*.md](roles/) | Per-node identity, success criteria, boundary, output schema, Inline Persona for Teammate | Before dispatching each teammate — extract Inline Persona |
| [dependencies.yaml](dependencies.yaml) | External CLI tools (`rg`, `git`) checked at startup | Step 0 — verify deps, report missing items, user decides go/no-go |

## Shared Return Contract

Every node returns a compact payload with, in addition to node-specific fields:

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

Use `needs_rerun` when a previous node can resolve the gap, `failed` when validation evidence is complete and a behavior/build/test failure remains, and `blocked` only when required Android/KMP/SPEC evidence, environment capability, or user input is missing and cannot be produced by rerunning another node.

## Optional Android Studio MCP Context

When the `jetbrains` MCP server is available, the controller may pass indexed IDE context to nodes: project modules/dependencies/VCS roots/run configs (`get_project_modules`, `get_project_dependencies`, `get_repositories`, `get_run_configurations`), file/symbol ownership (`find_files_by_glob`, `search_in_files_by_regex`, `get_symbol_info`), diagnostics (`get_file_problems`), and IDE build diagnostics (`build_project`). Always pass `projectPath: <kmp_target_project_path>`. MCP is advisory — required build/preview/test commands and the final validation report remain the source of truth.

## Shared Rules

- Each node must read its own role file before work and stay inside its responsibility boundary.
- Build and test commands must come from user input, project scripts, target understanding, or verified Gradle task discovery — never invented.
- A passing test (or build) that contradicts Android source/SPEC behavior is a validation failure.
- Nodes that edit code must list changed files and the evidence that justified each change; only `validation-remediation` edits target code.
- The controller must not substitute itself for a node's audit, fix, or test execution.
- Final success requires: migration trigger verified, fidelity audit complete, build/preview gate passed or explicitly blocked with evidence, tests executed when provided, fixes revalidated, and `validation-report` complete.
