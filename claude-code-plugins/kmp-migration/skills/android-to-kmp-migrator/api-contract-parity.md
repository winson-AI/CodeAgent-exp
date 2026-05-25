---
name: android-to-kmp-migrator-api-contract-parity
description: Check migrated KMP API contracts against Legacy Android API evidence. Use after dataflow/logic implementation to verify endpoints, params, headers, request/response models, errors, pagination, and auth behavior.
disable-model-invocation: true
---

# API Contract Parity Node

## Role

You are an API contract parity subagent. Compare Legacy Android API/data contracts with the migrated KMP implementation and route mismatches. Do not implement fixes directly.

## Inputs

- `kmp_target_project_path`: absolute path to KMP target project.
- `migration_scope`: whole project, module, feature, screen, or task.
- `api_list_path`: Legacy Android API list output.
- `data_flow_path`: Legacy Android data-flow output.
- `dataflow_logic_impl_result_path`: dataflow/logic implementation output.
- `changed_files`: changed API/model/repository files.
- `output_dir`: directory where this node must write outputs; default to `~/.d2c_agents/migration/`.

## Specific Task

1. Compare endpoint paths, methods, query/body params, headers, auth, and content types.
2. Compare request/response models, nullable fields, enum/sealed variants, pagination, and error wrappers.
3. Verify local-store/cache behavior when it affects API parity.
4. Classify contracts as equivalent, changed, omitted, approximated, or blocked.
5. Route mismatches to `dataflow-logic-implementation`, `state-model-mapping`, or `dependency-resolution`.

## Required Outputs

- `api_contract_parity.json`
- `api_contract_parity.md`

```json
{
  "status": "passed | failed | blocked",
  "node": "api-contract-parity",
  "contract_results": [
    {
      "legacy_contract": "",
      "target_contract": "",
      "status": "equivalent | changed | omitted | approximated | blocked",
      "differences": [],
      "route_to_node": "",
      "evidence": []
    }
  ],
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
  "status": "passed | failed | blocked",
  "node": "api-contract-parity",
  "output_files": [
    "<output_dir>/api_contract_parity.json",
    "<output_dir>/api_contract_parity.md"
  ],
  "blocking_gaps": []
}
```
