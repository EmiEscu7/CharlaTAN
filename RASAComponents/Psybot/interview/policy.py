import json
import os
from typing import Any, List, Dict, Text, Optional

import requests
from rasa.core.featurizers.tracker_featurizers import TrackerFeaturizer
from rasa.core.policies import Policy
from rasa.core.policies.policy import PolicyPrediction, confidence_scores_for
from rasa.shared.core.domain import Domain
from rasa.shared.core.events import SlotSet
from rasa.shared.core.generator import TrackerWithCachedStates
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.nlu.interpreter import NaturalLanguageInterpreter

from RASAComponents.Psybot.interview.elements import Question, Interview
from RASAComponents.Psybot.interview import question_analysis




def _load_questions(path: str) -> List[Question]:
    """Loads questions from a json file.

    Author: Bruno.

    Parameters
    ----------
    path
        Path where questions are stored.

    Returns
    -------
    List of parsed questions.
    """
    questions = []
    with open(path) as file:
        for raw_question in json.load(file):
            questions.append(Question(raw_question["id"],
                                      raw_question["text"],
                                      raw_question["in_starting_set"],
                                      raw_question["valid_answers"]
                                      ))

    return questions


def normalize(not_normalized: Dict[str, int]) -> Dict[str, float]:
    min_value = min(not_normalized.values())
    max_value = max(not_normalized.values())

    return {dim: round((value - min_value) / (max_value - min_value), 2)
            for dim, value in not_normalized.items()}


def _save_interview(
        result: Dict[str, str], interview: Interview, interviewee: str = "user"
):
    """Saves questions responses and generated profile into a json file.

    Author: Bruno.

    Parameters
    ----------
    result
        Questions responses.
    interview
        Finished interview.
    interviewee
        Name of the interviewee.
    """
    path = r"RASAComponents/Psybot/interview/results"
    with open(path + fr"\{interviewee}.json", 'w') as file:
        json.dump(result, file)

    normalized_profile = normalize(interview.interviewee_profile)
    print(f"Result for {interviewee}:", normalized_profile)

    url = "http://localhost:5000/learningstyle"

    requests.post(url, data={"id": interviewee,
                             "learning_style": normalized_profile})


class InterviewPolicy(Policy):
    """Custom rasa policy that handles conversation flow when an interview is
    being made.

    Author: Bruno.
    """

    def __init__(
            self,
            featurizer: Optional[TrackerFeaturizer] = None,
            priority: int = 2,
            should_finetune: bool = False,
            **kwargs: Any
    ) -> None:
        super().__init__(featurizer, priority, should_finetune, **kwargs)

        self._interview = Interview(_load_questions("RASAComponents/Psybot/interview/questions.json"))

        self._functions = question_analysis.get_all_functions()
        self._interview_result = {}

    @property
    def interview(self):
        return self._interview

    @interview.setter
    def interview(self, interview: Interview):
        self._interview = interview

    def train(
            self,
            training_trackers: List[TrackerWithCachedStates],
            domain: Domain,
            interpreter: NaturalLanguageInterpreter,
            **kwargs: Any
    ) -> None:
        pass

    def _ask_next_question(
            self,
            tracker: DialogueStateTracker,
            domain: Domain,
            prefix: str = ""
    ) -> "PolicyPrediction":
        """Updates slot that stores the next question to ask, so the action
        'action_ask_question' dispatches it to the interviewee.

        Author: Bruno.

        Parameters
        ----------
        tracker
            Rasa tracker.
        domain
            Rasa domain.
        prefix
            Text to put before the question to ask.
        """
        tracker.update(SlotSet("question_to_ask",
                               prefix + self._interview.next_question()))

        return self._prediction(confidence_scores_for(
            "action_ask_question", 1.0, domain)
        )

    def process_answer(self, text, intent_name):
        """Saves the received answer and executes all functions that are needed
        to analyze it.

        Author: Bruno.

        Parameters
        ----------
        text
            Received answer.
        intent_name
            Name of the intent for the received answer.
        """
        self._interview_result[self._interview.last_asked.text] = text

        q: Question = self._interview.last_asked
        if q.has_processing:
            key = q.free_answer_key if q.is_free_answer() else intent_name

            for func_info in q.functions_to_run(key):
                name, args = func_info["func"], func_info["args"]
                if name in self._functions:
                    self._functions[name](self._interview, **args)
                else:
                    raise KeyError("Function '{}' not recognized.".format(name))

    def _user_answered_question(
            self,
            tracker: DialogueStateTracker,
            domain: Domain,
            message: str,
            intent_name: str
    ) -> "PolicyPrediction":
        """Method that handles next action prediction when there is an interview
        in progress.

        Author: Bruno.

        Parameters
        ----------
        tracker
            Rasa tracker.
        domain
            Rasa domain.
        message
            Received answer.
        intent_name
            Name of the intent for the received answer.

        Returns
        -------
        PolicyPrediction
        """
        # If the last answer is valid for the question, then process it
        # and check if there are more questions to add.
        if self._interview.last_asked.valid_answer(intent_name):
            self.process_answer(message, intent_name)

            if not self._interview.no_more_questions():
                return self._ask_next_question(tracker, domain)

            _save_interview(self._interview_result, self._interview,
                            tracker.sender_id)
            self._interview.restart()
            return self._prediction(
                confidence_scores_for("utter_interview_finished", 1.0, domain))

        # If the answer for the last question asked isn't valid, then
        # ask the question again.
        return self._prediction(
            confidence_scores_for("action_ask_again", 1.0, domain))

    def predict_action_probabilities(
            self,
            tracker: DialogueStateTracker,
            domain: Domain,
            interpreter: NaturalLanguageInterpreter,
            **kwargs: Any
    ) -> "PolicyPrediction":
        """Policy that controls part of the conversation flow related to an
        interview.

        Author: Bruno.
        """

        # If the last thing rasa did was listen to user input, then we need to
        # analyze the intent so we can decide the next action to execute.
        if tracker.latest_action_name == "action_listen":
            intent_name = tracker.latest_message.intent["name"]

            # User wants an interview
            if (intent_name == "want_interview"
                    and not self._interview.in_progress):
                # The interview must start.
                self._interview.in_progress = True
                return self._ask_next_question(
                    tracker, domain,
                    prefix="Okay, empecemos con la entrevista.\n"
                )

            if self._interview.in_progress:
                return self._user_answered_question(
                    tracker, domain, tracker.latest_message.text, intent_name
                )

        # If the last thing rasa did was ask a question, then the next thing to
        # do is listen for a new user input.
        if tracker.latest_action_name == "utter_question_template":
            return self._prediction(confidence_scores_for(
                "action_listen", 1.0, domain
            ))

        # If there is no match in the conditions stated above, let the other
        # policies predict.
        return self._prediction(self._default_predictions(domain))

    def _metadata(self) -> Dict[Text, Any]:
        return {
            "priority": 2
        }

    @classmethod
    def _metadata_filename(cls) -> Text:
        return "interview_policy.json"
