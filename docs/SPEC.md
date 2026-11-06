# Exploration and integration specification

The ASM library controls exploration and decides which action to execute next. Its exploration driver observes the application, discovers available actions, and executes the selection. Existing evidence traces can provide prior execution evidence, and new executions produce additional evidence.

## Responsibilities

| Component | Responsibility |
| --- | --- |
| ASM library | Control the exploration cycle, maintain the model and state-model data through the abstraction library, select actions, switch ASMs, and apply exploration limits. |
| Abstraction library | Apply abstraction rules and retain references to supporting evidence. |
| Exploration driver | Provide application observation, action discovery and filtering, readiness checks, and action execution. Record evidence through the corresponding evidence adapter and library. |
| Customer application | Configure setup, input generation, abstraction, allowed interactions, oracles, and stopping conditions. |

Native ASM libraries use their corresponding evidence and abstraction libraries in the customer's process. The customer starts exploration with the configured exploration driver. For Playwright, that driver discovers browser actions; a script can perform setup and then start exploration without deriving its own action list.

## Existing tools and evidence

An existing testing tool can record traces through an evidence adapter independently of ASM exploration. Those traces can later provide historical evidence to an ASM.

~~~text
Existing testing tool -> evidence adapter/library -> evidence traces
Customer starts exploration -> ASM library -> exploration driver -> application
~~~

The ASM library requests the technology operations needed for its exploration cycle. The exploration driver performs those operations and reports their results; evidence-producing tools do not need to send live action lists to the ASM.

## Exploration cycle

1. The ASM library requests a current observation and available actions from its exploration driver.
2. The driver applies readiness checks, captures the state, discovers actions, and returns the eligible choices.
3. The ASM selects an action using the current state-model data and abstraction.
4. The ASM library requests execution; the driver checks applicability and invokes the operation.
5. The driver records the execution result and resulting observation through the evidence adapter. The ASM library receives the new evidence, updates its model, and decides whether to continue, switch ASM, or stop.

Oracle evaluations follow the configured testing flow and are reported separately from execution outcomes. The driver coordinates capture boundaries with its evidence adapter; recording available actions or oracle results does not automatically require another capture.

The [execution modes](../README.md#execution-modes) support an empty starting model or historical traces. New executions produce new evidence; historical traces and recorded observations remain unchanged.

## Rules shared by implementations

- Use the same abstraction for historical evidence and current observations throughout an ASM run.
- Select only an action currently offered by the driver. Historical actions guide navigation but cannot supply executable objects.
- Preserve source-qualified references, execution outcomes, capture limitations, and reasons that matching is unclear.
- Refresh a selection when its observation, offered choices, or ASM data revision changes.
- Keep browser readiness, target resolution, and execution in the driver.

[Exploration control](exploration-controller.md) defines how ASMs choose actions and switch. The [contract](contract.md) defines operations, counting, evidence updates, and errors. [Shared cases](../conformance/README.md) verify these rules; [release checks](versioning.md) explain compatibility declarations.
