import abc
from typing import Dict, List

from tour.topic.topics import Topic


class ConversationFlow(metaclass=abc.ABCMeta):
    """Abstract class that defines basic behavior required by a tour
    conversation.

    Author: Bruno.
    """

    def __init__(self, flow: List[Topic], name: str = ""):
        """Constructor.

        Author: Bruno.

        Parameters
        ----------
        flow
            Order of topics for the explanation.
        """
        self._name = name
        self._all_topics = {}
        for topic in flow:
            self._all_topics.update(topic.get())

        self._flow = flow
        self._to_explain_stack = [topic for topic in reversed(flow)]
        self._jump: bool = None
        self._current_topic: str = None

    def __eq__(self, other_iterator: object) -> bool:
        """Two iterators are equal if their names are equal.

        Author: Bruno.

        Parameters
        ----------
        other_iterator
            Other conversation.

        Returns
        -------
        True if iterators names are equal, False otherwise.
        """
        return self.name == other_iterator.name

    @property
    def name(self) -> str:
        return self._name

    @property
    def current_topic(self) -> str:
        return self._current_topic

    @current_topic.setter
    def current_topic(self, topic: str):
        self._current_topic = topic

    @property
    def jump(self) -> bool:
        return self._jump

    @jump.setter
    def jump(self, jump: bool):
        self._jump = jump

    @property
    def to_explain_stack(self) -> List[Topic]:
        return self._to_explain_stack.copy()

    @property
    def all_topics(self) -> Dict:
        return self._all_topics.copy()

    @abc.abstractmethod
    def next(self) -> str:
        """Determines next explanation to give. Must be implemented according to
        the way we want to give the tour.

        Author: Bruno.

        Returns
        -------
        Next explanation to give.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def accept(self, visitor) -> str:
        raise NotImplementedError

    def in_tour(self, intent_name: str) -> bool:
        return intent_name in self._all_topics

    def repeat(self) -> str:
        """Repeats the last explained topic. If possible, returns an utter for
        the explanation with one more level of detail.

        Author: Bruno.

        Returns
        -------
        The utter associated with the repetition.
        """
        return self._to_explain_stack[-1].repeat

    def is_older_topic(self, topic: Topic) -> bool:
        return topic not in self._to_explain_stack

    def restart(self):
        """Restarts the conversation.

        Author: Bruno.
        """
        self._to_explain_stack = [topic for topic in reversed(self._flow)]
        for topic in self._to_explain_stack:
            topic.restart()

    def get_last_topic(self) -> Topic:
        # Returns the next topic to the last topic explained(not subtopic)
        i = 1
        while self._to_explain_stack[-i] not in self._flow:
            i += 1
        return self._to_explain_stack[-i]

    def jump_to_topic(self, topic: Topic):
        # Jumps to the specified topic
        if topic.get_id() in self._all_topics:
            while (len(self._to_explain_stack) == 0
                   or self._to_explain_stack[-1] != topic):
                if len(self._to_explain_stack) > 0:
                    self._to_explain_stack.pop()
                else:
                    self.restart()
            while self._to_explain_stack[-1] not in self._flow:
                self._to_explain_stack.pop()
            self._to_explain_stack[-1].set_explained(True)

    def transfer_state(self, to: "ConversationFlow"):
        """Copies the flow state of another conversation.

        Author: Bruno.

        Parameters
        ----------
        to
            Iterator to transfer the current flow state.
        """
        to._to_explain_stack = self._to_explain_stack
