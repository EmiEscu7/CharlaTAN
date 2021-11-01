import abc
from rasa.shared.core.trackers import DialogueStateTracker


class Criterion(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def check(self, tracker: DialogueStateTracker) -> bool:
        raise NotImplementedError

class EqualPenultimateIntent(Criterion):
    """
    Checks if the penultimate event in the tracker is equal to a String
    Author: Tomas
    """
    def __init__(self, compare: str) -> None:
        """
        Constructor.
        Author: Tomas
        Parameters
        ----------
        compare
            String that is going to be compared to the penultimate event in the tracker
        """
        self._compare = compare

    def check(self, tracker: DialogueStateTracker) -> bool:
        """
        Checks if the penultimate event in the tracker is equal to attribute compare set in constructor.
        Author: Tomas
        Parameters
        ----------
        tracker
            Rasa tracker.
        Returns
        -------
        Returns true if the penultimate event is equal to the string set in constructor, else returns false.
        """
        if len(tracker.as_dialogue().events) > 5:
            penultimate_intent = str(tracker.as_dialogue().events[-4])
        else:
            penultimate_intent = None
        if penultimate_intent is not None and penultimate_intent.find(self._compare) != -1:
            return True
        else:
            return False

class EqualIntent(Criterion):

    def __init__(self, compare: str) -> None:
        self._compare = compare

    def check(self, tracker: DialogueStateTracker) -> bool:
        return self._compare == tracker.latest_message.intent['name']


class EqualAction(Criterion):

    def __init__(self, compare: str) -> None:
        self._compare = compare

    def check(self, tracker: DialogueStateTracker) -> bool:
        return self._compare == tracker.latest_action_name


class EqualEntity(Criterion):

    def __init__(self, compare: str) -> None:
        self._compare = compare

    def check(self, tracker: DialogueStateTracker) -> bool:
        entity = next(tracker.get_latest_entity_values("topic"), None)
        if entity is None:
            return self._compare is None

        return self._compare == entity.replace(" ", "_")


class EqualPenultimateEvent(Criterion):

    def __init__(self, compare: str) -> None:
        self._compare = compare

    def check(self, tracker: DialogueStateTracker) -> bool:
        if len(tracker.as_dialogue().events) > 5:
            penultimate_intent = str(tracker.as_dialogue().events[-4])
        else:
            penultimate_intent = None
        if (penultimate_intent is not None
                and penultimate_intent.find(self._compare) != -1):
            return True
        else:
            return False


class AndCriterion(Criterion):

    def __init__(self, criterion1: Criterion, criterion2: Criterion) -> None:
        self._criterion1 = criterion1
        self._criterion2 = criterion2

    def check(self, tracker: DialogueStateTracker) -> bool:
        return (self._criterion1.check(tracker)
                and self._criterion2.check(tracker))


class NotCriterion(Criterion):

    def __init__(self, criterion1: Criterion) -> None:
        self._criterion1 = criterion1

    def check(self, tracker: DialogueStateTracker) -> bool:
        return not self._criterion1.check(tracker)


class OrCriterion(Criterion):

    def __init__(self, criterion1: Criterion, criterion2: Criterion) -> None:
        self._criterion1 = criterion1
        self._criterion2 = criterion2

    def check(self, tracker: DialogueStateTracker) -> bool:
        return (self._criterion1.check(tracker)
                or self._criterion2.check(tracker))
