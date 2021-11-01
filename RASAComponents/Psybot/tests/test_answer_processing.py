import unittest

from RASAComponents.Psybot.interview.policy import InterviewPolicy
from RASAComponents.Psybot.interview.elements import Question, Interview


class TestQuestionAnalysis(unittest.TestCase):

    def test_processing(self):
        q1 = Question(q_id=1, text="q1", in_starting_set=True,
                      valid_answers={"answer_yes": [
                          {"func": "queue_question", "args": {"question_id": 2}}
                      ]})

        q2 = Question(q_id=2, text="q2", in_starting_set=False,
                      valid_answers={})

        policy = InterviewPolicy()
        policy.interview = Interview([q1, q2])

        policy.interview.next_question()
        policy.process_answer(text="testing", intent_name="answer_yes")

        # Only one question expected, because the asked is removed from the
        # interview, and the only one remaining is the new question queued.
        self.assertEqual(len(policy.interview), 1)
