import unittest

from RASAComponents.Psybot.interview.elements import Question


class TestFreeAnswer(unittest.TestCase):

    def test_free_answer_with_all(self):
        q1 = Question(q_id=1, text="q1", in_starting_set=True,
                      valid_answers={"all": [
                          {"func": "queue_question", "args": {"question_id": 2}}
                      ]})

        self.assertEqual(q1.is_free_answer(), True)

    def test_free_answer_with_empty(self):
        q1 = Question(q_id=1, text="q1", in_starting_set=True,
                      valid_answers={})

        self.assertEqual(q1.is_free_answer(), True)
