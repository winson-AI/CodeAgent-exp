---
name: kmp-mvvm
description: >
  KMP/CMP MVVM architecture with shared ViewModels. Use when building or reviewing
  Kotlin Multiplatform features that follow the MVVM pattern: ViewModel + StateFlow,
  UI state classes, state hoisting, collectAsStateWithLifecycle, Koin viewModel
  injection, or bridging shared ViewModels to SwiftUI on iOS. Triggers on MVVM,
  ViewModel, StateFlow, uiState, viewModelScope, KMP-ObservableViewModel, SKIE.
---

# KMP MVVM with shared ViewModels — architecture skill

References:
- https://kotlinlang.org/docs/multiplatform/compose-viewmodel.html
- https://touchlab.co/kmp-view-models

## Core concepts

MVVM separates concerns into three groups:

```
        observe (StateFlow)              user events (fun calls)
View ◄───────────────────────── ViewModel ◄──────────────────── View
 │                                  │
 │                                  ▼
 │                          Model (UseCase / Repository)
 └─ renders UiState                 │
                                    ▼
                            data / network / cache
```

- **Model** — domain + data layer (UseCases, Repositories) in `commonMain`
- **ViewModel** — holds and exposes immutable `UiState` as `StateFlow`, handles events
- **View** — Compose Multiplatform (shared) or native (SwiftUI/Compose), renders state only

MVVM vs MVI: MVVM exposes a single immutable `UiState` and *public methods* for events,
rather than dispatching `Action` objects through a reducer. Use MVVM when the team is
Android/Compose-native and the per-screen state is simple; reach for MVI/FlowRedux when
state transitions are complex enough to warrant an explicit state machine.

---

## Architecture layers

```
:shared/commonMain
  ├── feature/order/
  │   ├── presentation/
  │   │   ├── OrderUiState.kt        ← single immutable data class (the "Model" the View sees)
  │   │   └── OrderViewModel.kt      ← extends ViewModel, exposes StateFlow<OrderUiState>
  │   ├── domain/
  │   │   ├── OrderRepository.kt     ← interface
  │   │   └── PlaceOrderUseCase.kt   ← business logic, no Android deps
  │   └── data/
  │       └── OrderRepositoryImpl.kt ← actual impl (Ktor/SQLDelight)
  └── di/
      └── OrderModule.kt             ← Koin module: viewModelOf(::OrderViewModel)

:composeApp/commonMain
  └── feature/order/
      └── OrderScreen.kt             ← @Composable, koinViewModel() + collectAsStateWithLifecycle()

iosApp (Swift)                        ← observes ViewModel via KMP-ObservableViewModel
```

**Rule:** ViewModel, UiState, and all logic live in `:shared/commonMain`. The View only
collects state and calls ViewModel methods.

---

## Choosing the ViewModel base class

There are three viable approaches. Pick one per project and stay consistent.

| Approach | commonMain dependency | iOS story | When to use |
|---|---|---|---|
| **AndroidX `lifecycle-viewmodel` (multiplatform)** | `androidx.lifecycle:lifecycle-viewmodel:2.8+` | Manual lifecycle on iOS; brings `viewModelScope` baggage | CMP-first apps where iOS UI is also Compose |
| **KMP-ObservableViewModel** (rickclephas) | `com.rickclephas.kmp:kmp-observableviewmodel-core` | First-class: SwiftUI observes directly, handles store-owner boilerplate | **Recommended** when iOS uses SwiftUI; this is the official Kotlin-docs recommendation |
| **Pure Kotlin ViewModel** (your own `interface`/base) | none | Explicit Swift observer wrapper you write | Maximum control, zero androidx in commonMain |

The official Kotlin documentation recommends **KMP-ObservableViewModel** for SwiftUI
because there is no built-in `ViewModelStoreOwner` on iOS — the library ties the
ViewModel lifecycle to the SwiftUI view automatically.

---

## Coding guidance

### 1. Model UiState as a single immutable data class

```kotlin
// shared/commonMain/.../presentation/OrderUiState.kt
data class OrderUiState(
    val quantity: Int = 1,
    val items: List<OrderItem> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
)
```

Rules:
- One `UiState` per screen — never expose multiple loose `StateFlow`s for one screen
- All fields `val`, with sensible defaults
- Represent loading/error as fields (`isLoading`, `errorMessage`), or use a sealed
  `UiState` if states are mutually exclusive enough to warrant it
- Keep it free of framework types (no `Composable`, no `Color`, no `Painter`)

### 2. ViewModel exposes StateFlow, never MutableStateFlow

```kotlin
// shared/commonMain/.../presentation/OrderViewModel.kt
import com.rickclephas.kmp.observableviewmodel.ViewModel
import com.rickclephas.kmp.observableviewmodel.MutableStateFlow
import com.rickclephas.kmp.observableviewmodel.stateIn
import com.rickclephas.kmp.nativecoroutines.NativeCoroutinesState

class OrderViewModel(
    private val placeOrder: PlaceOrderUseCase,
    private val repository: OrderRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(viewModelScope, OrderUiState())

    @NativeCoroutinesState                       // exposes the flow cleanly to Swift
    val uiState: StateFlow<OrderUiState> = _uiState.asStateFlow()

    init { loadItems() }

    fun setQuantity(n: Int) {
        _uiState.update { it.copy(quantity = n) }
    }

    fun submit() {
        viewModelScope.coroutineScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            runCatching { placeOrder(_uiState.value.quantity) }
                .onSuccess { _uiState.update { s -> s.copy(isLoading = false) } }
                .onFailure { t -> _uiState.update { s -> s.copy(isLoading = false, errorMessage = t.message) } }
        }
    }

    private fun loadItems() { /* launch in viewModelScope, update _uiState */ }
}
```

Rules:
- `_uiState` is private `MutableStateFlow`; expose read-only `StateFlow` via `asStateFlow()`
- Always update via `update { copy(...) }` — atomic, avoids race conditions
- Launch coroutines in `viewModelScope` so they cancel when the ViewModel clears
- Annotate the public flow with `@NativeCoroutinesState` for clean Swift interop
- Never expose `suspend` functions to the View; the View calls plain `fun`, the VM launches

### 3. Compose Multiplatform View — state hoisting + lifecycle-aware collection

```kotlin
// composeApp/commonMain/.../OrderScreen.kt
@Composable
fun OrderScreen(viewModel: OrderViewModel = koinViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    OrderContent(
        state = uiState,
        onQuantityChange = viewModel::setQuantity,
        onSubmit = viewModel::submit,
    )
}

// Stateless, hoisted — fully previewable and testable
@Composable
private fun OrderContent(
    state: OrderUiState,
    onQuantityChange: (Int) -> Unit,
    onSubmit: () -> Unit,
) {
    Column {
        if (state.isLoading) LinearProgressIndicator()
        QuantityStepper(state.quantity, onQuantityChange)
        state.errorMessage?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        Button(onClick = onSubmit, enabled = !state.isLoading) { Text("Place order") }
    }
}
```

Rules:
- Split into a stateful screen (`koinViewModel()` + collect) and a stateless content
  composable that takes `state` + lambdas — this is **state hoisting**
- Use `collectAsStateWithLifecycle()` (not bare `collectAsState()`) so collection pauses
  when the UI is not visible
- Pass method references (`viewModel::setQuantity`), not the whole ViewModel, into content
- The stateless content composable has zero ViewModel dependency → trivially previewable

### 4. Dependency injection with Koin

```kotlin
// shared/commonMain/.../di/OrderModule.kt
val orderModule = module {
    singleOf(::OrderRepositoryImpl) bind OrderRepository::class
    factoryOf(::PlaceOrderUseCase)
    viewModelOf(::OrderViewModel)        // koin-compose-viewmodel
}
```

Compose retrieves it with `koinViewModel()` (from `koin-compose-viewmodel`), which
scopes the ViewModel to the navigation entry / composition correctly on all platforms.

### 5. iOS bridge (SwiftUI)

With KMP-ObservableViewModel + `@NativeCoroutinesState`, SwiftUI observes directly:

```swift
struct OrderView: View {
    @StateViewModel var viewModel = OrderViewModel(placeOrder: ..., repository: ...)

    var body: some View {
        VStack {
            if viewModel.uiState.isLoading { ProgressView() }
            Stepper("Qty: \(viewModel.uiState.quantity)",
                    value: Binding(get: { Int(viewModel.uiState.quantity) },
                                   set: { viewModel.setQuantity(n: Int32($0)) }))
            Button("Place order") { viewModel.submit() }
        }
    }
}
```

If you instead use AndroidX ViewModel + SKIE, SKIE maps `StateFlow` to a Swift
`AsyncSequence`/`@Observable` and you bridge it with an observer wrapper.

---

## Project structure checklist

```
:shared
  commonMain
    └── feature/order/
        ├── presentation/
        │   ├── OrderUiState.kt          ✓ single immutable data class
        │   └── OrderViewModel.kt        ✓ private Mutable, public StateFlow
        ├── domain/
        │   ├── OrderRepository.kt       ✓ interface
        │   └── PlaceOrderUseCase.kt     ✓ pure logic, no androidx
        ├── data/
        │   └── OrderRepositoryImpl.kt   ✓ Ktor / SQLDelight
        └── di/OrderModule.kt            ✓ viewModelOf(::OrderViewModel)

:composeApp
  commonMain
    └── feature/order/OrderScreen.kt     ✓ stateful screen + stateless content

iosApp                                   ✓ @StateViewModel, observes uiState
```

---

## Testing guidance

The ViewModel is a plain class — test it with `runTest` + Turbine, injecting fakes.

```kotlin
@Test
fun `submit sets loading then clears on success`() = runTest {
    val vm = OrderViewModel(
        placeOrder = FakePlaceOrderUseCase(succeeds = true),
        repository = FakeOrderRepository(),
    )
    vm.uiState.test {
        assertEquals(OrderUiState(), awaitItem())           // initial
        vm.setQuantity(3)
        assertEquals(3, awaitItem().quantity)
        vm.submit()
        assertTrue(awaitItem().isLoading)                   // loading on
        assertFalse(awaitItem().isLoading)                  // cleared after success
    }
}
```

The stateless content composable is tested separately with Compose UI tests / screenshot
tests — it takes a `UiState` directly, so no ViewModel is needed.

---

## Gradle dependencies

```kotlin
// shared/build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            // Recommended iOS-friendly ViewModel (official Kotlin docs)
            implementation("com.rickclephas.kmp:kmp-observableviewmodel-core:1.0.0-BETA-13")
            // OR the AndroidX multiplatform ViewModel
            // implementation("org.jetbrains.androidx.lifecycle:lifecycle-viewmodel:2.8.4")

            implementation("io.insert-koin:koin-core:4.0.0")
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")
        }
        commonTest.dependencies {
            implementation("app.cash.turbine:turbine:1.1.0")
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.9.0")
        }
    }
}

// composeApp/build.gradle.kts
commonMain.dependencies {
    implementation("io.insert-koin:koin-compose-viewmodel:4.0.0")  // koinViewModel()
    implementation("org.jetbrains.androidx.lifecycle:lifecycle-viewmodel-compose:2.8.4")
}
```

For SwiftUI interop, add the KMP-ObservableViewModel Swift package, or KMP-NativeCoroutines / SKIE.

---

## Anti-patterns to avoid

| Anti-pattern | Fix |
|---|---|
| Exposing `MutableStateFlow` publicly | Expose read-only `StateFlow` via `asStateFlow()` |
| Multiple loose `StateFlow`s for one screen | Combine into one `UiState` data class |
| Business logic inside the `@Composable` | Move to the ViewModel; the View only renders + calls methods |
| Passing the whole ViewModel into child composables | Hoist state: pass `UiState` + lambdas |
| `collectAsState()` instead of `collectAsStateWithLifecycle()` | Use the lifecycle-aware variant to pause off-screen collection |
| `suspend` functions exposed to the View | Keep them internal; the VM launches in `viewModelScope` |
| Framework types (`Color`, `Painter`) inside `UiState` | Keep `UiState` platform-agnostic data only |
| AndroidX ViewModel in commonMain when targeting SwiftUI | Prefer KMP-ObservableViewModel or a pure-Kotlin base |
| Mutating state with `.value = .value.copy()` under concurrency | Use `update { copy(...) }` for atomic updates |
