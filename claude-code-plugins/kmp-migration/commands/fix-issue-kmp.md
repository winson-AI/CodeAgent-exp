---
description: Fix a known KMP compile issue or migrated use-case failure with targeted edits and rerun gates.
argument-hint: "<kmp_target_project_path> <compile|use-case> <failure summary, command, log path, or acceptance criteria>"
---

# /fix-issue-kmp

You are fixing one confirmed Kotlin Multiplatform or Compose Multiplatform issue. The issue may be a compile/build failure or a migrated use-case failure. Keep the fix narrow, evidence-backed, and verified by the smallest trustworthy commands.

User arguments:

```text
$ARGUMENTS
```

## Trigger Boundary

Proceed only when the request contains or can identify:

- `kmp_target_project_path`: an absolute path to a KMP/CMP target project.
- `issue_type`: `compile` or `use_case`.
- concrete failure evidence: failing command, compiler/test output, log path, failing use case, or acceptance criteria.

For `use_case` issues, also require intended behavior from at least one of:

- user-provided expected behavior.
- `legacy_android_project_path`.
- `spec_dir`, `prd_path`, `design_path`, `plan_path`, or `verification_path`.
- `migration_report_path`.

If the target path or actionable failure evidence is missing, ask for it before editing. If intended behavior for a use case is missing, stop with a blocker instead of guessing.

## Supported Input Format

Accept natural language, or this structured format:

```yaml
kmp_target_project_path: /absolute/path/to/kmp-target
issue_type: compile | use_case
issue_summary: Short description of the failure
failing_command: ./gradlew :shared:compileKotlinMetadata
failure_log_path: /absolute/path/to/failure.log
use_case:
  name: Checkout happy path
  steps:
    - Open cart with one item
    - Tap checkout
  expected_result: Confirmation screen is shown
  actual_result: Payment state never leaves Loading
legacy_android_project_path: /absolute/path/to/android-source
spec_dir: /absolute/path/to/SPEC
migration_report_path: /absolute/path/to/migration_report.md
allowed_files:
  - /absolute/path/to/file1.kt
  - /absolute/path/to/file2.kt
user_provided_commands:
  build: ./gradlew :shared:compileKotlinMetadata
  test: ./gradlew :shared:check
  renderability: ./gradlew :composeApp:connectedDebugAndroidTest
output_dir: ~/.d2c_agents/fix-issue-kmp/<issue-name>
language: English
```

## Required Output Format

Return this concise JSON-like summary and write matching artifacts under `output_dir` when supplied, otherwise under `~/.d2c_agents/fix-issue-kmp/<timestamp>/`.

```json
{
  "status": "fixed | partially_fixed | blocked",
  "issue_type": "compile | use_case",
  "kmp_target_project_path": "",
  "root_causes": [],
  "changed_files": [],
  "commands_run": [
    {
      "command": "",
      "status": "passed | failed | blocked",
      "log_file": ""
    }
  ],
  "validation": {
    "build": "passed | failed | skipped | blocked",
    "use_case": "passed | failed | skipped | blocked",
    "renderability": "passed | failed | skipped | blocked"
  },
  "output_files": [
    "<output_dir>/fix_issue_kmp_report.md",
    "<output_dir>/fix_issue_kmp_report.json"
  ],
  "remaining_failures": [],
  "blocking_gaps": []
}
```

## Bug Fix Workflow

1. Normalize the request into the supported input fields. Resolve `~` and relative paths against the current working directory, then verify the target contains a Gradle/KMP/CMP project.
2. Establish the baseline by running the provided failing command first. If no command was provided, discover a trustworthy command from project docs, CI scripts, Gradle wrapper, or existing migration/validation artifacts.
3. Capture logs to files under `output_dir/logs/`. Summarize actionable errors only after preserving the full logs.
4. Classify each failure as `dependency`, `source-set`, `expect-actual`, `platform-api`, `resource`, `theme`, `navigation`, `state-model`, `ui`, `dataflow-logic`, `test-setup`, `environment`, or `unknown`.
5. Fix only confirmed target-code issues. Stay within `allowed_files` when supplied. Do not add dependencies, change root Gradle/settings files, regenerate wrappers, or broaden architecture unless the failure proves it is required.
6. For compile issues, trace the first real compiler error before editing. Ignore downstream unresolved symbols until the upstream error is fixed and rerun.
7. For use-case issues, reproduce the failing path with existing tests or the smallest project-convention test/harness. Cross-check behavior against user expectations, Android source, SPEC, or migration report before editing.
8. Preserve KMP source-set boundaries. Android-only APIs must stay in Android source sets or behind existing/necessary `expect`/`actual` abstractions.
9. After each fix pass, rerun the smallest command that exposed the failure. Then rerun the broader build/check or affected use-case command. Do not claim success from static inspection alone.
10. Stop after three fix passes if the same failure repeats without new evidence. Report the blocker, last command output, and the next required input.

## External Command Strategy

Run commands from `kmp_target_project_path`. Prefer the project Gradle wrapper (`./gradlew`) when present. Use user-provided commands first, then documented project/CI commands, then discovered Gradle tasks.

Discovery commands:

```bash
./gradlew projects
./gradlew tasks --all
./gradlew :<module>:tasks --all
```

Compile/build gates, using only tasks that exist in the target project:

```bash
./gradlew :<module>:compileKotlinMetadata --stacktrace
./gradlew :<module>:compileDebugKotlinAndroid --stacktrace
./gradlew :<module>:compileKotlinJvm --stacktrace
./gradlew :<module>:compileKotlinIosSimulatorArm64 --stacktrace
./gradlew :<module>:check --stacktrace
```

Use-case and regression gates, using project conventions:

```bash
./gradlew :<module>:test --stacktrace
./gradlew :<module>:allTests --stacktrace
./gradlew :<module>:connectedDebugAndroidTest --stacktrace
./gradlew :<module>:verifyPaparazziDebug --stacktrace
./gradlew :<module>:validateScreenshotDebug --stacktrace
```

Performance rules for fix iteration:

- Run the smallest failing command first; run broader `check` or platform test commands only after the focused gate passes.
- Add `--stacktrace` for diagnostics. Add `--info` only when stacktrace logs do not identify the owner. Avoid `--debug` unless explicitly needed.
- Avoid `clean` by default. Use it once only when stale generated output or cache state is a credible root cause.
- Do not use `--continue` for the primary confirmation command. It is allowed only as a secondary diagnostic pass to collect independent failures after the first root cause is understood.
- Record command duration when practical and mention if the final verification relied on a slow or partial gate.

## Report Requirements

Write `fix_issue_kmp_report.md` with:

- normalized input summary.
- baseline failure command and log path.
- root cause analysis.
- exact files changed.
- commands run before and after the fix.
- remaining failures or blockers.
- final status and rerun recommendations.

Write `fix_issue_kmp_report.json` using the required output schema.
