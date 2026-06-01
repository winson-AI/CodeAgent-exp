---
description: Understand a legacy Android project, module, feature, question, or target code path through android-project-analyst exploration mode.
argument-hint: "<source_project_path> [question | module | feature | screen | target code path]"
---

# /legacy-android-understand

Invoke `android-project-analyst` in `exploration` mode to understand Legacy Android code. Use this command when the user wants an evidence-backed answer, module analysis, feature/screen analysis, or target-code explanation without starting migration work.

User arguments:

```text
$ARGUMENTS
```

## Trigger Boundary

Proceed only when the request contains or can identify:

- `source_project_path`: an absolute path to a Legacy Android project.
- exploration intent: understand, analyze, document, onboard, answer a code question, inspect a module, inspect a feature/screen, or explain target code.

Do not use this command for:

- Android-to-KMP implementation or migration execution.
- KMP target validation or compile fixes.
- quick single-symbol lookup that does not need structured Android understanding.
- non-Android codebases.

If `source_project_path` is missing or the path does not contain Android evidence, ask for the path before dispatching `android-project-analyst`.

## Supported Input Format

Accept natural language, or this structured format:

```yaml
source_project_path: /absolute/path/to/legacy-android
analysis_scope: whole project | module | feature | screen | target code
question: What should be explained after analysis?
module: app | feature-checkout | :feature:profile
feature: checkout happy path
screen: CheckoutActivity | CartFragment | ProfileScreen
target_code:
  - app/src/main/java/com/example/checkout/CheckoutViewModel.kt
  - feature/profile/src/main/java/com/example/profile/ProfileRepository.kt
output_dir: ~/.a2c_agents/understand/<scope-name>
language: English
```

Input interpretation:

- If `question` is provided, analyze the project or scoped code enough to answer it with source-backed evidence.
- If `module`, `feature`, or `screen` is provided, set `analysis_scope` to that module, feature, or screen.
- If `target_code` is provided, trace how those files/classes participate in UI, architecture, APIs, resources, data flow, and logic.
- If only `source_project_path` is provided, analyze the whole project.

## Agent Invocation Contract

Dispatch `android-project-analyst` with this normalized prompt:

```text
Use the android-project-analyst agent in exploration mode.

source_project_path: <absolute path to Android project>
analysis_scope: <whole project | module | feature | screen | target code description>
mode: exploration
output_dir: <optional artifact root; default ~/.a2c_agents/understand/>
language: <language or English>

Focus:
- Answer the user's question when one was provided.
- Analyze the requested module, feature, screen, or target code paths when provided.
- Generate evidence-backed SPEC artifacts under <output_dir>/SPEC: prd.md, design.md, verification.md.
- Do not create migration plan artifacts unless the user explicitly asks for migration in a separate request.
```

## Optional Android Studio MCP Context

When the `jetbrains` MCP server is available, allow `android-project-analyst` to use Android Studio indexed context as an assistant for project structure and code intelligence:

- `get_project_modules`, `get_project_dependencies`, and `get_repositories` for module/dependency/VCS topology.
- `find_files_by_glob`, `search_in_files_by_regex`, and `get_symbol_info` for target-code and symbol understanding.
- `get_file_problems` for diagnostics on scope-critical files.

Always pass `projectPath: <source_project_path>` for MCP calls. MCP evidence should improve the answer and SPEC representation, but source paths and analyst node outputs remain required.

## Required Output Format

Return this concise JSON-like summary after `android-project-analyst` completes:

```json
{
  "status": "completed | blocked",
  "mode": "exploration",
  "source_project_path": "",
  "analysis_scope": "",
  "question_answer": "",
  "target_code_reviewed": [],
  "spec_outputs": [
    "<output_dir>/SPEC/prd.md",
    "<output_dir>/SPEC/design.md",
    "<output_dir>/SPEC/verification.md"
  ],
  "key_findings": [],
  "blocking_gaps": []
}
```

## Exploration Steps

1. Normalize the input into `source_project_path`, `analysis_scope`, optional `question`, optional `module`, optional `feature`, optional `screen`, optional `target_code`, `output_dir`, and `language`.
2. Verify the source path exists and contains Android evidence such as `AndroidManifest.xml`, `settings.gradle`, `settings.gradle.kts`, `build.gradle`, `build.gradle.kts`, or a module using `com.android.*`.
3. Force `mode: exploration`. Do not infer migration mode from a target path or KMP mention inside this command.
4. Dispatch `android-project-analyst` with the normalized invocation contract.
5. Require the analyst output to include `prd.md`, `design.md`, and `verification.md` under `<output_dir>/SPEC`.
6. If the input included a `question`, answer it only after the analysis completes and cite the generated SPEC or source paths surfaced by the analyst.
7. If the input included `module`, `feature`, `screen`, or `target_code`, summarize how that scope fits into UI, architecture, data flow, logic/control flow, APIs, resources, and Android ecosystem constraints.
8. If the analyst reports gaps, preserve them in `blocking_gaps` instead of filling them with assumptions.

## Report Expectations

The final response should prioritize:

- direct answer to the user's question, when provided.
- module/feature/screen or target-code understanding.
- SPEC artifact paths.
- key source-backed findings.
- unresolved gaps and recommended next analysis targets.
