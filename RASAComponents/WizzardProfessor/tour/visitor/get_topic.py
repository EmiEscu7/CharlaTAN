from RASAComponents.WizzardProfessor.tour.topic.topics import Topic
from RASAComponents.WizzardProfessor.tour.iterator.iterator import Iterator
from RASAComponents.WizzardProfessor.tour.visitor.visitor import Visitor


class GetTopic(Visitor):

    def __init__(self, topic: str, example: bool = None) -> None:
        self._topic = topic
        self._example = example

    def visit_sequential(self, it: Iterator) -> str:
        if it.is_older_topic(Topic(self._topic, [])):
            if it.get_jump() is None:
                it.set_current_topic(self._topic)
                return "utter_cross_examine_jump_sequential"
            else:
                return self.get_topic(it)
        else:
            return self.get_topic(it)

    def visit_global(self, it: Iterator) -> str:
        if not it.is_older_topic(Topic(self._topic, [])) and not it.get_to_explain()[-1].get_id() == self._topic:
            if it.get_jump() is None:
                it.set_current_topic(self._topic)
                return "utter_cross_examine_jump_global"
            else:
                return self.get_topic(it, it.get_jump())
        else:
            return self.get_topic(it)

    def visit_neutral(self, it: Iterator) -> str:
        return self.get_topic(it)

    def get_topic(self, it: Iterator, jump : bool = False) -> str:
        if it.is_older_topic(Topic(self._topic, [])):
            if self._example == None:
                it.set_current_topic(self._topic)
                return "utter_cross_examine_example"
        if self._topic not in it.get_intents_to_topic():
            return "action_topic_not_recognized"
        if jump:
            it.jump_to_topic(Topic(self._topic, []))
        if self._example == True:
            return it.get_intents_to_topic()[self._topic].get_example()
        return it.get_intents_to_topic()[self._topic].get_explanation()
