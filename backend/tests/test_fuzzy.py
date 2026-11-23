import unittest

from fuzzy.inference import analyze, recommend
from fuzzy.membership_functions import iritasi


class FuzzyTests(unittest.TestCase):
    def test_membership_functions_keep_existing_parameters(self):
        self.assertAlmostEqual(float(iritasi["tinggi"].mf[-1]), 1.0)
        self.assertAlmostEqual(float(iritasi["rendah"].mf[0]), 1.0)

    def test_inference_returns_existing_severity_labels(self):
        score, label = analyze(1, 0, 0, 1)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertEqual(label, "ringan")
        self.assertEqual(analyze(2, 1, 9, 3)[1], "berat")

    def test_recommendation_selects_dominant_symptom(self):
        dominant, recommendation = recommend(2, 8, 1, 1)
        self.assertEqual(dominant, "jerawat")
        self.assertTrue(recommendation)


if __name__ == "__main__":
    unittest.main()
