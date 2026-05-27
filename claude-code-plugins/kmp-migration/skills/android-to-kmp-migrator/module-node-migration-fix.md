---
name: android-to-kmp-migrator-module-node-migration-fix
description: Apply focused fixes for one reviewed module or node migration slice. Use only after module-node-migration-review returns needs_fix with actionable findings and target files.
disable-model-invocation: true
---

# Module Node Migration Fix

## Role

You are a module/node migration fix subagent. Apply narrowly scoped fixes from a review report. Preserve the owning node's skill contract and the target KMP project's conventions. Do not perform unrelated cleanup or broad redesign.

## Optional Android Studio MCP Assistance

When the `jetbrains` MCP server is available, use it as optional bug-fix assistance:

- Use `get_file_problems` on `allowed_files` before and after the fix to confirm the local diagnostic delta.
- Use `get_symbol_info` to understand failing symbols before editing.
- Prefer `rename_refactoring` for semantic symbol renames and `reformat_file` for changed Kotlin/Compose files.
- Use `build_project` after fixing a build-related issue when the controller asks for an IDE diagnostic hook. This supplements, but does not replace, the required re-review and build/check gates.

Always pass `projectPath: <kmp_target_project_path>` when calling MCP tools. If MCP is unavailable or stale, continue with review evidence and record the gap in the fix output.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `legacy_android_project_path`: absolute path to Legacy Android source, when available.
- `migration_scope`: whole project, module, feature, screen, or task.
- `module_or_node_scope`: exact module, screen, feature, resource group, route, state holder, API group, or node output being fixed.
- `owning_node`: node that originally produced the reviewed output.
- `owning_node_skill_path`: skill spec for the owning node.
- `owning_node_output_path`: output from the owning node.
- `review_report_path`: `module_node_migration_review.json` or equivalent report with findings.
- `allowed_files`: file paths this fix node may edit.
- `upstream_evidence_paths`: relevant SPEC and upstream node outputs.
- `migration_workspace_state_path`: current workspace state ledger.
- `output_dir`: directory where this node must write outputs; default to `~/.d2c_agents/migration/`.

## Specific Task

1. Read the review report and fix only `must_fix` findings assigned to `module-node-migration-fix`.
2. Keep changes inside `allowed_files` and the declared `module_or_node_scope`.
3. Preserve target project conventions, source-set placement, dependency decisions, and single-project invariant.
4. Do not add dependencies, root Gradle files, settings files, wrappers, placeholder TODOs, or unrelated refactors.
5. Use Android Studio MCP diagnostics/refactoring/formatting hooks when available and scoped to `allowed_files`.
6. If a finding cannot be fixed within scope, return it as a blocker with the exact upstream node or user input needed.
7. Produce a fix summary and the changed-file list for re-review.

## Required Outputs

- `module_node_migration_fix.json`
- `module_node_migration_fix.md`
- changed target files listed in JSON

```json
{
  "status": "fixed | partially_fixed | blocked",
  "node": "module-node-migration-fix",
  "module_or_node_scope": "",
  "owning_node": "",
  "fixed_findings": [],
  "unfixed_findings": [
    {
      "finding_id": "",
      "reason": "",
      "route_to": "owning_node | verification_node | controller | user"
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
  "requires_re_review": true,
  "blocking_gaps": []
}
```

## Shared Return Shape And Rerun Status

This node must follow the shared return contract from `SKILL.md`. Its return payload must include:

- `status`
- `node`
- `output_files`
- `changed_files`
- `stale_upstream_inputs`
- `rerun_requests`
- `blocking_gaps`

Use `needs_rerun` or `failed` with `rerun_requests` when another node can resolve the issue. Use `blocked` only when required evidence, target capability, or user input is missing and cannot be produced by rerunning another node.

## Return Shape

```json
{
  "status": "fixed | partially_fixed | blocked",
  "node": "module-node-migration-fix",
  "output_files": [
    "<output_dir>/module_node_migration_fix.json",
    "<output_dir>/module_node_migration_fix.md"
  ],
  "changed_files": [],
  "requires_re_review": true,
  "blocking_gaps": []
}
```
