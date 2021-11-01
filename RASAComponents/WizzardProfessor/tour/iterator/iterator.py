import abc
from typing import Dict, List

from tour.topic.topics import Topic


class Iterator(metaclass=abc.ABCMeta):
    def __init__(self, flow: List[Topic], name: str = ""):
        self._name = name
        self._all_topics = {}
        # Obtains all the topics and examples that the tour contains.
        for topic in flow:
            self._all_topics.update(topic.get())

        self._flow = flow
        self._to_explain = [topic for topic in reversed(flow)]
        self._jump = None
        self._current_topic = None

    def in_tour(self, intent_name: str) -> bool:
        return intent_name in self._all_topics

    @abc.abstractmethod
    def next(self) -> str:
        raise NotImplementedError

    def get_current_topic(self) -> str:
        return self._current_topic

    def set_current_topic(self, topic: str):
        self._current_topic = topic

    def get_jump(self) -> bool:
        return self._jump

    def set_jump(self, jump: bool):
        self._jump = jump

    def repeat(self) -> str:
        return self._to_explain[-1].repeat

    def get_to_explain(self) -> List:
        return self._to_explain.copy()

    def get_intents_to_topic(self) -> Dict:
        return self._all_topics.copy()

    def is_older_topic(self, topic: Topic) -> bool:
        if topic in self._to_explain:
            return False
        else:
            return True

    def restart(self):
        self._to_explain = [topic for topic in reversed(self._flow)]
        for topic in self._to_explain:
            topic.restart()

    def get_last_topic(self) -> Topic:
        # Returns the next topic to the last topic explained(not subtopic)
        i = 1
        while self._to_explain[-i] not in self._flow:
            i += 1
        return self._to_explain[-i]

    def jump_to_topic(self, topic: Topic):
        # Jumps to the specified topic
        if topic.get_id() in self._all_topics:
            while len(self._to_explain) == 0 or self._to_explain[-1] != topic:
                if len(self._to_explain) > 0:
                    self._to_explain.pop()
                else:
                    self.restart()
            while self._to_explain[-1] not in self._flow:
                self._to_explain.pop()
            self._to_explain[-1].set_explained(True)
