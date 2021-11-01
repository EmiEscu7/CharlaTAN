import unittest

from RASAComponents.Psybot.interview.policy import normalize


class TestNormalize(unittest.TestCase):
    def test_normalization_min_is_zero(self):
        not_normalized = {"A": 5, "C": 3, "D": 0, "B": 11}
        normalized = {"A": round(5/11, 2), "C": round(3/11, 2),
                      "D": round(0/11, 2), "B": round(11/11, 2)}

        self.assertEqual(normalize(not_normalized), normalized)

    def test_normalization_min_is_not_zero(self):
        not_normalized = {"A": 5, "C": 3, "D": 2, "B": 11}
        normalized = {"A": round((5-2)/(11-2), 2),
                      "C": round((3-2)/(11-2), 2),
                      "D": round((2-2)/(11-2), 2),
                      "B": round((11-2)/(11-2), 2)}

        self.assertEqual(normalize(not_normalized), normalized)
