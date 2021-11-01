import os
from pathlib import Path
from typing import Any, List, Dict, Text, Optional

from rasa.core.featurizers.tracker_featurizers import TrackerFeaturizer
from rasa.core.policies.policy import (
    PolicyPrediction, confidence_scores_for, Policy
)
from rasa.shared.core.domain import Domain
from rasa.shared.core.events import SlotSet
from rasa.shared.core.generator import TrackerWithCachedStates
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.nlu.interpreter import NaturalLanguageInterpreter

from RASAComponents.ScrumAssistant.tour import util
from RASAComponents.ScrumAssistant.tour.chain import util as chain_util, node
from RASAComponents.ScrumAssistant.tour.learning_styles_detection import Dimension, LearningStyleDetector


class ScrumAssistantPolicy(Policy):
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
        conversation_flows = util.create_conversation_flows(Path("RASAComponents/ScrumAssistant/info/flow.json"))
        self._current_flow = conversation_flows[
            ScrumAssistantPolicy.DEFAULT_DIMENSION_LEVEL]

        # Chain of responsibility. TODO Create from script.
        self._last_node = node.DefaultNode(criterion=None)
        # Flag used to know if the utters were set in _last_node.
        self._first_prediction = False
        self._functions = chain_util.chain_builder(self._last_node)

        # Set to False if the assistant is used outside AgileTalk or if you
        # don't require intervention.
        self._allow_intervention = True

        # Set to False if the assistant is used outside AgileTalk.
        self._set_timer_after_utter = True

        if raw_dimension is None:
            # raw_dimensions is None if the policy is being instantiated for
            # training. The dimension must be created.
            dimension = util.create_dimension(conversation_flows)
        else:
            # raw_dimension is not None if the policy is being instantiated when
            # starting rasa server. The dimension must be parsed from a json.
            dimension = Dimension.from_dict(raw_dimension, conversation_flows)

        self._ls_detector = LearningStyleDetector(
            dimension, ScrumAssistantPolicy.DEFAULT_DIMENSION_LEVEL
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

        # This allows the intervention of an outsider. Remember to set the flag
        # to False if you are using the assistant outside AgileTalk or if you
        # don't require intervention.
        if (self._allow_intervention
                and tracker.latest_action_name == "action_listen"
                and intent_name == "nlu_fallback"):
            return self._prediction(
                confidence_scores_for("action_default_fallback", 1.0, domain)
            )

        action = self._functions.next(self._current_flow, tracker)

        # If the timer must not be set, then predict the given utter with 1.0
        # confidence.
        if not self._set_timer_after_utter:
            return self._prediction(confidence_scores_for(action, 1.0, domain))

        if action == "action_listen":
            return self._prediction(confidence_scores_for("action_listen",
                                                          1.0, domain))

        # Otherwise, predict 'action_set_timer' with 1.0 confidence. This action
        # adds a metadata field to the message, which contains a flag that is
        # used in unity to set a timer after the message is received.
        tracker.update(SlotSet("next_topic", action))
        tracker.update(
            SlotSet("must_set_timer", util.must_set_timer(intent_name, action))
        )
        return self._prediction(confidence_scores_for(
            "action_set_timer", 1.0, domain)
        )

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
        return "scrum_assistant_policy.json"
