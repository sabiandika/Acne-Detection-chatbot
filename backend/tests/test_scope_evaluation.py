import json
import unittest
from pathlib import Path

from services.scope_filter import classify_intent


class ScopeEvaluationTests(unittest.TestCase):
    def test_scope_dataset(self):
        path = Path(__file__).parent / "evaluation" / "chatbot_cases.json"
        with path.open(encoding="utf-8") as dataset:
            cases = json.load(dataset)
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(classify_intent(case["message"]), case["expected_intent"])


if __name__ == "__main__":
    unittest.main()
