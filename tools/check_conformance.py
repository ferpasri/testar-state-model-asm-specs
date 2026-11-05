"""Validate shared fixture consistency; native ASM runners verify selection behavior."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reference_key(reference, record_type):
    return reference["source"], reference["run"], reference[record_type]


def evidence_indexes(sources, selected_runs):
    selected = {(item["source"], item["run"]) for item in selected_runs}
    executions = {}
    observations = {}
    for source in sources.values():
        evidence = source["evidence"]
        sequences = {item["id"]: item["test_run"] for item in evidence["sequences"]}
        for observation in evidence["observations"]:
            run = sequences[observation["test_sequence"]]
            if (source["id"], run) in selected:
                observations[(source["id"], run, observation["id"])] = observation
        for record in evidence["executions"]:
            execution = record["execution"]
            run = sequences[execution["test_sequence"]]
            if (source["id"], run) in selected:
                executions[(source["id"], run, execution["id"])] = record
    return observations, executions


def check_rankings(name, response, executions, asm):
    rankings = response.get("rankings", [])
    identifiers = [item["choice_id"] for item in rankings]
    require(identifiers == sorted(set(identifiers)), name + ": rankings must have unique sorted choices")
    for ranking in rankings:
        references = ranking["supporting_executions"]
        keys = [reference_key(item, "execution") for item in references]
        require(len(keys) == len(set(keys)), name + ": duplicate supporting execution")
        require(all(key in executions for key in keys), name + ": missing supporting execution")
        if ranking["recorded_executions"] is None:
            require(ranking["count_scope"] is None and ranking["status_counts"] is None and not references,
                    name + ": unknown counts must retain null scope and statuses")
            require(not ranking["eligible"] or asm["name"] == "random",
                    name + ": unvisited choices require known counts")
        else:
            require(ranking["eligible"] and ranking["count_scope"] is not None,
                    name + ": counted choice needs an eligible counting scope")
            require(ranking["recorded_executions"] == len(references),
                    name + ": inconsistent execution count")
            actual_statuses = {status: 0 for status in ranking["status_counts"]}
            for key in keys:
                actual_statuses[executions[key]["status"]] += 1
            require(ranking["status_counts"] == actual_statuses, name + ": inconsistent status counts")


def check_navigation(name, response, observations, executions):
    navigation = response["navigation"]
    references = navigation["supporting_executions"]
    require(navigation["distance"] == len(references), name + ": inconsistent navigation distance")
    target = reference_key(navigation["target_state"], "observation")
    require(target in observations, name + ": missing navigation target")
    for reference in references:
        key = reference_key(reference, "execution")
        require(key in executions and executions[key]["status"] == "completed",
                name + ": navigation needs completed execution support")
        result = executions[key]["resultingObservation"]
        require(result is not None and (key[0], key[1], result) in observations,
                name + ": navigation needs a resulting observation")


def check_random_choices(name, step, response, selected, cached):
    draws = step.get("random_choices", [])
    for draw in draws:
        require(0 <= draw["index"] < draw["size"], name + ": random index outside requested range")
    if response["result_type"] != "selected":
        require(not draws, name + ": no-action selection must not consume randomness")
        return
    if cached:
        require(not draws, name + ": cached selection must not consume randomness")
        return
    if response["reason"] == "navigate_to_unvisited_actions":
        return
    choices = [ranking for ranking in response["rankings"] if ranking["eligible"]]
    if response["reason"] == "local_unvisited_action":
        choices = [ranking for ranking in choices if ranking["recorded_executions"] == 0]
    if len(choices) > 1:
        require(len(draws) == 1 and draws[0]["size"] == len(choices),
                name + ": wrong random-choice transcript")
        require(choices[draws[0]["index"]]["choice_id"] == selected["choice_id"],
                name + ": random transcript selects another choice")
    else:
        require(not draws, name + ": a single choice needs no random draw")


def validate_case(name, data, expected, schemas):
    schemas["case-input.schema.json"].validate(data)
    schemas["case-expected.schema.json"].validate(expected)
    invalid_configuration = list(schemas["configuration.schema.json"].iter_errors(data["configuration"]))
    initialization = expected["initialization"]
    failed = initialization["result_type"] == "error"
    require(not invalid_configuration or (failed and initialization["code"] == "invalid_configuration"),
            name + ": invalid configuration requires the corresponding initialization error")
    require(data["initial_evidence"] in data["evidence_sets"], name + ": missing initial evidence")
    require(len(data["steps"]) == len(expected["responses"]), name + ": wrong response count")
    require(not failed or not data["steps"], name + ": steps after rejected initialization")
    initial = data["evidence_sets"][data["initial_evidence"]]
    sources = {item["id"]: item for item in initial["sources"]}
    selected_runs = initial["selected_runs"]
    context = None
    cached_selections = {}
    for step, response in zip(data["steps"], expected["responses"]):
        if "evidence_set" in step:
            require(step["evidence_set"] in data["evidence_sets"], name + ": missing update evidence")
        if response["result_type"] in ["evidence_updated", "execution_updated"]:
            update = data["evidence_sets"][step["evidence_set"]]
            sources.update({item["id"]: item for item in update["sources"]})
            selected_runs = update["selected_runs"]
        if response["result_type"] == "context_ready":
            context = step["context"]
        if response["result_type"] not in ["selected", "no_action"]:
            continue
        require(0 <= response["asm_index"] < len(data["configuration"]["asms"]),
                name + ": invalid active ASM index")
        asm = data["configuration"]["asms"][response["asm_index"]]
        observations, executions = evidence_indexes(sources, selected_runs)
        check_rankings(name, response, executions, asm)
        if response["rankings"]:
            require(context is not None and
                    {item["choice_id"] for item in response["rankings"]} ==
                    {item["choice_id"] for item in context["choices"]},
                    name + ": rankings must explain all offered choices")
        selected = None
        cached = False
        if response["result_type"] == "selected":
            require(context is not None and context["context_id"] == response["context_id"],
                    name + ": selected context is not current")
            selected = next((item for item in response["rankings"]
                             if item["choice_id"] == response["choice_id"]), None)
            require(selected is not None and selected["eligible"], name + ": invalid selected ranking")
            if response["reason"] == "local_unvisited_action":
                require(asm["name"] == "unvisited" and selected["recorded_executions"] == 0,
                        name + ": a local unvisited selection must have zero executions")
            if response["reason"] == "random_action":
                require(asm["name"] == "random", name + ": random result requires Random ASM")
            if response["reason"] == "navigate_to_unvisited_actions":
                require(asm["name"] == "unvisited", name + ": navigation requires Unvisited ASM")
                check_navigation(name, response, observations, executions)
            key = (response["context_id"], response["knowledge_revision"], response["asm_index"])
            cached = key in cached_selections
            if cached:
                require(response == cached_selections[key], name + ": repeated selection changed")
            cached_selections[key] = response
        if step["operation"] == "select":
            check_random_choices(name, step, response, selected, cached)


def load_schemas():
    schemas = {}
    for path in (ROOT / "schemas").glob("*.schema.json"):
        schema = read(path)
        Draft202012Validator.check_schema(schema)
        schemas[path.name] = Draft202012Validator(schema)
    return schemas


def main():
    schemas = load_schemas()
    manifest = read(ROOT / "conformance/manifest.json")
    schemas["manifest.schema.json"].validate(manifest)
    total = 0
    for suite in manifest["suites"].values():
        directory = ROOT / "conformance" / suite["directory"]
        require(directory.resolve().is_relative_to((ROOT / "conformance").resolve()), "Unsafe suite path")
        require(len(suite["cases"]) == len(set(suite["cases"])), "Repeated case name")
        expected_paths = set()
        for name in suite["cases"]:
            case = directory / name
            require(case.resolve().is_relative_to(directory.resolve()), "Unsafe case path")
            expected_paths.add(case.resolve())
            data = read(case / "input.json")
            expected = read(case / "expected.json")
            validate_case(name, data, expected, schemas)
            print("VALID", name)
            total += 1
        actual = {path.resolve() for path in directory.iterdir() if path.is_dir()}
        require(actual == expected_paths, "Unlisted case directory")
    print("Validated", total, "shared ASM cases and", len(schemas), "schemas.")


if __name__ == "__main__":
    main()
