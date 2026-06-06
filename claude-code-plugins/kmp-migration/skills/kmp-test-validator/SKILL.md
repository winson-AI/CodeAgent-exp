---
name: kmp-test-validator
description: |
  Swarm Skill pipeline that validates Android-to-KMP migration output: workspace ledger, fidelity gate (trust + restoreability modes), code gate (build + fix modes), optional business testing (behavioral + Figma UI submodules), and final validation report.
  Use with the kmp-test-validator controller after android-to-kmp-migrator has produced validation-ready package V0, or when given Android source/SPEC plus a KMP target for migrated behavior validation.
  Do NOT use for generic KMP testing, KMP-only feature work, isolated Gradle troubleshooting, Android analysis, or non-migration refactors.
version: "0.5"
kind: swarm-skill
disable-model-invocation: false
roles:
  - id: validation-workspace-state
    kind: ai_agent
    purpose: Validation ledger — node status, handoff gates VG0–VG5, supplement/remediation cycle counts, stale inputs, blockers. No audit, build, fix, or verdict.
    skills: []
    tools: [git]
  - id: validation-fidelity-gate
    kind: ai_agent
    purpose: Fidelity gate — mode trust (pre-build Android/SPEC vs KMP) or restoreability (post-build module/function audit, migrator supplement routing). Read-only.
    skills: []
    tools: [rg, git]
  - id: validation-code-gate
    kind: ai_agent
    purpose: Code gate — mode build (3-scenario compile/preview) or fix (edit target KMP project to resolve build/preview failures). Only fix mode edits production code.
    skills: []
    tools: [rg, git]
  - id: validation-business-testing
    kind: ai_agent
    purpose: Optional business testing — behavioral submodule (user test cases) and ui_comparison submodule (Figma) after VG3.
    skills: []
    tools: [rg, git]
  - id: validation-report
    kind: ai_agent
    purpose: Final verdict synthesis — passed/failed/blocked from verified fidelity, code-gate, business-testing, and fix evidence.
    skills: []
    tools: [git]
---

# KMP Test Validator Swarm Skill

This is the agent-facing registry and team definition for the `kmp-test-validator` controller. It validates Android-to-KMP migration output against Android source, analyst SPEC, and migrator artifacts.

The team is a **serial pipeline with two controller loops**: code-gate fix remediation and migrator supplement.

**Canonical file recording system**: [output-contract.md](output-contract.md) defines paths, migrator `V0` inputs, handoff gates `VG0`–`VG5`, and mode contracts. The Leader MUST read `output-contract.md` before the first dispatch.

## Protocol Summary

0. **Pre-flight** — [dependencies.yaml](dependencies.yaml); verify migrator `V0`; lock output root.
1. **Workspace state** — ledger + `handoff_gates`.
2. **Fidelity gate `trust`** — migration trigger + pre-build fidelity (`VG1`).
3. **Code gate `build`** — three-scenario compile + build/preview (`VG2`); on failure → code gate `fix` → rerun `build` (max 3 cycles).
4. **Fidelity gate `restoreability`** — post-build restoreability (`VG3`); migrator supplement loop (max 3) when required.
5. **Business testing** — optional behavioral / Figma submodules when user inputs exist (`VG4`).
6. **Final report** — `validation-report` (`VG5`).

## Roles

| id | Modes | Role file |
|---|---|---|
| `validation-workspace-state` | — | [roles/validation-workspace-state.md](roles/validation-workspace-state.md) |
| `validation-fidelity-gate` | `trust \| restoreability` | [roles/validation-fidelity-gate.md](roles/validation-fidelity-gate.md) |
| `validation-code-gate` | `build \| fix` | [roles/validation-code-gate.md](roles/validation-code-gate.md) |
| `validation-business-testing` | `behavioral \| ui_comparison` submodules | [roles/validation-business-testing.md](roles/validation-business-testing.md) |
| `validation-report` | — | [roles/validation-report.md](roles/validation-report.md) |

## Files

| File | What it contains |
|---|---|
| [output-contract.md](output-contract.md) | Canonical paths, V0 upstream, VG0–VG5 gates |
| [workflow.md](workflow.md) | Pipeline, gates, controller loops |
| [bind.md](bind.md) | Guardrails and resource limits |
| [dependencies.yaml](dependencies.yaml) | Upstream V0, optional inputs, MCP, tools |
| [roles/](roles/) | Role specs |

## Strict Output Schedule

```text
output_root = <output_dir or ~/.a2c_agents/validation>/kmp-test-validator
fidelity_gate_dir = <output_root>/fidelity-gate
code_gate_dir = <output_root>/code-gate
business_testing_dir = <output_root>/business-testing
```

See [output-contract.md](output-contract.md) for full layout. No validator artifact inside migration output root.

## Output Artifact Content Matrix

| Owner | Artifacts | Required content |
|---|---|---|
| Leader | `run_manifest.json`, `upstream_migration_index.json` | V0 verification, dependency preflight |
| `validation-workspace-state` | `validation_workspace_state.*` | `handoff_gates` VG0–VG5, cycle counts |
| `validation-fidelity-gate` | `trust/validation_fidelity_trust.*`, `restoreability/validation_restoreability_audit.*` | Pre-build trust or post-build restoreability per mode |
| `validation-code-gate` | `build/validation_code_build.*`, `fix/<cycle>/validation_code_fix.*`, code-gate logs | Compile scenario + build/preview (build mode) or target KMP edits + `changed_files` + reruns (fix mode) |
| `validation-business-testing` | `validation_business_testing.*`, logs | Submodule outcomes or explicit skip |
| `validation-report` | `kmp_validation_report.*` | Evidence-backed final verdict |

## Shared Return Contract

```json
{
  "status": "completed | passed | failed | needs_rerun | needs_migrator_supplement | blocked",
  "node": "node-name",
  "mode": "trust | restoreability | build | fix",
  "output_dir": "<node output dir>",
  "output_files": [],
  "changed_files": [],
  "stale_upstream_inputs": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```

## Shared Rules

- Dispatch only role IDs listed in this registry.
- Only `validation-code-gate` mode `fix` edits target production code.
- Fidelity-gate modes are read-only; restoreability routes gaps to migrator supplement.
- Code-gate `build` uses three compile scenarios only; `fix` uses error DB when configured.
- Business-testing submodules require user inputs; skipped is not pass-by-omission.
