# Selection contract

The ASM library coordinates exploration and selects from actions discovered by its technology integration. The integration keeps the executable technology objects; a choice identifier identifies which operation to invoke.

The operations below define the selection and reporting boundary. The library's exploration entry point coordinates this boundary with the integration's observation, discovery, and execution capabilities. A customer starts exploration rather than having to implement that cycle. Historical evidence can come from independently recorded tool traces.

## Start

Supply `configuration`, reconstructed `sources`, and `selected_runs`. Configuration contains an explicit `abstraction` rule definition and an ordered `asms` list. Each entry has a `name` (`unvisited` or `random`) and positive `action_limit`. Unvisited entries may set `unmatched_choices` to `exclude` (default) or `isolated`. Optional `total_action_limit` limits invoked actions across the run. The [controller](exploration-controller.md) defines selection and switching.

Abstraction rules include an `actions` section. State grouping and action grouping are both needed for history-based selection. The abstraction rules stay fixed during an ASM run. The controller switches among the configured ASMs.

A technology integration can supply documented default rules. It resolves those defaults into the same explicit configuration before starting the ASM. Generic ASM libraries accept the resolved definition.

Sources use the reconstructed collection structure defined by [abstraction conformance](https://github.com/ferpasri/testar-abstraction-specs/tree/main/conformance). An evidence reader validates the trace and lifecycle first. The ASM retains its own stored history and model, builds the abstract model through its native abstraction library, and starts at knowledge revision zero. This revision is a run-local counter that identifies which accepted evidence a decision used. Historical evidence supplied by the caller stays unchanged.

## Current observation and eligible actions

| Field | Meaning |
| --- | --- |
| `context_id` | Identifier for this observation and offered choice list, unique within the run. |
| `observation` | The `source`, `run`, and `observation` reference in accepted evidence. |
| `choices` | Eligible options. Each has `choice_id`, `action_description`, and nullable `target_widget`. |

The observation belongs to a selected, active test run and sequence and is the latest observation in that sequence. If that sequence already has a recorded execution awaiting its execution result or resulting observation, setting the context returns `execution_in_progress`; the earlier execution must be resolved first. Each description/widget pair occurs in its recorded available-action list. The eligible list may be a subset of that list, for example after safety filters. Choice identifiers are unique within the context.

Two executable choices may refer to the same recorded binding. They remain separate choices. Choice identifiers select executable options; they do not establish identity between traces.

Setting a context replaces the previous one. Repeating the current context with the same identifier and content is harmless. Reusing an identifier with changed content is a conflict; a retired context cannot be restored. A changed choice list needs a new context identifier, even when it refers to the same observation.

A missing property used by abstraction can leave a choice unmatched. A missing widget binding is represented by a recorded null target and its known capture limitation. A reference to a widget absent from the recorded state is invalid evidence.

## Operations

These are logical operations. Native libraries may use language-appropriate method names and record classes.

| Operation | Input and behavior |
| --- | --- |
| `set_context` | Accept the current observation reference and eligible choices. |
| `select` | Return a selection or an explicit no-action reason. Selection alone does not add an execution or change history counts. |
| `begin_execution` | Accept a returned selection and a fresh source-qualified execution reference immediately before invocation. Check context, knowledge revision, and choice; reserve one execution. |
| `report_execution` | Supply that execution reference and an evidence update containing its recorded status. Pending statuses retain the reservation; completed, failed, or incomplete statuses release it. |
| `report_not_invoked` | Release the reservation when the operation was never invoked and no execution record was accepted. Require a fresh context before another selection. |
| `update_evidence` | Accept reconstructed source snapshots and selected runs, preserving existing records. Rebuild selection knowledge when accepted evidence changes. |
| `cancel` | Stop further selections and invocations. Final execution/evidence reports remain accepted. |

A reservation holds the chosen operation and its source observation until the integration reports what happened. It is ASM coordination data; execution facts are recorded through the evidence adapter.

One execution can be reserved at a time per ASM run. Independent runs can coordinate other executions. Context replacement while a reservation is active returns `execution_in_progress`.

The integration checks readiness and target applicability before beginning. It records the selected action through its evidence adapter and invokes the operation after `begin_execution` succeeds. The ASM library's exploration entry point coordinates these steps through the technology integration.

A call that was invoked and raised an error has an execution error. `report_not_invoked` is for an operation that was never called. It does not fabricate an Evidence Event or turn an execution error into an unexecuted choice.

## Selection result

A selection contains `result_type: "selected"`, `context_id`, `knowledge_revision`, the original `choice_id`, and `asm_index` (the zero-based configuration entry). Its `reason` is `local_unvisited_action`, `navigate_to_unvisited_actions`, or `random_action`.

The `rankings` list explains all offered choices: `match`, `eligible`, `count_scope`, `recorded_executions`, `status_counts`, and `supporting_executions`. Here `eligible` means usable by the active ASM's matching policy. Entries are listed by Unicode code-point order of `choice_id`; their order is diagnostic, not a preference for smaller execution counts.

A navigation selection also has `navigation`: `target_state` (a representative observation reference), `distance`, `unvisited_actions`, and ordered `supporting_executions` (one completed execution reference per route step). Use the smallest source/run/observation reference to represent each abstract state, and the smallest source/run/execution reference to represent each abstract transition. Compare reference components in Unicode code-point order. Route representatives identify supporting evidence, not a promise that one original sequence followed the entire route.

Unvisited target counts include distinct, unambiguously matched available abstract actions with zero matching executions. Missing availability data supplies no presumed actions. The current state cannot be a navigation target: its actions were already checked against the current eligible choices. When known unvisited actions exist but none can be reached with an eligible first step, the Unvisited ASM returns `no_reachable_unvisited_actions`. When none are known, it returns `no_unvisited_actions`.

`begin_execution` accepts the last returned selection only while its context and knowledge revision still apply. It validates the choice identifier as well. A context replacement, stored history and model change, or consumed selection prevents silently invoking the old selection.

### Random choice

Implementations use an unbiased `choose_index(size)` provider returning an integer from zero through `size - 1`. Native APIs can allow the caller to supply that provider. Production defaults use the language's random generator; shared cases supply exact size/index pairs.

Sort executable choices by `choice_id`, target states by representative observation reference, and shortest routes by their ordered transition-reference lists before drawing. Do not draw for a single option. For Unvisited ASM, draw for a local choice, or for a tied target, then a tied shortest route, then matching first-step choices, in that order. Random ASM draws once among all offered choices. Repeated `select` calls reuse the last decision while context, knowledge revision, and controller entry remain unchanged; they consume no further randomness.

### No-action results

A no-action result contains `result_type: "no_action"` and one of these reasons, checked in this order:

1. `cancelled`: cancellation was requested.
2. `execution_in_progress`: a reserved execution is still outstanding.
3. `no_context`: a current context has not been supplied or needs refreshing.
4. `action_limit_reached`: the overall action limit is exhausted.
5. `no_available_choices`: the current eligible list is empty.

When these preconditions permit selection, the controller tries at most one cycle through the configured entries. With one entry it returns that ASM's reason: `no_comparable_choices`, `no_unvisited_actions`, or `no_reachable_unvisited_actions`. With several entries and no applicable selection it returns `no_applicable_asm`. Results include `asm_index`; an unsuccessful full cycle leaves the starting entry active. Matching exclusions are checked before searching for unvisited actions.

An invoked execution consumes the active entry's limit once, when its first execution record is accepted. It keeps that entry until terminal reporting releases the reservation. On the next selection, a reached entry limit advances to the next entry and resets the new entry's count. `report_not_invoked` consumes neither an entry limit nor the overall limit. The overall limit includes only executions begun through this ASM run, not other incoming historical records.

Selections and no-action results include a nonempty human-readable `message`. Shared tests compare structured reasons and rankings; message wording can differ between languages.

## Execution counts

Count distinct source/run/execution references matching the abstract source state and action under the configured abstraction. All evidence execution statuses contribute to the total; `status_counts` preserves their separate meanings. A failed attempt therefore makes an action visited, although it supplies no completed transition for navigation. Actual execution parameters determine the action group used for counting.

| Field | Meaning |
| --- | --- |
| `count_scope` | `abstract_action`, `recorded_binding`, or null when the count is unknown. |
| `recorded_executions` | Total distinct matching execution records, or null. |
| `status_counts` | Separate counts for the statuses defined by the [evidence format](https://github.com/ferpasri/testar-evidence-specs/blob/main/docs/evidence-format.md#lifecycle-and-validation), or null. |
| `supporting_executions` | The original references counted, without duplicates. |

Unknown correspondence means an unknown count, not zero. With `unmatched_choices: "exclude"`, Unvisited ASM excludes unmatched or ambiguous choices. With `"isolated"`, it counts executions only for that exact source/run/observation/action-description/target-widget binding and labels the count `recorded_binding`. Those local counts establish no cross-observation match. Zero under this policy allows a local unvisited selection but contributes no navigation target.

Random ASM can select unmatched choices; their counts remain null with no supporting references. Counts explain evidence but do not affect random selection. [Abstraction Specs](https://github.com/ferpasri/testar-abstraction-specs/blob/main/docs/terminology.md#model-links-and-support) owns matching and supporting-reference definitions.

## Evidence updates

An update contains an `update_id` unique within the ASM run, reconstructed `sources`, and `selected_runs`. A snapshot is the reader's current collection of reconstructed records for one evidence source. Each supplied source is a full snapshot for that source; omitted sources remain accepted. Selected runs are the complete active selection scope and retain the previously selected runs.

A new source extends knowledge. An existing source can add observations, descriptions, executions, and sequences, and advance execution or run lifecycle records. It retains immutable observation content, description content, and previously recorded execution arguments. An existing result or resulting observation cannot be rewritten. Final execution statuses remain final. Evidence libraries validate these lifecycle changes before the ASM accepts them.

Identical source-qualified records count once. A repeated update identifier with equivalent content is a retry. Changed content under the same update identifier is `conflicting_update`. Changed immutable records, removed accepted records within a supplied snapshot, or lifecycle regressions are `conflicting_evidence`. Record collection order and object-property order do not make an equivalent update different; ordered values inside records keep their meaning.

Accepted changes advance `knowledge_revision` by one per update. An identical retry or a fresh update containing already accepted content leaves the revision and counts unchanged. Updating display metadata or a source fingerprint is also an accepted change when the source snapshot remains valid.

A new latest observation invalidates a context referring to an older observation. A terminal execution report also retires its context: after an execution error, a caller should reassess the application before trying another action. Merely updating unrelated historical knowledge keeps the current context available, but selections must be recomputed at the new revision.

`report_execution` requires the reserved execution to refer to the selected source observation, action description, target widget, and run. Actual execution parameters remain evidence supplied by the integration. The report can jump directly to a completed record when the adapter already captured the result, or provide successive pending and terminal snapshots. Repeated accepted reports do not add another execution.

## Errors and atomicity

| Code | Meaning |
| --- | --- |
| `invalid_configuration` | Unsupported ASM/options or unsuitable abstraction configuration. |
| `invalid_evidence` | Input records, source identities, selected runs, or references fail validation. |
| `conflicting_evidence` | An update rewrites or removes accepted facts or regresses lifecycle. |
| `conflicting_update` | An accepted update identifier is reused with a different payload. |
| `invalid_context` | Unknown observation, inactive or older observation, duplicate choice identifier, or unreported binding. |
| `context_conflict` | A context identifier is reused with changed content. |
| `stale_context` | A retired context identifier is supplied again. |
| `stale_selection` | The selection's context or revision has been superseded or consumed. |
| `invalid_selection` | The choice was not the selected current option. |
| `execution_in_progress` | An operation requires the outstanding reservation to finish first. |
| `unknown_execution` | A report does not identify an execution reserved by this run. |
| `execution_reference_reused` | Beginning an execution would reuse an accepted or previously reserved identity. |
| `execution_mismatch` | A reported execution does not belong to its selected observation and binding. |
| `execution_already_recorded` | A never-invoked report conflicts with an accepted execution record. |
| `cancelled` | Beginning an execution after cancellation was requested. |
| `processing_limit` | Abstraction or evidence processing exceeds supported limits. |

Errors include a nonempty message and leave stored history and model, revision, context, reservation, and update identities unchanged. Calls are serialized within one run. Implementations can return native exceptions for errors; conformance runners compare their codes.
