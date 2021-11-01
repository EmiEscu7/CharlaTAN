import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from RASAComponents.ScrumAssistant.tour import event_handling


class ActionDefaultFallback(Action):
    """ Bot doubt custom action

        When the bot doubts on a question, this custom action appears. It publishes the doubt event for the view subscription and prepares the scene to later train the bot.

        Parameters:
        Action -- .

        Author: Martín Visca
    """

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        last_user_input = tracker.latest_message.get('text')
        
        # Publishes the doubt event.
        publisher = event_handling.EventPublisher("log_eventos")
        message = last_user_input
        publisher.publish("BotEnDuda", { "message" : message }) 

        return []


class TopicNotRecognized(Action):

    def name(self) -> Text:
        return "action_topic_not_recognized"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message("No reconozco el tema del que me estas "
                                 "preguntando. Por favor volveme a preguntar")
        return []

