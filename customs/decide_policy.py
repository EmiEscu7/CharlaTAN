
from typing import Optional, Any, Dict, List, Text

from rasa.shared.core.domain import Domain
from rasa.core.featurizers.tracker_featurizers import (
    TrackerFeaturizer,
)
from rasa.shared.nlu.interpreter import NaturalLanguageInterpreter
from rasa.core.policies.policy import Policy, PolicyPrediction, confidence_scores_for
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.core.generator import TrackerWithCachedStates
from rasa.core.constants import MEMOIZATION_POLICY_PRIORITY

# imports others policies
from customs.psybot_interview.policy import InterviewPolicy
from customs.scrum_assistant_tour.policy import AssistantPolicy


# imports propios
from .custom_tracker import CustomTracker


class DecidePolicy(Policy):

    def __init__(
            self,
            featurizer: Optional[TrackerFeaturizer] = None,
            priority: int = MEMOIZATION_POLICY_PRIORITY,
            answered: Optional[bool] = None,
            **kwargs: Any,
    ) -> None:
        super().__init__(featurizer, priority, **kwargs)
        self.answered = False
        self.differents_policies = {
            "psybot": InterviewPolicy(),
            "scrum_assistant": AssistantPolicy()
        }
        self.scrum_assistant = False

    def train(
            self,
            training_trackers: List[TrackerWithCachedStates],
            domain: Domain,
            interpreter: NaturalLanguageInterpreter,
            **kwargs: Any,
    ) -> None:
        """Trains the policy on given training trackers.
        Args:
            training_trackers:
                the list of the :class:`rasa.core.trackers.DialogueStateTracker`
            domain: the :class:`rasa.shared.core.domain.Domain`
            interpreter: Interpreter which can be used by the polices for featurization.
        """
        pass

    def predict_action_probabilities(
            self,
            tracker: DialogueStateTracker,
            domain: Domain,
            interpreter: NaturalLanguageInterpreter,
            **kwargs: Any,
    ) -> PolicyPrediction:

        if not self.answered:

            # get id to the person that sent the message
            sender_id = tracker.current_state()['sender_id']

            # get a updated custom tracker to the conversation
            custom_tracker = self.obtener_tracker(sender_id, tracker)

            intents = tracker._latest_message_data()["intent_ranking"]

            # get type of bot
            type = custom_tracker.get_latest_event().metadata["type"]

            print("ESTOS SON LOS INTENTS RECONOZIDOS CON SUS PROB AL INICIO -------->>>>>")
            for intent in intents:
                print(intent["name"] + ":    " + str(intent["confidence"]))

            """
                if intent not is of interest to the bot, him confidence will be 0
            """
            for intent in intents:
                if type not in intent["name"]:
                    intent["confidence"] = 0

            print("ESTOS SON LOS INTENTS RECONOZIDOS CON SUS PROB DSP DEL CALCULO -------->>>>>")
            for intent in intents:
                print(intent["name"] + ":    " + str(intent["confidence"]))

            final_intent = ""
            max_value = 0

            """
                get the intent that have max value of confidence
            """
            for intent in intents:
                if intent["confidence"] > max_value:
                    max_value = intent["confidence"]
                    final_intent = intent["name"]

            tracker.latest_message.intent["name"] = final_intent
            tracker.latest_message.intent["confidence"] = max_value

            #result = confidence_scores_for(final_intent, 1.0, domain)
            if "scrum_assistant" == type:
                self.scrum_assistant = True
            self.answered = True
            print("EL INTENT SELECCIONADO ES ---->>>> " + str(final_intent))
            return self.differents_policies[str(type)].predict_action_probabilities(tracker, domain, interpreter)
        else:
            if self.scrum_assistant:
                return self.differents_policies["scrum_assistant"].predict_action_probabilities(tracker, domain, interpreter)
            else:
                self.answered = False
                return self._prediction(confidence_scores_for('action_listen', 1.0, domain))



    def _metadata(self) -> Dict[Text, Any]:
        return {
            "priority": self.priority,
        }

    @classmethod
    def _metadata_filename(cls) -> Text:
        return "developer_policy.json"

    def obtener_tracker(self, sender_id, tracker: DialogueStateTracker):

        """
            Este metodo dado un "sender id" obtiene un custom tracker para esa conversacion. Si esta conversacion ya existia, devuelve el tracker obtenido a partir del context manager, en caso contrario (no habia una conversacion previa con esa persona),se genera un nuevo.
            Independientemente de lo anterior, se utiliza "tracker" original de la conversacion (no el custom) para actualizar los campos del custom tracker

            Retorna: Un custom tracker actualizado.

        """

        # Si ya habia una conversacion con la persona que tiene ese id, busco el tracker
        """
        if (self.context_manager.exist_sender(sender_id)):
            custom_tracker = self.context_manager.get_tracker(sender_id)

        # Si no, genero un custom tracker para esa persona
        else:
        """
        custom_tracker = CustomTracker(
            tracker.sender_id,
            tracker.slots.values(),
            tracker._max_event_history,
            tracker.sender_source,
            tracker.is_rule_tracker
        )
        custom_tracker.update_tracker(tracker)
        return custom_tracker
