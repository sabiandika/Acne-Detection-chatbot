import unittest

from models.schemas import FuzzyInput, validate_chat_request
from pydantic import ValidationError


class ValidationTests(unittest.TestCase):
    def test_chat_request_keeps_compatible_shape(self):
        self.assertEqual(validate_chat_request({"message": " jerawat "}), ({"message": "jerawat"}, None))

    def test_fuzzy_requires_all_values_in_range(self):
        with self.assertRaises(ValidationError):
            FuzzyInput.model_validate({"keminyakan": None, "jerawat": 2, "iritasi": 1, "kekeringan": 1})
        with self.assertRaises(ValidationError):
            FuzzyInput.model_validate({"keminyakan": 11, "jerawat": 2, "iritasi": 1, "kekeringan": 1})


if __name__ == "__main__":
    unittest.main()
