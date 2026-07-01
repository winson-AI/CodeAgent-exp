---
name: ponytail-review
description: Reviews code or diffs only for over-engineering and removable complexity. Use when the user asks what can be deleted, whether code is over-built, or for a Ponytail-style review that finds reinvention, unnecessary dependencies, speculative abstractions, dead flexibility, and shrinkable logic.
version: "0.1"
kind: review-skill
disable-model-invocation: false
license: MIT
---

# Ponytail Review

Review for unnecessary complexity only. The best outcome is a shorter diff.

## Scope

Find:

- `delete`: dead code, unused flexibility, speculative feature, redundant layer.
- `stdlib`: hand-rolled logic replaced by a standard library API.
- `native`: dependency or code replaced by a native platform feature.
- `yagni`: abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink`: same behavior in fewer lines.

Do not report correctness, security, accessibility, migration fidelity, or performance issues here unless the user explicitly asks for a normal review too. A single smoke test, assertion self-check, or smallest migration/build gate is Ponytail minimum, not bloat.

## Method

1. Read the changed files or requested scope.
2. Identify code that can be removed or replaced by existing project code, standard APIs, native platform features, or installed dependencies.
3. Prefer root deletion over smaller cosmetic simplifications.
4. For each finding, name the location, what to cut, and what replaces it.
5. End with `net: -N lines possible` when you can estimate it. If nothing should be cut, say `Lean already. Ship.`

## Format

```text
<path>: <tag>: <what to cut>. <replacement>.
```

Examples:

```text
src/repo/UserRepo.kt: yagni: Repository interface has one implementation. Inline until a second implementation exists.
ui/DateField.tsx: native: custom date picker for plain date entry. Use <input type="date">, 0 deps.
```
