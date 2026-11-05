# ASMs and exploration control

An **exploration objective** is what the configured exploration aims to discover. It guides the choice of ASMs, abstraction, and execution limits.

## Unvisited ASM

1. Choose randomly among currently eligible actions with zero matching executions.
2. Otherwise, find reachable abstract states with known unvisited abstract actions.
3. Prefer the nearest state: the one requiring the fewest directed transitions.
4. Among equally near states, prefer the most distinct unvisited abstract actions; choose randomly if states still tie.
5. Choose a shortest route to that state, then return a currently offered action matching its first step. Choose randomly among equivalent shortest routes and matching executable choices.

Only completed recorded transitions supply navigation steps. Observation-order links and transitions in the reverse direction do not supply a route. The first step must match a currently eligible action; later steps are checked when reached. Repeated supporting records do not make an abstract action or transition count as several alternatives.

Reassess after each execution. A recorded route describes previous outcomes; it does not guarantee the same outcome now. An unmatched choice can use observation-local counting under the explicit [isolated policy](contract.md#execution-counts), but does not establish a route between abstract states.

## Random ASM

Choose uniformly among all currently eligible executable choices, regardless of execution counts or whether abstraction can match them.

## Switching and stopping

Configuration lists ASMs in the order to try, with an `action_limit` for each entry. The controller starts at the first entry. It switches to the next entry when that limit is reached or the active ASM cannot supply an action; after the last entry it returns to the first.

One invoked tool-level action counts once, including an execution error or a compound action. Pending execution reports and retries count the same invocation once. An operation reported as never invoked does not count. Historical executions do not consume the current run's limits.

Switch only after an outstanding execution is resolved. A new turn using an ASM entry starts its count at zero. If none of the configured ASMs can supply an action, check each entry once and return a no-action result. An optional overall action limit ends further selection.

## Navigation and changing behavior

[Dynamism, multiple observed outcomes, and non-determinism](https://github.com/ferpasri/testar-abstraction-specs/blob/main/docs/terminology.md#changing-application-behavior) are defined in Abstraction Specs. Unexpected outcomes trigger a new route calculation from the newly observed state. They do not by themselves establish application non-determinism.

Action limits allow exploration to switch even when changing content continually produces new abstract states or actions. Further progress measures and route-retry controls are tracked in [TODO](../TODO.md).

## Discovery around known paths ASM

This exploration approach revisits modeled states to discover additional actions and explore their surroundings. Previous traces may record only the actions that were executed, leaving other available actions unknown; revisiting those states allows exploration to discover them. Target selection depends on the exploration objective; limited action information or low execution counts alone do not establish that a state needs more exploration. Its selection policy and shared cases remain in [TODO](../TODO.md).
