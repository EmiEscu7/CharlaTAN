from typing import List, Dict, Any, Deque

from rasa.shared.core import events
from rasa.shared.core.events import Event
from rasa.shared.core.generator import TrackerWithCachedStates

from .conversation import abstract_flow


def count_intents_from_story(
        tracker_events: Deque[Event],
        domain_intents: List[str]
) -> Dict[str, int]:
    """This function counts the amount of intents in a story.

    Author: Bruno.

    Parameters
    ----------
    tracker_events
        Existing events in the tracker that contains the story.
    domain_intents
        List of intents that exists in the domain.

    Returns
    -------
    A dict {k: v}, where k is an intent name, and v is the number of
    occurrences.
    """
    intents_count = dict.fromkeys(domain_intents, 0)
    for event in tracker_events:
        if isinstance(event, events.UserUttered):
            intent_name = event.as_dict()["parse_data"]["intent"]["name"]
            intents_count[intent_name] += 1
    return intents_count


def validate_level_name(
        dimension: "Dimension",
        dimension_level: str,
        custom_message: str = ""
) -> bool:
    """Checks if the dimension level exists in the given dimension.

    Author: Bruno.

    Parameters
    ----------
    dimension
        Dimension that has to contain the received dimension level.
    dimension_level
        Dimension level name.
    custom_message
        Custom text to add to the message displayed in case the check fails.

    Returns
    -------
    True.

    Raises
    ------
    KeyError if the dimension doesn't contains a dimension level with the given
    name.
    """
    if len(custom_message) != 0:
        custom_message = " " + custom_message

    # Checks if the level exists in the dimension.
    if not dimension.exist_level(dimension_level):
        raise KeyError(
            "The level '{}'{} is not valid for the dimension '{}'. "
            "Valid levels are '{}'.".format(
                dimension_level, custom_message, dimension,
                str(dimension.levels_names())
            )
        )

    return True


class DimensionLevel:
    """Class that represents a particular level of a dimension.

    Author: Bruno.
    """

    @staticmethod
    def from_dict(
            raw_dimension_level: Dict[str, Any],
            iterators: Dict[str, abstract_flow.ConversationFlow]
    ) -> "DimensionLevel":
        """Transform a dict into a DimensionLevel object.

        Author: Bruno.

        Parameters
        ----------
        raw_dimension_level
            Dict {k: v}, where k is an attribute name and v is the corresponding
            value.
        iterators
            Dict {k: v} where k is an conversation name, and v is an Iterator
            object.

        Returns
        -------
        DimensionLevel created.
        """
        if "intents_occurrences" in raw_dimension_level.keys():
            intents_occurrences = raw_dimension_level["intents_occurrences"]
        else:
            intents_occurrences = {}

        return DimensionLevel(
            raw_dimension_level["name"],
            iterators[raw_dimension_level["conversation"]],
            intents_occurrences
        )

    def __init__(
            self,
            name: str,
            it: abstract_flow.ConversationFlow,
            intents_occurrences: Dict[str, int] = None
    ):
        """Constructor.

        Author: Bruno.

        Parameters
        ----------
        name
            Name of the dimension level.
        it
            Iterator to use when the level is being used.
        intents_occurrences
            Dict {k: v} where k is an intent name and v is the number of
            occurrences.
        """
        self._name = name
        if intents_occurrences is None:
            self._intents_occurrences = {}
        else:
            self._intents_occurrences = intents_occurrences

        self._iterator = it

    def __repr__(self) -> str:
        return "DimensionLevel(name={}, intents={})".format(
            self.name, str(self._intents_occurrences))

    def __eq__(self, o: object) -> bool:
        """Checks if two DimensionLevel are equals.

        Author: Bruno.

        Parameters
        ----------
        o
            Other DimensionLevel.
        Returns
        -------
        True if names are equal, False otherwise.
        """
        return self.name == o.name

    def as_dict(self) -> Dict[str, Any]:
        """Transforms a DimensionLevel object into a dict.

        Author: Bruno.

        Returns
        -------
        Dict {k: v}, where k is an attribute name, and v is the corresponding
        value.
        """
        return {
            "name": self.name,
            "conversation": self._iterator.name,
            "intents_occurrences": self._intents_occurrences
        }

    @property
    def name(self) -> str:
        return self._name

    @property
    def it(self) -> abstract_flow.ConversationFlow:
        return self._iterator

    def get_weight(self, intent: str) -> float:
        """The weight of an intent is its number of occurrences divided by the
        sum of occurrences of all intents.

        Author: Bruno.

        Parameters
        ----------
        intent
            Intent name.

        Returns
        -------
        Weight of the intent.
        """
        return (self._intents_occurrences[intent] /
                sum(self._intents_occurrences.values()))

    def update_intents_occurrences(self, intents_count: Dict[str, int]):
        """Updates the occurrences for the received intents.

        Author: Bruno.

        Parameters
        ----------
        intents_count
            Dict {k: v}, where k is an intent name, and v is the number of
            occurrences.
        """
        for intent, count in intents_count.items():
            if intent not in self._intents_occurrences.keys():
                self._intents_occurrences[intent] = 0
            self._intents_occurrences[intent] += count


class Dimension:
    """Class that represents a dimension of a learning style.

    Author: Bruno.
    """

    @staticmethod
    def from_dict(
            raw_dimension: Dict[str, Any],
            iterators: Dict[str, abstract_flow.ConversationFlow]
    ) -> "Dimension":
        """Transform a dict into a Dimension object.

        Author: Bruno.

        Parameters
        ----------
        raw_dimension
            Dict {k: v}, where k is an attribute name and v is the corresponding
            value.
        iterators
            Dict {k: v} where k is an conversation name, and v is an Iterator
            object.

        Returns
        -------
        Dimension created.
        """
        return Dimension(
            raw_dimension["name"],
            raw_dimension["threshold"],
            [DimensionLevel.from_dict(raw_dimension_level, iterators)
             for raw_dimension_level in raw_dimension["levels"]]
        )

    def __init__(
            self, name: str, threshold: float, levels: List["DimensionLevel"]
    ):
        """Constructor.

        Author: Bruno.

        Parameters
        ----------
        name
            Name of the dimension level.
        threshold
            Number that defines when the conversation must be switched.
        levels
            Levels of the dimension.
        """
        self._name = name
        self._threshold = threshold

        self._levels = {level.name: level for level in levels}

    def __repr__(self) -> str:
        return "Dimension(name={}, levels={})".format(
            self.name, repr([level for level in self._levels.values()]))

    # noinspection PyUnresolvedReferences
    def __eq__(self, o: object) -> bool:
        """Checks if two Dimension are equals.

        Author: Bruno.

        Parameters
        ----------
        o
            Other Dimension.
        Returns
        -------
        True if names, thresholds and levels are equal, False otherwise.
        """
        return (self.name == o.name
                and self.threshold == o.threshold
                and self.levels_names() == o.levels_names())

    def as_dict(self) -> Dict[str, Any]:
        """Transforms a Dimension object into a dict.

        Author: Bruno.

        Returns
        -------
        Dict {k: v}, where k is an attribute name, and v is the corresponding
        value.
        """
        return {
            "name": self.name,
            "threshold": self.threshold,
            "levels": [level.as_dict() for level in self._levels.values()]
        }

    @property
    def name(self) -> str:
        return self._name

    @property
    def threshold(self) -> float:
        return self._threshold

    def exist_level(self, level_name: str) -> bool:
        """Checks if a level exists in the dimension.

        Author: Bruno.

        Parameters
        ----------
        level_name
            Name of the level.

        Returns
        -------
        True if the dimension contains a level equal to the received level name.
        """
        return level_name in self._levels.keys()

    def levels_names(self) -> List[str]:
        """Returns the names of all the levels contained.

        Author: Bruno.

        Returns
        -------
        List of levels names.
        """
        return [level_name for level_name in self._levels.keys()]

    def update_level(self, level: str, intents_count: Dict[str, int]):
        """Updates the occurrences for the received intents, for a specific
        level.

        Author: Bruno.

        Parameters
        ----------
        level
            Name of the level to update.
        intents_count
            Dict {k: v}, where k is an intent name, and v is the number of
            occurrences.
        """
        self._levels[level].update_intents_occurrences(intents_count)

    def get_weights(self, intent_name: str) -> Dict[str, float]:
        """Calculates the weight for the received intent, in each possible
        level.

        Author: Bruno.

        Parameters
        ----------
        intent_name
            Intent name.

        Returns
        -------
        A dict {k: v}, where k is a dimension level name, and v is the weight of
        the intent in the given dimension level.
        """
        return {level_name: self._levels[level_name].get_weight(intent_name)
                for level_name in self.levels_names()}

    def get_iterator(self, level_name: str) -> abstract_flow.ConversationFlow:
        """Gets the conversation associated to the level name.

        Author: Bruno.

        Parameters
        ----------
        level_name
            Dimension level name.

        Returns
        -------
        The conversation associated to the received dimension level name.
        """
        return self._levels[level_name].it


class LearningStyleDetector:
    """Class responsible for detecting the user learning style during the tour.

    Author: Bruno.
    """

    def __init__(
            self,
            dimension: "Dimension",
            default_level_name: str
    ):
        """Constructor.

        Author: Bruno.

        Parameters
        ----------
        dimension
            Dimension that is going to be analyzed during the tour.
        default_level_name
            Default dimension level.
        """
        validate_level_name(dimension, default_level_name,
                            "present in the learning style")

        self._values = {level_name: 0. for level_name
                        in dimension.levels_names()}
        self._dimension = dimension
        self._current_level_name = default_level_name

    def current_state(self) -> Dict[str, float]:
        """Returns the current values for each dimension level.

        Author: Bruno.

        Returns
        -------
        A dict {k: v}, where k is a level name, and v is a level value.
        """
        return {level: round(value, 3) for level, value in self._values.items()}

    def dimension_as_dict(self) -> Dict[str, Any]:
        """Transforms the stored dimension into a dict.

        Author: Bruno.

        Returns
        -------
        The dimension as a dict.
        """
        return self._dimension.as_dict()

    def extract_intents_occurrences(
            self,
            domain_intents: List[str],
            training_trackers: List[TrackerWithCachedStates]
    ) -> "Dimension":
        """Process existing stories in the training trackers, to extract the
        number of intents in each story.

        Author: Bruno.

        Parameters
        ----------
        domain_intents
            List of intents that exists in the domain.
        training_trackers
            List of trackers received in the train method of the policy.

        Returns
        -------
        The dimension stored in the object.
        """
        for tracker in training_trackers:
            story_name = tracker.as_dialogue().as_dict()["name"]
            _, dimension_name, dimension_level_name = story_name.split("_")

            if dimension_name == self._dimension.name:
                validate_level_name(self._dimension, dimension_level_name,
                                    "present in the training story")

                intents_count = count_intents_from_story(tracker.events,
                                                         domain_intents)
                self._dimension.update_level(dimension_level_name,
                                             intents_count)
            else:
                raise TypeError(
                    "The dimension '{}' detected in the story name is not the "
                    "dimension '{}' used in the LearningStyleDetector".format(
                        dimension_name, self._dimension.name
                    )
                )

        return self._dimension

    def get_next_iterator(self, intent_name: str) -> abstract_flow.ConversationFlow:
        """Obtains the next conversation to use in the TourPolicy.

        Author: Bruno.

        Parameters
        ----------
        intent_name
            Name of the last intent received.

        Returns
        -------
        The selected conversation.
        """
        # Updates level values.
        weights = self._dimension.get_weights(intent_name)
        for level_name, intent_weight in weights.items():
            self._values[level_name] += intent_weight

        # The new level will be the level with maximum value that surpasses the
        # dimension threshold.
        max_level, max_level_value = None, float("-inf")
        for level_name, level_value in self._values.items():
            if level_value > max_level_value:
                max_level, max_level_value = level_name, level_value

        if max_level is None:
            raise TypeError(
                "Error in 'LearningStyleDetector.get_next_iterator(args)' when "
                "obtaining the next conversation to use."
            )

        if max_level_value > self._dimension.threshold:
            self._current_level_name = max_level
            return self._dimension.get_iterator(max_level)

        return self._dimension.get_iterator(self._current_level_name)
