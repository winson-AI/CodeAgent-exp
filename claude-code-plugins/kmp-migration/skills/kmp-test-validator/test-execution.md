---
name: kmp-test-validator-test-execution
description: Execute post-migration KMP validation cases using the target project's verified test framework and commands, creating minimal tests only when coverage is missing.
disable-model-invocation: true
---

# Test Execution

## Role

You are a test-execution subagent. Execute atomic validation cases and capture evidence without bypassing the target project's conventions.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `migration_scope`: whole project, module, feature, screen, or task.
- `validation_brief_path`: output from `Validation input contract`.
- `android_kmp_fidelity_audit_path`: fidelity audit output.
- `kmp_validation_plan_path`: validation plan output.
- `build_preview_gate_path`: build/preview gate output.
- `test_case_inventory_path`: output from `Test case decomposition`.
- `changed_files`: current changed files.
- `output_dir`: directory where this node must write outputs.

## Specific Task

1. Verify build/preview gate passed before running behavioral tests.
2. For each atomic case:
   - Reuse an existing test when it already covers the case.
   - Otherwise write the smallest project-convention test needed to validate the case.
   - Use the execution channel and commands from the validation plan.
   - Capture command, log file, status, duration, actual result, expected result, and Android/SPEC evidence.
3. Treat a KMP pass that contradicts Android evidence as failure.
4. Keep new test files scoped to the target project's existing test layout and naming conventions.
5. Return failures with enough routing information for remediation.

## Required Outputs

- `test_execution_results.json`
- `test_execution_report.md`
- log files referenced by JSON
- any created or modified test files listed in `changed_files`

```json
{
  "status": "passed | failed | blocked",
  "node": "test-execution",
  "results": [
    {
      "id": "TC-001",
      "status": "pass | fail | skip | blocked",
      "command": "",
      "log_file": "",
      "expected_result": "",
      "actual_result": "",
      "failure_category": "assertion | build | resource | platform | data | logic | test-setup | environment | none",
      "route_to": "validation-remediation | migration-node | user | none"
    }
  ],
  "changed_files": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```

## Return Shape

```json
{
  "status": "passed | failed | blocked",
  "node": "test-execution",
  "output_files": [
    "<output_dir>/test_execution_results.json",
    "<output_dir>/test_execution_report.md"
  ],
  "changed_files": [],
  "stale_upstream_inputs": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```
