from typing import List, Dict, Any


class Question:
    """Class with data and behaviour related to a interview question.

    Author
    ------
    Bruno.
    """
    def __init__(
            self,
            q_id: int,
            text: str,
            in_starting_set: bool,
            valid_answers: Dict[str, List[Dict[str, Any]]]
    ):
        """
        Constructor.

        Parameters
        ----------
        q_id: id of the question.
        text: question to ask.
        in_starting_set: determines if the question must be asked in every
        interview or not.
        valid_answers: valid intents as answers, and corresponding functions
        names to execute, with required arguments.
        """
        self._id = q_id
        self._text = text
        self._in_starting_set = in_starting_set
        self._valid_answers = valid_answers

        self.answered = False

    def __str__(self) -> str:
        return ("id={}, text={}, in_starting_set={}"
                .format(self.id, self._text, self._in_starting_set))

    @property
    def id(self) -> int:
        return self._id

    @property
    def text(self) -> str:
        return self._text

    @property
    def in_starting_set(self) -> bool:
        return self._in_starting_set

    @property
    def has_processing(self):
        return len(self._valid_answers) > 0

    @property
    def free_answer_key(self):
        return "all"

    def is_free_answer(self):
        """
        A question can receive any answer if valid_answers attribute is empty,
        or if the first key stored in it is "all".

        Returns
        -------
        True if the question can receive any answer, False otherwise.
        """
        if len(self._valid_answers) == 0:
            return True

        return next(iter(self._valid_answers.keys())) == self.free_answer_key

    def valid_answer(self, intent_name: str):
        return (self.is_free_answer()
                or intent_name in self._valid_answers.keys())

    def functions_to_run(self, key: str):
        return self._valid_answers[key]


class Interview:
    """
    Class with functionality related to interviews.

    Author
    ------
    Bruno.
    """

    def __init__(self, questions: List[Question]):
        self._to_ask: List[Question] = []
        self._question_info: Dict[str, Question] = {}

        # The order is reversed so the first received question is the first
        # asked.
        for q in reversed(questions):
            if q.in_starting_set:
                self._to_ask.append(q)
            self._question_info[q.id] = q

        self._interviewee_profile: Dict[str, int] = {}
        self._last_asked = None
        self.in_progress = False

    def __len__(self) -> int:
        return len(self._to_ask)

    @property
    def last_asked(self):
        return self._last_asked

    @property
    def interviewee_profile(self):
        return self._interviewee_profile

    def get_question(self, q_id: int) -> "Question":
        return self._question_info[q_id]

    def restart(self):
        self.in_progress = False
        # Doesn't needs to revert because order was reverted when creating the
        # object.
        for q_id, q in self._question_info.items():
            q.answered = False  # The question is available to be asked again.
            # Fills the queue of questions to ask.
            if q.in_starting_set:
                self._to_ask.append(q)

        self._interviewee_profile.clear()

    def no_more_questions(self):
        return len(self._to_ask) == 0

    def next_question(self) -> str:
        if self.no_more_questions():
            raise ValueError(
                "There are no more questions to ask in this interview."
            )

        # The question is marked so it is not asked again.
        self._last_asked = self._to_ask.pop()
        self._last_asked.answered = True
        return self._last_asked.text

    def queue_question(self, question):
        if not question.answered:
            self._to_ask.append(question)

    def update_profile(self, dimension: str, value: int):
        """
        Updates the profile of the interviewee.

        Parameters
        ----------
        dimension: dimension to update.
        value: value to sum to the existing one.
        """
        if dimension not in self._interviewee_profile:
            self._interviewee_profile[dimension] = value
        else:
            self._interviewee_profile[dimension] += value
