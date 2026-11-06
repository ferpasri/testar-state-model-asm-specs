# TODO

## Shared contract and cases

- [x] Define current observations, available choices, selections, action execution contexts, reports, cancellation, and errors.
- [x] Document matching execution records, status counts, and ambiguous or unmatched comparisons.
- [x] Define source-qualified update identities, retry handling, immutable records, and selection invalidation.
- [x] Add language-independent schemas and shared cases with expected public results.
- [x] Record shared compatibility identifiers and the release/conformance process.
- [x] Validate fixture structure and expected count/reference consistency in CI.
- [x] Review the abstraction cases for native-language interpretation; remaining portability decisions are tracked in Abstraction Specs.
- [x] Verify the ASM scenarios against the first native implementations before those libraries declare compatibility.
- [ ] Extend cases for additional source/run lifecycle and selection-scope boundaries, processing limits, and complete update conflict combinations.

## ASMs and exploration control

- [x] Document the main ASM terms in the [terminology table](docs/terminology.md).
- [x] Reference Evidence and Abstraction terminology instead of duplicating their recorded-data and model definitions.
- [x] Align schemas and cases with the Unvisited ASM, including local priority, directed navigation, exhaustion, and current eligible choices.
- [x] Document the [controller architecture](docs/exploration-controller.md), ASMs, action count limits, and switching conditions.
- [x] Define ordered ASM configuration, per-entry and overall action limits, bounded switching, and execution coordination.
- [x] Describe the Unvisited ASM with navigation, the Random ASM, and the Discovery around known paths ASM.
- [x] Define random local choices, target ties, equivalent shortest routes, and stable reference ordering.
- [ ] Define how discovery around known paths chooses destinations and local actions according to the exploration objective; avoid using low execution counts alone as a measure of interest.
- [x] Add shared cases for nearest states, distinct unvisited actions, random ties, and random selection independent of counts.
- [ ] Extend the controller with objective-specific progress measures, loop detection, and route retry controls.
- [x] Define an injectable random-index provider and shared test transcripts for equivalent decisions across languages.
- [x] Add cases for action-count switching, exhaustion switching, unexpected route outcomes, and a finite unsuccessful controller cycle.
- [ ] Add cases for dynamic action growth and future progress/retry controls.

## Native Java and Python libraries

- [x] Implement the shared operations using the corresponding abstraction and evidence libraries.
- [x] Provide an exploration entry point controlling the observe/discover/select/execute/update cycle through technology capabilities, verified by native cycle tests.
- [ ] Add shared cases for the complete exploration entry point.
- [x] Connect accepted current observations and historical sources through the native abstraction APIs.
- [x] Retain one accepted state-model data store; avoid unnecessary copies of complete models between components.
- [x] Validate snapshot extensions through the evidence library and preserve original input traces.
- [x] Download published ASM cases and run the same scenarios in both language libraries.
- [x] Verify equivalent decision explanations and unvisited ASM behavior.
- [x] Package ordinary Java and Python dependencies and reproducible installations.
- [ ] Measure selection and update overhead before choosing incremental model optimizations.

## Exploration drivers

- [ ] Define and document default abstraction rules for each technology and behavior when captured properties are missing.
- [ ] Implement Playwright observation, action discovery, filtering, and execution capabilities using the existing evidence adapters; connect them to the ASM-controlled exploration entry point.
- [ ] Coordinate capture readiness, discovered bindings, buffered observations, and unavailable-target refresh.
- [ ] Demonstrate default exploration, custom abstraction, and exploration with historical evidence.
- [ ] Test setup/login, action exclusions, input generation, oracle reporting, limits, and stopping.
- [ ] Verify valid new evidence and unchanged historical traces after exploration.

## Later work

- [ ] Add ASMs for other exploration objectives with their own shared behavior and cases.
- [ ] Evaluate model checkpoints and incremental updates after the first end-to-end integrations.
- [ ] Add further native languages and exploration drivers as needed.
