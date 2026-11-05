# Compatibility and releases

The [conformance manifest](../conformance/manifest.json) identifies the case format, ASM contract, evidence schema, abstraction rule language and behavior, and ASM/controller behavior. A specification release can add explanations and cases while retaining those identifiers.

Language libraries declare the shared releases they verify and their supported identifiers in machine-readable metadata. Their first two package version components follow the TESTAR compatibility family; patch releases can advance independently.

## Prepare shared cases

Language projects download a published GitHub release of this repository, record its tag and archive digest, and verify its manifest before running cases. Case inputs and expected results stay in this repository. A runner translates the operations to the library's public API and compares original references, decisions, structured reasons, and counts.

The corresponding abstraction library separately runs the cases from [Abstraction Specs](https://github.com/ferpasri/testar-abstraction-specs). Evidence readers run the Evidence Specs cases.

## Release checks

1. Validate schemas and all listed case files.
2. Run the ASM cases in each implementation declaring support.
3. Review compatibility identifiers when selection or update semantics change.
4. Commit the reviewed specification and cases, then publish a matching immutable tag.

A publication used to start implementation can precede native conformance verification. Compatibility claims belong to the implementation release after its tests pass.
