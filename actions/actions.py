import random
from typing import Text, Dict, Any, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher


"""
    ACTIONS RELATED TO PSYBOT
"""
class AskAgain(Action):
    """Custom action that asks again the last asked question.

    Author: Bruno.
    """
    def name(self) -> Text:
        return "action_ask_again"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        question = tracker.get_slot("question_to_ask")
        dispatcher.utter_message(
            "Todavia estamos en la entrevista. Terminemosla y despues me "
            "preguntas lo que quieras.\n"
            "Te repito la pregunta: {}".format(question))
        return []


class AskQuestion(Action):
    """Custom action that asks a question.

    Author: Bruno.
    """
    def name(self) -> Text:
        return "action_ask_question"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(tracker.get_slot("question_to_ask"))
        return []


class InterviewNotStarted(Action):
    """Custom action that tells the user that the interview has not started yet.

    Author: Bruno.
    """
    def name(self) -> Text:
        return "action_interview_not_starte"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            "No podes responder preguntas si la entrevista no inicio.")
        return [UserUtteranceReverted()]



"""
    ACTIONS RELATED TO WIZZARD PROFESSOR
"""

class ActionSetTimer(Action):
    """Action used to set a flag in 'metadata' field of the json send to the
    user that is talking to the assistant.

    Author: Dana.
    """
    
    def name(self) -> Text:
        return "action_set_timer"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        utter = tracker.get_slot("next_topic")
        msg = {
            "message": random.choice(domain["responses"][utter])['text'],
            "sender": "user",
            "metadata": {
                "timer": tracker.get_slot("must_set_timer")
            }
        }

        dispatcher.utter_message(json_message=msg)
        return []