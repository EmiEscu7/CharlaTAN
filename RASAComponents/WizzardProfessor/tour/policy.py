import os
from typing import Any, List, Dict, Text, Optional

from rasa.core.featurizers.tracker_featurizers import TrackerFeaturizer
from rasa.core.policies.policy import (
    PolicyPrediction, confidence_scores_for, Policy
)
from rasa.shared.core.domain import Domain
from rasa.shared.core.generator import TrackerWithCachedStates
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.nlu.interpreter import NaturalLanguageInterpreter

from tour import util
from tour.chain import util as chain_util, node
from tour.learning_styles_detection import Dimension, LearningStyleDetector


class AssistantPolicy(Policy):
    """Custom policy that predict the next action to execute in the tour.

    Author: Bruno.
    """
    DEFAULT_DIMENSION_LEVEL = "neutral"

    @staticmethod
    def _valid_for_training(tracker: TrackerWithCachedStates) -> bool:
        """Checks if a tracker can be used as a training tracker.

        Author: Bruno.

        Parameters
        ----------
        tracker
            Tracker to validate.

        Returns
        -------
        True if the tracker can be used in training, False otherwise.
        """
        story_name = tracker.as_dialogue().as_dict()["name"]
        return (
                not hasattr(tracker, "is_augmented")  # Only original stories.
                or not tracker.is_augmented  # Only original stories.
                # Only stories usable in training.
                and story_name.startswith("train")
                # The story name format is train_<dimension>_<level>
                and story_name.count("_") == 2
        )

    def __init__(
            self,
            raw_dimension: Dict[str, Any] = None,
            featurizer: Optional[TrackerFeaturizer] = None,
            priority: int = 2,
            should_finetune: bool = False,
            **kwargs: Any
    ) -> None:
        """Constructor.

        Author: Bruno.
        """
        super().__init__(featurizer, priority, should_finetune, **kwargs)

        # Iterator.
        conversation_flows = util.create_conversation_flows(
            "info" + os.path.sep + "flow.json")
        self._current_flow = conversation_flows[
            AssistantPolicy.DEFAULT_DIMENSION_LEVEL]

        # Chain of responsibility. TODO Create from script.
        self._last_node = node.DefaultNode(criterion=None)
        # Flag used to know if the utters were set in _last_node.
        self._first_prediction = False
        self._functions = chain_util.chain_builder(self._last_node)

        if raw_dimension is None:
            # raw_dimensions is None if the policy is being instantiated for
            # training. The dimension must be created.
            dimension = util.create_dimension(conversation_flows)
        else:
            # raw_dimension is not None if the policy is being instantiated when
            # starting rasa server. The dimension must be parsed from a json.
            dimension = Dimension.from_dict(raw_dimension, conversation_flows)

        self._ls_detector = LearningStyleDetector(
            dimension, AssistantPolicy.DEFAULT_DIMENSION_LEVEL
        )

    def train(
            self,
            training_trackers: List[TrackerWithCachedStates],
            domain: Domain,
            interpreter: NaturalLanguageInterpreter,
            **kwargs: Any
    ) -> None:
        """Trains the policy. Only specific trackers are selected for the
        training.

        Author: Bruno.
        """
        # Selects only valid trackers.
        training_trackers = [tracker for tracker in training_trackers
                             if self._valid_for_training(tracker)]

        self._ls_detector.extract_intents_occurrences(domain.intents,
                                                      training_trackers)

    def _update_iterator(self, intent_name: str, switch_iterators: bool = True):
        """Switches the current conversation.

        Author: Bruno.

        Parameters
        ----------
        intent_name
            Name of the last detected intent.
        """
        if switch_iterators:
            print("current state:", self._ls_detector.current_state())
            next_iterator = self._ls_detector.get_next_iterator(intent_name)
            if self._current_flow != next_iterator:
                self._current_flow.transfer_state(next_iterator)
                self._current_flow = next_iterator

    def predict_action_probabilities(
            self,
            tracker: DialogueStateTracker,
            domain: Domain,
            interpreter: NaturalLanguageInterpreter,
            **kwargs: Any
    ) -> "PolicyPrediction":
        """Predicts the next action to execute, based on the last action
        executed and the last intent detected. If the detected intent is not
        related to the tour, then this policy won't made a prediction.

        Author: Bruno.
        """
        intent_name = tracker.latest_message.intent["name"]

        # Sets utters for the default node only one time.
        if not self._first_prediction:
            self._last_node.utters = domain.responses.keys()
            self._first_prediction = True

        self._update_iterator(intent_name, switch_iterators=False)

        return self._prediction(confidence_scores_for(
            self._functions.next(self._current_flow, tracker), 1.0, domain)
        )

        # If the last thing rasa did was listen to a user message, we need to
        # send back a response.
        # if tracker.latest_action_name == "action_listen":
        #     self._update_iterator(intent_name, switch_iterators=False)
        #
        #     # The user wants to continue with next explanation.
        #     if intent_name == "affirm":
        #         utter_explanation = self._it.next()
        #         util.move_to_a_location(utter_explanation)
        #         util.move_task(utter_explanation)
        #         if utter_explanation == 'utter_end_tour':
        #             self._it.restart()
        #
        #     # The user didn't understand and needs a re explanation.
        #     elif intent_name == "not_understand" or intent_name == "deny":
        #         utter_explanation = self._it.repeat()
        #
        #     # The user gives an input that the bot doesn't recognize.
        #     elif intent_name == "nlu_fallback":
        #         return self._prediction(confidence_scores_for("action_default_fallback", 1.0, domain))
        #
        #     # The user wants an explanation of a specific topic.
        #     elif self._it.in_tour(intent_name):
        #         action: Action = self._it.get_explanation(intent_name)
        #         utter_explanation = action.name
        #         if action.slot_value is not None:
        #             tracker.update(SlotSet("tema", action.slot_value))
        #
        #     # The user needs an example.
        #     elif intent_name == "need_example":
        #         utter_explanation = self._it.get_example(self._last_topic)
        #
        #     # Intent not related to the tour.
        #     else:
        #         utter_explanation = f"utter_{intent_name}"
        #
        #     self._last_topic = utter_explanation.replace("utter_", "")
        #     tracker.update(SlotSet("next_topic", utter_explanation))
        #     tracker.update(
        #         SlotSet("must_set_timer", must_set_timer(intent_name,
        #                                                  utter_explanation))
        #     )
        #     return self._prediction(confidence_scores_for(
        #         "action_set_timer", 1.0, domain)
        #     )

        # If rasa latest action isn't "action_listen", it means the last thing
        # rasa did was send a response, so now we need to listen again to allow
        # the user to talk to us again.
        # return self._prediction(confidence_scores_for(
        #     "action_listen", 1.0, domain)
        # )

    def _metadata(self) -> Dict[Text, Any]:
        """Information of the policy generated in the training.

        Author: Bruno.

        Returns
        -------
        Information of the policy generated in the training, as a dict.
        """
        return {
            "priority": 2,
            "raw_dimension": self._ls_detector.dimension_as_dict()
        }

    @classmethod
    def _metadata_filename(cls) -> Text:
        return "assistant_policy.json"
