---
name: kmp-expert
description: >
  Foundational Kotlin Multiplatform / Compose Multiplatform knowledge for KMP/CMP
  development. Use when working on any KMP/CMP task: project setup, source set
  hierarchy, expect/actual, Gradle/version-catalog config, choosing the library
  stack (Ktor, SQLDelight, Room, Koin, serialization), iOS interop (SKIE,
  KMP-NativeCoroutines), Wasm/web targets, or debugging build/source-set issues.
  Triggers on Kotlin Multiplatform, KMP, CMP, Compose Multiplatform, commonMain,
  expect/actual, shared module, iosMain, klib, Kotlin/Native.
---

# Kotlin Multiplatform / Compose Multiplatform — expert skill

This is the foundational knowledge layer for KMP/CMP work. For presentation
architecture, see the companion `kmp-mvvm` and `kmp-mvi-flowredux` skills — this
skill covers everything beneath them: structure, source sets, interop, and the stack.

References:
- https://kotlinlang.org/docs/multiplatform/multiplatform-discover-project.html
- https://kotlinlang.org/docs/multiplatform/multiplatform-hierarchy.html
- https://blog.jetbrains.com/kotlin/2026/05/new-kmp-default-structure/

## KMP vs CMP — know which one you mean

- **KMP (Kotlin Multiplatform)** — shares non-UI logic (networking, persistence,
  business rules). You build the UI natively per platform (Compose on Android,
  SwiftUI on iOS). Officially supported by Google for Android/iOS logic sharing.
- **CMP (Compose Multiplatform)** — a declarative UI framework layered on top of KMP
  that lets you share the UI too. On iOS it renders via Skia (Skiko), not native widgets.

Decision rule: push as much as possible into `commonMain`. Use KMP-only when you need
the deepest native iOS fidelity; use CMP when one UI codebase outweighs that.

---

## Compilation targets

| Target | Compiler | Output |
|---|---|---|
| Android / JVM backend | Kotlin/JVM | JVM bytecode |
| iOS / macOS / watchOS / tvOS / Linux / Windows | Kotlin/Native (LLVM) | Native binary / `.framework` |
| Web | Kotlin/Wasm (or legacy Kotlin/JS) | WebAssembly / JS |

Kotlin/Native produces standalone binaries with no VM, which is how KMP gets native
performance on iOS.

---

## Project structure (JetBrains 2026 default)

The default structure changed in 2026 to give each module a single responsibility,
aligning with Android Gradle Plugin 9.0.

```
project-root/
├── shared/          ← KMP library: ALL shared code (the only multiplatform module)
│   └── src/
│       ├── commonMain/      ← 80–90% of code lives here
│       ├── androidMain/     ← Android actuals + JVM-only deps
│       ├── iosMain/         ← iOS actuals (intermediate; see hierarchy below)
│       ├── desktopMain/     ← JVM desktop actuals
│       ├── wasmJsMain/      ← web actuals
│       └── commonTest/
├── androidApp/      ← thin Android entry point, depends on :shared
├── iosApp/          ← Xcode project consuming the shared framework
├── desktopApp/      ← JVM desktop entry point
└── webApp/          ← Wasm/JS entry point
```

The old single `composeApp` module that mixed library + app concerns is replaced by a
clean `shared` library plus separate `*App` modules. Generate new projects at
`kmp.jetbrains.com`. Reference samples: `KMP-App-Template`, `kotlinconf-app`, RSS Reader.

For large apps, modularize further: feature modules (`:feature-x`) each split into
`domain`/`data`/`presentation`, plus shared `:core-network`, `:core-db`, `:core-ui`.

---

## Source set hierarchy — the mental model

Source sets form a tree. During compilation for a target, Kotlin combines **all** source
sets on the path from `commonMain` down to the platform leaf.

```
                 commonMain
                /          \
          appleMain       jvmAndroidShared (you create if needed)
          /      \         /        \
     iosMain   macosMain  androidMain  desktopMain
     /    \
iosArm64  iosSimulatorArm64
```

Key facts:
- `commonMain` compiles to every target; code here may use only multiplatform APIs.
- **Intermediate source sets** (`iosMain`, `appleMain`, `nativeMain`) share code among a
  subset of targets. Put `actual` declarations in the intermediate set (e.g. `iosMain`),
  not in each leaf (`iosArm64Main`, `iosSimulatorArm64Main`).
- The **default hierarchy template** (modern Kotlin) auto-wires `nativeMain`, `appleMain`,
  `iosMain`, etc. You rarely need manual `dependsOn` anymore.
- Kotlin does **not** auto-share a JVM+Android source set. If their deps overlap, create a
  custom intermediate set and wire it with `dependsOn` (IDE intellisense may complain but
  it compiles).

---

## expect / actual — the platform contract

The cornerstone mechanism. Declare an `expect` in `commonMain`; provide an `actual` per
target (or per intermediate source set).

```kotlin
// commonMain
expect fun getPlatform(): Platform
interface Platform { val name: String }

// androidMain
actual fun getPlatform(): Platform = object : Platform {
    override val name = "Android ${Build.VERSION.SDK_INT}"
}

// iosMain
actual fun getPlatform(): Platform = object : Platform {
    override val name = UIDevice.currentDevice.systemName()
}
```

Three forms:
1. `expect fun` / `actual fun` — functions (most common)
2. `expect class` / `actual class` — full classes
3. **Interface + expect factory** (recommended) — declare an `interface` in common, an
   `expect fun buildX(): Interface` factory, and platform `actual` factories returning
   platform impls. This keeps common code free of platform types and is easier to test.

Prefer the interface+factory form over `expect class`; it avoids the strictness of
matching every member signature across platforms.

When NOT to use expect/actual: if a library already provides a multiplatform API (Ktor,
SQLDelight, kotlinx-datetime), use it directly in `commonMain` — no expect/actual needed.

---

## The standard 2026 library stack

Verify multiplatform support at `klibs.io` before adding any dependency.

| Concern | Library | Notes |
|---|---|---|
| Networking | **Ktor client** | `commonMain` core + per-platform engine (OkHttp/Android, Darwin/iOS, CIO/desktop) |
| Serialization | **kotlinx.serialization** | apply the plugin to the module that defines `@Serializable` types |
| Persistence | **SQLDelight** (typed SQL) or **Room KMP** (Google, DAO-style) | SQLDelight for control; Room for Android-team familiarity |
| Key-value | **multiplatform-settings** or **DataStore** | small prefs |
| DI | **Koin** | no codegen → fast multiplatform compile; `koin-compose-viewmodel` for CMP |
| Dates/time | **kotlinx-datetime** | multiplatform `Instant`, `LocalDate`, time zones |
| Coroutines | **kotlinx-coroutines-core** | the concurrency backbone |
| Image loading | **Coil 3** | multiplatform |
| Navigation | Navigation-Compose (KMP), **Voyager**, or **Decompose** | Decompose pairs well with KMP lifecycle |
| Testing | **kotlinx-coroutines-test** + **Turbine** | flow testing |

---

## Gradle configuration (modern, terse)

```kotlin
// shared/build.gradle.kts
plugins {
    kotlin("multiplatform")
    kotlin("plugin.serialization")
    id("com.android.library")
}

kotlin {
    androidTarget()
    iosX64(); iosArm64(); iosSimulatorArm64()
    jvm("desktop")
    wasmJs { browser() }

    // Default hierarchy template auto-creates iosMain/appleMain/nativeMain.
    sourceSets {
        commonMain.dependencies {
            implementation(libs.ktor.client.core)
            implementation(libs.kotlinx.serialization.json)
            implementation(libs.koin.core)
            implementation(libs.kotlinx.coroutines.core)
        }
        androidMain.dependencies { implementation(libs.ktor.client.okhttp) }
        iosMain.dependencies     { implementation(libs.ktor.client.darwin) }
        getByName("desktopMain").dependencies { implementation(libs.ktor.client.cio) }
        commonTest.dependencies  {
            implementation(libs.turbine)
            implementation(libs.kotlinx.coroutines.test)
        }
    }
}
```

Use a `gradle/libs.versions.toml` version catalog for all dependency coordinates —
it is the standard for keeping versions consistent across modules.

---

## iOS interop — the hard part

Kotlin/Native exports through an Objective-C bridge, which is lossy: sealed classes lose
exhaustiveness, `Int?` becomes a boxed `KotlinInt`, and `suspend` functions become
completion-handler callbacks. Mitigations:

| Tool | What it fixes |
|---|---|
| **SKIE** | Maps Kotlin `Flow` → Swift `AsyncSequence`, sealed classes → Swift enums with associated values, default args. Easy setup, less verbose. |
| **KMP-NativeCoroutines** | Maps `suspend`/`Flow` to Swift `async/await`, Combine, or RxSwift with proper cancellation. The more battle-tested option. |
| **KMP-ObservableViewModel** | Lets SwiftUI observe Kotlin ViewModels and handles the iOS lifecycle/store-owner boilerplate. |
| **Swift Export (emerging)** | Direct Kotlin→Swift modules (suspend→async/await, sealed→enums) without the ObjC layer. Still experimental — don't build production architecture on it yet. |

Practical rules:
- Reduce the exported surface: mark internal code `internal`/`private` and enable
  `explicitApi()` so you don't export everything by default.
- Annotate the flows/suspend functions you expose with the chosen tool's annotation
  (`@NativeCoroutines`, `@NativeCoroutinesState`).
- iOS engineers should never see `KotlinInt` or completion handlers — that's a sign your
  interop layer is missing.

---

## Common gotchas

| Symptom | Cause | Fix |
|---|---|---|
| `@Serializable` compiles but crashes at runtime | serialization plugin not on the module defining the type | Apply `kotlin("plugin.serialization")` to that module |
| IDE shows red but it compiles | IntelliSense lagging on intermediate source sets | Sync Gradle; the build is the source of truth |
| Can't share code across JVM + Android | Kotlin doesn't auto-create that intermediate set | Create a custom source set with `dependsOn` |
| iOS sees opaque classes, no exhaustive switch | Raw ObjC bridge without SKIE | Add SKIE or KMP-NativeCoroutines |
| Slow Kotlin/Native builds | Native compilation is inherently slower than JVM | Use `embedAndSign`/`SKIE` caching; iterate on Android/desktop, verify on iOS less often |
| `expect class` won't compile — member mismatch | strict signature matching across platforms | Switch to interface + `expect` factory function |
| Coroutine on iOS never cancels | exposed raw `suspend` without interop annotation | Annotate with `@NativeCoroutines` for proper cancellation |
| Android-only API leaked into commonMain | wrote `android.*` import in common code | Move it behind expect/actual or an interface |

---

## Build/run quick reference

```bash
./gradlew :shared:build                 # compile the shared library, all targets
./gradlew :androidApp:installDebug      # build + install Android app
./gradlew :desktopApp:run               # run desktop (JVM) app
./gradlew :shared:iosSimulatorArm64Test # run iOS tests on simulator
# iOS app itself is built/run from Xcode (iosApp project) consuming the framework
```

---

## When advising on KMP/CMP work

1. Default to putting code in `commonMain`; only drop to platform source sets when an API
   genuinely differs. Reach for expect/actual last, libraries first.
2. Check `klibs.io` for multiplatform support before suggesting any dependency.
3. For UI: ask whether they want shared UI (CMP) or native UI (KMP-only) before scaffolding.
4. For presentation logic, defer to the `kmp-mvvm` or `kmp-mvi-flowredux` skill.
5. Always consider the iOS interop cost of anything exposed across the Swift boundary.
