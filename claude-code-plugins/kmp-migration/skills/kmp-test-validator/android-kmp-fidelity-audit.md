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
- `output_dir`: directory where this node must write outputs; default to `~/.d2c_agents/validation/`.

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
