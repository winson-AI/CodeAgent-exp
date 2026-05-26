---
name: kmp-test-validator
description: Controller support skill registry for post-migration KMP validation. Use only with the kmp-test-validator controller after an Android-to-KMP migration report is ready for validation; it defines node skill specs for validation input checks, Android/KMP fidelity audit, KMP validation planning, build/preview gates, test decomposition, test execution, remediation, and final validation reporting.
disable-model-invocation: true
---

# KMP Test Validator Node Skill Registry

This directory stores node skill specs used by the `kmp-test-validator` controller. The controller owns migration-scenario gating, routing, output validation, re-dispatch, and final readiness decisions. Node subagents own bounded validation work.

## Default Output Directory

Unless the user or controller provides an explicit `output_dir`, write validation and node artifacts under `~/.d2c_agents/validation/`.

## Methodology Boundary

When learning from another workflow, use methodology only: controller/subagent separation, explicit input and output contracts, small node responsibilities, gated verification, serial execution where artifacts depend on previous artifacts, and final synthesis after verified node completion. Do not copy project-specific commands, framework assumptions, private examples, or reference workflow content.

## Trigger Boundary

Use this skill only for validation of Android-to-KMP migration output. Valid entry points include:

- The `android-to-kmp-migrator` controller invokes validation after `migration-report` returns `ready_for_validation`.
- The user explicitly provides Android source or Android SPEC artifacts, a KMP target project, and asks to validate migrated KMP behavior against the Android migration scope.

Do not use it for generic KMP project testing, KMP-only feature development, non-migration refactors, isolated Gradle troubleshooting, or Android project analysis without migrated KMP output.

## Node Skills

| Node | Skill spec | Responsibility |
|---|---|---|
| `Validation workspace state` | [validation-workspace-state.md](validation-workspace-state.md) | Maintain validation node status, output files, changed-file ownership, rerun history, blockers, and stale upstream inputs. |
| `Validation input contract` | [validation-input-contract.md](validation-input-contract.md) | Verify that the request is a migration validation scenario and normalize required paths, SPEC, report, changed files, commands, and acceptance inputs. |
| `Android KMP fidelity audit` | [android-kmp-fidelity-audit.md](android-kmp-fidelity-audit.md) | Compare Android source/SPEC against migrated KMP across UI, logic, data flow, and control flow before tests are trusted. |
| `KMP validation plan` | [kmp-validation-plan.md](kmp-validation-plan.md) | Understand target KMP structure, discover trusted build/test entry points, map validation scope to source sets/modules, and produce an execution plan. |
| `Build preview gate` | [build-preview-gate.md](build-preview-gate.md) | Establish compile/build and Compose preview or renderability readiness before behavioral tests run. |
| `Test case decomposition` | [test-case-decomposition.md](test-case-decomposition.md) | Decompose user tests, SPEC acceptance criteria, and migration report validation inputs into atomic runnable cases. |
| `Test execution` | [test-execution.md](test-execution.md) | Execute or create minimal project-convention tests for atomic cases and capture pass/fail/skip evidence. |
| `Validation remediation` | [validation-remediation.md](validation-remediation.md) | Apply targeted fixes for confirmed validation failures, then route back to build/test gates. |
| `Validation report` | [validation-report.md](validation-report.md) | Synthesize fidelity, build, preview, tests, fixes, blockers, and final validation status. |

## Required Dispatch Order

1. Initialize `Validation workspace state`.
2. Run `Validation input contract`; stop if the migration trigger is not satisfied.
3. Run `Android KMP fidelity audit`.
4. Run `KMP validation plan`.
5. Run `Build preview gate`; do not run behavioral tests until compile/build and required preview/renderability gates pass or are explicitly blocked.
6. Run `Test case decomposition` when test cases, use cases, or acceptance criteria are available.
7. Run `Test execution` for each atomic case.
8. Run `Validation remediation` for confirmed failures that can be fixed within the KMP target scope, then re-run affected gates and tests.
9. Refresh `Validation workspace state` after every node group and before final reporting.
10. Run `Validation report`.

## Optional Android Studio MCP Context

When the `jetbrains` MCP server is available, the controller may pass indexed IDE context to validation nodes:

- project modules, dependencies, VCS roots, and run configurations from `get_project_modules`, `get_project_dependencies`, `get_repositories`, and `get_run_configurations`.
- file and symbol ownership from `find_files_by_glob`, `search_in_files_by_regex`, and `get_symbol_info`.
- diagnostics from `get_file_problems` for changed or failing files.
- IDE build diagnostics from `build_project` after remediation or before rerunning build gates.

This MCP context is advisory. Required build/preview/test commands and final validation reports remain the source of truth.

## Shared Return Contract

Every node must return a compact JSON-compatible payload with:

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

Use `needs_rerun` when a previous node can resolve the gap. Use `failed` when validation evidence is complete and a behavior/build/test failure remains. Use `blocked` only when required Android/KMP/SPEC evidence, environment capability, or user input is missing and cannot be produced by rerunning another node.

## Controller Validation Rules

- The controller may dispatch nodes, validate return payloads and output files, update workspace state, and route reruns.
- The controller must not replace a node by directly performing its detailed audit, implementation fix, or test execution.
- Nodes that edit code must list changed files and the evidence that justified each change.
- Build and test commands must come from user input, project scripts, target understanding, or verified Gradle task discovery. Do not invent commands.
- A passing test that contradicts Android source/SPEC behavior is a validation failure.
- Final success requires: migration trigger verified, fidelity audit complete, build/preview gate passed or explicitly blocked with evidence, tests executed when provided, fixes revalidated, and `validation-report` complete.
