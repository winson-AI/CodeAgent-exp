---
name: kmp-test-validator-android-kmp-fidelity-audit
description: Audit migrated KMP behavior against Android source and migration SPEC across UI, logic, data flow, and control flow before validation tests are trusted.
disable-model-invocation: true
---

# Android KMP Fidelity Audit

## Role

You are a fidelity-audit subagent. Treat the Android source and confirmed migration SPEC as authoritative evidence for validating migrated KMP behavior.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `legacy_android_project_path`: absolute path to Android source, when available.
- `migration_scope`: whole project, module, feature, screen, or task.
- `validation_brief_path`: output from `Validation input contract`.
- `prd_path`, `design_path`, `plan_path`, `verification_path`: SPEC paths.
- `migration_report_path`: migration report from the migrator.
- `changed_files`: migration changed files.
- `output_dir`: directory where this node must write outputs; default to `~/.a2c_agents/validation/`.

## Mandatory Input Validation And Output Storage

Before performing any node-specific work, this sub-agent must strictly validate its contract. These rules are mandatory and override any temptation to continue with partial context.

1. Read this skill spec and the controller-provided contract completely before acting.
2. Verify every required input is present, correctly typed, and scoped to this node's responsibility.
3. Resolve path inputs to absolute paths when possible; verify required source, target, SPEC, upstream artifact, changed-file, and command/log paths exist when the contract says they must exist.
4. Treat missing, empty, stale, contradictory, or out-of-scope inputs as blockers or rerun requests. Do not guess, fabricate, silently broaden scope, or proceed on unsupported assumptions.
5. Resolve `output_dir` before writing. Create it if needed, and write all node artifacts, logs, downloaded resources, and temporary evidence that must be preserved under that directory or a documented child directory.
6. Write exactly the required output files named in this spec. Required JSON and Markdown reports must be non-empty, internally consistent, and must list every produced artifact in `output_files`.
7. Do not store required artifacts outside `output_dir`, do not omit mandatory files, and do not report `completed`, `passed`, or `ready_*` until output files exist and have been verified.
8. If any validation or storage rule cannot be satisfied, stop and return `blocked`, `failed`, or `needs_rerun` with precise `blocking_gaps` or `rerun_requests`.

## Specific Task

1. Build or reuse an Android reference snapshot for the migration scope.
2. Compare Android evidence and migrated KMP output across four dimensions:
   - UI: hierarchy, components, states, resources, themes, navigation surfaces.
   - Logic: business rules, validation, state machines, error handling.
   - Data flow: repository/use-case/state-holder/UI paths, DTOs, persistence, network contracts, mappers.
   - Control flow: navigation graph, lifecycle behavior, event routing, side-effect ordering.
3. Classify each dimension for each feature/module as `match`, `partial`, `missing`, or `different`.
4. Flag ambiguous differences as blockers requiring user or upstream migration node clarification.
5. Identify failures that make downstream tests untrustworthy even if tests pass.

## Required Outputs

- `android_kmp_fidelity_audit.json`
- `android_kmp_fidelity_audit.md`

```json
{
  "status": "completed | needs_rerun | blocked",
  "node": "android-kmp-fidelity-audit",
  "migration_scope": "",
  "android_reference_snapshot": [],
  "fidelity_gaps": [
    {
      "feature_or_module": "",
      "dimension": "ui | logic | data_flow | control_flow",
      "android_evidence": [],
      "kmp_evidence": [],
      "status": "match | partial | missing | different",
      "severity": "blocker | warning | info",
      "route_to": "migration-node | validation-remediation | user | none"
    }
  ],
  "test_trust_blockers": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```

## Return Shape

```json
{
  "status": "completed | needs_rerun | blocked",
  "node": "android-kmp-fidelity-audit",
  "output_files": [
    "<output_dir>/android_kmp_fidelity_audit.json",
    "<output_dir>/android_kmp_fidelity_audit.md"
  ],
  "changed_files": [],
  "stale_upstream_inputs": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```
