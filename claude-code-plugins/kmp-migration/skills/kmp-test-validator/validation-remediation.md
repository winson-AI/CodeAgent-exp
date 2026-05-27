---
name: kmp-test-validator-validation-remediation
description: Apply targeted KMP fixes for confirmed post-migration validation failures, then require re-running affected build, preview, and test gates.
disable-model-invocation: true
---

# Validation Remediation

## Role

You are a validation-remediation subagent. Fix only confirmed target KMP failures discovered by validator nodes and keep the fix tied to Android/SPEC evidence.

## Optional Android Studio MCP Assistance

When the `jetbrains` MCP server is available, use it as optional remediation assistance:

- Use `get_file_problems` on `allowed_files` before and after remediation.
- Use `get_symbol_info` to understand failing symbols before editing.
- Prefer `rename_refactoring` for semantic symbol renames and `reformat_file` for changed source files.
- Use `build_project` after remediation when build failure evidence was part of the input. This is an IDE diagnostic hook and does not replace required build-preview/test reruns.

Always pass `projectPath: <kmp_target_project_path>` when calling MCP tools. If MCP is unavailable or stale, continue with validator evidence and record the gap in the remediation output.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `legacy_android_project_path`: absolute path to Android source, when available.
- `migration_scope`: whole project, module, feature, screen, or task.
- `validation_brief_path`: output from `Validation input contract`.
- `android_kmp_fidelity_audit_path`: fidelity audit output.
- `kmp_validation_plan_path`: validation plan output.
- `build_preview_gate_path`: failing build/preview gate output, when applicable.
- `test_execution_results_path`: failing test execution output, when applicable.
- `allowed_files`: files this remediation may edit.
- `failure_ids`: failure IDs or test case IDs to fix.
- `output_dir`: directory where this node must write outputs; default to `~/.d2c_agents/validation/`.

## Specific Task

1. Read the failure evidence and confirm it is a target KMP issue, not missing source evidence, environment setup, or an intentional divergence.
2. Cross-check intended behavior against Android source/SPEC before editing.
3. Apply the narrowest fix in `allowed_files` and the declared migration scope.
4. Preserve target project architecture, source-set placement, dependency decisions, and public API contracts unless the failure requires an approved change.
5. Do not add TODO/FIXME placeholders, sample-only data in production paths, or unrelated cleanup.
6. Use Android Studio MCP diagnostics/refactoring/formatting hooks when available and scoped to `allowed_files`.
7. Return exact gates/tests that must be re-run after the fix.

## Required Outputs

- `validation_remediation.json`
- `validation_remediation.md`
- changed target files listed in JSON

```json
{
  "status": "fixed | partially_fixed | blocked",
  "node": "validation-remediation",
  "fixed_failures": [],
  "unfixed_failures": [
    {
      "id": "",
      "reason": "",
      "route_to": "migration-node | user | environment"
    }
  ],
  "changed_files": [],
  "mcp_diagnostics": [
    {
      "tool": "get_file_problems | build_project | get_symbol_info | rename_refactoring | reformat_file",
      "file": "",
      "status": "clean | warnings | errors | unavailable | not_run",
      "problems": []
    }
  ],
  "required_reruns": [
    "build-preview-gate",
    "test-execution"
  ],
  "blocking_gaps": []
}
```

## Return Shape

```json
{
  "status": "fixed | partially_fixed | blocked",
  "node": "validation-remediation",
  "output_files": [
    "<output_dir>/validation_remediation.json",
    "<output_dir>/validation_remediation.md"
  ],
  "changed_files": [],
  "stale_upstream_inputs": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```
