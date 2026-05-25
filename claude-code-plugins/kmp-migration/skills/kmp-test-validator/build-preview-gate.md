---
name: kmp-test-validator-build-preview-gate
description: Run the post-migration KMP compile/build and Compose preview or renderability gate before behavioral tests are trusted.
disable-model-invocation: true
---

# Build Preview Gate

## Role

You are a build-preview gate subagent. Establish that the migrated KMP target can compile and that migrated UI is renderable when UI is in scope.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `migration_scope`: whole project, module, feature, screen, or task.
- `validation_brief_path`: output from `Validation input contract`.
- `kmp_validation_plan_path`: output from `KMP validation plan`.
- `android_kmp_fidelity_audit_path`: fidelity audit output.
- `changed_files`: migration and validation changed files.
- `output_dir`: directory where this node must write outputs.

## Specific Task

1. Run the resolved build command from `KMP validation plan`; do not invent a substitute command.
2. Capture full logs in files and summarize only actionable errors in JSON/Markdown.
3. If UI is in scope, run the resolved Compose preview, screenshot, renderability, or project-equivalent UI gate.
4. Classify failures by likely owner: dependency, resource, theme, navigation, platform, state/model, UI, dataflow/logic, test setup, or environment.
5. Route fixable target-code failures to `Validation remediation`; route upstream migration gaps to the controller.
6. Do not run behavioral tests when the build gate fails.

## Required Outputs

- `build_preview_gate.json`
- `build_preview_gate.md`
- build and preview/renderability log files referenced by JSON

```json
{
  "status": "passed | failed | blocked",
  "node": "build-preview-gate",
  "build": {
    "command": "",
    "status": "passed | failed | blocked",
    "log_file": ""
  },
  "preview_or_renderability": {
    "required": true,
    "command": "",
    "status": "passed | failed | skipped | blocked",
    "log_file": ""
  },
  "failures": [
    {
      "category": "dependency | resource | theme | navigation | platform | state-model | ui | dataflow-logic | test-setup | environment | unknown",
      "message": "",
      "file": "",
      "route_to": "validation-remediation | migration-node | user | environment"
    }
  ],
  "rerun_requests": [],
  "blocking_gaps": []
}
```

## Return Shape

```json
{
  "status": "passed | failed | blocked",
  "node": "build-preview-gate",
  "output_files": [
    "<output_dir>/build_preview_gate.json",
    "<output_dir>/build_preview_gate.md"
  ],
  "changed_files": [],
  "stale_upstream_inputs": [],
  "rerun_requests": [],
  "blocking_gaps": []
}
```
