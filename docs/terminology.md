# ASM terminology

## ASM and its inputs

An **ASM** is an **action selection mechanism**: it selects the next action to execute. The Unvisited ASM uses a State Model to find unvisited actions and navigate toward them. The Random ASM chooses among eligible actions randomly. The exploration controller can switch between configured ASMs during execution.

Recorded observations, states, available and eligible actions, executions, and their statuses are defined in [Evidence terminology](https://github.com/ferpasri/testar-evidence-specs/blob/main/docs/terminology.md). State Models, abstract states, actions, transitions, and their matching rules are defined in [Abstraction terminology](https://github.com/ferpasri/testar-abstraction-specs/blob/main/docs/terminology.md).

Dynamism, multiple observed outcomes, and non-determinism are defined in [Abstraction terminology](https://github.com/ferpasri/testar-abstraction-specs/blob/main/docs/terminology.md#changing-application-behavior). The ASM decides how to respond during exploration; the [exploration controller](exploration-controller.md#navigation-and-changing-behavior) explains navigation, retries, and switching.

## Main terms

Use these TESTAR terms consistently in implementations and their documentation.

| Term | Meaning |
| --- | --- |
| ASM | Action selection mechanism. |
| Exploration objective | What the configured exploration aims to discover. |
| ASM run | Execution using a configured ASM or combination of ASMs. It can use information from several evidence traces. |
| ASM data revision | In-memory counter for one ASM run. It starts at zero and increases when an accepted update changes the data used for selection. It lets the ASM detect a selection made before that change. |
| Unvisited ASM | First try an unvisited action in the current state. Otherwise, navigate to the nearest modeled state with unvisited actions; prefer more unvisited actions among equally near states, then choose randomly between states that still tie. |
| Random ASM | Choose uniformly among the currently eligible actions. |
| Discovery around known paths ASM | Revisit modeled states and explore their surroundings to discover additional interactions, according to the exploration objective. |
| State-model data | The derived State Model and supporting recorded observations, actions, and executions maintained by an ASM run. |
| Action selector | Code applying an ASM to choose the next eligible action, including navigation when needed. |
| Action execution context | The selected action, its source observation, and invocation information retained to coordinate execution and recognize repeated reports. |
| Exploration controller | Logic inside the ASM library that chooses the active ASM, tracks its action count, and decides when to switch or stop. |
| Exploration driver | Code through which the ASM library observes the application, discovers eligible actions, and executes its selection. It records new evidence through the corresponding evidence adapter and reports the results to the ASM library. |
| Unvisited action | An abstract action with no matching execution record in the data used by the ASM. |
| Navigation | Use known executed transitions to choose currently eligible actions along a route. Check the reached state after each execution. |
| Route | A sequence of known directed transitions used to reach another abstract state. |
| Target state | The abstract state the ASM wants to reach. |
| Target action | The action the ASM wants to execute. It may first need to navigate to that action's source state. |
| Nearest modeled state | A reachable state requiring the fewest directed transitions from the current state. |
| Action count limit | Maximum number of invoked tool-level actions allocated to an ASM or the overall execution. A compound action counts once. |
| Progress | Changes considered useful for the exploration objective, such as discovering an abstract state, action, or transition. |
| Switching condition | A reason to change the active ASM or target, such as an action limit, repeated loops, or route failures. |

The [exploration controller](exploration-controller.md) describes the agreed ASMs. Technical API fields and execution coordination are explained where they are used in the [selection contract](contract.md).
