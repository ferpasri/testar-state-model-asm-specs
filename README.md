# TESTAR ASM specification

Shared specification for state-model-based exploration and action selection. ASM libraries control exploration using an abstract model. Exploration drivers observe the application, discover actions, and execute selections. New executions produce concrete evidence for further exploration and inspection.

This repository defines terminology, integration behavior, and shared conformance cases. Language libraries implement that behavior. Exploration drivers connect those libraries to the application under test.

## Execution modes

| Mode | Starting model | Abstraction | During exploration |
| --- | --- | --- | --- |
| Default exploration | Empty | Default rules supplied with the implementation | Build state-model data and record new evidence. |
| Configured exploration | Empty | Rules supplied by the user | Build state-model data under those rules and record new evidence. |
| Exploration with historical evidence | Constructed from supplied traces | Rules supplied by the user | Use the initial state-model data, extend it with new executions, and record new evidence. |

An initially empty model acquires its first observation before the first selection. Historical evidence remains unchanged. Different abstraction rules can later produce a different model from the same traces.

## Architecture

Each ASM library coordinates exploration in the customer's language and process, using its corresponding abstraction library. A exploration driver supplies application operations and records new evidence through an evidence adapter. Existing tools can independently produce traces used as historical input; starting ASM exploration does not require an existing exploratory testing tool.

## Shared behavior and maintenance

Implementations verify shared behavior against published conformance cases. Supported contracts and case releases belong in machine-readable compatibility metadata; [release checks](docs/versioning.md) describe the process.

- [ASM terminology](docs/terminology.md)
- [Exploration and integration specification](docs/SPEC.md)
- [Selection and evidence-update contract](docs/contract.md)
- [ASMs and exploration control](docs/exploration-controller.md)
- [Shared conformance cases](conformance/README.md)
- [Compatibility and releases](docs/versioning.md)
- [Implementation decisions and work](TODO.md)

Evidence terminology follows [TESTAR Evidence](https://github.com/ferpasri/testar-evidence-specs/blob/main/docs/terminology.md). State Model and abstraction terms follow [Abstraction terminology](https://github.com/ferpasri/testar-abstraction-specs/blob/main/docs/terminology.md).
