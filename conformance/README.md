# Shared ASM conformance cases

These cases verify selection, navigation, controller switching, and evidence updates through a library's public API. The [manifest](manifest.json) lists the cases and compatibility identifiers.

## Input and expected result

Each case contains `input.json` and `expected.json`.

| Input field | Meaning |
| --- | --- |
| `configuration` | Explicit abstraction, ordered ASMs with action limits, and optional overall limit. |
| `evidence_sets` | Named reconstructed source snapshots and selected runs. This is fixture shorthand; the library receives the data. |
| `initial_evidence` | The evidence set supplied at startup. |
| `steps` | Ordered operations. An `evidence_set` name identifies data supplied to an update. |

`expected.json` contains the initialization result and one public-result projection per step. Messages must be nonempty but their wording can differ between implementations. Runtime-generated abstract model identifiers are not compared.

A `select` step may contain `random_choices`: ordered `{"size": 2, "index": 1}` pairs. The runner supplies a random provider that checks the requested size, returns the given index, and fails if calls are missing or unexpected. An omitted list means no random calls. This tests selection independently of a language's random generator.

## Runner requirements

1. Start with the supplied configuration and initial evidence; compare initialization.
2. Perform each step and compare its structured response, including the chosen action, active ASM index, counts, references, and any navigation explanation.
3. Compare rankings in choice-identifier order. Supporting count references are unordered; navigation steps and operation order are significant.
4. Verify that caller-owned evidence and configuration remain unchanged.
5. Repeat after reversing source, selected-run, record-collection, and offered-choice order. Preserve semantic order inside records, including widget lists and observation indexes.

Abstraction behavior is verified separately by [Abstraction Specs](https://github.com/ferpasri/testar-abstraction-specs/tree/main/conformance). Native ASM implementations verify these scenarios end to end. Browser readiness, discovery, capture coordination, and physical execution belong to technology integration tests.

## Validate fixture data

From this repository:

~~~powershell
python -m pip install -r requirements-dev.txt
python tools/check_conformance.py
~~~

This check validates schemas, the case inventory, evidence references, expected counts, navigation support, and random-choice transcripts. It does not substitute for running the cases against native ASM implementations.
