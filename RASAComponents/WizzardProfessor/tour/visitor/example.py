from tour.iterator.iterator import Iterator
from tour.visitor.visitor import Visitor

AMT_EXAMPLE_NEUTRAL = 2


class Example(Visitor):

    def __init__(self, topic: str = None) -> None:
        self._topic = topic

    def visit_sequential(self, it: Iterator) -> str:
        example = self.search(it)
        if example is None:
            return it.get_intents_to_topic()[self._topic].get_example()
        return example

    def visit_global(self, it: Iterator) -> str:
        example = self.search(it)
        if example is None:
            example = it.get_intents_to_topic()[self._topic].get_example()
            it.get_intents_to_topic()[self._topic].set_current_example(0)
        return example

    def visit_neutral(self, it: Iterator) -> str:
        example = self.search(it)
        if example is None:
            example = it.get_intents_to_topic()[self._topic].get_example()
            if it.get_intents_to_topic()[self._topic].get_current_example() > AMT_EXAMPLE_NEUTRAL:
                it.get_intents_to_topic()[self._topic].set_current_example(0)
        return example

    def search(self, it: Iterator) -> str:
        if self._topic is None:
            return it.get_to_explain()[-1].get_example()
        else:
            if self._topic not in it.get_intents_to_topic():
                return "action_topic_not_recognized"
            else:
                return None
