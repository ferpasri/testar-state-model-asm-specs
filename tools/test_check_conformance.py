"""Regression checks for errors that would make shared fixtures misleading."""

import unittest
from copy import deepcopy

from check_conformance import ROOT, load_schemas, read, validate_case


class ConformanceValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = load_schemas()

    def case(self, name):
        directory = ROOT / "conformance/cases" / name
        return read(directory / "input.json"), read(directory / "expected.json")

    def assert_invalid(self, name, data, expected, message):
        with self.assertRaisesRegex(ValueError, message):
            validate_case(name, data, expected, self.schemas)

    def test_wrong_status_counts_are_rejected(self):
        name = "all-execution-statuses"
        data, expected = self.case(name)
        ranking = expected["responses"][-1]["rankings"][0]
        ranking["status_counts"]["completed"] += 1
        self.assert_invalid(name, data, expected, "status counts")

    def test_navigation_requires_completed_execution_support(self):
        name = "navigation-nearest-state"
        data, expected = self.case(name)
        history = data["evidence_sets"]["initial"]["sources"][1]
        history["evidence"]["executions"][0]["status"] = "failed"
        ranking = expected["responses"][-1]["rankings"][0]
        ranking["status_counts"]["completed"] = 0
        ranking["status_counts"]["failed"] = 1
        self.assert_invalid(name, data, expected, "completed execution support")

    def test_navigation_distance_matches_route_length(self):
        name = "navigation-nearest-state"
        data, expected = self.case(name)
        expected["responses"][-1]["navigation"]["distance"] += 1
        self.assert_invalid(name, data, expected, "navigation distance")

    def test_navigation_target_must_exist(self):
        name = "navigation-nearest-state"
        data, expected = self.case(name)
        expected["responses"][-1]["navigation"]["target_state"]["observation"] = "missing"
        self.assert_invalid(name, data, expected, "navigation target")

    def test_out_of_range_random_index_is_rejected(self):
        name = "random-current-choices"
        data, expected = self.case(name)
        data["steps"][1]["random_choices"][0]["index"] = 2
        self.assert_invalid(name, data, expected, "random index")

    def test_cached_selection_must_not_draw_again(self):
        name = "random-current-choices"
        data, expected = self.case(name)
        data["steps"][2]["random_choices"] = deepcopy(data["steps"][1]["random_choices"])
        self.assert_invalid(name, data, expected, "cached selection")

    def test_positive_count_is_not_local_unvisited(self):
        name = "unvisited-exhausted"
        data, expected = self.case(name)
        response = expected["responses"][-1]
        response.update({"result_type": "selected", "reason": "local_unvisited_action", "choice_id": "choice-1"})
        self.assert_invalid(name, data, expected, "zero executions")


if __name__ == "__main__":
    unittest.main()
