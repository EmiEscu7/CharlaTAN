import unittest

from RASAComponents.Psybot.interview.elements import Question, Interview
from RASAComponents.Psybot.interview.question_analysis import (
    queue_question
)


class TestQuestionAnalysis(unittest.TestCase):

    def test_queue_question(self):
        q1 = Question(q_id=1, text="q1", in_starting_set=True, valid_answers={})

        q2 = Question(q_id=2, text="q2", in_starting_set=False,
                      valid_answers={})
        interview = Interview([q1, q2])

        queue_question(interview, question_id=2)
        self.assertEqual(len(interview), 2)
