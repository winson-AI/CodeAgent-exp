---
name: kmp-mvi-flowredux
description: >
  KMP/CMP MVI architecture using FlowRedux state machines. Use when building or
  reviewing Kotlin Multiplatform features that need MVI pattern: state machines,
  sealed State/Action classes, unidirectional data flow, Compose Multiplatform UI
  wiring, or when the user mentions FlowRedux, MVI, state machine, inState, onEnter,
  dispatch, or sealed interface State.
---

# KMP MVI with FlowRedux — architecture skill

Reference: https://freeletics.github.io/FlowRedux/

## Core concepts

MVI (Model-View-Intent) enforces **unidirectional data flow**:

```
Action (Intent) ──► StateMachine ──► State ──► UI
       ▲                                        │
       └────────────────────────────────────────┘
                      dispatch()
```

FlowRedux models this as an explicit **state machine** with a Coroutines DSL:
- `State` — sealed interface; each subtype is a discrete screen state
- `Action` — sealed interface; every user gesture or external event
- `FlowReduxStateMachineFactory` — holds the `spec { }` DSL and produces instances
- `FlowReduxStateMachine` — public API: `state: Flow<State>` + `suspend dispatch(action)`

---

## Architecture layers

```
:shared/commonMain
  ├── feature/
  │   ├── model/
  │   │   ├── FeatureState.kt        ← sealed interface State + subtypes
  │   │   └── FeatureAction.kt       ← sealed interface Action + subtypes
  │   ├── statemachine/
  │   │   └── FeatureStateMachineFactory.kt  ← FlowReduxStateMachineFactory
  │   └── domain/
  │       └── FeatureRepository.kt   ← interface; expect/actual for platform impl
  └── di/
      └── FeatureModule.kt           ← Koin module wiring factory + repo

:composeApp/commonMain
  └── feature/
      ├── FeatureScreen.kt           ← @Composable, uses produceStateMachine()
      └── FeatureViewModel.kt        ← optional: ViewModel wrapper for lifecycle
```

**Rule:** All state machine logic lives in `:shared/commonMain`. The UI layer
(`:composeApp`) only renders state and dispatches actions — zero business logic.

---

## Coding guidance

### 1. Define State and Action as sealed interfaces

```kotlin
// shared/commonMain/.../model/ItemListState.kt
sealed interface ItemListState {
    data object Loading : ItemListState
    data class ShowContent(val items: List<Item>) : ItemListState
    data class Error(val message: String, val countdown: Int) : ItemListState
}

// shared/commonMain/.../model/ItemListAction.kt
sealed interface ItemListAction {
    data object RetryLoading : ItemListAction
    data class ToggleFavorite(val itemId: Int) : ItemListAction
}
```

Rules:
- `State` subtypes are `data object` (no fields) or `data class` (immutable fields)
- Never put UI logic inside a `State` — it is plain data
- `Action` subtypes carry only the payload the handler needs — nothing else

### 2. Write the StateMachineFactory in commonMain

```kotlin
// shared/commonMain/.../statemachine/ItemListStateMachineFactory.kt
class ItemListStateMachineFactory(
    private val repository: ItemRepository
) : FlowReduxStateMachineFactory<ItemListState, ItemListAction>() {

    init {
        initializeWith { Loading }

        spec {
            inState<Loading> {
                onEnter { state ->
                    try {
                        val items = repository.loadItems()
                        state.override { ShowContent(items) }
                    } catch (t: Throwable) {
                        state.override { Error(t.message ?: "Unknown error", countdown = 3) }
                    }
                }
            }

            inState<Error> {
                on<RetryLoading> { _, state ->
                    state.override { Loading }
                }

                collectWhileInState(timerEverySecond()) { _, state ->
                    val next = state.snapshot.countdown - 1
                    if (next <= 0) state.override { Loading }
                    else state.mutate { copy(countdown = next) }
                }
            }

            inState<ShowContent> {
                on<ToggleFavorite>(executionPolicy = ExecutionPolicy.Unordered) { action, state ->
                    // delegate to child state machine — see composing section
                    state.mutate { copy(items = items.map { item ->
                        if (item.id == action.itemId) item.copy(toggling = true) else item
                    }) }
                }
            }
        }
    }
}
```

Rules:
- One factory per feature/screen — not one global machine
- `initializeWith { }` always first in `init`
- Extract large handlers into `private suspend fun` for readability and unit-testability
- Never call `state.override` or `state.mutate` after the function returns — these are the only mutation points

### 3. DSL blocks reference

| Block | Triggers when | Typical use |
|---|---|---|
| `onEnter { }` | State is entered | Load data, start timers |
| `on<Action> { }` | Action arrives while in this state | User interactions |
| `collectWhileInState(flow) { }` | Flow emits while in this state | Countdown, realtime updates |
| `onActionEffect<Action> { }` | Like `on<>` but does NOT transition state | Logging, analytics side-effects |
| `condition { }` | Wraps sub-blocks with a predicate | Feature flags, conditional handlers |
| `untilIdentityChanged { }` | Re-enters block when identity field changes | Pagination, refresh on id change |

### 4. ExecutionPolicy — choose deliberately

```kotlin
// Default: CancelPrevious — cancel in-flight handler when same action fires again
on<SearchQueryChanged> { action, state -> ... }

// Unordered — run in parallel, no order guarantee; use for independent async ops
on<ToggleFavorite>(executionPolicy = ExecutionPolicy.Unordered) { ... }

// Ordered — sequential; use when order matters and you must not cancel
on<PageLoad>(executionPolicy = ExecutionPolicy.Ordered) { ... }

// Throttled — ignore re-triggers within duration; use for debounce-like behaviour
on<ButtonClick>(executionPolicy = ExecutionPolicy.Throttled(500.milliseconds)) { ... }
```

### 5. Compose Multiplatform UI wiring

```kotlin
// composeApp/commonMain/.../FeatureScreen.kt
@Composable
fun ItemListScreen(factory: ItemListStateMachineFactory) {
    val stateMachine = factory.produceStateMachine()   // FlowRedux compose extension
    val state by stateMachine.state.collectAsState()   // or use stateMachine.state.value

    when (val s = state) {
        is Loading     -> LoadingIndicator()
        is ShowContent -> ContentList(s.items, onToggle = {
            stateMachine.dispatch(ToggleFavorite(it))  // dispatch is non-suspending in compose ext
        })
        is Error       -> ErrorView(s.message, s.countdown, onRetry = {
            stateMachine.dispatch(RetryLoading)
        })
    }
}
```

For Android ViewModel lifecycle:

```kotlin
class ItemListViewModel @Inject constructor(
    private val factory: ItemListStateMachineFactory
) : ViewModel() {
    private val stateMachine = factory.shareIn(viewModelScope)
    val state: StateFlow<ItemListState> = stateMachine.state
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), Loading)

    fun dispatch(action: ItemListAction) {
        viewModelScope.launch { stateMachine.dispatch(action) }
    }
}
```

### 6. Composing state machines (hierarchical)

Delegate a sub-problem to a child state machine rather than bloating the parent spec:

```kotlin
inState<ShowContent> {
    onActionStartStateMachine(
        stateMachineFactoryBuilder = { action: ToggleFavorite ->
            FavoriteStatusStateMachineFactory(
                itemId = action.itemId,
                httpClient = httpClient
            )
        }
    ) { favoriteStatus: FavoriteStatus ->
        // merge child state into parent state
        mutate { copy(items = items.updateFavoriteStatus(favoriteStatus)) }
    }
}
```

Use `onEnterStartStateMachine()` when you want a child machine to start on state entry
rather than on an explicit action.

### 7. Effects (side-effects without state transition)

```kotlin
inState<ShowContent> {
    onActionEffect<ToggleFavorite> { action, stateSnapshot ->
        analytics.track("toggle_favorite", mapOf("id" to action.itemId))
        // cannot mutate state from an effect block
    }
}
```

Use `*Effect` variants whenever you need to react to an action or event but must not
change state (navigation events, analytics, logging).

---

## Project structure checklist

```
:shared
  commonMain
    └── feature/itemlist/
        ├── model/
        │   ├── ItemListState.kt          ✓ sealed interface, data classes, immutable
        │   └── ItemListAction.kt         ✓ sealed interface
        ├── statemachine/
        │   ├── ItemListStateMachineFactory.kt  ✓ extends FlowReduxStateMachineFactory
        │   └── FavoriteStatusStateMachineFactory.kt  ✓ child machine
        ├── domain/
        │   └── ItemRepository.kt         ✓ interface only
        └── data/
            └── ItemRepositoryImpl.kt     ✓ actual implementation (or expect/actual)

:composeApp
  commonMain
    └── feature/itemlist/
        ├── ItemListScreen.kt             ✓ @Composable, pure render + dispatch
        └── ItemListViewModel.kt          ✓ only if AndroidX lifecycle needed
```

---

## Testing guidance

Prefer **functional integration tests** with Turbine over unit tests per handler.

```kotlin
// Use runTest + Turbine for the full state machine
@Test
fun `loading transitions to ShowContent on success`() = runTest {
    val factory = ItemListStateMachineFactory(FakeItemRepository(items = sampleItems))
    val sm = factory.shareIn(backgroundScope)

    sm.state.test {
        assertEquals(Loading, awaitItem())
        assertEquals(ShowContent(sampleItems), awaitItem())
    }
}

// Override initial state to test mid-flow without replaying all transitions
@Test
fun `retry from Error transitions to Loading`() = runTest {
    val factory = ItemListStateMachineFactory(FakeItemRepository())
    factory.initializeWith { Error("oops", countdown = 3) }
    val sm = factory.shareIn(backgroundScope)

    sm.state.test {
        assertEquals(Error("oops", 3), awaitItem())
        sm.dispatch(RetryLoading)
        assertEquals(Loading, awaitItem())
    }
}
```

For **unit testing handlers**, extract them to `private suspend fun` and test with
`ChangeableState` + `changedState.reduce(snapshot)` directly.

---

## Gradle dependencies

```kotlin
// shared/build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            // FlowRedux core (KMP)
            implementation("com.freeletics.flowredux:flowredux:2.0.1")
            // Coroutines
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")
        }
    }
}

// composeApp/build.gradle.kts
commonMain.dependencies {
    // FlowRedux Compose extensions (produceStateMachine, dispatch)
    implementation("com.freeletics.flowredux:compose:2.0.1")
}

// Testing
commonTest.dependencies {
    implementation("app.cash.turbine:turbine:1.1.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.9.0")
}
```

---

## Anti-patterns to avoid

| Anti-pattern | Fix |
|---|---|
| Business logic inside `@Composable` | Move to `inState { }` handlers |
| Mutable state inside `State` data class | All fields must be `val`; use `state.mutate { copy(...) }` |
| One giant state machine for the whole app | One factory per screen/feature |
| `state.override` called after a `return` | Override is the last expression in the lambda |
| Catching all `Throwable` silently | Log or encode the error into an `Error` state subtype |
| Skipping `ExecutionPolicy` on concurrent actions | Explicitly choose `Unordered` or `Ordered` where needed |
| Navigation logic inside state | Use `onActionEffect` + a navigation callback; state stays pure data |
